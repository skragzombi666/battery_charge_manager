"""Pilot integration distinguishes held observations from unobserved time."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import unittest
from test_core import MeasurementSample, ChargeSession, manager_module
from custom_components.battery_charge_manager.models import CalibrationRecord
from custom_components.battery_charge_manager import metering, energy_policy


def trace(seconds, *, stale=True, restart_at=None):
    state, samples = {}, []
    origin = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for second in seconds:
        at = origin + timedelta(seconds=second)
        metering.advance(state, at.timestamp(), 2, None, None, fresh=not stale,
                         restart=second == restart_at)
        samples.append(MeasurementSample(at.isoformat(), power_w=2,
            power_estimate_wh=state['power_estimate_wh'], power_energy_wh=state['power_wh'],
            power_report_fresh=not stale, power_integral_valid=state['power_valid'],
            metering_quality=deepcopy(state)))
    return samples


class PilotMeteringTests(unittest.TestCase):
    def test_held_observations_are_explicit_source_with_separate_quality(self):
        points = trace(range(0, 3601, 30))
        report = metering.compare(points, points[-1].timestamp, 0)
        self.assertEqual(energy_policy.choose(report, 'power_reported')['source'], 'power_reported')
        self.assertAlmostEqual(report['power_estimate_gross_wh'], 2)
        self.assertEqual(report['held_seconds'], 3600)
        self.assertEqual(report['longest_held_seconds'], 3600)
        self.assertFalse(report['power_complete'])
        self.assertEqual(energy_policy.choose(report, 'power')['source'], None)

    def test_even_small_real_recording_gap_prevents_approval(self):
        points = trace([0, 121, *range(151, 20012, 30)])
        report = metering.compare(points, points[-1].timestamp, 0)
        self.assertTrue(report['estimate_complete'])  # legacy 99% display test
        self.assertFalse(report['reported_complete'])
        self.assertEqual(report['unknown_seconds'], 121)
        self.assertIsNone(energy_policy.choose(report, 'power_reported')['source'])

    def test_unobserved_prefix_and_restart_are_not_integrated(self):
        points = trace(range(0, 361, 30), restart_at=180)
        start = (datetime.fromisoformat(points[0].timestamp) - timedelta(seconds=5)).isoformat()
        report = metering.compare(points, points[-1].timestamp, 0, start)
        self.assertFalse(report['reported_complete'])
        self.assertEqual(report['unknown_seconds'], 35)

    def test_metadata_roundtrips_without_fabricating_historical_approval(self):
        old = dict(calibration_id='old', setup_id='s', battery_id='b')
        record = CalibrationRecord.from_dict(old)
        self.assertEqual(record.usage_approval, 'pending')
        self.assertEqual(record.approval_history, [])
        record.energy_basis = 'gross'
        record.usb_comparison = {'energy_wh': 4.590, 'interval': 'full_run'}
        again = CalibrationRecord.from_dict(record.as_dict())
        self.assertEqual(again.usb_comparison, record.usb_comparison)
        session = ChargeSession(pilot={'energy_basis': 'gross', 'rest_reference': {'id': 'r'}})
        self.assertEqual(ChargeSession.from_dict(session.as_dict()).pilot, session.pilot)

    def test_rest_record_roundtrip(self):
        from custom_components.battery_charge_manager.pilot_models import RestMeasurement
        record = RestMeasurement('r', 's', 2, 'b', 3, 1, ['A'])
        self.assertEqual(RestMeasurement.from_dict(record.as_dict()).as_dict(), record.as_dict())
        self.assertEqual(record.usage_approval, 'pending')
