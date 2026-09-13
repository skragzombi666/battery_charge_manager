import json
import unittest
from unittest.mock import AsyncMock

import test_measurement_history as history
from types import SimpleNamespace
from test_core import ChargeSession, CalibrationRecord, MeasurementSample


class ExportCommentTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        history.MeasurementHistoryTests.setUp(self)
        self.manager.hass.config = SimpleNamespace(time_zone="Europe/Zurich")
    calibration = history.MeasurementHistoryTests.calibration
    idle = history.MeasurementHistoryTests.idle

    async def test_export_includes_invalid_old_revisions_full_traces_and_audit(self):
        trace = [MeasurementSample(timestamp=f'2026-09-13T10:{i // 60:02}:{i % 60:02}+00:00', gross_energy_wh=i / 1000) for i in range(800)]
        record = self.calibration(valid=False, samples=trace, comment='USB-C 4.711 Wh',
                                  validity_history=[{'reason': 'test'}], analysis_history=[{'analysis_revision': 1}])
        self.idle(samples=trace)
        self.setup.revision = 3
        self.manager.charge_history = [{'session_id': str(i)} for i in range(100)]
        payload = self.manager.export_measurements()
        json.dumps(payload, allow_nan=False)
        self.assertEqual(len(payload['calibrations'][0]['samples']), 800)
        self.assertEqual(len(payload['idle_measurements'][0]['samples']), 800)
        self.assertEqual(len(payload['charge_history']), 100)
        self.assertFalse(payload['calibrations'][0]['valid'])
        self.assertEqual(payload['calibrations'][0]['setup_revision'], 1)
        self.assertEqual(payload['setups'][0]['revision'], 3)
        self.assertEqual(payload['calibrations'][0]['validity_history'], [{'reason': 'test'}])
        payload['calibrations'][0]['validity_history'].clear()
        self.assertTrue(record.validity_history)

    async def test_comment_edits_keep_measurement_unchanged_and_reject_conflict(self):
        record = self.calibration(valid=False, comment='Initial')
        before = record.as_dict()
        await self.manager.async_set_calibration_comment('cal', 'Initial\nUSB measurement', expected_comment='Initial', actor_id='u')
        after = record.as_dict()
        for key in before:
            if key not in {'comment', 'comment_history'}:
                self.assertEqual(before[key], after[key], key)
        restored = CalibrationRecord.from_dict(after)
        self.assertEqual(restored.comment, 'Initial\nUSB measurement')
        self.assertEqual(restored.comment_history[0]['previous_comment'], 'Initial')
        with self.assertRaisesRegex(Exception, 'changed elsewhere'):
            await self.manager.async_set_calibration_comment('cal', 'lost update', expected_comment='Initial')
        await self.manager.async_set_calibration_comment('cal', '', expected_comment=record.comment)
        self.assertEqual(record.comment, '')
        self.assertEqual(len(record.comment_history), 2)

    async def test_start_passes_comment_before_session_begins(self):
        self.manager._async_begin_session = AsyncMock()
        await self.manager.async_start_calibration('Same discharge method', actor_id='u')
        args = self.manager._async_begin_session.call_args.kwargs
        self.assertEqual(args['comment'], 'Same discharge method')
        self.assertEqual(args['comment_actor_id'], 'u')

    async def test_restart_and_aborted_history_retain_comment_and_samples(self):
        self.assertEqual(ChargeSession.from_dict(None).comment, '')
        session = ChargeSession(mode='calibrating', comment='Test', comment_history=[{'comment': 'Test'}],
                                samples=[MeasurementSample(timestamp='2026-09-13T10:00:00+00:00')])
        self.manager.session = ChargeSession.from_dict(session.as_dict())
        self.assertEqual(self.manager.session.comment, 'Test')
        self.manager._append_charge_history(valid=False, reason='Stopped')
        item = self.manager.export_measurements()['charge_history'][0]
        self.assertEqual(item['comment'], 'Test')
        self.assertEqual(len(item['session']['samples']), 1)
        self.assertNotIn('session', self.manager.frontend_state()['charge_history'][0])
