from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from test_core import (
    BatteryChargeManager,
    BatteryType,
    CalibrationRecord,
    ChargerSetup,
    ConfigEntry,
    FakeHass,
    IdleMeasurement,
    MeasurementSample,
)


class Release011RegressionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.hass = FakeHass()
        self.manager = BatteryChargeManager(self.hass, ConfigEntry())
        self.setup = ChargerSetup(
            setup_id="setup-1",
            name="Setup",
            switch_entity="switch.charger",
            energy_sensor="sensor.energy",
            power_sensor="sensor.power",
            port_labels=["A", "B", "C", "D"],
            revision=1,
        )
        self.battery = BatteryType(
            battery_id="battery-1",
            name="Battery",
            nominal_capacity_mah=1700,
            technology="Li-Ion USB-C",
            form_factor="AA",
            revision=1,
        )
        self.manager.setups[self.setup.setup_id] = self.setup
        self.manager.batteries[self.battery.battery_id] = self.battery
        self.manager.selected_setup_id = self.setup.setup_id
        self.manager.selected_battery_id = self.battery.battery_id

    async def test_calibration_can_start_without_idle_measurement(self) -> None:
        captured = {}

        async def fake_begin_session(**kwargs):
            captured.update(kwargs)

        self.manager._async_begin_session = fake_begin_session

        await self.manager.async_start_calibration()

        self.assertEqual(captured["mode"], "calibrating")
        self.assertEqual(captured["setup"], self.setup)
        self.assertEqual(captured["battery"], self.battery)

    async def test_fixed_idle_duration_below_minimum_is_clamped(self) -> None:
        for requested in (0, 1, 4.9):
            with self.subTest(requested=requested):
                captured = {}

                async def fake_begin_session(**kwargs):
                    captured.update(kwargs)

                self.manager._async_begin_session = fake_begin_session

                await self.manager.async_start_idle_measurement(
                    mode="fixed",
                    duration_minutes=requested,
                )

                self.assertEqual(captured["duration_minutes"], 5.0)

    async def test_pending_calibration_is_corrected_after_reliable_idle_measurement(
        self,
    ) -> None:
        start = datetime(2026, 8, 31, 10, 0, tzinfo=timezone.utc)
        endpoint = start + timedelta(minutes=60)
        samples = [
            MeasurementSample(
                timestamp=start.isoformat(),
                gross_energy_wh=0.0,
                net_energy_wh=0.0,
                power_w=3.2,
                switch_state="on",
            ),
            MeasurementSample(
                timestamp=(start + timedelta(minutes=30)).isoformat(),
                gross_energy_wh=1.6,
                net_energy_wh=1.6,
                power_w=3.2,
                switch_state="on",
            ),
            MeasurementSample(
                timestamp=endpoint.isoformat(),
                gross_energy_wh=3.2,
                net_energy_wh=3.2,
                power_w=0.2,
                switch_state="on",
            ),
        ]
        record = CalibrationRecord(
            calibration_id="calibration-pending",
            setup_id=self.setup.setup_id,
            setup_revision=self.setup.revision,
            setup_snapshot=self.setup.snapshot(),
            battery_id=self.battery.battery_id,
            battery_revision=self.battery.revision,
            battery_snapshot=self.battery.snapshot(),
            quantity=1,
            ports=["A"],
            switch_on_at=start.isoformat(),
            charge_started_at=start.isoformat(),
            charge_finished_at=endpoint.isoformat(),
            session_finished_at=endpoint.isoformat(),
            gross_energy_wh=3.2,
            net_energy_wh=3.2,
            idle_baseline_power_w=None,
            idle_correction_status="pending",
            confidence="low",
            samples=samples,
        )
        self.manager.calibrations[record.calibration_id] = record
        idle = IdleMeasurement(
            measurement_id="idle-1",
            setup_id=self.setup.setup_id,
            setup_revision=self.setup.revision,
            setup_snapshot=self.setup.snapshot(),
            duration_seconds=3600,
            gross_energy_wh=0.2,
            average_power_w=0.2,
            median_power_w=0.2,
            reliable=True,
            confidence="high",
        )
        self.manager.idle_measurements[idle.measurement_id] = idle

        corrected = await self.manager.async_reprocess_pending_calibrations(
            self.setup.setup_id
        )

        self.assertEqual(corrected, 1)
        self.assertEqual(record.idle_correction_status, "applied")
        self.assertAlmostEqual(record.idle_baseline_power_w, 0.2)
        self.assertAlmostEqual(record.idle_energy_wh, 0.2)
        self.assertAlmostEqual(record.net_energy_wh, 3.0)
        self.assertEqual(record.idle_measurement_ids, ["idle-1"])
        self.assertGreaterEqual(record.analysis_revision, 2)
        summary = self.manager.calibration_summary(
            self.setup.setup_id,
            self.battery.battery_id,
            1,
        )
        self.assertEqual(summary["pending_count"], 0)
        self.assertAlmostEqual(summary["median_net_energy_wh"], 3.0)


if __name__ == "__main__":
    unittest.main()
