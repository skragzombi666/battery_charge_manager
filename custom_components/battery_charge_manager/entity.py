"""Base entities for Battery Charge Manager."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN, NAME, VERSION
from .manager import BatteryChargeManager


class BatteryChargeManagerEntity(Entity):
    """Base entity linked to the manager dispatcher."""

    _attr_has_entity_name = True

    def __init__(
        self,
        manager: BatteryChargeManager,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Initialize entity."""
        self.manager = manager
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="Battery Charge Manager",
            model="Calibrated energy charge controller",
            sw_version=VERSION,
        )

    async def async_added_to_hass(self) -> None:
        """Register update listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.manager.signal,
                self._handle_manager_update,
            )
        )

    @callback
    def _handle_manager_update(self) -> None:
        """Update entity state."""
        self.async_write_ha_state()
