from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import unittest

from test_core import (
    BatteryChargeManager, ChargerSetup, ChargeSession, ConfigEntry,
    FakeHass, State, IdleMeasurement, CalibrationRecord, BatteryType, MeasurementSample,
    manager_module,
)


class SafetyRegressionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hass = FakeHass()
        self.manager = BatteryChargeManager(self.hass, ConfigEntry())
        self.setup = ChargerSetup("setup", "Charger", "switch.charger", "sensor.energy")
        self.manager.setups["setup"] = self.setup
        self.manager.selected_setup_id = "setup"
        self.hass.states.values["switch.charger"] = State("off")
        self.hass.states.values["sensor.energy"] = State("1000", {"unit_of_measurement": "Wh"})
        self.commands = []
        parent = self

        class Services:
            async def async_call(self, domain, service, data, **kwargs):
                parent.commands.append(service)
                parent.hass.states.values[data["entity_id"]] = State("on" if service == "turn_on" else "off")

        self.hass.services = Services()

    async def test_failed_on_confirmation_always_sends_off(self):
        async def wait_for_state(entity, expected, **kwargs):
            return expected == "off"
        self.manager._async_wait_for_switch_state = wait_for_state
        with self.assertRaisesRegex(Exception, "ON"):
            await self.manager._async_begin_session(
                mode="idle_measuring", setup=self.setup, battery=None, target_energy_wh=None,
            )
        self.assertEqual(self.commands, ["turn_on", "turn_off"])
        self.assertEqual(self.hass.states.get("switch.charger").state, "off")
        self.assertFalse(self.manager.session.valid)

    async def test_unknown_switch_state_after_restart_requests_verified_off(self):
        self.hass.states.values["switch.charger"] = State("unavailable")
        self.manager.session = ChargeSession(
            session_id="active", setup_id="setup", mode="charging",
            session_started_at=datetime.now(timezone.utc).isoformat(),
        )
        await self.manager._async_resume_session()
        self.assertEqual(self.commands, ["turn_off"])
        self.assertEqual(self.hass.states.get("switch.charger").state, "off")
        self.assertFalse(self.manager.session.valid)
        self.assertTrue(self.manager.charge_history)

    async def test_backwards_energy_counter_aborts_without_inventing_energy(self):
        now = datetime.now(timezone.utc).isoformat()
        self.hass.states.values["switch.charger"] = State("on")
        self.hass.states.values["sensor.energy"] = State("999.9", {"unit_of_measurement": "Wh"})
        self.manager.session = ChargeSession(
            session_id="active", setup_id="setup", mode="charging",
            session_started_at=now, switch_on_at=now, last_raw_energy_wh=1000,
            gross_energy_wh=0.5, net_energy_wh=0.5,
        )
        await self.manager._async_sample("heartbeat")
        self.assertAlmostEqual(self.manager.session.gross_energy_wh, 0.5)
        self.assertEqual(self.commands, ["turn_off"])
        self.assertFalse(self.manager.session.valid)
        self.assertIn("backwards", self.manager.session.end_reason)

    async def test_reanalysis_without_endpoint_evidence_downgrades_old_high_confidence(self):
        record = CalibrationRecord(
            "cal", "setup", 1, {}, "battery", 1, {}, 1, ["A"],
            session_started_at="2026-09-01T10:00:00Z", switch_on_at="2026-09-01T10:00:00Z",
            charge_finished_at="2026-09-01T11:00:00Z", end_method="energy_plateau_and_low_power",
            end_detected_at="2026-09-01T11:10:00Z",
            confidence="high", net_energy_wh=3,
            samples=[MeasurementSample("2026-09-01T10:00:00Z", power_w=3.2),
                     MeasurementSample("2026-09-01T11:00:00Z", power_w=3.2, gross_energy_wh=3.2)],
        )
        self.manager._apply_idle_correction(record, baseline=0.2, measurement_ids=[], quality="stable")
        self.assertEqual(record.confidence, "low")
        self.assertEqual(record.end_method, "idle_reanalysis_unconfirmed")
        self.assertIsNone(record.end_detected_at)
        self.assertEqual(record.analysis_history[0]["end_detected_at"], "2026-09-01T11:10:00Z")
        self.assertEqual(record.analysis_history[0]["confidence"], "high")

    def test_confirmed_reanalysis_uses_confirmation_time_from_its_trace(self):
        record = CalibrationRecord(
            "cal", "setup", 1, {}, "battery", 1, {}, 1, ["A"],
            session_started_at="2026-09-01T10:00:00Z", switch_on_at="2026-09-01T10:00:00Z",
            charge_finished_at="2026-09-01T11:00:00Z", end_detected_at="2026-09-01T11:01:00Z",
            samples=[MeasurementSample("2026-09-01T10:00:00Z", power_w=3.2),
                     MeasurementSample("2026-09-01T11:00:00Z", power_w=3.2, gross_energy_wh=3.2),
                     MeasurementSample("2026-09-01T11:30:00Z", power_w=0.2, gross_energy_wh=3.3)],
        )
        self.manager._apply_idle_correction(record, baseline=0.2, measurement_ids=[], quality="stable")
        self.assertEqual(record.end_method, "retrospective_idle_reanalysis")
        self.assertEqual(record.charge_finished_at, "2026-09-01T11:00:00Z")
        self.assertEqual(record.end_detected_at, "2026-09-01T11:30:00Z")
        self.assertEqual(record.analysis_history[0]["end_detected_at"], "2026-09-01T11:01:00Z")

    def test_below_detection_results_do_not_drag_measured_baseline_to_zero(self):
        for number in range(2):
            self.manager.idle_measurements[str(number)] = IdleMeasurement(
                str(number), "setup", 1, {}, reliable=True,
                below_detection_limit=True, upper_bound_power_w=0.3,
            )
        self.manager.idle_measurements["measured"] = IdleMeasurement(
            "measured", "setup", 1, {}, reliable=True, median_power_w=0.2,
        )
        summary = self.manager.idle_summary("setup")
        self.assertAlmostEqual(summary["baseline_power_w"], 0.2)
        self.assertEqual(summary["measurement_ids"], ["measured"])

    async def test_conflicting_idle_measurements_do_not_supply_operational_correction(self):
        for number, watts in enumerate((0.1, 1.0)):
            self.manager.idle_measurements[str(number)] = IdleMeasurement(
                str(number), "setup", 1, {}, reliable=True, median_power_w=watts,
            )
        summary = self.manager.idle_summary("setup")
        self.assertEqual(summary["quality"], "unstable")
        self.assertFalse(summary["usable"])

    async def test_session_clock_includes_on_confirmation_time(self):
        seen = {}
        async def switch_on(setup):
            seen["started"] = self.manager.session.switch_on_at
        async def sample(source):
            pass
        self.manager._async_switch_on_checked = switch_on
        self.manager._async_sample = sample
        await self.manager._async_begin_session(
            mode="idle_measuring", setup=self.setup, battery=None, target_energy_wh=None,
        )
        self.assertIsNotNone(seen["started"])
        self.assertEqual(self.manager.session.switch_on_at, seen["started"])

    async def test_normal_charge_requires_usable_idle_baseline(self):
        self.manager.batteries["battery"] = BatteryType("battery", "AA", 1700, "Li-Ion", "AA")
        self.manager.selected_battery_id = "battery"
        self.manager.calibrations["cal"] = CalibrationRecord(
            "cal", "setup", 1, {}, "battery", 1, {}, 1, ["A"], net_energy_wh=3,
        )
        with self.assertRaisesRegex(Exception, "idle measurement"):
            await self.manager.async_start_charge()
        self.assertEqual(self.commands, [])

    async def test_sensor_bursts_coalesce_persistence_but_shutdown_flushes_latest(self):
        writes = []
        class CaptureStore:
            async def async_save(self, data):
                writes.append(data)
        self.manager.store = CaptureStore()
        start = datetime(2026, 9, 1, tzinfo=timezone.utc)
        self.hass.states.values["switch.charger"] = State("on")
        self.manager.session = ChargeSession(
            session_id="idle", setup_id="setup", mode="idle_measuring",
            session_started_at=start.isoformat(), switch_on_at=start.isoformat(),
            last_raw_energy_wh=1000, requested_duration_minutes=300,
            idle_measurement_mode="fixed",
        )
        for i in range(40):
            self.hass.states.values["sensor.energy"] = State(str(1000+i*.001), {"unit_of_measurement": "Wh"})
            with patch.object(manager_module.dt_util, "utcnow", return_value=start+timedelta(seconds=i)):
                await self.manager._async_sample("sensor")
        self.assertLessEqual(len(writes), 2)
        await self.manager.async_shutdown()
        self.assertAlmostEqual(writes[-1]["session"]["gross_energy_wh"], .039)
        self.assertEqual(self.commands, [])
