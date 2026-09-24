"""Completion must never confuse retaining a run with accepting a calibration."""
from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from test_core import (BatteryChargeManager, BatteryType, ChargerSetup, ChargeSession,
                       ConfigEntry, FakeHass, MeasurementSample, State)


class MemoryStore:
    def __init__(self, data=None):
        self.data = deepcopy(data or {})
    async def async_load(self):
        return deepcopy(self.data)
    async def async_save(self, data):
        self.data = deepcopy(data)


def setup_manager():
    hass = FakeHass()
    manager = BatteryChargeManager(hass, ConfigEntry())
    setup = ChargerSetup('setup', 'Setup', 'switch.charger', 'sensor.energy', power_sensor='sensor.power')
    battery = BatteryType('battery', '3 Wh cell', None, 'Li-Ion', 'AA', nominal_energy_wh=3)
    manager.setups['setup'] = setup
    manager.batteries['battery'] = battery
    manager.selected_setup_id = 'setup'
    manager.selected_battery_id = 'battery'
    hass.states.values.update({'switch.charger': State('on'),
                              'sensor.energy': State('18', {'unit_of_measurement': 'Wh'}),
                              'sensor.power': State('0.2', {'unit_of_measurement': 'W'})})
    commands = []
    class Services:
        async def async_call(self, domain, service, data, **kwargs):
            commands.append(service)
            hass.states.values[data['entity_id']] = State('on' if service == 'turn_on' else 'off')
    hass.services = Services()
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=10)
    points = [MeasurementSample(start.isoformat(), power_w=2, net_power_w=2, power_estimate_wh=0),
              MeasurementSample(now.isoformat(), power_w=.2, net_power_w=.2,
                                power_estimate_wh=5.75, power_energy_wh=1.35)]
    manager.session = ChargeSession(
        session_id='run', setup_id='setup', battery_id='battery', mode='calibrating',
        session_started_at=start.isoformat(), switch_on_at=start.isoformat(),
        charge_started_at=start.isoformat(), last_sample_at=now.isoformat(),
        last_significant_at=now.isoformat(), idle_baseline_power_w=0,
        source_decision={'mode': 'auto'}, samples=points,
    )
    manager.store = MemoryStore()
    return manager, hass, commands


