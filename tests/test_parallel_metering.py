from datetime import datetime, timedelta, timezone
import unittest

from test_core import MeasurementSample
from custom_components.battery_charge_manager import metering


class ParallelMeteringTests(unittest.TestCase):
    def test_power_integral_uses_previous_value_and_keeps_apparent_separate(self):
        state = {}
        metering.advance(state, 0, 2.2, 230, .03)
        metering.advance(state, 60, 0, 230, .03)
        self.assertAlmostEqual(state['power_wh'], 2.2 / 60)
        self.assertAlmostEqual(state['apparent_vah'], 6.9 / 60)
        self.assertTrue(state['power_valid'])

    def test_gap_and_restart_never_invent_energy(self):
        state = {}
        metering.advance(state, 0, 2, None, None)
        metering.advance(state, 600, 2, None, None)
        self.assertEqual(state['power_wh'], 0)
        self.assertFalse(state['power_valid'])
        state = {}
        metering.advance(state, 0, 2, None, None)
        metering.advance(state, 30, 2, None, None, restart=True)
        self.assertFalse(state['power_valid'])
        self.assertEqual(state['power_wh'], 0)

    def test_stale_nan_and_missing_power_are_not_usable(self):
        for value, fresh in [(float('nan'), True), (None, True), (2, False)]:
            state = {}
            metering.advance(state, 0, value, None, None, fresh=fresh)
            metering.advance(state, 30, 2, None, None)
            self.assertEqual(state['covered_seconds'], 0)

    def test_old_samples_have_no_fabricated_parallel_values(self):
        sample = MeasurementSample.from_dict({'timestamp': '2026-09-13T00:00:00Z'})
        self.assertIsNone(sample.power_energy_wh)
        self.assertIsNone(sample.apparent_energy_vah)

    def report(self, power=5.5, step=1, eligible=True):
        return {'meter_net_wh': 6, 'power_net_wh': power,
                'power_eligible': eligible, 'meter_step_wh': step,
                'power_step_wh': .05, 'reason': 'usable'}

    def test_requires_three_calibrations_and_never_selects_apparent(self):
        self.assertEqual(metering.select_source([self.report()] * 2)['source'], 'meter')
        result = metering.select_source([self.report()] * 3)
        self.assertEqual(result['source'], 'power')
        self.assertEqual(result['median_net_wh'], 5.5)

    def test_fine_meter_bad_coverage_and_disagreement_keep_meter(self):
        for report in [self.report(step=.01), self.report(eligible=False), self.report(power=2)]:
            self.assertEqual(metering.select_source([report] * 3)['source'], 'meter')

    def test_variable_power_results_do_not_gain_trust_from_smoothness(self):
        reports = [self.report(power=p) for p in (4.5, 5.5, 7)]
        self.assertEqual(metering.select_source(reports)['source'], 'meter')

    def test_endpoint_excludes_confirmation_tail_and_keeps_coarse_counter(self):
        start = datetime(2026, 9, 13, tzinfo=timezone.utc)
        samples = [MeasurementSample(
            timestamp=(start + timedelta(seconds=i * 30)).isoformat(),
            raw_energy_wh=int(i / 60), gross_energy_wh=int(i / 60),
            power_w=2, power_energy_wh=i / 60, apparent_energy_vah=i / 20,
            power_integral_valid=True, power_report_fresh=True,
            metering_quality={'covered_seconds': i * 30, 'meter_step_wh': 1,
                'max_power_step_wh': 2 / 120, 'report_count': i + 1,
                'max_report_interval_seconds': 30},
        ) for i in range(181)]
        report = metering.compare(samples, samples[120].timestamp, 0)
        self.assertEqual(report['power_net_wh'], 2)
        self.assertEqual(report['apparent_energy_vah'], 6)
        self.assertTrue(report['power_eligible'])
        self.assertEqual(report['meter_step_wh'], 1)

from unittest.mock import AsyncMock, patch
from test_core import (
    BatteryChargeManager, BatteryType, CalibrationRecord, ChargerSetup,
    ChargeSession, ConfigEntry, FakeHass, IdleMeasurement, State,
)


class ParallelManagerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.manager = BatteryChargeManager(FakeHass(), ConfigEntry())
        self.setup = ChargerSetup('s', 'Charger', 'switch.s', 'sensor.e', power_sensor='sensor.p')
        self.manager.setups['s'] = self.setup
        self.manager.batteries['b'] = BatteryType('b', 'AA', 1700, 'Li-Ion', 'AA')
        self.manager.selected_setup_id = 's'
        self.manager.selected_battery_id = 'b'
        self.manager.idle_measurements['i'] = IdleMeasurement(
            'i', 's', 1, self.setup.snapshot(), reliable=True, average_power_w=0)
        self.start = datetime(2026, 9, 13, tzinfo=timezone.utc)
        self.manager.hass.states.values.update({
            'switch.s': State('on'), 'sensor.e': State('0', {'unit_of_measurement': 'Wh'}),
            'sensor.p': State('2', {'unit_of_measurement': 'W'}),
        })
        self.manager.hass.states.values['sensor.p'].last_reported = self.start
        self.manager._async_evaluate_session = AsyncMock(return_value=False)
        self.manager._async_switch_off_checked = AsyncMock(return_value=True)
        self.manager._async_switch_on_checked = AsyncMock()

    def session(self, source='meter'):
        self.manager.session = ChargeSession(
            mode='charging', setup_id='s', battery_id='b', energy_source=source,
            session_started_at=self.start.isoformat(), switch_on_at=self.start.isoformat(),
            last_raw_energy_wh=0, idle_baseline_power_w=0, target_energy_wh=3)

    async def sample(self, seconds, source='heartbeat'):
        with patch('custom_components.battery_charge_manager.manager.dt_util.utcnow',
                   return_value=self.start + timedelta(seconds=seconds)):
            await self.manager._async_sample(source)

    async def test_parallel_power_continues_between_counter_steps(self):
        self.session('power')
        await self.sample(0)
        await self.sample(30)
        self.assertAlmostEqual(self.manager.session.gross_energy_wh, 2 / 120)
        self.assertEqual(self.manager.session.metering['meter_wh'], 0)
        self.assertAlmostEqual(self.manager.session.samples[-1].power_energy_wh, 2 / 120)

    async def test_meter_remains_default_and_power_survives_serialization(self):
        self.session()
        await self.sample(0)
        await self.sample(30)
        self.assertEqual(self.manager.session.gross_energy_wh, 0)
        restored = ChargeSession.from_dict(self.manager.session.as_dict())
        self.assertAlmostEqual(restored.metering['power_wh'], 2 / 120)

    async def test_power_session_stops_on_gap_instead_of_switching_source(self):
        self.session('power')
        await self.sample(0)
        await self.sample(300)
        self.assertFalse(self.manager.session.active)
        self.assertIn('power', self.manager.session.end_reason.lower())

    async def test_backward_counter_still_aborts(self):
        self.session('power')
        self.manager.session.last_raw_energy_wh = 1
        await self.sample(0)
        self.assertFalse(self.manager.session.active)

    async def test_resuming_power_session_aborts(self):
        self.session('power')
        await self.manager._async_resume_session()
        self.assertFalse(self.manager.session.active)

    def calibrate(self, count=3):
        for i in range(count):
            self.manager.calibrations[str(i)] = CalibrationRecord(
                str(i), 's', 1, self.setup.snapshot(), 'b', 1,
                self.manager.batteries['b'].snapshot(), 1, ['A'],
                net_energy_wh=6, gross_energy_wh=6, confidence='high',
                idle_measurement_ids=['i'],
                metering_comparison={'power_eligible': True, 'meter_net_wh': 6,
                    'power_net_wh': 5.5, 'meter_step_wh': 1, 'power_step_wh': .02})

    async def test_selected_calibration_and_live_target_use_same_source(self):
        self.calibrate()
        summary = self.manager.calibration_summary('s', 'b', 1)
        self.assertEqual(summary['energy_source'], 'power')
        self.assertEqual(summary['median_net_energy_wh'], 5.5)
        self.manager.hass.states.values['switch.s'] = State('off')
        async def turn_on(_setup):
            self.manager.hass.states.values['switch.s'] = State('on')
        self.manager._async_switch_on_checked = turn_on
        await self.manager.async_start_charge()
        self.assertEqual(self.manager.session.energy_source, 'power')
        self.assertEqual(self.manager.session.target_energy_wh, 2.75)
        self.assertEqual(len(self.manager.session.source_decision['record_ids']), 3)

    def test_excluded_and_different_quantity_records_do_not_enter_source_target(self):
        self.calibrate()
        self.manager.calibrations['2'].valid = False
        self.assertEqual(self.manager.calibration_summary('s', 'b', 1)['record_ids'], ['0','1'])
        self.manager.calibrations['2'].valid = True
        self.manager.calibrations['2'].quantity = 2
        self.assertEqual(self.manager.calibration_summary('s', 'b', 1)['record_ids'], ['0','1'])

    async def test_voltage_and_current_are_diagnostics_only(self):
        self.setup.voltage_sensor = 'sensor.v'
        self.setup.current_sensor = 'sensor.a'
        self.manager.hass.states.values['sensor.v'] = State('230', {'unit_of_measurement': 'V'})
        self.manager.hass.states.values['sensor.a'] = State('30', {'unit_of_measurement': 'mA'})
        self.session('power')
        await self.sample(0)
        await self.sample(30)
        self.assertAlmostEqual(self.manager.session.metering['apparent_vah'], 6.9 / 120)
        self.assertAlmostEqual(self.manager.session.gross_energy_wh, 2 / 120)


