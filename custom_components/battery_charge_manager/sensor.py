"""Sensor entities for Battery Charge Manager."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SESSION_CHARGING
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
            TargetEnergySensor(manager, entry),
            DeliveredEnergySensor(manager, entry),
            ProgressSensor(manager, entry),
            BatteryInfoSensor(manager, entry),
        ]
    )


class StatusSensor(BatteryChargeManagerEntity, SensorEntity):
    """Charge manager status."""

    _attr_translation_key = "status"
    _attr_icon = "mdi:battery-sync"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(manager, entry, "status")

    @property
    def native_value(self) -> str:
        """Return current mode."""
        return self.manager.session.mode

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return session attributes."""
        session = self.manager.session
        battery = self.manager.batteries.get(session.battery_id or "")
        return {
            "battery": battery.name if battery else None,
            "quantity": session.quantity,
            "target_percent": session.target_percent,
            "started_at": session.started_at,
            "finished_at": session.finished_at,
            "end_reason": session.end_reason,
            "switch_entity": self.manager.switch_entity,
            "energy_sensor": self.manager.energy_sensor,
            "power_sensor": self.manager.power_sensor,
        }


class TargetEnergySensor(BatteryChargeManagerEntity, SensorEntity):
    """Calculated target energy."""

    _attr_translation_key = "target_energy"
    _attr_icon = "mdi:target"
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(manager, entry, "target_energy")

    @property
    def native_value(self) -> float | None:
        """Return target energy."""
        value = self.manager.session.target_energy_wh
        return round(value, 4) if value is not None else None


class DeliveredEnergySensor(BatteryChargeManagerEntity, SensorEntity):
    """Energy delivered in the current session."""

    _attr_translation_key = "delivered_energy"
    _attr_icon = "mdi:lightning-bolt"
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(manager, entry, "delivered_energy")

    @property
    def native_value(self) -> float:
        """Return delivered energy."""
        return round(self.manager.session.delivered_energy_wh, 4)


class ProgressSensor(BatteryChargeManagerEntity, SensorEntity):
    """Charge progress."""

    _attr_translation_key = "progress"
    _attr_icon = "mdi:progress-clock"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(manager, entry, "progress")

    @property
    def native_value(self) -> float | None:
        """Return charge progress."""
        value = self.manager.progress_percent
        return round(value, 1) if value is not None else None


class BatteryInfoSensor(BatteryChargeManagerEntity, SensorEntity):
    """Selected battery metadata and calibration summary."""

    _attr_translation_key = "battery_info"
    _attr_icon = "mdi:battery-information"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(manager, entry, "battery_info")

    @property
    def native_value(self) -> str | None:
        """Return selected battery name."""
        battery = self.manager.active_battery
        return battery.name if battery else None

    @property
    def entity_picture(self) -> str | None:
        """Return battery image."""
        battery = self.manager.active_battery
        return battery.image.get("media_content_id") if battery and battery.image else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return battery details."""
        battery = self.manager.active_battery
        if battery is None:
            return {}
        return {
            "battery_id": battery.battery_id,
            "nominal_capacity_mah": battery.nominal_capacity_mah,
            "technology": battery.technology,
            "form_factor": battery.form_factor,
            "image": battery.image,
            "calibrations": self.manager.calibration_summary(battery),
        }
