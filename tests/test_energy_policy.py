import unittest
from datetime import datetime, timedelta, timezone
from test_core import MeasurementSample
from custom_components.battery_charge_manager import energy_policy


class EnergyPolicyTests(unittest.TestCase):
    def report(self, **changes):
        return dict(meter_net_wh=6, power_net_wh=5.8, meter_step_wh=1,
                    power_step_wh=.02, power_complete=True, **changes)

    def test_single_calibration_can_choose_power(self):
        self.assertEqual(energy_policy.choose(self.report(), 'auto')['source'], 'power')

    def test_fixed_modes_and_missing_data(self):
        self.assertEqual(energy_policy.choose(self.report(), 'meter')['source'], 'meter')
        self.assertEqual(energy_policy.choose(self.report(), 'power')['source'], 'power')
        report=self.report(); report['power_complete']=False
        self.assertIsNone(energy_policy.choose(report, 'power')['source'])
        self.assertEqual(energy_policy.choose(report, 'auto')['source'], 'meter')

    def test_conflict_is_not_silently_accepted_by_auto(self):
        report=self.report(); report['meter_net_wh']=1
        self.assertIsNone(energy_policy.choose(report, 'auto')['source'])
        self.assertEqual(energy_policy.choose(report, 'power')['source'], 'power')

    def test_good_power_can_replace_non_advancing_counter(self):
        report=self.report();report['meter_net_wh']=0;report['meter_step_wh']=None
        self.assertEqual(energy_policy.choose(report,'power')['source'],'power')
        self.assertEqual(energy_policy.choose(report,'auto')['source'],'power')

    def test_tail_requires_low_fresh_power_and_full_confirmation(self):
        start=datetime(2026,9,14,tzinfo=timezone.utc)
        samples=[MeasurementSample(timestamp=(start+timedelta(seconds=i*30)).isoformat(),
                                   power_w=2 if i<10 else .05, power_report_fresh=True)
                 for i in range(51)]
        endpoint, confirmed=energy_policy.power_endpoint(samples, 0, .12, 1200)
        self.assertTrue(confirmed)
        self.assertEqual(endpoint,samples[10])
        samples[-1].power_report_fresh=False
        self.assertEqual(energy_policy.power_endpoint(samples,0,.12,1200),(None,False))

    def test_counter_plateau_during_active_power_is_not_an_endpoint(self):
        start=datetime(2026,9,14,tzinfo=timezone.utc)
        samples=[MeasurementSample(timestamp=(start+timedelta(minutes=i)).isoformat(),
                                   power_w=2, gross_energy_wh=1, power_report_fresh=True)
                 for i in range(30)]
        self.assertEqual(energy_policy.power_endpoint(samples,0,.12,1200),(None,False))


from unittest.mock import AsyncMock
from copy import deepcopy
import test_parallel_metering as parallel
from test_core import BatteryChargeManager, FakeHass, ConfigEntry, ChargeSession
from custom_components.battery_charge_manager.history import chart_samples
from custom_components.battery_charge_manager import metering