class MeteringEvidenceTests(unittest.TestCase):
    def trace(self, report_period=30, first_seconds=0):
        from copy import deepcopy
        start = datetime(2026, 9, 13, tzinfo=timezone.utc)
        state = {}
        result = []
        for seconds in range(first_seconds, 7201, 30):
            metering.advance(state, seconds, 2, 230, .03,
                             reported_at=seconds // report_period * report_period,
                             raw_energy=int(seconds / 1800))
            result.append(MeasurementSample(
                timestamp=(start + timedelta(seconds=seconds)).isoformat(),
                gross_energy_wh=int(seconds / 1800), raw_energy_wh=int(seconds / 1800),
                power_w=2, power_energy_wh=state['power_wh'],
                power_integral_valid=state['power_valid'], power_report_fresh=True,
                metering_quality=deepcopy(state)))
        return start, result

    def test_heartbeats_do_not_turn_slow_sensor_reports_into_good_coverage(self):
        start, trace = self.trace(report_period=300)
        report = metering.compare(trace, trace[-1].timestamp, 0, start.isoformat())
        self.assertFalse(report['power_eligible'])
        self.assertEqual(report['max_report_interval_seconds'], 300)

    def test_compacted_trace_has_identical_endpoint_evidence(self):
        start, trace = self.trace()
        full = metering.compare(trace, trace[-1].timestamp, 0, start.isoformat())
        compact = metering.compare(trace[::8], trace[-1].timestamp, 0, start.isoformat())
        self.assertTrue(full['power_eligible'])
        self.assertEqual(full, compact)

    def test_idle_correction_uses_switch_on_not_first_observation(self):
        start, trace = self.trace(first_seconds=30)
        report = metering.compare(trace, trace[-1].timestamp, .2, start.isoformat())
        self.assertAlmostEqual(report['power_net_wh'], trace[-1].power_energy_wh - .2 * trace[-1].metering_quality['covered_seconds'] / 3600)
        self.assertAlmostEqual(report['idle_energy_wh'], .4)
        self.assertAlmostEqual(report['meter_net_wh'], 3.6)

    def test_parallel_sample_and_record_evidence_roundtrip(self):
        _, trace = self.trace()
        sample = trace[-1]
        self.assertEqual(MeasurementSample.from_dict(sample.as_dict()).as_dict(), sample.as_dict())
        record = CalibrationRecord('c','s',1,{},'b',1,{},1,['A'],
                                   metering_comparison={'power_eligible': True, 'power_net_wh': 3.6})
        self.assertEqual(CalibrationRecord.from_dict(record.as_dict()).metering_comparison,
                         record.metering_comparison)

