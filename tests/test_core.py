from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "custom_components" / "battery_charge_manager"


def _module(name: str) -> types.ModuleType:
    module = types.ModuleType(name)
    sys.modules[name] = module
    return module


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _install_stubs() -> None:
    custom_components = _module("custom_components")
    custom_components.__path__ = [str(ROOT / "custom_components")]
    package = _module("custom_components.battery_charge_manager")
    package.__path__ = [str(PACKAGE)]

    homeassistant = _module("homeassistant")
    components = _module("homeassistant.components")
    persistent_notification = _module(
        "homeassistant.components.persistent_notification"
    )

    async def async_create(*_args, **_kwargs):
        return None

    persistent_notification.async_create = async_create
    components.persistent_notification = persistent_notification
    homeassistant.components = components

    config_entries = _module("homeassistant.config_entries")

    class ConfigEntry:
        def __init__(self, options=None):
            self.options = options or {}
            self.entry_id = "test-entry"

    config_entries.ConfigEntry = ConfigEntry
    homeassistant.config_entries = config_entries

    const = _module("homeassistant.const")

    class UnitOfEnergy:
        WATT_HOUR = "Wh"
        KILO_WATT_HOUR = "kWh"

    class UnitOfPower:
        WATT = "W"
        KILO_WATT = "kW"

    class UnitOfTemperature:
        CELSIUS = "°C"
        FAHRENHEIT = "°F"
        KELVIN = "K"

    const.UnitOfEnergy = UnitOfEnergy
    const.UnitOfPower = UnitOfPower
    const.UnitOfTemperature = UnitOfTemperature
    homeassistant.const = const

    core = _module("homeassistant.core")

    class State:
        def __init__(self, state: str, attributes=None):
            self.state = state
            self.attributes = attributes or {}

    class Event:
        def __init__(self, data=None):
            self.data = data or {}

    class HomeAssistant:
        pass

    core.State = State
    core.Event = Event
    core.HomeAssistant = HomeAssistant
    core.callback = lambda function: function
    homeassistant.core = core

    exceptions = _module("homeassistant.exceptions")

    class HomeAssistantError(Exception):
        pass

    exceptions.HomeAssistantError = HomeAssistantError
    homeassistant.exceptions = exceptions

    helpers = _module("homeassistant.helpers")
    dispatcher = _module("homeassistant.helpers.dispatcher")
    dispatcher.async_dispatcher_send = lambda *_args, **_kwargs: None
    event = _module("homeassistant.helpers.event")
    event.async_call_later = lambda *_args, **_kwargs: lambda: None
    event.async_track_state_change_event = lambda *_args, **_kwargs: lambda: None
    event.async_track_time_interval = lambda *_args, **_kwargs: lambda: None
    storage = _module("homeassistant.helpers.storage")

    class Store:
        def __class_getitem__(cls, _item):
            return cls

        def __init__(self, *_args, **_kwargs):
            pass

        async def async_load(self):
            return None

        async def async_save(self, _data):
            return None

    storage.Store = Store
    helpers.dispatcher = dispatcher
    helpers.event = event
    helpers.storage = storage
    homeassistant.helpers = helpers

    util = _module("homeassistant.util")

    class DtUtil:
        @staticmethod
        def utcnow():
            return datetime.now(timezone.utc)

        @staticmethod
        def parse_datetime(value):
            if not value:
                return None
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    util.dt = DtUtil
    sys.modules["homeassistant.util.dt"] = DtUtil
    homeassistant.util = util


_install_stubs()
const = _load(
    "custom_components.battery_charge_manager.const", PACKAGE / "const.py"
)
models = _load(
    "custom_components.battery_charge_manager.models", PACKAGE / "models.py"
)
manager_module = _load(
    "custom_components.battery_charge_manager.manager", PACKAGE / "manager.py"
)

BatteryChargeManager = manager_module.BatteryChargeManager
BatteryType = models.BatteryType
CalibrationRecord = models.CalibrationRecord
ChargerSetup = models.ChargerSetup
ChargeSession = models.ChargeSession
IdleMeasurement = models.IdleMeasurement
MeasurementSample = models.MeasurementSample
State = sys.modules["homeassistant.core"].State
ConfigEntry = sys.modules["homeassistant.config_entries"].ConfigEntry


class FakeStates:
    def __init__(self):
        self.values = {}

    def get(self, entity_id):
        return self.values.get(entity_id)


