"""Regression traces for low-power battery charging, not cell-state estimation."""
from datetime import datetime, timedelta, timezone
import unittest
from test_core import BatteryChargeManager, FakeHass, ConfigEntry, ChargeSession, MeasurementSample


class PhaseTrackingTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 9, 23, 18, tzinfo=timezone.utc)
        self.manager = BatteryChargeManager(FakeHass(), ConfigEntry())
        self.manager.session = ChargeSession(mode='calibrating', phase='main_charge',
            charge_started_at=self.start.isoformat(), switch_on_at=self.start.isoformat())

    def sample(self, seconds, power, fresh=True):
        now = self.start + timedelta(seconds=seconds)
        s = self.manager.session
        s.samples.append(MeasurementSample(timestamp=now.isoformat(), power_w=power,
            net_power_w=power, power_report_fresh=fresh))
        s.current_net_power_w = power
        s.peak_net_power_w = max(s.peak_net_power_w or 0, power)
        s.last_sample_at = now.isoformat()
        self.manager._update_significant_and_taper(now)
        return s.phase

    def trace(self, start, stop, power, fresh=True):
        for second in range(start, stop + 1, 30):
            self.sample(second, power, fresh)

    def test_startup_zero_and_first_high_sample_are_not_taper(self):
        self.sample(-30, 0)
        self.assertEqual(self.sample(0, 2.1), 'undetermined')
        self.assertIsNone(self.manager.session.taper_started_at)

    def test_early_zeros_inside_start_window_do_not_latch_taper(self):
        self.sample(0, 0)
        self.sample(30, 0)
        self.sample(60, 2.1)
        self.trace(90, 1080, 2.1)
        self.assertEqual(self.manager.session.phase, 'main_charge')
        self.assertIsNone(self.manager.session.taper_started_at)

    def test_single_peak_is_not_a_main_charge_reference(self):
        self.sample(0, 12)
        self.trace(30, 1200, 2.1)
        self.assertEqual(self.manager.session.phase, 'main_charge')

    def test_screenshot_trace_with_moderate_drop_stays_main_charge(self):
        self.trace(0, 2400, 2.1)
        self.sample(2401, 2.3)
        self.trace(2430, 5940, 1.8)
        self.assertEqual(self.manager.session.phase, 'main_charge')

    def test_sustained_drop_after_established_main_charge_detects_taper(self):
        self.trace(0, 600, 2.1)
        self.trace(630, 990, .8)
        self.assertEqual(self.manager.session.phase, 'taper')
        self.assertIsNotNone(self.manager.session.taper_started_at)

    def test_recovery_returns_to_main_charge_and_clears_taper(self):
        self.trace(0, 600, 2.1)
        self.trace(630, 990, .8)
        self.trace(1020, 1200, 2.1)
        self.assertEqual(self.manager.session.phase, 'main_charge')
        self.assertIsNone(self.manager.session.taper_started_at)

    def test_brief_dip_and_event_burst_do_not_outvote_elapsed_time(self):
        self.trace(0, 600, 2.1)
        for i in range(100):
            self.sample(601 + i / 1000, .5)
        self.sample(602, 2.1)
        self.trace(630, 930, 2.1)
        self.assertEqual(self.manager.session.phase, 'main_charge')

    def test_stale_low_power_is_not_evidence_of_taper(self):
        self.trace(0, 600, 2.1)
        self.trace(630, 1200, .5, fresh=False)
        self.assertEqual(self.manager.session.phase, 'undetermined')

    def test_old_latched_startup_flag_is_repaired(self):
        self.manager.session.taper_started_at = self.start.isoformat()
        self.manager.session.phase = 'taper'
        self.trace(0, 600, 2.1)
        self.assertEqual(self.manager.session.phase, 'main_charge')
        self.assertIsNone(self.manager.session.taper_started_at)

    def test_gaps_do_not_establish_a_main_charge_reference(self):
        self.sample(0, 8)
        self.sample(300, 8)
        self.trace(330, 930, 2)
        self.assertEqual(self.manager.session.phase, 'main_charge')

    def test_phase_tracking_survives_serialization(self):
        self.trace(0, 600, 2.1)
        self.manager.session = ChargeSession.from_dict(self.manager.session.as_dict())
        self.trace(630, 990, .8)
        self.assertEqual(self.manager.session.phase, 'taper')
        self.manager.session = ChargeSession.from_dict(self.manager.session.as_dict())
        self.trace(1020, 1200, 2.1)
        self.assertEqual(self.manager.session.phase, 'main_charge')

    def test_phase_hint_never_overwrites_charge_end_confirmation(self):
        self.trace(0, 600, 2.1)
        s = self.manager.session
        s.candidate_end_at = s.last_sample_at
        s.phase = 'confirming_end'
        self.trace(630, 990, .05)
        self.assertEqual(s.phase, 'confirming_end')
        self.assertIsNotNone(s.candidate_end_at)
