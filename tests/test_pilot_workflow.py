"""Pilot user workflows retain evidence and require an explicit target decision."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import unittest
from test_core import ChargeSession, State, CalibrationRecord, manager_module
from test_retention_completion import setup_manager, MemoryStore
from test_pilot_metering import trace
from test_rest_reference import points
from custom_components.battery_charge_manager import metering


def pilot_manager():
    manager, hass, commands = setup_manager()
    manager.session = ChargeSession()
    manager.energy_mode = 'power_reported'
    hass.states.values['switch.charger'] = State('off')
    return manager, hass, commands


class PilotWorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def test_pilot_starts_without_counter_but_checks_required_power(self):
        manager, hass, commands = pilot_manager()
        hass.states.values['sensor.energy'] = State('unavailable')
        await manager.async_start_calibration()
        self.assertTrue(manager.session.active)
        self.assertEqual(manager.session.energy_source, 'power_reported')
        self.assertEqual(manager.session.pilot['energy_basis'], 'gross')
        hass.states.values['sensor.power'] = State('unavailable')
        await manager._async_sample('heartbeat')
        self.assertFalse(manager.session.active)
        self.assertEqual(commands, ['turn_on', 'turn_off'])
        self.assertEqual(len(manager.calibrations), 1)

    async def test_counter_reset_is_diagnostic_and_no_automatic_end(self):
        manager, hass, commands = pilot_manager()
        await manager.async_start_calibration()
        hass.states.values['sensor.energy'] = State('0', {'unit_of_measurement': 'Wh'})
        await manager._async_sample('heartbeat')
        self.assertTrue(manager.session.active)
        self.assertTrue(manager.session.metering['counter_discontinuous'])
        # A low-power proposal never switches off a pilot calibration.
        manager.session.pilot['rest_reference'] = {'statistics': {'eligible': True, 'upper_power_w': .13, 'tolerance_w': .03}}
        manager.session.samples = points([1]*10+[.1]*41)
        manager.session.charge_started_at = manager.session.samples[0].timestamp
        manager.session.gross_energy_wh = .2
        manager.session.net_energy_wh = .2
        await manager._async_evaluate_session(datetime.fromisoformat(manager.session.samples[-1].timestamp))
        self.assertTrue(manager.session.active)
        self.assertEqual(manager.session.pilot['proposal']['status'], 'suggested')
        self.assertEqual(commands, ['turn_on'])

    async def test_rest_prepare_confirmation_finish_and_single_reference_approval(self):
        manager, _, commands = pilot_manager()
        await manager.async_prepare_rest_reference()
        self.assertIsNone(manager.session.pilot['confirmed_at'])
        await manager.async_confirm_rest_reference()
        self.assertIsNotNone(manager.session.pilot['confirmed_at'])
        samples = points([.1]*71)
        manager.session.samples = samples
        manager.session.pilot['confirmed_at'] = samples[0].timestamp
        manager.session.session_started_at = samples[0].timestamp
        manager.session.last_sample_at = samples[-1].timestamp
        await manager._async_evaluate_session(datetime.fromisoformat(samples[-1].timestamp))
        self.assertFalse(manager.session.active)
        record = next(iter(manager.rest_measurements.values()))
        self.assertTrue(record.statistics['eligible'])
        self.assertEqual(record.usage_approval, 'pending')
        self.assertIsNone(manager.rest_reference_summary()['reference'])
        await manager.async_set_usage_approval('rest', record.measurement_id, True, 'Reviewed USB end state', 1)
        self.assertEqual(manager.rest_reference_summary()['reference']['measurement_id'], record.measurement_id)
        self.assertEqual(commands, ['turn_on', 'turn_off'])
        manager.batteries['battery'].revision += 1
        self.assertIsNone(manager.rest_reference_summary()['reference'])
        self.assertIn('rest_measurements', manager.export_measurements())

    async def test_finish_is_not_a_charge_endpoint_and_approval_follows_review(self):
        manager, _, _ = pilot_manager()
        await manager.async_start_calibration()
        samples = trace(range(0, 3601, 30))
        manager.session.samples = samples
        manager.session.switch_on_at = manager.session.session_started_at = samples[0].timestamp
        manager.session.charge_started_at = samples[0].timestamp
        manager.session.last_sample_at = samples[-1].timestamp
        await manager.async_finish_calibration()
        record = next(iter(manager.calibrations.values()))
        self.assertIsNone(record.charge_finished_at)
        self.assertIsNone(record.charge_duration_seconds)
        self.assertEqual(record.usage_approval, 'pending')
        with self.assertRaises(manager_module.HomeAssistantError):
            await manager.async_set_usage_approval('calibration', record.calibration_id, True, 'review', 1)
        await manager.async_set_calibration_endpoint(record.calibration_id, samples[-1].timestamp,
            reason='Selected from trace and USB comparison', expected_analysis_revision=1)
        await manager.async_set_usage_approval('calibration', record.calibration_id, True, 'review', 2)
        self.assertAlmostEqual(manager.calibration_summary('setup', 'battery', 1)['median_net_energy_wh'], 2)
        self.assertEqual(record.usage_approval, 'approved')
        await manager.async_set_calibration_endpoint(record.calibration_id, samples[-2].timestamp,
            reason='refined boundary', expected_analysis_revision=2)
        self.assertEqual(record.usage_approval, 'pending')
        self.assertIsNone(manager.calibration_summary('setup', 'battery', 1)['median_net_energy_wh'])

    async def test_rest_stop_and_restart_retain_excluded_attempt(self):
        manager, _, _ = pilot_manager()
        await manager.async_prepare_rest_reference()
        await manager.async_stop()
        record = next(iter(manager.rest_measurements.values()))
        self.assertEqual(record.completion_status, 'aborted')
        self.assertEqual(record.usage_approval, 'pending')
        self.assertTrue(record.samples)
        await manager.async_prepare_rest_reference()
        await manager._async_resume_session()
        self.assertFalse(manager.session.active)
        self.assertEqual(len(manager.rest_measurements), 2)

    async def test_stale_approval_and_nonfinite_usb_rejected(self):
        manager, _, _ = pilot_manager()
        record = CalibrationRecord.from_dict(dict(calibration_id='r', setup_id='setup', battery_id='battery'))
        manager.calibrations['r'] = record
        with self.assertRaises(manager_module.HomeAssistantError):
            await manager.async_set_usage_approval('calibration', 'r', True, 'review', 0)
        with self.assertRaises(manager_module.HomeAssistantError):
            await manager.async_set_usb_comparison('r', float('nan'), 'full run', 1)

    async def test_normal_pilot_charge_aborts_on_real_recording_gap(self):
        from unittest.mock import patch
        manager, hass, commands = pilot_manager()
        manager.session = ChargeSession(mode='charging',session_id='run', setup_id='setup',battery_id='battery',
            energy_source='power_reported',target_energy_wh=3,session_started_at=manager._now_iso())
        hass.states.values['switch.charger'] = State('on')
        await manager._async_sample('heartbeat')
        later = datetime.now(timezone.utc)+timedelta(minutes=3)
        with patch.object(manager_module.dt_util, 'utcnow', return_value=later):
            await manager._async_sample('heartbeat')
        self.assertFalse(manager.session.active)
        self.assertEqual(commands, ['turn_off'])

    async def test_rest_archive_reopen_export_and_raw_page_preserve_evidence(self):
        from pathlib import Path
        from types import SimpleNamespace
        import tempfile
        import json
        from test_core import BatteryChargeManager, ConfigEntry
        manager, hass, _ = pilot_manager()
        with tempfile.TemporaryDirectory() as folder:
            hass.config = SimpleNamespace(path=lambda *p: str(Path(folder).joinpath(*p)),time_zone='UTC')
            await manager._async_open_archive({})
            await manager.async_prepare_rest_reference()
            original = deepcopy([p.as_dict() for p in manager.session.samples])
            await manager.async_stop()
            record = next(iter(manager.rest_measurements.values()))
            info = manager.archive.trace_info(record.trace_id)
            restored = BatteryChargeManager(hass, ConfigEntry())
            restored.store = MemoryStore()
            await restored.async_load()
            again = restored.rest_measurements[record.measurement_id]
            self.assertEqual(restored.archive.trace_info(again.trace_id), info)
            self.assertTrue(restored.archive.verify_trace(again.trace_id))
            page = await restored.async_raw_measurement_page('rest',again.measurement_id,0,100)
            self.assertEqual(page['samples'], original)
            exported = json.loads(''.join(await restored.async_archive_export()))
            self.assertEqual(exported['rest_measurements'][0]['usage_approval'],'pending')
            self.assertEqual(exported['schema_version'],6)

    async def test_pilot_target_retains_source_basis_and_no_load_reference(self):
        from test_core import IdleMeasurement
        from pilot_fixtures import reviewed
        manager, hass, _ = pilot_manager()
        manager.energy_basis = 'no_load_corrected'
        manager.idle_measurements['i'] = IdleMeasurement('i','setup',1,manager.active_setup.snapshot(),reliable=True,average_power_w=.1)
        record = CalibrationRecord.from_dict(dict(calibration_id='r',setup_id='setup',battery_id='battery',
            ports=['A'],energy_source='power_reported',energy_basis='no_load_corrected',idle_measurement_ids=['i'],
            metering_comparison={'reported_complete':True,'power_estimate_gross_wh':2,'power_estimate_net_wh':1.9},
            pilot={'energy_basis':'no_load_corrected','idle_reference':manager.idle_summary('setup')}))
        manager.calibrations['r'] = reviewed(manager,record)
        await manager.async_start_charge()
        self.assertEqual(manager.session.target_energy_wh,.95)
        self.assertEqual(manager.session.idle_baseline_power_w,.1)
        await manager.async_set_energy_basis('gross')
        await manager.async_set_energy_mode('meter')
        self.assertEqual(manager.session.energy_source,'power_reported')
        self.assertEqual(manager.session.pilot['energy_basis'],'no_load_corrected')
        self.assertEqual(manager.session.target_energy_wh,.95)

    async def test_approval_fingerprint_survives_serialized_precision(self):
        from pilot_fixtures import reviewed
        manager, _, _ = pilot_manager()
        record = CalibrationRecord.from_dict(dict(calibration_id='r',setup_id='setup',battery_id='battery',
            idle_baseline_power_w=1/3,energy_source='power_reported',energy_basis='gross',
            metering_comparison={'reported_complete':True,'power_estimate_net_wh':2,'power_estimate_gross_wh':2}))
        reviewed(manager,record)
        self.assertTrue(manager._usage_current(record))
        restored = CalibrationRecord.from_dict(record.as_dict())
        self.assertTrue(manager._usage_current(restored))
