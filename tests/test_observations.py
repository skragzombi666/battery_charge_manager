"""Reported values must survive async queueing, including identical and invalid receipts."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import importlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from test_core import MeasurementSample, State
from test_retention_completion import setup_manager
from custom_components.battery_charge_manager import metering


class ObservationTests(unittest.IsolatedAsyncioTestCase):
    async def test_reports_capture_values_before_waiting_for_sample_lock(self):
        manager, hass, _ = setup_manager()
        manager.session.samples = []
        manager.session.metering = {}
        now = datetime.now(timezone.utc)
        manager.session.session_started_at = manager.session.switch_on_at = now.isoformat()
        manager.session.charge_started_at = None
        one = State('2.1', {'unit_of_measurement': 'W'})
        one.last_reported = now
        two = State('1.8', {'unit_of_measurement': 'W'})
        two.last_reported = now + timedelta(milliseconds=1)
        await manager._sample_lock.acquire()
        try:
            hass.states.values['sensor.power'] = one
            first = manager._async_state_changed(SimpleNamespace(
                event_type='state_changed', data={'entity_id': 'sensor.power', 'new_state': one}))
            hass.states.values['sensor.power'] = two
            second = manager._async_state_changed(SimpleNamespace(
                event_type='state_changed', data={'entity_id': 'sensor.power', 'new_state': two}))
            # Both observations have been captured synchronously; callbacks return tasks.
            await asyncio.sleep(.002)
        finally:
            manager._sample_lock.release()
        await asyncio.gather(first, second)
        self.assertEqual([p.power_w for p in manager.session.samples], [2.1, 1.8])
        self.assertEqual(manager.session.samples[0].provenance['event_type'], 'state_changed')
        self.assertEqual(manager.session.samples[0].provenance['states']['sensor.power']['state'], '2.1')

    async def test_unchanged_report_is_retained_and_distinguished_from_heartbeat(self):
        manager, hass, _ = setup_manager()
        manager.session.samples = []
        now = datetime.now(timezone.utc)
        manager.session.session_started_at = manager.session.switch_on_at = now.isoformat()
        manager.session.charge_started_at = None
        state = State('1.8', {'unit_of_measurement': 'W'})
        state.last_reported = now
        hass.states.values['sensor.power'] = state
        event = SimpleNamespace(event_type='state_reported', data={
            'entity_id': 'sensor.power', 'new_state': state,
            'last_reported': now, 'old_last_reported': now-timedelta(seconds=30)})
        await manager._async_state_changed(event)
        await manager._async_sample('heartbeat')
        self.assertEqual(len(manager.session.samples), 2)
        first, last = manager.session.samples
        self.assertEqual(first.provenance['event_type'], 'state_reported')
        self.assertEqual(last.provenance['event_type'], 'heartbeat')
        self.assertFalse(last.provenance['new_report'])
        self.assertEqual(first.provenance['states']['sensor.power']['last_reported'], now.isoformat())

    async def test_invalid_report_is_archived_before_safe_abort(self):
        from custom_components.battery_charge_manager.archive import RawArchive
        manager, hass, commands = setup_manager()
        with tempfile.TemporaryDirectory() as folder:
            manager.archive = RawArchive(Path(folder) / 'raw.sqlite')
            manager.archive.initialize()
            manager.session.trace_id = 'session:run'
            bad = State('unavailable', {'unit_of_measurement': 'W', 'diagnostic': 'lost'})
            hass.states.values['sensor.power'] = bad
            await manager._async_state_changed(SimpleNamespace(
                event_type='state_changed', data={'entity_id': 'sensor.power', 'new_state': bad}))
            self.assertEqual(commands, ['turn_off'])
            self.assertEqual(manager.archive.trace_info('session:run')['event_count'], 1)
            import json
            exported = json.loads(''.join(manager.archive.iter_export({})))
            event = exported['raw_archive']['traces'][0]['events'][0]
            self.assertEqual(event['states']['sensor.power']['state'], 'unavailable')
            self.assertEqual(event['states']['sensor.power']['attributes']['diagnostic'], 'lost')
            self.assertFalse(manager.session.active)

    def test_partial_integral_subtracts_idle_only_for_covered_time(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        points = [MeasurementSample(start.isoformat()), MeasurementSample(
            (start+timedelta(hours=10)).isoformat(), power_energy_wh=1.35,
            power_estimate_wh=5.75, meter_energy_wh=0,
            metering_quality={'covered_seconds': 3600, 'estimate_covered_seconds': 36000})]
        report = metering.compare(points, points[-1].timestamp, .1)
        self.assertAlmostEqual(report['power_net_wh'], 1.25)
        self.assertAlmostEqual(report['power_estimate_net_wh'], 4.75)
        self.assertAlmostEqual(report['power_idle_energy_wh'], .1)
        self.assertFalse(report['power_complete'])

    def test_sample_roundtrip_keeps_unknown_fields_and_full_precision(self):
        raw = {'timestamp': '2026-01-01T00:00:00+00:00', 'gross_energy_wh': .123456789123,
               'extra_device_field': {'value': 123}, 'provenance': {'new_report': False}}
        result = MeasurementSample.from_dict(raw).as_dict()
        for key, value in raw.items():
            self.assertEqual(result[key], value)

    def test_integration_records_interval_acceptance_and_gap_reason(self):
        state = {}
        metering.advance(state, 0, 2, None, None, reported_at=0)
        metering.advance(state, 30, 2, None, None, reported_at=30)
        self.assertAlmostEqual(state['last_interval']['accepted_seconds'], 30)
        metering.advance(state, 300, 2, None, None, reported_at=30, fresh=False)
        self.assertEqual(state['last_interval']['reason'], 'sample_gap')
        self.assertEqual(state['last_interval']['accepted_seconds'], 0)
