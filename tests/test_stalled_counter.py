"""A zero counter delta is not zero consumption and not permission to trust gaps."""
from copy import deepcopy
from unittest.mock import AsyncMock
import unittest
from test_core import ChargeSession
import test_parallel_metering as parallel
from custom_components.battery_charge_manager import energy_policy, metering


class StalledCounterPolicyTests(unittest.TestCase):
    def report(self, **changes):
        result = dict(meter_net_wh=0, meter_gross_wh=0, meter_step_wh=None,
            power_net_wh=3.16, power_step_wh=.02, power_complete=True,
            max_report_interval_seconds=30)
        result.update(changes)
        return result

    def test_auto_uses_complete_resolved_integration_for_zero_counter_delta(self):
        result = energy_policy.choose(self.report(), 'auto')
        self.assertEqual(result['source'], 'power')
        self.assertEqual(result['reason'], 'counter_not_advancing')
        self.assertFalse(result['absolute_accuracy_known'])

    def test_forced_counter_never_silently_switches(self):
        self.assertIsNone(energy_policy.choose(self.report(), 'meter')['source'])

    def test_estimated_or_coarse_integration_cannot_replace_counter_automatically(self):
        for changes in [dict(power_complete=False, power_estimate_net_wh=3.16, estimate_complete=True),
                        dict(power_step_wh=1), dict(max_report_interval_seconds=600),
                        dict(power_net_wh=None)]:
            with self.subTest(changes=changes):
                self.assertIsNone(energy_policy.choose(self.report(**changes), 'auto')['source'])

    def test_positive_conflicting_counter_is_not_treated_as_stalled(self):
        for changes in [dict(meter_net_wh=1, meter_gross_wh=1),
                        dict(meter_net_wh=0, meter_gross_wh=.1)]:
            self.assertIsNone(energy_policy.choose(self.report(**changes), 'auto')['source'])

    def test_comparison_retains_both_gross_values_and_idle_correction(self):
        start, trace = parallel.MeteringEvidenceTests().trace()
        report = metering.compare(trace, trace[-1].timestamp, .1, start.isoformat())
        self.assertAlmostEqual(report.get('power_gross_wh', -1), 4)
        self.assertAlmostEqual(report.get('idle_energy_wh', -1), .2)
        self.assertAlmostEqual(report['power_net_wh'], 3.8)
        self.assertEqual(report.get('meter_gross_wh'), trace[-1].gross_energy_wh)


class StalledCounterCompletionTests(unittest.IsolatedAsyncioTestCase):
    setUp = parallel.ParallelManagerTests.setUp

    def prepare(self, mode='auto', complete=True):
        start, trace = parallel.MeteringEvidenceTests().trace()
        for sample in trace:
            sample.meter_energy_wh = sample.gross_energy_wh = sample.net_energy_wh = 0
            sample.raw_energy_wh = 18
            sample.metering_quality['meter_step_wh'] = None
            sample.power_integral_valid = complete
        self.manager.session = ChargeSession(mode='calibrating', setup_id='s', battery_id='b',
            quantity=1, ports=['A'], session_started_at=start.isoformat(),
            switch_on_at=start.isoformat(), charge_started_at=start.isoformat(),
            last_sample_at=trace[-1].timestamp, last_significant_at=trace[-1].timestamp,
            idle_baseline_power_w=0, idle_measurement_ids=['i'], samples=trace,
            source_decision={'mode': mode, 'end_policy': 'observed_power'},
            metering={'power_wh':4, 'power_estimate_wh':4, 'meter_wh':0})
        return trace

    async def test_manual_completion_with_good_integration_and_zero_counter(self):
        for mode in ['auto', 'power']:
            with self.subTest(mode=mode):
                trace = self.prepare(mode)
                value = await self.manager.async_finish_calibration()
                self.assertAlmostEqual(value, 4)
                record = list(self.manager.calibrations.values())[-1]
                self.assertEqual(record.energy_source, 'power')
                self.assertTrue(record.manual_override)
                self.assertEqual(record.confidence, 'low')
                self.assertEqual(record.metering_comparison['meter_net_wh'], 0)
                self.assertTrue(all(s.meter_energy_wh == 0 for s in record.samples))

    async def test_estimate_only_manual_completion_stops_without_accepting_estimate(self):
        self.prepare(complete=False)
        self.manager._async_switch_off_checked = AsyncMock(return_value=True)
        await self.manager.async_finish_calibration()
        self.manager._async_switch_off_checked.assert_awaited_once()
        self.assertFalse(self.manager.session.active)
        record = list(self.manager.calibrations.values())[-1]
        self.assertEqual(record.completion_status, 'manual_unusable')
        self.assertIsNone(self.manager._record_source_choice(record)['source'])

    def test_safety_energy_limit_is_not_blind_to_zero_counter(self):
        self.prepare()
        self.manager.session.metering['power_wh'] = 101
        self.assertTrue(self.manager._calibration_exceeds_safety_limit())

    def test_safety_limit_uses_source_matched_reference_after_counter_stall(self):
        parallel.ParallelManagerTests.calibrate(self, count=1)
        record = self.manager.calibrations['0']
        record.metering_comparison.update(meter_gross_wh=0, meter_net_wh=0, meter_step_wh=None)
        self.prepare()
        self.assertEqual(self.manager.calibration_summary('s', 'b', 1)['median_net_energy_wh'], 5.5)
        self.manager.session.metering['power_wh'] = 8.3
        self.assertTrue(self.manager._calibration_exceeds_safety_limit())

    async def test_automatic_completion_uses_confirmed_power_endpoint_with_zero_counter(self):
        from datetime import datetime, timedelta
        trace = self.prepare()
        end = datetime.fromisoformat(trace[-1].timestamp)
        for i in range(41):
            tail = deepcopy(trace[-1])
            tail.timestamp = (end + timedelta(seconds=30 * (i + 1))).isoformat()
            tail.power_w = tail.net_power_w = 0
            tail.power_report_fresh = True
            tail.metering_quality['covered_seconds'] = 7200 + 30 * (i + 1)
            tail.metering_quality['report_count'] += 1
            trace.append(tail)
        self.manager.session.peak_net_power_w = 2
        self.assertTrue(self.manager._detect_calibration_end(datetime.fromisoformat(trace[-1].timestamp)))
        result = await self.manager._async_complete_calibration(automatic=True, reason='test')
        self.assertEqual(result.energy_source, 'power')
        self.assertEqual(result.source_decision['reason'], 'counter_not_advancing')
        self.assertAlmostEqual(result.gross_energy_wh, 4)
        self.assertAlmostEqual(result.net_energy_wh, 4)
        self.assertEqual(result.end_method, 'observed_low_power')
        self.assertEqual(result.metering_comparison['meter_gross_wh'], 0)
        self.manager._async_switch_off_checked.assert_awaited_once()
