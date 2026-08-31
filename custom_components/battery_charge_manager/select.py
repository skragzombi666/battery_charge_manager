"""Select entities for Battery Charge Manager."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, QUANTITIES
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
            BatteryTypeSelect(manager, entry),
            BatteryQuantitySelect(manager, entry),
        ]
    )


class BatteryTypeSelect(BatteryChargeManagerEntity, SelectEntity):
    """Select battery type."""

    _attr_translation_key = "battery_type"
    _attr_icon = "mdi:battery"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize select."""
        super().__init__(manager, entry, "battery_type")

    @property
    def options(self) -> list[str]:
        """Return battery names."""
        return [battery.name for battery in self.manager.batteries.values()]

    @property
    def current_option(self) -> str | None:
        """Return selected battery name."""
        battery = self.manager.active_battery
        return battery.name if battery else None

    @property
    def entity_picture(self) -> str | None:
        """Return selected battery image when available."""
        battery = self.manager.active_battery
        return battery.image.get("media_content_id") if battery and battery.image else None

    async def async_select_option(self, option: str) -> None:
        """Select a battery by display name."""
        for battery_id, battery in self.manager.batteries.items():
            if battery.name == option:
                await self.manager.async_select_battery(battery_id)
                return
        raise ValueError(f"Unknown battery type: {option}")


class BatteryQuantitySelect(BatteryChargeManagerEntity, SelectEntity):
    """Select the number of batteries charged in parallel."""

    _attr_translation_key = "quantity"
    _attr_icon = "mdi:counter"
    _attr_options = QUANTITIES

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize select."""
        super().__init__(manager, entry, "quantity")

    @property
    def current_option(self) -> str:
        """Return current quantity."""
        return str(self.manager.selected_quantity)

    async def async_select_option(self, option: str) -> None:
        """Select quantity."""
        await self.manager.async_select_quantity(int(option))
