"""Lossless archive regressions; no user/private measurements in fixtures."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest

import test_core  # installs minimal Home Assistant import boundary


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'measurements.sqlite3'

    def archive(self):
        name = 'custom_components.battery_charge_manager.archive'
        self.assertIsNotNone(importlib.util.find_spec(name), 'A transactional raw archive is required')
        return importlib.import_module(name).RawArchive(self.path)

    def test_retains_100001_samples_and_121_runs_after_reopen(self):
        a = self.archive()
        a.initialize({})
        points = [{'timestamp': f'2026-01-01T00:00:{i:06d}', 'power_w': (i % 7) / 10,
                   'unknown_raw_field': {'sequence': i}} for i in range(100_001)]
        a.append_samples('stress', points)
        histories = [{'session_id': str(i), 'reason': 'Stopped by user'} for i in range(121)]
        a.save_state({'charge_history': histories, 'session': {'mode': 'idle'}})
        b = self.archive()
        restored = b.initialize({})
        self.assertEqual(restored['charge_history'], histories)
        got = b.read_samples('stress')
        self.assertEqual(len(got), 100_001)
        self.assertEqual(got, points)
        self.assertEqual(b.trace_info('stress')['sample_count'], len(points))
        self.assertTrue(b.verify_trace('stress'))
        self.assertEqual(b.read_samples('stress', 99_999, 2), points[-2:])

    def test_legacy_import_retains_unknown_fields_and_is_idempotent(self):
        points = [{'timestamp': '2026-01-01T00:00:00+00:00', 'power_w': 0.1,
                   'unknown': [1, {'a': 'ä'}]}, {'timestamp': '2026-01-01T00:00:00+00:00', 'power_w': 0.1}]
        legacy = {'extra_top': {'keep': True}, 'calibrations': [], 'idle_measurements': [],
                  'charge_history': [{'session_id': 'x', 'mode': 'calibrating',
                       'session': {'session_id': 'x', 'samples': points, 'mode': 'calibrating'}}],
                  'session': {'session_id': 'x', 'samples': points, 'mode': 'idle'}}
        original = deepcopy(legacy)
        a = self.archive()
        data = a.initialize(legacy)
        self.assertEqual(legacy, original)
        trace = data['session']['trace_id']
        self.assertEqual(a.read_samples(trace), points)
        self.assertEqual(data['session']['archived_sample_count'], 2)
        self.assertNotIn('samples', data['session'])
        a.initialize(legacy)
        self.assertEqual(a.trace_info(trace)['sample_count'], 2)
        exported = json.loads(''.join(a.iter_export({'export_schema_version': 2})))
        self.assertIn(original, [d['payload'] for d in exported['raw_archive']['documents']])
        self.assertEqual(exported['raw_archive']['traces'][0]['samples'], points)

    def test_conflicting_write_rolls_back_without_replacing_original(self):
        a = self.archive()
        a.initialize({})
        first = [{'timestamp': 't', 'power_w': 1.0}]
        a.append_samples('t', first)
        a.append_samples('t', first, start=0)  # exact retry, not a new observation
        with self.assertRaises(ValueError):
            a.append_samples('t', [{'timestamp': 't', 'power_w': 99.0}], start=0)
        self.assertEqual(a.read_samples('t'), first)
        self.assertTrue(a.verify_trace('t'))

    def test_observations_and_checkpoint_are_durable_and_not_deduplicated(self):
        a = self.archive()
        a.initialize({})
        event = {'event_type': 'state_reported', 'value': '2.10', 'unit': 'W'}
        a.append_event('s', event)
        a.append_event('s', event)
        a.append_samples('s', [{'timestamp': 't', 'power_w': 2.1}],
                         checkpoint={'session_id': 's', 'mode': 'calibrating'})
        b = self.archive()
        state = b.initialize({})
        self.assertEqual(state['session']['session_id'], 's')
        exported = json.loads(''.join(b.iter_export({})))
        self.assertEqual(exported['raw_archive']['traces'][0]['events'], [event, event])

    def test_evaluation_revisions_never_overwrite_previous_payload(self):
        a = self.archive()
        a.initialize({})
        a.save_state({'calibrations': [{'calibration_id': 'a', 'value': 1}]})
        a.save_state({'calibrations': [{'calibration_id': 'a', 'value': 2}]})
        exported = json.loads(''.join(a.iter_export({})))
        states = [d['payload'] for d in exported['raw_archive']['documents']]
        self.assertIn({'calibrations': [{'calibration_id': 'a', 'value': 1}]}, states)
        self.assertIn({'calibrations': [{'calibration_id': 'a', 'value': 2}]}, states)

class DivergentSnapshotTests(unittest.TestCase):
    def test_divergent_legacy_snapshots_of_same_session_are_both_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = importlib.import_module('custom_components.battery_charge_manager.archive').RawArchive(Path(folder) / 'archive.sqlite')
            first = [{'timestamp': '2026-01-01', 'power_w': 2}]
            second = [{'timestamp': '2026-01-01', 'power_w': 3}]
            original = {'charge_history': [{'session_id': 'x', 'session': {'session_id': 'x', 'samples': first}}],
                        'session': {'session_id': 'x', 'samples': second}}
            result = archive.initialize(original)
            one, two = result['charge_history'][0]['session']['trace_id'], result['session']['trace_id']
            self.assertNotEqual(one, two)
            self.assertEqual(archive.read_samples(one), first)
            self.assertEqual(archive.read_samples(two), second)
