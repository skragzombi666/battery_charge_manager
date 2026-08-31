"""Sensor entities for Battery Charge Manager."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .entity import BatteryChargeManagerEntity
from .manager import BatteryChargeManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    manager: BatteryChargeManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            StatusSensor(manager, entry),
            PhaseSensor(manager, entry),
            TargetEnergySensor(manager, entry),
            GrossEnergySensor(manager, entry),
            IdleEnergySensor(manager, entry),
            NetEnergySensor(manager, entry),
            ProgressSensor(manager, entry),
            CurrentPowerSensor(manager, entry),
            CurrentTemperatureSensor(manager, entry),
            ElapsedTimeSensor(manager, entry),
            IdleBaselineSensor(manager, entry),
            CalibrationQualitySensor(manager, entry),
            BatteryInfoSensor(manager, entry),
        ]
    )


class StatusSensor(BatteryChargeManagerEntity, SensorEntity):
    """Session status with complete lifecycle metadata."""

    _attr_translation_key = "status"
    _attr_icon = "mdi:battery-sync"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "status")

    @property
    def native_value(self) -> str:
        return self.manager.session.mode

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        session = self.manager.session
        setup = self.manager.setups.get(session.setup_id or "")
        battery = self.manager.batteries.get(session.battery_id or "")
        return {
            "setup": setup.name if setup else None,
            "battery": battery.name if battery else None,
            "quantity": session.quantity,
            "ports": session.ports,
            "target_percent": session.target_percent,
            "session_started_at": session.session_started_at,
            "switch_on_at": session.switch_on_at,
            "charge_started_at": session.charge_started_at,
            "taper_started_at": session.taper_started_at,
            "candidate_end_at": session.candidate_end_at,
            "charge_finished_at": session.charge_finished_at,
            "end_detected_at": session.end_detected_at,
            "switch_off_at": session.switch_off_at,
            "session_finished_at": session.session_finished_at,
            "end_reason": session.end_reason,
            "restart_count": session.restart_count,
            "sample_count": len(session.samples),
            "idle_baseline_power_w": session.idle_baseline_power_w,
            "idle_measurement_ids": session.idle_measurement_ids,
            "idle_quality": session.idle_quality,
            "peak_temperature_c": session.peak_temperature_c,
        }


class PhaseSensor(BatteryChargeManagerEntity, SensorEntity):
    """Current recognized charging phase."""

    _attr_translation_key = "phase"
    _attr_icon = "mdi:chart-timeline-variant"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "phase")

    @property
    def native_value(self) -> str:
        return self.manager.session.phase


class TargetEnergySensor(BatteryChargeManagerEntity, SensorEntity):
    """Calculated relative target energy."""

    _attr_translation_key = "target_energy"
    _attr_icon = "mdi:target"
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "target_energy")

    @property
    def native_value(self) -> float | None:
        value = self.manager.session.target_energy_wh
        return round(value, 4) if value is not None else None


class _EnergySensor(BatteryChargeManagerEntity, SensorEntity):
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 3


class GrossEnergySensor(_EnergySensor):
    _attr_translation_key = "gross_energy"
    _attr_icon = "mdi:transmission-tower-import"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "gross_energy")

    @property
    def native_value(self) -> float:
        return round(self.manager.session.gross_energy_wh, 5)


class IdleEnergySensor(_EnergySensor):
    _attr_translation_key = "idle_energy"
    _attr_icon = "mdi:power-plug-off-outline"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "idle_energy")

    @property
    def native_value(self) -> float:
        return round(self.manager.session.idle_energy_wh, 5)


class NetEnergySensor(_EnergySensor):
    _attr_translation_key = "net_energy"
    _attr_icon = "mdi:lightning-bolt"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "net_energy")

    @property
    def native_value(self) -> float:
        return round(self.manager.session.net_energy_wh, 5)


class ProgressSensor(BatteryChargeManagerEntity, SensorEntity):
    """Relative target progress."""

    _attr_translation_key = "progress"
    _attr_icon = "mdi:progress-clock"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "progress")

    @property
    def native_value(self) -> float | None:
        value = self.manager.progress_percent
        return round(value, 1) if value is not None else None


class CurrentPowerSensor(BatteryChargeManagerEntity, SensorEntity):
    """Current gross smart-plug power."""

    _attr_translation_key = "current_power"
    _attr_icon = "mdi:flash"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "current_power")

    @property
    def native_value(self) -> float | None:
        value = self.manager.session.current_power_w
        return round(value, 3) if value is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "net_power_w": self.manager.session.current_net_power_w,
            "peak_power_w": self.manager.session.peak_power_w,
            "peak_net_power_w": self.manager.session.peak_net_power_w,
        }


class CurrentTemperatureSensor(BatteryChargeManagerEntity, SensorEntity):
    """Current optional setup temperature."""

    _attr_translation_key = "current_temperature"
    _attr_icon = "mdi:thermometer"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "current_temperature")

    @property
    def native_value(self) -> float | None:
        value = self.manager.session.current_temperature_c
        return round(value, 2) if value is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"peak_temperature_c": self.manager.session.peak_temperature_c}


class ElapsedTimeSensor(BatteryChargeManagerEntity, SensorEntity):
    """Elapsed session time."""

    _attr_translation_key = "elapsed_time"
    _attr_icon = "mdi:timer-outline"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "elapsed_time")

    @property
    def native_value(self) -> int:
        started = dt_util.parse_datetime(
            self.manager.session.session_started_at or ""
        )
        if started is None:
            return 0
        finished = dt_util.parse_datetime(
            self.manager.session.session_finished_at or ""
        )
        end = finished or dt_util.utcnow()
        return max(0, round((end - started).total_seconds()))


class IdleBaselineSensor(BatteryChargeManagerEntity, SensorEntity):
    """Aggregated setup idle power baseline."""

    _attr_translation_key = "idle_baseline"
    _attr_icon = "mdi:power-plug-off-outline"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 3

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "idle_baseline")

    @property
    def native_value(self) -> float | None:
        setup = self.manager.active_setup
        if setup is None:
            return None
        value = self.manager.idle_summary(setup.setup_id)["baseline_power_w"]
        return round(value, 5) if value is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        setup = self.manager.active_setup
        return self.manager.idle_summary(setup.setup_id) if setup else {}


class CalibrationQualitySensor(BatteryChargeManagerEntity, SensorEntity):
    """Quality of the selected exact calibration profile."""

    _attr_translation_key = "calibration_quality"
    _attr_icon = "mdi:check-decagram-outline"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "calibration_quality")

    @property
    def native_value(self) -> str:
        setup = self.manager.active_setup
        battery = self.manager.active_battery
        if setup is None or battery is None:
            return "none"
        return self.manager.calibration_summary(
            setup.setup_id,
            battery.battery_id,
            self.manager.selected_quantity,
        )["quality"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        setup = self.manager.active_setup
        battery = self.manager.active_battery
        if setup is None or battery is None:
            return {}
        return self.manager.calibration_summary(
            setup.setup_id,
            battery.battery_id,
            self.manager.selected_quantity,
        )


class BatteryInfoSensor(BatteryChargeManagerEntity, SensorEntity):
    """Selected battery metadata and per-quantity summaries."""

    _attr_translation_key = "battery_info"
    _attr_icon = "mdi:battery-information"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "battery_info")

    @property
    def native_value(self) -> str | None:
        battery = self.manager.active_battery
        return battery.name if battery else None

    @property
    def entity_picture(self) -> str | None:
        battery = self.manager.active_battery
        if battery is None or not battery.image:
            return None
        if isinstance(battery.image, str):
            return battery.image
        return battery.image.get("media_content_id") or battery.image.get("url")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        battery = self.manager.active_battery
        setup = self.manager.active_setup
        if battery is None:
            return {}
        result = battery.as_dict()
        if setup:
            result["calibrations"] = {
                str(quantity): self.manager.calibration_summary(
                    setup.setup_id, battery.battery_id, quantity
                )
                for quantity in range(1, len(setup.port_labels) + 1)
            }
            result["linear_model"] = self.manager.linear_profile_model(
                setup.setup_id, battery.battery_id
            )
        return result