class EnergyModeIntegrationTests(unittest.IsolatedAsyncioTestCase):
    setUp = parallel.ParallelManagerTests.setUp
    calibrate = parallel.ParallelManagerTests.calibrate

    async def test_settings_persist_without_changing_active_source_or_target(self):
        self.manager.session = ChargeSession(mode='charging',energy_source='meter',target_energy_wh=3)
        self.manager.store.async_save = AsyncMock()
        await self.manager.async_set_energy_mode('power')
        saved = self.manager.store.async_save.call_args.args[0]
        self.assertEqual(saved['energy_mode'],'power')
        self.assertEqual(self.manager.session.energy_source,'meter')
        self.assertEqual(self.manager.session.target_energy_wh,3)
        saved['session'] = ChargeSession().as_dict()
        restored=BatteryChargeManager(FakeHass(),ConfigEntry())
        restored.store.async_load=AsyncMock(return_value=saved)
        await restored.async_load()
        self.assertEqual(restored.energy_mode,'power')

    async def test_one_record_and_forced_modes_use_source_matched_targets(self):
        self.calibrate(count=1)
        self.assertEqual(self.manager.calibration_summary('s','b',1)['median_net_energy_wh'],5.5)
        await self.manager.async_set_energy_mode('meter')
        self.assertEqual(self.manager.calibration_summary('s','b',1)['median_net_energy_wh'],6)
        await self.manager.async_set_energy_mode('power')
        self.assertEqual(self.manager.calibration_summary('s','b',1)['median_net_energy_wh'],5.5)
        self.manager.calibrations['0'].metering_comparison['power_eligible']=False
        self.assertIsNone(self.manager.calibration_summary('s','b',1)['median_net_energy_wh'])

    def test_auto_does_not_mix_sources_from_different_calibrations(self):
        self.calibrate(count=2)
        first,second=self.manager.calibrations.values()
        first.session_started_at='2026-09-13T00:00:00+00:00'
        second.session_started_at='2026-09-14T00:00:00+00:00'
        second.metering_comparison['meter_step_wh']=.01
        summary=self.manager.calibration_summary('s','b',1)
        self.assertEqual(summary['energy_source'],'meter')
        self.assertEqual(summary['record_ids'],['1'])
        self.assertEqual(summary['median_net_energy_wh'],6)

    def test_conflicting_calibration_cannot_be_used_even_when_marked_valid(self):
        self.calibrate(count=1)
        record=self.manager.calibrations['0']
        record.net_energy_wh=1
        record.metering_comparison.update(meter_net_wh=1,power_eligible=False,
                                         power_estimate_net_wh=6.7,estimate_complete=True)
        self.assertEqual(self.manager.calibration_summary('s','b',1)['count'],0)
        self.assertFalse(self.manager._measurement_row(record)['used'])
        self.assertEqual(self.manager._measurement_row(record)['usage_reason'],'sources_disagree')

    def test_selected_record_and_idle_reanalysis_never_overwrite_counter_trace(self):
        self.calibrate(count=1)
        record=self.manager.calibrations['0']
        self.manager._select_calibration_energy(record,'auto')
        self.assertEqual(record.energy_source,'power')
        self.assertEqual(record.net_energy_wh,5.5)
        self.assertEqual(record.metering_comparison['meter_net_wh'],6)

    async def test_completion_and_idle_reanalysis_preserve_selected_energy_and_audit(self):
        start, trace = parallel.MeteringEvidenceTests().trace()
        for i, sample in enumerate(trace):
            sample.gross_energy_wh = sample.meter_energy_wh = sample.raw_energy_wh = i // 40
        endpoint = trace[-1].timestamp
        trace[-1].power_w = 0
        for i in range(1, 41):
            tail = deepcopy(trace[240])
            tail.timestamp = (start + timedelta(seconds=7200 + 30*i)).isoformat()
            tail.metering_quality['covered_seconds'] = 7200 + 30*i
            tail.metering_quality['report_count'] += i
            trace.append(tail)
        self.manager.session = ChargeSession(
            mode='calibrating', setup_id='s', battery_id='b', quantity=1, ports=['A'],
            session_started_at=start.isoformat(), switch_on_at=start.isoformat(),
            charge_started_at=start.isoformat(), candidate_end_at=endpoint,
            candidate_end_net_energy_wh=6, candidate_end_gross_energy_wh=6,
            gross_energy_wh=6, net_energy_wh=6, idle_baseline_power_w=0,
            idle_measurement_ids=['i'], samples=trace,
            source_decision={'mode':'power', 'end_policy':'observed_power'})
        record = await self.manager._async_complete_calibration(automatic=True, reason='done')
        self.assertEqual(record.energy_source, 'power')
        self.assertAlmostEqual(record.net_energy_wh, 4)
        self.assertAlmostEqual(record.energy_at_detection_wh, 4)
        self.assertEqual(record.metering_comparison['meter_net_wh'], 6)
        self.assertEqual(record.end_method, 'observed_low_power')
        self.manager.energy_mode = 'meter'
        self.manager._apply_idle_correction(record, baseline=.1, measurement_ids=['i'], quality='stable')
        self.assertEqual(record.source_decision['mode'], 'power')
        self.assertEqual(record.charge_finished_at, endpoint)
        self.assertAlmostEqual(record.net_energy_wh, 3.8)
        self.assertAlmostEqual(record.gross_energy_wh, 4)
        self.assertAlmostEqual(record.energy_at_detection_wh, 4 - .1*8400/3600)
        self.assertAlmostEqual(record.metering_comparison['meter_net_wh'], 5.8)
        self.assertEqual(record.samples[-1].gross_energy_wh, 6)
        self.assertEqual(record.analysis_history[-1]['energy_source'], 'power')
        self.assertAlmostEqual(record.analysis_history[-1]['net_energy_wh'], 4)

    def test_new_end_detection_cannot_stop_on_counter_plateau_with_high_watts(self):
        start=datetime(2026,9,14,tzinfo=timezone.utc)
        samples=[MeasurementSample(timestamp=(start+timedelta(seconds=i*30)).isoformat(),
                                   power_w=2,net_power_w=2,gross_energy_wh=1,net_energy_wh=1,
                                   power_report_fresh=True) for i in range(100)]
        self.manager.session=ChargeSession(mode='calibrating', setup_id='s',battery_id='b',
            net_energy_wh=1, charge_started_at=start.isoformat(),samples=samples,
            peak_net_power_w=2, source_decision={'mode':'auto','end_policy':'observed_power'})
        self.assertFalse(self.manager._detect_calibration_end(start+timedelta(seconds=2970)))
        self.assertIsNone(self.manager.session.candidate_end_at)
        for i in range(41):
            samples.append(MeasurementSample(timestamp=(start+timedelta(seconds=3000+i*30)).isoformat(),
                power_w=0, net_power_w=0,net_energy_wh=1,power_report_fresh=True))
        self.assertTrue(self.manager._detect_calibration_end(start+timedelta(seconds=4200)))
        self.assertEqual(self.manager.session.charge_finished_at,samples[100].timestamp)

    def test_held_estimate_remains_distinct_from_incomplete_accepted_integral(self):
        state={}
        for seconds in range(0,601,30):
            metering.advance(state,seconds,2,230,.02,reported_at=0)
        self.assertAlmostEqual(state['power_estimate_wh'],2/6)
        self.assertLess(state['power_wh'],state['power_estimate_wh'])
        self.assertFalse(state['power_valid'])

    def test_old_chart_estimate_is_computed_before_thinning_without_mutation(self):
        start=datetime(2026,9,14,tzinfo=timezone.utc)
        samples=[MeasurementSample(timestamp=(start+timedelta(seconds=i*30)).isoformat(),power_w=2) for i in range(1001)]
        trace=chart_samples(samples,limit=100)
        self.assertLessEqual(len(trace),100)
        self.assertAlmostEqual(trace[-1]['power_estimate_wh'],2*30000/3600)
        self.assertIsNone(samples[-1].power_estimate_wh)

    def test_compacted_old_complete_integral_is_not_replaced_by_zero_estimate(self):
        samples=[MeasurementSample(timestamp='2026-09-14T00:00:00+00:00',power_w=2,
                   power_energy_wh=0,power_integral_valid=True),
                 MeasurementSample(timestamp='2026-09-14T01:00:00+00:00',power_w=2,
                   power_energy_wh=2,power_integral_valid=True)]
        trace=chart_samples(samples)
        self.assertEqual(trace[-1]['power_estimate_wh'],2)
        self.assertTrue(trace[-1]['power_integral_valid'])

    def test_gap_only_comparison_is_ineligible_not_an_exception(self):
        start=datetime(2026,9,14,tzinfo=timezone.utc)
        state={};samples=[]
        for seconds in [0,600]:
            metering.advance(state,seconds,2,230,.02,reported_at=seconds)
            samples.append(MeasurementSample(timestamp=(start+timedelta(seconds=seconds)).isoformat(),
                power_energy_wh=state['power_wh'],power_estimate_wh=state['power_estimate_wh'],
                power_integral_valid=state['power_valid'],metering_quality=deepcopy(state)))
        report=metering.compare(samples,samples[-1].timestamp,0)
        self.assertFalse(report['power_eligible'])
        self.assertFalse(report['estimate_complete'])

    async def test_changing_to_power_can_use_complete_run_with_zero_counter(self):
        self.calibrate(count=1)
        record=self.manager.calibrations['0']
        record.metering_comparison.update(meter_net_wh=0, meter_step_wh=None)
        self.manager._select_calibration_energy(record,'auto')
        self.assertEqual(record.net_energy_wh,5.5)
        await self.manager.async_set_energy_mode('power')
        self.assertEqual(self.manager.calibration_summary('s','b',1)['median_net_energy_wh'],5.5)
        self.assertTrue(self.manager._measurement_row(record)['used'])

    async def test_ineligible_trusted_meter_does_not_hide_usable_manual_power(self):
        self.calibrate(count=2)
        self.manager.calibrations['0'].metering_comparison={}
        self.manager.calibrations['1'].confidence='low'
        await self.manager.async_set_energy_mode('power')
        summary=self.manager.calibration_summary('s','b',1)
        self.assertEqual(summary['record_ids'],['1'])
        self.assertEqual(summary['median_net_energy_wh'],5.5)