class PowerStartupTests(unittest.IsolatedAsyncioTestCase):
    setUp = ParallelManagerTests.setUp
    session = ParallelManagerTests.session
    sample = ParallelManagerTests.sample

    async def test_old_off_reading_waits_for_first_fresh_report(self):
        self.session('power')
        old = self.manager.hass.states.values['sensor.p']
        old.last_reported = self.start - timedelta(hours=1)
        await self.sample(0)
        self.assertTrue(self.manager.session.active)
        fresh = State('2', {'unit_of_measurement': 'W'})
        fresh.last_reported = self.start + timedelta(seconds=30)
        self.manager.hass.states.values['sensor.p'] = fresh
        await self.sample(30)
        await self.sample(60)
        self.assertTrue(self.manager.session.active)
        self.assertAlmostEqual(self.manager.session.gross_energy_wh, 2 / 120)

    async def test_stale_report_after_good_start_aborts(self):
        self.session('power')
        self.manager.hass.states.values['sensor.p'].last_reported = self.start
        for seconds in range(0, 151, 30):
            await self.sample(seconds)
        self.assertFalse(self.manager.session.active)

    async def test_first_fresh_report_after_deadline_cannot_bypass_timeout(self):
        self.session('power')
        state = self.manager.hass.states.values['sensor.p']
        state.last_reported = self.start - timedelta(hours=1)
        for seconds in range(0, 121, 30):
            await self.sample(seconds)
        state.last_reported = self.start + timedelta(seconds=121)
        await self.sample(121)
        self.assertFalse(self.manager.session.active)

    async def test_no_first_fresh_report_times_out(self):
        self.session('power')
        self.manager.hass.states.values['sensor.p'].last_reported = self.start - timedelta(hours=1)
        for seconds in range(0, 151, 30):
            await self.sample(seconds)
        self.assertFalse(self.manager.session.active)

class ParallelCutoffTests(unittest.IsolatedAsyncioTestCase):
    setUp = ParallelManagerTests.setUp
    session = ParallelManagerTests.session
    sample = ParallelManagerTests.sample

    async def test_integrated_power_cuts_off_between_wh_meter_updates(self):
        self.session('power')
        self.manager.session.target_energy_wh = .01
        self.manager._async_evaluate_session = BatteryChargeManager._async_evaluate_session.__get__(self.manager)
        await self.sample(0)
        await self.sample(30)
        self.assertFalse(self.manager.session.active)
        self.assertEqual(self.manager.session.end_reason, 'Target energy reached')
        self.assertEqual(self.manager.session.metering['meter_wh'], 0)
        self.assertEqual(self.manager.charge_history[-1]['energy_source'], 'power')

    async def test_complete_calibration_stores_same_endpoint_comparison(self):
        start, trace = MeteringEvidenceTests().trace()
        self.manager.session = ChargeSession(
            mode='calibrating', comment='USB reference', comment_history=[{'comment': 'USB reference'}], setup_id='s', battery_id='b', quantity=1, ports=['A'],
            session_started_at=start.isoformat(), switch_on_at=start.isoformat(),
            charge_started_at=start.isoformat(), candidate_end_at=trace[-1].timestamp,
            candidate_end_net_energy_wh=4, candidate_end_gross_energy_wh=4,
            gross_energy_wh=4, net_energy_wh=4, idle_baseline_power_w=0,
            idle_measurement_ids=['i'], samples=trace)
        record = await self.manager._async_complete_calibration(automatic=True, reason='done')
        self.assertEqual(record.comment, 'USB reference')
        self.assertEqual(record.comment_history, [{'comment': 'USB reference'}])
        self.assertTrue(record.metering_comparison['power_eligible'])
        self.assertAlmostEqual(record.metering_comparison['power_net_wh'], 4)
        self.manager._apply_idle_correction(record, baseline=.1, measurement_ids=['i'], quality='stable')
        self.assertAlmostEqual(record.metering_comparison['power_net_wh'], 3.8)
        self.assertAlmostEqual(record.analysis_history[-1]['metering_comparison']['power_net_wh'], 4)
