"""Number entities for Battery Charge Manager."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SESSION_IDLE
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
    """Set relative target charge energy."""

    _attr_translation_key = "target_charge"
    _attr_icon = "mdi:battery-50"
    _attr_native_min_value = 20
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "target_charge")

    @property
    def native_value(self) -> float:
        return float(self.manager.target_percent)

    @property
    def available(self) -> bool:
        return self.manager.session.mode == SESSION_IDLE

    async def async_set_native_value(self, value: float) -> None:
        await self.manager.async_set_target_percent(round(value))