class FakeHass:
    def __init__(self):
        self.states = FakeStates()
        self.data = {}


class ModelTests(unittest.TestCase):
    def test_versioned_models_round_trip(self):
        battery = BatteryType(
            battery_id="battery-1",
            name="USB-C AA",
            manufacturer="Example",
            model="AA-1700",
            nominal_capacity_mah=1700,
            nominal_voltage_v=1.5,
            nominal_energy_wh=2.55,
            technology="Li-Ion USB-C",
            form_factor="AA",
            discharge_method="Use until normal device cutoff",
            rest_time_minutes=30,
            starting_condition_notes="Same device and temperature range",
            revision=3,
        )
        self.assertEqual(
            BatteryType.from_dict(battery.as_dict()).as_dict(),
            battery.as_dict(),
        )

        setup = ChargerSetup(
            setup_id="setup-1",
            name="Four-port USB",
            switch_entity="switch.charger",
            energy_sensor="sensor.charger_energy",
            power_sensor="sensor.charger_power",
            temperature_sensor="sensor.charger_temperature",
            port_labels=["A", "B", "C", "D"],
            revision=2,
        )
        self.assertEqual(setup.ports_for_quantity(3), ["A", "B", "C"])
        self.assertEqual(
            ChargerSetup.from_dict(setup.as_dict()).as_dict(),
            setup.as_dict(),
        )

    def test_legacy_session_migration(self):
        session = ChargeSession.from_dict(
            {
                "mode": "charging",
                "battery_id": "battery-1",
                "quantity": 4,
                "delivered_energy_wh": 4.2,
                "last_energy_wh": 123.4,
                "started_at": "2026-08-31T12:00:00+00:00",
            }
        )
        self.assertEqual(session.gross_energy_wh, 4.2)
        self.assertEqual(session.net_energy_wh, 4.2)
        self.assertEqual(session.last_raw_energy_wh, 123.4)
        self.assertEqual(session.session_started_at, "2026-08-31T12:00:00+00:00")

    def test_idle_baseline_prefers_median(self):
        measurement = IdleMeasurement(
            measurement_id="idle-1",
            setup_id="setup-1",
            setup_revision=1,
            setup_snapshot={},
            average_power_w=0.31,
            median_power_w=0.24,
        )
        self.assertAlmostEqual(measurement.baseline_power_w, 0.24)


