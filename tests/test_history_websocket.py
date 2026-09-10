"""Exercise actual handler bodies without the unavailable HA transport runtime.

HA's decorators/schema validation are outside these unit tests. Extracting the
functions keeps their argument forwarding and exception handling unmodified.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

from test_core import (
    BatteryChargeManager, BatteryType, CalibrationRecord, ChargerSetup,
    ConfigEntry, FakeHass, IdleMeasurement, manager_module,
)


def handler_namespace():
    path = Path(__file__).resolve().parents[1] / "custom_components/battery_charge_manager/websocket_api.py"
    names = {
        "_manager", "_send_error", "ws_get_measurement",
        "ws_set_measurement_validity", "ws_set_measurement_revision_approval",
        "ws_reanalyze_calibration",
    }
    parsed = ast.parse(path.read_text())
    functions = [node for node in parsed.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and node.name in names]
    for node in functions:
        node.decorator_list = []
    module = ast.Module(body=ast.parse("from __future__ import annotations").body + functions, type_ignores=[])
    namespace = {
        "DOMAIN": "battery_charge_manager",
        "HomeAssistantError": manager_module.HomeAssistantError,
        "websocket_api": SimpleNamespace(ERR_HOME_ASSISTANT_ERROR="home_assistant_error"),
    }
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)
    return namespace


HANDLERS = handler_namespace()


class HistoryWebsocketTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hass = FakeHass()
        self.manager = BatteryChargeManager(self.hass, ConfigEntry())
        self.hass.data["battery_charge_manager"] = {"entry": self.manager}
        self.setup = ChargerSetup("setup", "Charger", "switch.charger", "sensor.energy")
        self.battery = BatteryType("battery", "AA", 1700, "Li-Ion", "AA")
        self.manager.setups["setup"] = self.setup
        self.manager.batteries["battery"] = self.battery
        self.idle = IdleMeasurement("idle", "setup", 1, self.setup.snapshot(),
                                    reliable=True, average_power_w=0.2)
        self.manager.idle_measurements["idle"] = self.idle
        self.replies = []
        self.connection = SimpleNamespace(
            user=SimpleNamespace(id="reviewer"),
            send_result=lambda *args: self.replies.append(("result", *args)),
            send_error=lambda *args: self.replies.append(("error", *args)),
        )

    def test_detail_lookup_returns_record_and_missing_record_error(self):
        handler = HANDLERS["ws_get_measurement"]
        handler(self.hass, self.connection, {"id": 1, "record_type": "idle", "record_id": "idle"})
        self.assertEqual(self.replies[0][2]["measurement_id"], "idle")
        self.assertEqual(self.replies[0][2]["chart_samples"], [])
        handler(self.hass, self.connection, {"id": 2, "record_type": "idle", "record_id": "missing"})
        self.assertEqual(self.replies[1][:3], ("error", 2, "home_assistant_error"))

    async def test_approval_records_actor_and_rejects_a_stale_revision(self):
        self.setup.revision = 2
        payload = {"id": 3, "record_type": "idle", "record_id": "idle", "approved": True,
                   "reason": "Only description changed", "expected_setup_revision": 1}
        handler = HANDLERS["ws_set_measurement_revision_approval"]
        await handler(self.hass, self.connection, payload)
        self.assertEqual(self.replies[-1][0], "error")
        self.assertEqual(self.idle.revision_approvals, [])
        payload["expected_setup_revision"] = 2
        await handler(self.hass, self.connection, payload)
        self.assertEqual(self.replies[-1], ("result", 3))
        self.assertEqual(self.idle.revision_approvals[0]["actor_id"], "reviewer")
        self.assertEqual(self.idle.setup_revision, 1)

    async def test_calibration_approval_requires_reviewed_battery_revision(self):
        calibration = CalibrationRecord("cal", "setup", 1, self.setup.snapshot(),
            "battery", 1, self.battery.snapshot(), 1, ["A"], net_energy_wh=3)
        self.manager.calibrations["cal"] = calibration
        self.battery.revision = 2
        payload = {"id": 4, "record_type": "calibration", "record_id": "cal", "approved": True,
                   "reason": "Description", "expected_setup_revision": 1}
        await HANDLERS["ws_set_measurement_revision_approval"](self.hass, self.connection, payload)
        self.assertEqual(self.replies[-1][0], "error")
        self.assertEqual(calibration.revision_approvals, [])

    async def test_validity_logs_actor_and_reason(self):
        await HANDLERS["ws_set_measurement_validity"](self.hass, self.connection,
            {"id": 5, "record_type": "idle", "record_id": "idle", "valid": False, "reason": "Battery attached"})
        self.assertEqual(self.replies[-1], ("result", 5))
        self.assertFalse(self.idle.valid)
        self.assertEqual(self.idle.validity_history[-1]["actor_id"], "reviewer")
        self.assertEqual(self.idle.validity_history[-1]["reason"], "Battery attached")

    async def test_reanalysis_returns_operation_errors_to_the_client(self):
        await HANDLERS["ws_reanalyze_calibration"](self.hass, self.connection,
            {"id": 6, "record_id": "missing", "expected_setup_revision": 1, "expected_battery_revision": 1})
        self.assertEqual(self.replies[-1][:3], ("error", 6, "home_assistant_error"))


if __name__ == "__main__":
    unittest.main()