class RetentionCompletionTests(unittest.IsolatedAsyncioTestCase):
    async def test_manual_zero_meter_and_incomplete_power_finishes_and_retains(self):
        manager, hass, commands = setup_manager()
        raw = deepcopy([s.as_dict() for s in manager.session.samples])
        await manager.async_finish_calibration()
        self.assertEqual(commands, ['turn_off'])
        self.assertFalse(manager.session.active)
        self.assertEqual(len(manager.calibrations), 1)
        record = next(iter(manager.calibrations.values()))
        self.assertEqual([s.as_dict() for s in record.samples], raw)
        self.assertFalse(manager._record_source_choice(record).get('source'))
        self.assertEqual(record.completion_status, 'manual_unusable')
        await manager.async_finish_calibration()
        self.assertEqual(len(manager.calibrations), 1)
        self.assertEqual(commands, ['turn_off'])

    async def test_stop_retains_visible_attempt_and_never_makes_it_eligible(self):
        manager, _, commands = setup_manager()
        await manager.async_stop()
        await manager.async_stop()
        rows = manager.frontend_state()['calibrations']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['completion_status'], 'aborted')
        self.assertFalse(rows[0]['used'])
        self.assertTrue(rows[0]['has_trace'])
        record = next(iter(manager.calibrations.values()))
        record.valid = True  # a validity annotation must not bypass incomplete evidence
        self.assertIsNone(manager._record_source_choice(record)['source'])
        self.assertEqual(commands, ['turn_off'])

    async def test_every_burst_sample_and_all_histories_remain(self):
        manager, _, _ = setup_manager()
        manager.session.samples = []
        start = datetime.now(timezone.utc)
        for i in range(10_001):
            manager._append_sample(MeasurementSample((start + timedelta(milliseconds=i)).isoformat(), power_w=0), 'state_change')
        self.assertEqual(len(manager.session.samples), 10_001)
        full_trace = manager.session.samples
        manager.session.samples = full_trace[:2]
        for i in range(121):
            manager.session.session_id = f'run-{i}'
            manager._append_charge_history(valid=False, reason='retained')
        manager.session.samples = full_trace
        await manager._async_save()
        self.assertEqual(len(manager.store.data['charge_history']), 121)
        self.assertEqual(len(manager.store.data['session']['samples']), 10_001)

    async def test_legacy_stopped_run_migrates_visible_and_raw_unchanged(self):
        manager, hass, _ = setup_manager()
        await manager.async_stop()
        # Simulate precisely the v0.4.1 shape: history + current, no visible calibration.
        legacy = deepcopy(manager.store.data)
        legacy['calibrations'] = []
        points = legacy['session']['samples']
        points[0]['unknown_original'] = {'keep': 'exactly'}
        legacy['charge_history'][0]['session']['samples'] = deepcopy(points)
        with tempfile.TemporaryDirectory() as folder:
            hass.config = SimpleNamespace(path=lambda *p: str(Path(folder).joinpath(*p)), time_zone='UTC')
            hass.async_add_executor_job = lambda fn, *a: asyncio.to_thread(fn, *a)
            restored = BatteryChargeManager(hass, ConfigEntry())
            restored.store = MemoryStore(legacy)
            await restored.async_load()
            self.assertEqual(len(restored.calibrations), 1)
            record = next(iter(restored.calibrations.values()))
            self.assertEqual(record.archived_sample_count, 2)
            self.assertEqual(restored.archive.read_samples(record.trace_id), points)
            self.assertFalse(record.samples, 'Historic traces should be loaded on demand')
            detail = await restored.async_measurement_details('calibration', record.calibration_id)
            self.assertEqual(detail['sample_count'], 2)
            self.assertTrue(detail['chart_samples'])
            self.assertFalse(record.samples)
            again = BatteryChargeManager(hass, ConfigEntry())
            again.store = MemoryStore(legacy)
            await again.async_load()
            self.assertEqual(len(again.calibrations), 1)
            self.assertEqual(again.archive.read_samples(record.trace_id), points)

    async def test_concurrent_stop_and_finish_create_one_record(self):
        manager, _, commands = setup_manager()
        await asyncio.gather(manager.async_finish_calibration(), manager.async_stop())
        self.assertEqual(commands, ['turn_off'])
        self.assertEqual(len(manager.calibrations), 1)
        self.assertEqual(len(manager.charge_history), 1)

    async def test_storage_failure_stops_and_preserves_in_memory_trace(self):
        from unittest.mock import patch
        from custom_components.battery_charge_manager.archive import RawArchive
        manager, _, commands = setup_manager()
        with tempfile.TemporaryDirectory() as folder:
            manager.archive = RawArchive(Path(folder) / 'raw.sqlite')
            manager.archive.initialize()
            original = deepcopy(manager.session.samples)
            with patch.object(manager.archive, 'append_samples', side_effect=OSError('disk full')):
                with self.assertRaisesRegex(Exception, 'saved'):
                    await manager._async_save()
            self.assertEqual(commands, ['turn_off'])
            self.assertEqual(manager.session.samples, original)
            self.assertFalse(manager.session.active)
            with self.assertRaisesRegex(Exception, 'archive'):
                manager._ensure_idle()
            self.assertTrue(manager.charge_history)

    async def test_missing_battery_context_cannot_prevent_shutdown(self):
        manager, _, commands = setup_manager()
        manager.batteries.clear()
        try:
            await manager.async_finish_calibration()
        except Exception:
            pass
        self.assertEqual(commands, ['turn_off'])
        self.assertFalse(manager.session.active)
        self.assertTrue(manager.charge_history)

    async def test_new_charge_cannot_start_inside_an_endpoint_revision(self):
        manager, _, _ = setup_manager()
        await manager.async_stop()
        record=next(iter(manager.calibrations.values()))
        entered=asyncio.Event();proceed=asyncio.Event();started=[]
        async def hydrate(_): entered.set();await proceed.wait()
        manager._async_hydrate=hydrate
        async def begin(**_):started.append(True)
        manager._async_begin_session=begin
        editing=asyncio.create_task(manager.async_set_calibration_endpoint(record.calibration_id,record.samples[-1].timestamp,
            reason='Documented endpoint',expected_analysis_revision=1))
        await entered.wait()
        starting=asyncio.create_task(manager.async_start_calibration())
        await asyncio.sleep(.01)
        self.assertFalse(started,'Starting while analysis is awaiting disk corrupts context')
        proceed.set();await editing;await starting
        self.assertEqual(started,[True])

    async def test_stopped_idle_measurement_is_visible_but_not_a_baseline(self):
        manager,_,_=setup_manager();manager.session.mode='idle_measuring'
        manager.session.battery_id=None
        await manager.async_stop()
        self.assertEqual(len(manager.idle_measurements),1)
        r=next(iter(manager.idle_measurements.values()))
        self.assertEqual(r.completion_status,'aborted')
        self.assertFalse(r.valid);self.assertFalse(r.reliable)
        self.assertTrue(r.samples or r.archived_sample_count)
