"""Presentation must preserve the location and kind of missing evidence."""
from copy import deepcopy
import unittest
from test_rest_reference import points
from custom_components.battery_charge_manager.history import chart_samples


class PilotHistoryTests(unittest.TestCase):
    def test_short_stale_interval_keeps_exact_boundaries_and_meter_continuity(self):
        samples = points([1]*2000, step=1)
        for i, sample in enumerate(samples):
            sample.power_report_fresh = not 999 <= i <= 1001
            sample.meter_energy_wh = i/3600
            sample.power_estimate_wh = i/3600
        original = deepcopy([p.as_dict() for p in samples])
        result = chart_samples(samples, 200)
        by_index = {p['raw_index']:p for p in result}
        for index in (998, 999, 1001, 1002, 1003):
            self.assertIn(index, by_index)
        self.assertTrue(by_index[999]['chart_channels']['power']['held'])
        self.assertFalse(by_index[999]['chart_channels']['meter']['gap_before'])
        self.assertFalse(by_index[999]['chart_channels']['power']['gap_before'])
        self.assertEqual([p.as_dict() for p in samples], original)

    def test_real_gap_only_spans_its_original_neighbors(self):
        samples = points([1]*2000, step=1)
        del samples[900:1200]
        result = chart_samples(samples, 200)
        gaps = [(result[i-1]['timestamp'], p['timestamp']) for i,p in enumerate(result)
                if i and p['chart_channels']['power']['gap_before']]
        self.assertEqual(gaps, [(samples[899].timestamp, samples[900].timestamp)])

    def test_dense_quality_transitions_use_bounded_envelope_with_quality_counts(self):
        samples = points([0, .3]*4000, step=1)
        for i,sample in enumerate(samples):
            sample.power_report_fresh = i%4 < 2
        result = chart_samples(samples, 240)
        self.assertLessEqual(len(result), 240)
        envelopes = {p['chart_bucket']['id']:p['chart_bucket'] for p in result if p.get('chart_bucket')}
        self.assertTrue(envelopes)
        self.assertTrue(any(b['held_seconds'] > 0 for b in envelopes.values()))
        self.assertTrue(all(b['power_w']['max'] == .3 for b in envelopes.values()))
        self.assertEqual(result[0]['timestamp'], samples[0].timestamp)
        self.assertEqual(result[-1]['timestamp'], samples[-1].timestamp)