class ManagerStatisticsTests(unittest.TestCase):
    def setUp(self):
        self.hass = FakeHass()
        self.manager = BatteryChargeManager(self.hass, ConfigEntry())
        self.setup = ChargerSetup(
            setup_id="setup-1",
            name="Setup",
            switch_entity="switch.charger",
            energy_sensor="sensor.energy",
            power_sensor="sensor.power",
            port_labels=["A", "B", "C", "D"],
            revision=2,
        )
        self.battery = BatteryType(
            battery_id="battery-1",
            name="Battery",
            nominal_capacity_mah=1700,
            technology="Li-Ion USB-C",
            form_factor="AA",
            revision=3,
        )
        self.manager.setups[self.setup.setup_id] = self.setup
        self.manager.batteries[self.battery.battery_id] = self.battery
        self.manager.selected_setup_id = self.setup.setup_id
        self.manager.selected_battery_id = self.battery.battery_id

    def test_idle_measurements_are_combined_and_version_filtered(self):
        for index, value in enumerate((0.20, 0.22)):
            item = IdleMeasurement(
                measurement_id=f"idle-{index}",
                setup_id=self.setup.setup_id,
                setup_revision=self.setup.revision,
                setup_snapshot={},
                average_power_w=value,
                median_power_w=value,
                reliable=True,
                confidence="high",
            )
            self.manager.idle_measurements[item.measurement_id] = item
        old = IdleMeasurement(
            measurement_id="old-idle",
            setup_id=self.setup.setup_id,
            setup_revision=1,
            setup_snapshot={},
            average_power_w=0.5,
            reliable=True,
        )
        self.manager.idle_measurements[old.measurement_id] = old

        summary = self.manager.idle_summary(self.setup.setup_id)
        self.assertAlmostEqual(summary["baseline_power_w"], 0.21)
        self.assertEqual(summary["reliable_count"], 2)
        self.assertEqual(summary["outdated_count"], 1)
        self.assertEqual(summary["quality"], "stable")

    def test_calibration_quality_and_linear_model(self):
        values = {1: [2.9, 3.0, 3.1], 2: [5.8, 6.0, 6.1], 4: [11.7, 11.9, 12.0]}
        for quantity, energies in values.items():
            for index, energy in enumerate(energies):
                record = CalibrationRecord(
                    calibration_id=f"{quantity}-{index}",
                    setup_id=self.setup.setup_id,
                    setup_revision=self.setup.revision,
                    setup_snapshot=self.setup.snapshot(),
                    battery_id=self.battery.battery_id,
                    battery_revision=self.battery.revision,
                    battery_snapshot=self.battery.snapshot(),
                    quantity=quantity,
                    ports=self.setup.ports_for_quantity(quantity),
                    session_started_at=(
                        datetime(2026, 8, 1, tzinfo=timezone.utc)
                        + timedelta(days=index)
                    ).isoformat(),
                    charge_duration_seconds=7200 + index * 60,
                    net_energy_wh=energy,
                    confidence="high",
                )
                self.manager.calibrations[record.calibration_id] = record

        summary = self.manager.calibration_summary(
            self.setup.setup_id, self.battery.battery_id, 1
        )
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["quality"], "stable")
        self.assertAlmostEqual(summary["median_net_energy_wh"], 3.0)
        self.assertEqual(summary["median_charge_duration_seconds"], 7260)

        fitted = self.manager.linear_profile_model(
            self.setup.setup_id, self.battery.battery_id
        )
        self.assertTrue(fitted["available"])
        self.assertGreater(fitted["r_squared"], 0.99)
        self.assertFalse(fitted["operational_use"])

    def test_automatic_endpoint_is_retrospective(self):
        start = datetime(2026, 8, 31, 10, 0, tzinfo=timezone.utc)
        self.manager.session = ChargeSession(
            mode="calibrating",
            setup_id=self.setup.setup_id,
            battery_id=self.battery.battery_id,
            charge_started_at=start.isoformat(),
            last_significant_at=(start + timedelta(minutes=10)).isoformat(),
            last_significant_net_energy_wh=3.0,
            peak_net_power_w=4.0,
            net_energy_wh=3.03,
        )
        samples = []
        for minute in range(0, 41, 2):
            energy = 0.3 * min(minute, 10) + 0.001 * max(0, minute - 10)
            samples.append(
                MeasurementSample(
                    timestamp=(start + timedelta(minutes=minute)).isoformat(),
                    gross_energy_wh=energy,
                    net_energy_wh=energy,
                    power_w=0.2 if minute > 10 else 4.0,
                    net_power_w=0.02 if minute > 10 else 3.8,
                    switch_state="on",
                )
            )
        self.manager.session.samples = samples
        self.manager.session.last_sample_at = samples[-1].timestamp
        self.manager.session.current_net_power_w = 0.02

        first = self.manager._detect_calibration_end(start + timedelta(minutes=20))
        self.assertFalse(first)
        self.assertEqual(
            self.manager.session.candidate_end_at,
            (start + timedelta(minutes=10)).isoformat(),
        )
        second = self.manager._detect_calibration_end(start + timedelta(minutes=31))
        self.assertTrue(second)
        self.assertEqual(
            self.manager.session.charge_finished_at,
            (start + timedelta(minutes=10)).isoformat(),
        )

    def test_idle_trace_can_be_reliable_from_power_sensor(self):
        start = datetime(2026, 8, 31, 10, 0, tzinfo=timezone.utc)
        self.hass.states.values["sensor.energy"] = State(
            "1.000", {"unit_of_measurement": "kWh"}
        )
        self.manager.session = ChargeSession(
            mode="idle_measuring",
            setup_id=self.setup.setup_id,
            switch_on_at=start.isoformat(),
            last_sample_at=(start + timedelta(minutes=65)).isoformat(),
            gross_energy_wh=0.22,
        )
        self.manager.session.samples = [
            MeasurementSample(
                timestamp=(start + timedelta(minutes=minute)).isoformat(),
                raw_energy_wh=1000 + 0.0035 * minute,
                gross_energy_wh=0.0035 * minute,
                power_w=0.20 + (0.002 if minute % 2 else -0.002),
                switch_state="on",
            )
            for minute in range(0, 66, 5)
        ]
        assessment = self.manager._assess_idle_trace()
        self.assertTrue(assessment["reliable"])
        self.assertEqual(assessment["confidence"], "high")
        self.assertAlmostEqual(assessment["median_power_w"], 0.2, places=2)


if __name__ == "__main__":
    unittest.main()
