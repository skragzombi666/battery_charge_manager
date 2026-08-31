"""Select entities for Battery Charge Manager."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
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
    """Set up select entities."""
    manager: BatteryChargeManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ChargingSetupSelect(manager, entry),
            BatteryTypeSelect(manager, entry),
            QuantitySelect(manager, entry),
        ]
    )


class ChargingSetupSelect(BatteryChargeManagerEntity, SelectEntity):
    """Select active physical charging setup."""

    _attr_translation_key = "charging_setup"
    _attr_icon = "mdi:power-socket-eu"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "charging_setup")

    @property
    def options(self) -> list[str]:
        return [item.name for item in self.manager.setups.values()]

    @property
    def current_option(self) -> str | None:
        setup = self.manager.active_setup
        return setup.name if setup else None

    @property
    def available(self) -> bool:
        return self.manager.session.mode == SESSION_IDLE and bool(self.options)

    async def async_select_option(self, option: str) -> None:
        for setup in self.manager.setups.values():
            if setup.name == option:
                await self.manager.async_select_setup(setup.setup_id)
                return


class BatteryTypeSelect(BatteryChargeManagerEntity, SelectEntity):
    """Select battery type."""

    _attr_translation_key = "battery_type"
    _attr_icon = "mdi:battery"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "battery_type")

    @property
    def options(self) -> list[str]:
        return [item.name for item in self.manager.batteries.values()]

    @property
    def current_option(self) -> str | None:
        battery = self.manager.active_battery
        return battery.name if battery else None

    @property
    def available(self) -> bool:
        return self.manager.session.mode == SESSION_IDLE and bool(self.options)

    async def async_select_option(self, option: str) -> None:
        for battery in self.manager.batteries.values():
            if battery.name == option:
                await self.manager.async_select_battery(battery.battery_id)
                return


class QuantitySelect(BatteryChargeManagerEntity, SelectEntity):
    """Select number of batteries and fixed first-N ports."""

    _attr_translation_key = "quantity"
    _attr_icon = "mdi:counter"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        super().__init__(manager, entry, "quantity")

    @property
    def options(self) -> list[str]:
        setup = self.manager.active_setup
        maximum = len(setup.port_labels) if setup else 1
        return [str(value) for value in range(1, maximum + 1)]

    @property
    def current_option(self) -> str:
        return str(self.manager.selected_quantity)

    @property
    def available(self) -> bool:
        return self.manager.session.mode == SESSION_IDLE

    async def async_select_option(self, option: str) -> None:
        await self.manager.async_select_quantity(int(option))
