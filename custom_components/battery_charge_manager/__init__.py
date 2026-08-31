"""Battery Charge Manager integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .manager import BatteryChargeManager


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Battery Charge Manager from a config entry."""
    manager = BatteryChargeManager(hass, entry)
    await manager.async_load()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = manager

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        manager: BatteryChargeManager = hass.data[DOMAIN].pop(entry.entry_id)
        await manager.async_shutdown()
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when integration options change."""
    await hass.config_entries.async_reload(entry.entry_id)
