"""Use elapsed-time evidence for pulsed tails; never fit to nominal cell energy."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib
import unittest

from test_core import MeasurementSample, ChargeSession

START = datetime(2026, 1, 1, tzinfo=timezone.utc)


def trace(main_seconds=7200, tail_seconds=1800, fresh=True):
    points, energy, accepted = [], 0.0, 0.0
    for i in range(0, main_seconds + tail_seconds + 1, 10):
        power = 2.0 if i < main_seconds else (0.4 if i % 40 == 0 else 0.02)
        if points:
            energy += points[-1].power_w * 10 / 3600
            accepted = energy if fresh else 0
        points.append(MeasurementSample((START+timedelta(seconds=i)).isoformat(),
            power_w=power, net_power_w=power, meter_energy_wh=0,
            power_energy_wh=accepted, power_estimate_wh=energy,
            power_report_fresh=fresh, power_integral_valid=fresh,
            metering_quality={'covered_seconds': i if fresh else 0,
                              'estimate_covered_seconds': i, 'report_count': i//10+1,
                              'max_report_interval_seconds': 10, 'max_power_step_wh': 2/360,
                              'meter_step_wh': None}))
    return points


class RegimeAnalysisTests(unittest.TestCase):
    def analysis(self):
        try:
            return importlib.import_module('custom_components.battery_charge_manager.analysis')
        except ModuleNotFoundError:
            self.fail('Analysis module missing')

    def test_pulsed_tail_confirms_after_twenty_minutes_and_excludes_tail_energy(self):
        analysis = self.analysis()
        points = trace(tail_seconds=1200)
        previous = {}
        for i in range(720, len(points)):
            result = analysis.regime_transition(points[:i+1], 2, 0, previous)
            if result.get('candidate_at'):
                previous = result
        self.assertTrue(result['confirmed'])
        self.assertEqual(result['candidate_at'], (START+timedelta(hours=2)).isoformat())
        summary = analysis.energy_segments(points, result['candidate_at'], 0, 3, 1, START.isoformat())
        self.assertAlmostEqual(summary['charge']['power_estimate_net_wh'], 4)
        self.assertGreater(summary['post_charge']['power_estimate_net_wh'], 0)
        self.assertAlmostEqual(summary['nominal']['input_to_nominal_ratio'], 4/3)
        self.assertNotIn('efficiency', summary['nominal'])

    def test_unfresh_tail_or_missing_reference_never_confirms(self):
        analysis = self.analysis()
        self.assertFalse(analysis.regime_transition(trace(fresh=False), 2, 0, {})['confirmed'])
        self.assertFalse(analysis.regime_transition(trace(), None, 0, {})['confirmed'])

    def test_sustained_recovery_or_substantial_high_pulses_reject_candidate(self):
        analysis = self.analysis()
        points = trace(tail_seconds=900)
        previous = analysis.regime_transition(points, 2, 0, {})
        self.assertTrue(previous.get('candidate_at'))
        for i in range(8110, 8501, 10):
            points.append(MeasurementSample((START+timedelta(seconds=i)).isoformat(),
                                           power_w=1.8, net_power_w=1.8, power_report_fresh=True))
        result = analysis.regime_transition(points, 2, 0, previous)
        self.assertFalse(result['confirmed'])
        self.assertIsNone(result.get('candidate_at'))

    def test_nominal_value_never_changes_any_segment_or_detected_endpoint(self):
        analysis = self.analysis()
        points = trace()
        original = deepcopy([p.as_dict() for p in points])
        end = (START+timedelta(hours=2)).isoformat()
        small = analysis.energy_segments(points, end, 0.02, 3, 1, START.isoformat())
        large = analysis.energy_segments(points, end, 0.02, 30, 1, START.isoformat())
        self.assertEqual(small['charge'], large['charge'])
        self.assertEqual(small['post_charge'], large['post_charge'])
        self.assertEqual(original, [p.as_dict() for p in points])
        self.assertGreater(small['charge']['power_estimate_net_wh'], 3)

    def test_missing_endpoint_or_baseline_is_not_reported_as_zero(self):
        analysis = self.analysis()
        summary = analysis.energy_segments(trace(), None, None, 3, 1, START.isoformat())
        self.assertIsNone(summary['charge'])
        self.assertIsNone(summary['post_charge'])
        self.assertIsNone(summary['total']['power_net_wh'])
        self.assertIsNone(summary['nominal']['input_to_nominal_ratio'])

    def test_idle_mean_weights_elapsed_time_not_event_counts_or_median(self):
        analysis = self.analysis()
        # 10 s at .4 W, 30 s at 0 W -> .1 W. Duplicate zero events cannot lower it.
        points = [MeasurementSample((START+timedelta(seconds=t)).isoformat(), power_w=p,
                                    power_report_fresh=True)
                  for t, p in [(0,.4), (10,0), (11,0), (12,0), (13,0), (40,0)]]
        stats = analysis.window_statistics(points, START.timestamp(), (START+timedelta(seconds=40)).timestamp())
        self.assertAlmostEqual(stats['mean_power_w'], .1)
        self.assertEqual(stats['coverage_percent'], 100)

    def test_phase_is_undetermined_without_sustained_fresh_reference(self):
        from custom_components.battery_charge_manager import phase_tracking
        session = ChargeSession(mode='calibrating', phase='main_charge',
            charge_started_at=START.isoformat(), current_net_power_w=.2,
            samples=[MeasurementSample(START.isoformat(), power_w=2, net_power_w=2),
                     MeasurementSample((START+timedelta(hours=5)).isoformat(), power_w=.2, net_power_w=.2)])
        phase_tracking.update(session, START+timedelta(hours=5))
        self.assertEqual(session.phase, 'undetermined')
