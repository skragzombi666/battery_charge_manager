from __future__ import annotations

import unittest

from test_core import BatteryChargeManager, ConfigEntry, FakeHass


class BatteryNominalEnergyTests(unittest.IsolatedAsyncioTestCase):
    async def test_nominal_capacity_is_optional_when_nominal_energy_is_given(self) -> None:
        manager = BatteryChargeManager(FakeHass(), ConfigEntry())

        battery = await manager.async_add_or_update_battery(
            {
                "name": "3600",
                "manufacturer": "Tosiicop",
                "model": "TPBattery-AA",
                "nominal_capacity_mah": None,
                "nominal_voltage_v": 1.5,
                "nominal_energy_wh": 3.6,
                "technology": "Li-Ion USB-C",
                "form_factor": "AA",
            }
        )

        self.assertIsNone(battery.nominal_capacity_mah)
        self.assertAlmostEqual(battery.nominal_energy_wh, 3.6)


if __name__ == "__main__":
    unittest.main()
