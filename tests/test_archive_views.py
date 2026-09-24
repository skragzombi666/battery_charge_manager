"""Raw archive export and presentation must never imply complete missing traces."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from test_core import MeasurementSample, manager_module
from test_retention_completion import setup_manager, MemoryStore
RawArchive = importlib.import_module(manager_module.__package__ + '.archive').RawArchive

history = importlib.import_module(manager_module.__package__ + '.history')

class ArchiveViewsTests(unittest.IsolatedAsyncioTestCase):
    def test_chart_marks_real_gaps_and_keeps_extrema_without_mutating_raw(self):
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        points = [MeasurementSample((t+timedelta(seconds=i*30)).isoformat(), power_w=2,
                                   net_power_w=2, power_report_fresh=True) for i in range(1500)]
        points[721].power_w = 19
        # genuine original gap, not merely the distance between display points
        for p in points[1000:]:
            p.timestamp = (datetime.fromisoformat(p.timestamp)+timedelta(hours=1)).isoformat()
        before = [p.as_dict() for p in points]
        view = history.chart_samples(points, 240)
        self.assertTrue(any(p.get('chart_gap_before') for p in view))
        self.assertEqual(max(p['power_w'] for p in view), 19)
        self.assertLessEqual(len(view), 240)
        self.assertEqual(before, [p.as_dict() for p in points])
        self.assertTrue(all('raw_index' in p for p in view))

    def test_export_snapshot_does_not_move_during_stream(self):
        with tempfile.TemporaryDirectory() as root:
            archive = RawArchive(Path(root)/'a.db'); archive.initialize({})
            archive.append_samples('run', [{'timestamp':'first','raw':1}])
            export = archive.iter_export({'export_format':'test'})
            first = next(export)
            archive.append_samples('run', [{'timestamp':'second','raw':2}])
            data = json.loads(first+''.join(export))
            self.assertEqual(data['raw_archive']['traces'][0]['sample_count'], 1)
            self.assertEqual(len(data['raw_archive']['traces'][0]['samples']), 1)

    async def test_export_and_raw_page_include_all_data_and_unwritten_memory(self):
        manager, hass, _ = setup_manager()
        with tempfile.TemporaryDirectory() as root:
            manager.archive = RawArchive(Path(root)/'a.db'); manager.archive.initialize({})
            await manager._async_save()
            self.assertTrue(hasattr(manager, 'async_archive_export'), 'Missing streaming manager export')
            gen = await manager.async_archive_export()
            data = json.loads(''.join(gen))
            self.assertEqual(data['retention']['automatic_deletion'], False)
            self.assertEqual(len(data['raw_archive']['traces'][0]['samples']), 2)
            page = await manager.async_raw_measurement_page('session','run',0,1)
            self.assertEqual(len(page['samples']), 1)
            self.assertEqual(page['next_offset'], 1)
            manager.session.samples.append(MeasurementSample('2026-09-24T12:00:00+00:00', power_w=99))
            manager._pending_observations.append({'raw': 'not yet persisted'})
            manager._archive_error = 'disk full'
            data = json.loads(''.join(await manager.async_archive_export()))
            self.assertEqual(data['uncommitted_memory']['samples'][0]['power_w'], 99)
            self.assertEqual(data['uncommitted_memory']['observations'][0]['raw'], 'not yet persisted')

    async def test_recovered_attempt_has_visible_energy_comparison(self):
        manager, _, _ = setup_manager()
        manager.session.metering = {'power_estimate_wh':5.75, 'power_wh':1.35, 'meter_wh':0,
                                    'total_seconds':36000, 'covered_seconds':27000,
                                    'estimate_covered_seconds':36000, 'power_valid':False}
        await manager.async_stop()
        row = manager.frontend_state()['calibrations'][0]
        self.assertEqual(row['metering_comparison']['power_estimate_gross_wh'], 5.75)
        self.assertEqual(row['completion_status'], 'aborted')
        self.assertFalse(row['used'])
        self.assertIsNone(row['analysis_summary']['charge'])

    def test_known_fresh_display_decimation_is_not_a_data_gap(self):
        t=datetime(2026,1,1,tzinfo=timezone.utc)
        points=[MeasurementSample((t+timedelta(seconds=30*i)).isoformat(),power_w=2,net_power_w=2,
            power_report_fresh=True,interval_quality={'seconds':30,'accepted_seconds':30,'reason':'fresh_held'}) for i in range(1000)]
        self.assertFalse(any(p['chart_gap_before'] for p in history.chart_samples(points,40)))

    def test_presentation_notifications_throttle_but_final_state_is_immediate(self):
        from unittest.mock import patch
        manager,_,_=setup_manager()
        with patch.object(manager_module,'async_dispatcher_send') as send:
            manager._notify(force=False)
            manager._notify(force=False)
            self.assertEqual(send.call_count,1)
            manager._notify()
            self.assertEqual(send.call_count,2)
