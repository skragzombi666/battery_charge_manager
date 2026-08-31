"""Number entities for Battery Charge Manager."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BatteryChargeManagerEntity
from .manager import BatteryChargeManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    manager: BatteryChargeManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TargetChargeNumber(manager, entry)])


class TargetChargeNumber(BatteryChargeManagerEntity, NumberEntity):
    """Storage-charge target percentage."""

    _attr_translation_key = "target_charge"
    _attr_icon = "mdi:battery-50"
    _attr_native_min_value = 20
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize number."""
        super().__init__(manager, entry, "target_charge")

    @property
    def native_value(self) -> float:
        """Return target percentage."""
        return float(self.manager.target_percent)

    async def async_set_native_value(self, value: float) -> None:
        """Set target percentage."""
        await self.manager.async_set_target_percent(round(value))
