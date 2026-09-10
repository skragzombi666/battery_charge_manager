from datetime import datetime, timedelta, timezone
import unittest

from test_core import (
    BatteryChargeManager, BatteryType, CalibrationRecord, ChargerSetup,
    ChargeSession, ConfigEntry, FakeHass, IdleMeasurement, MeasurementSample,
)


class MeasurementHistoryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.manager = BatteryChargeManager(FakeHass(), ConfigEntry())
        self.setup = ChargerSetup("setup", "Charger", "switch.charger", "sensor.energy")
        self.battery = BatteryType("battery", "AA", 1700, "Li-Ion", "AA")
        self.manager.setups["setup"] = self.setup
        self.manager.batteries["battery"] = self.battery
        self.manager.selected_setup_id = "setup"
        self.manager.selected_battery_id = "battery"

    def idle(self, record_id="idle", **kwargs):
        record = IdleMeasurement(record_id, "setup", 1, self.setup.snapshot(),
                                 reliable=True, average_power_w=0.2, **kwargs)
        self.manager.idle_measurements[record_id] = record
        return record

    def calibration(self, record_id="cal", **kwargs):
        record = CalibrationRecord(
            record_id, "setup", 1, self.setup.snapshot(), "battery", 1,
            self.battery.snapshot(), 1, ["A"], net_energy_wh=3.0, **kwargs,
        )
        self.manager.calibrations[record_id] = record
        return record

    async def approve(self, kind, record_id, approved=True, reason="Description corrected"):
        await self.manager.async_set_measurement_revision_approval(
            kind, record_id, approved, reason,
            expected_setup_revision=self.setup.revision,
            expected_battery_revision=self.battery.revision if kind == "calibration" else None,
        )

    async def test_old_idle_approval_changes_use_without_rewriting_origin(self):
        record = self.idle()
        origin = record.as_dict()
        self.setup.revision = 2
        self.assertIsNone(self.manager.idle_summary("setup")["baseline_power_w"])
        await self.approve("idle", "idle")
        self.assertEqual(self.manager.idle_summary("setup")["measurement_ids"], ["idle"])
        self.assertEqual(record.setup_revision, 1)
        self.assertEqual(record.setup_snapshot, origin["setup_snapshot"])
        row = self.manager.frontend_state()["idle_measurements"][0]
        self.assertTrue(row["used"])
        self.assertEqual(row["revision_status"], "approved")
        self.assertEqual(row["current_setup_revision"], 2)
        self.setup.revision = 3
        self.assertEqual(self.manager.idle_summary("setup")["measurement_ids"], [])

    async def test_calibration_approval_is_exact_pair_and_preserves_quantity(self):
        self.calibration(confidence="high")
        self.setup.revision = 2
        self.battery.revision = 4
        await self.approve("calibration", "cal")
        self.assertEqual(self.manager.calibration_summary("setup", "battery", 1)["record_ids"], ["cal"])
        self.assertEqual(self.manager.calibration_summary("setup", "battery", 2)["record_ids"], [])
        self.battery.revision = 5
        self.assertEqual(self.manager.calibration_summary("setup", "battery", 1)["record_ids"], [])

    async def test_revoke_and_validity_are_independent_and_persist(self):
        record = self.idle()
        self.setup.revision = 2
        await self.approve("idle", "idle")
        await self.manager.async_set_measurement_validity("idle", "idle", False, "Battery attached")
        self.assertEqual(self.manager.idle_summary("setup")["measurement_ids"], [])
        await self.manager.async_set_measurement_validity("idle", "idle", True, "Reviewed")
        self.assertEqual(self.manager.idle_summary("setup")["measurement_ids"], ["idle"])
        await self.approve("idle", "idle", False, "Arrangement differs")
        self.assertTrue(record.valid)
        self.assertEqual(self.manager.idle_summary("setup")["measurement_ids"], [])
        restored = IdleMeasurement.from_dict(record.as_dict())
        self.assertEqual(len(restored.validity_history), 2)
        self.assertEqual(restored.validity_history[0]["reason"], "Battery attached")
        self.assertTrue(restored.revision_approvals[0]["revoked_at"])
        self.assertEqual(restored.revision_approvals[0]["revoke_reason"], "Arrangement differs")

    async def test_stale_or_unjustified_approval_does_not_mutate(self):
        record = self.idle()
        self.setup.revision = 2
        with self.assertRaisesRegex(Exception, "revision"):
            await self.manager.async_set_measurement_revision_approval(
                "idle", "idle", True, "Formal", expected_setup_revision=1,
            )
        with self.assertRaisesRegex(Exception, "reason"):
            await self.approve("idle", "idle", reason="  ")
        self.assertEqual(record.revision_approvals, [])
        self.manager.session = ChargeSession(mode="charging")
        with self.assertRaisesRegex(Exception, "active"):
            await self.approve("idle", "idle")

    async def test_invalid_idle_reference_excludes_dependent_calibration_until_restored(self):
        self.idle()
        self.calibration(confidence="high", idle_measurement_ids=["idle"])
        await self.manager.async_set_measurement_validity("idle", "idle", False, "Bad measurement")
        self.assertEqual(self.manager.calibration_summary("setup", "battery", 1)["record_ids"], [])
        row = self.manager.frontend_state()["calibrations"][0]
        self.assertEqual(row["usage_reason"], "invalid_idle_reference")
        self.assertTrue(row["valid"])
        await self.manager.async_set_measurement_validity("idle", "idle", True)
        self.assertEqual(self.manager.calibration_summary("setup", "battery", 1)["record_ids"], ["cal"])

    def test_usage_reports_lower_confidence_exclusion_separately_from_validity(self):
        self.calibration("low", confidence="low")
        self.calibration("high", confidence="high")
        rows = {x["calibration_id"]: x for x in self.manager.frontend_state()["calibrations"]}
        self.assertTrue(rows["high"]["used"])
        self.assertTrue(rows["low"]["valid"])
        self.assertFalse(rows["low"]["used"])
        self.assertEqual(rows["low"]["usage_reason"], "lower_confidence")

    def test_historical_details_are_on_demand_bounded_and_preserve_peak(self):
        start = datetime(2026, 9, 1, tzinfo=timezone.utc)
        samples = [MeasurementSample(
            (start + timedelta(seconds=i)).isoformat(),
            power_w=90 if i == 333 else 0.2, gross_energy_wh=i / 10000,
        ) for i in range(1500)]
        record = self.idle(samples=samples)
        self.setup.revision = 2
        self.setup.charger_model = "Corrected description"
        row = self.manager.frontend_state()["idle_measurements"][0]
        self.assertNotIn("samples", row)
        self.assertNotIn("chart_samples", row)
        detail = self.manager.measurement_details("idle", "idle")
        self.assertLessEqual(len(detail["chart_samples"]), 600)
        self.assertEqual(detail["sample_count"], 1500)
        self.assertEqual(detail["chart_samples"][0]["timestamp"], samples[0].timestamp)
        self.assertEqual(detail["chart_samples"][-1]["timestamp"], samples[-1].timestamp)
        self.assertIn(90, [s["power_w"] for s in detail["chart_samples"]])
        self.assertEqual(detail["setup_snapshot"], record.setup_snapshot)
        change = next(x for x in detail["revision_differences"] if x["field"] == "charger_model")
        self.assertEqual(change["current"], "Corrected description")

    def test_used_records_are_not_lost_behind_global_history_cutoff(self):
        self.idle(started_at="2020-01-01")
        for index in range(105):
            self.manager.idle_measurements[str(index)] = IdleMeasurement(
                str(index), "another-setup", 1, {}, started_at="2026-01-01",
            )
        self.assertIn("idle", [x["measurement_id"] for x in self.manager.frontend_state()["idle_measurements"]])

    async def test_reanalysis_retains_prior_result_and_replaces_invalid_reference(self):
        old = self.idle("old")
        old.valid = False
        self.idle("new")
        record = self.calibration(
            idle_measurement_ids=["old"], idle_baseline_power_w=0.1,
            session_started_at="2026-09-01T10:00:00+00:00",
            switch_on_at="2026-09-01T10:00:00+00:00",
            charge_finished_at="2026-09-01T11:00:00+00:00",
            samples=[
                MeasurementSample("2026-09-01T10:00:00+00:00", gross_energy_wh=0, power_w=3.2),
                MeasurementSample("2026-09-01T11:00:00+00:00", gross_energy_wh=3.2, power_w=0.2),
            ],
        )
        await self.manager.async_reanalyze_calibration(
            "cal", expected_setup_revision=1, expected_battery_revision=1,
        )
        self.assertEqual(record.idle_measurement_ids, ["new"])
        self.assertEqual(record.analysis_history[0]["idle_measurement_ids"], ["old"])
        self.assertEqual(record.analysis_revision, 2)
        self.assertEqual(record.setup_revision, 1)
        self.assertAlmostEqual(record.net_energy_wh, 3.0)
        self.assertEqual(self.manager.calibration_summary("setup", "battery", 1)["record_ids"], ["cal"])

    async def test_restoring_reliable_idle_reprocesses_pending_calibration(self):
        idle = self.idle(valid=False)
        record = self.calibration(
            idle_correction_status="pending",
            session_started_at="2026-09-01T10:00:00+00:00",
            charge_finished_at="2026-09-01T11:00:00+00:00",
            samples=[MeasurementSample("2026-09-01T11:00:00+00:00", gross_energy_wh=3.2)],
        )
        await self.manager.async_set_measurement_validity("idle", idle.measurement_id, True)
        self.assertEqual(record.idle_correction_status, "applied")
        self.assertEqual(record.idle_measurement_ids, ["idle"])
