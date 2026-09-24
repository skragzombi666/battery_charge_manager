from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from test_retention_completion import setup_manager
from test_regime_analysis import trace, START
from custom_components.battery_charge_manager.archive import RawArchive
from test_core import ChargeSession


class EndpointRevisionTests(unittest.IsolatedAsyncioTestCase):
    async def test_explicit_endpoint_revision_keeps_raw_and_prior_analysis(self):
        manager, _, _ = setup_manager()
        manager.session.samples = trace()
        manager.session.session_started_at = manager.session.switch_on_at = START.isoformat()
        manager.session.last_sample_at = manager.session.samples[-1].timestamp
        await manager.async_stop()
        record = next(iter(manager.calibrations.values()))
        raw = deepcopy([p.as_dict() for p in record.samples])
        with tempfile.TemporaryDirectory() as folder:
            manager.archive = RawArchive(Path(folder)/'raw.sqlite')
            manager.archive.initialize()
            await manager._async_save()
            digest = manager.archive.trace_info(record.trace_id)['sha256_chain']
            await manager.async_set_calibration_endpoint(record.calibration_id, '2026-01-01T02:00:00+00:00',
                reason='Observed drop in input draw', expected_analysis_revision=1, actor_id='reviewer')
            self.assertEqual(record.analysis_revision, 2)
            self.assertAlmostEqual(record.analysis_summary['charge']['power_estimate_net_wh'], 4)
            self.assertFalse(record.calibration_eligible)
            self.assertFalse(record.valid)
            self.assertIsNone(manager._record_source_choice(record)['source'])
            self.assertEqual(record.analysis_history[0]['endpoint_reason'], 'Observed drop in input draw')
            self.assertEqual(manager.archive.trace_info(record.trace_id)['sha256_chain'], digest)
            self.assertEqual(manager.archive.read_samples(record.trace_id), raw)
            self.assertFalse(record.samples)
            with self.assertRaisesRegex(Exception, 'changed'):
                await manager.async_set_calibration_endpoint(record.calibration_id, '2026-01-01T02:00:00+00:00',
                    reason='Stale request', expected_analysis_revision=1)

    async def test_end_detector_handles_pulses_without_using_nominal_energy(self):
        manager, _, _ = setup_manager()
        manager.session = ChargeSession(mode='calibrating', setup_id='setup', battery_id='battery',
            session_id='run', switch_on_at=START.isoformat(), charge_started_at=START.isoformat(),
            idle_baseline_power_w=0, source_decision={'mode':'auto','end_policy':'observed_power'},
            phase_tracking={'version':1, 'reference_power_w':2}, peak_net_power_w=2,
            metering={'power_wh':4})
        points = trace(tail_seconds=1200)
        from datetime import datetime
        confirmed = False
        for i in range(720, len(points)):
            manager.session.samples = points[:i+1]
            manager.session.last_sample_at = points[i].timestamp
            confirmed = manager._detect_calibration_end(datetime.fromisoformat(points[i].timestamp))
        self.assertTrue(confirmed)
        self.assertEqual(manager.session.candidate_end_at, '2026-01-01T02:00:00+00:00')
        self.assertEqual(manager.session.end_evidence['method'], 'sustained_low_input')

    async def test_idle_assessment_does_not_accept_stale_pulses_as_zero_baseline(self):
        manager, _, _ = setup_manager()
        manager.session.mode = 'idle_measuring'
        manager.session.samples = trace(main_seconds=0, tail_seconds=2100, fresh=False)
        manager.session.switch_on_at = START.isoformat()
        manager.session.last_sample_at = manager.session.samples[-1].timestamp
        report = manager._assess_idle_trace()
        self.assertFalse(report['reliable'])
        self.assertEqual(report['baseline_method'], 'time_weighted_power')
