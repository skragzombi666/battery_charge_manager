"""Rest detection is an explicit, time-weighted comparison, never a timer guess."""
from datetime import datetime, timedelta, timezone
import unittest
from test_core import MeasurementSample
from custom_components.battery_charge_manager import rest_reference


def points(powers, step=30):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [MeasurementSample((start + timedelta(seconds=i*step)).isoformat(),
                             power_w=p, power_report_fresh=False) for i, p in enumerate(powers)]


class RestReferenceTests(unittest.TestCase):
    def test_repowers_and_warmup_excluded_from_weighted_mean(self):
        # 5 min preparation, 5 min warm-up, 30 min pulsing residual.
        samples = points([2]*20 + [0, 0, .3]*20 + [0])
        report = rest_reference.assess(samples, samples[10].timestamp, samples[-1].timestamp)
        self.assertTrue(report['eligible'])
        self.assertAlmostEqual(report['mean_power_w'], .1)
        self.assertEqual(report['median_power_w'], 0)
        self.assertEqual(report['block_means_w'], [.09, .105, .105])
        self.assertAlmostEqual(report['tolerance_w'], .15)
        self.assertEqual(report['held_seconds'], 1800)

    def test_short_or_gapped_reference_never_eligible(self):
        samples = points([.1]*71)
        report = rest_reference.assess(samples, samples[0].timestamp, samples[-1].timestamp)
        self.assertTrue(report['eligible'])
        self.assertAlmostEqual(report['tolerance_w'], .03)
        self.assertFalse(report['resolution_known'])
        samples.pop(50); samples.pop(50); samples.pop(50); samples.pop(50)
        self.assertFalse(rest_reference.assess(samples, samples[0].timestamp, samples[-1].timestamp)['eligible'])
        self.assertFalse(rest_reference.assess(samples[:10], samples[0].timestamp, samples[9].timestamp)['eligible'])

    def test_unstable_reference_and_profile(self):
        samples = points([0]*30 + [.1]*20 + [.5]*20 + [.5])
        report = rest_reference.assess(samples, samples[0].timestamp, samples[-1].timestamp)
        self.assertFalse(report['eligible'])
        self.assertEqual(report['reason'], 'unstable_blocks')
        a = rest_reference.profile_key('s', 1, 'b', 1, 2, ['A','B'])
        self.assertNotEqual(a, rest_reference.profile_key('s', 1, 'b', 2, 2, ['A','B']))
        self.assertNotEqual(a, rest_reference.profile_key('s', 1, 'b', 1, 2, ['B','A']))

    def test_requires_prior_load_and_twenty_minutes_and_withdraws_on_reload(self):
        reference = {'eligible': True, 'upper_power_w': .13, 'tolerance_w': .03}
        samples = points([1]*10 + [.1]*41)
        result = rest_reference.suggest(samples, reference)
        self.assertEqual(result['status'], 'suggested')
        self.assertEqual(result['endpoint_at'], samples[10].timestamp)
        self.assertEqual(rest_reference.suggest(samples[:-1], reference)['status'], 'candidate')
        self.assertNotEqual(rest_reference.suggest(points([.1]*60), reference)['status'], 'suggested')
        renewed = points([1]*10 + [.1]*40 + [1]*11)
        self.assertNotEqual(rest_reference.suggest(renewed, reference, result)['status'], 'suggested')

    def test_actual_gap_and_restart_break_confirmation(self):
        reference = {'eligible': True, 'upper_power_w': .13, 'tolerance_w': .03}
        samples = points([1]*10 + [.1]*41)
        samples[30].interval_quality = {'reason': 'restart'}
        self.assertNotEqual(rest_reference.suggest(samples, reference)['status'], 'suggested')
        samples[30].interval_quality = {}
        del samples[20:25]
        self.assertNotEqual(rest_reference.suggest(samples, reference)['status'], 'suggested')

    def test_gap_in_partial_window_immediately_withdraws_proposal(self):
        reference = {'eligible': True, 'upper_power_w': .13, 'tolerance_w': .03}
        samples = points([1]*10 + [.1]*41)
        samples.append(MeasurementSample((datetime.fromisoformat(samples[-1].timestamp)+timedelta(seconds=170)).isoformat(), power_w=.1))
        self.assertNotEqual(rest_reference.suggest(samples, reference)['status'], 'suggested')
