"""Button entities for Battery Charge Manager."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SESSION_CALIBRATING, SESSION_IDLE
from .entity import BatteryChargeManagerEntity
from .manager import BatteryChargeManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up buttons."""
    manager: BatteryChargeManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            StartChargeButton(manager, entry),
            StopButton(manager, entry),
            StartCalibrationButton(manager, entry),
            FinishCalibrationButton(manager, entry),
        ]
    )


class StartChargeButton(BatteryChargeManagerEntity, ButtonEntity):
    """Start storage charging."""

    _attr_translation_key = "start_charge"
    _attr_icon = "mdi:battery-charging"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize button."""
        super().__init__(manager, entry, "start_charge")

    @property
    def available(self) -> bool:
        """Only allow starting while idle."""
        return self.manager.session.mode == SESSION_IDLE

    async def async_press(self) -> None:
        """Start charging."""
        await self.manager.async_start_charge()


class StopButton(BatteryChargeManagerEntity, ButtonEntity):
    """Stop charging or calibration."""

    _attr_translation_key = "stop"
    _attr_icon = "mdi:stop-circle-outline"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize button."""
        super().__init__(manager, entry, "stop")

    @property
    def available(self) -> bool:
        """Only available during a session."""
        return self.manager.session.mode != SESSION_IDLE

    async def async_press(self) -> None:
        """Stop session."""
        await self.manager.async_stop("Stopped by user")


class StartCalibrationButton(BatteryChargeManagerEntity, ButtonEntity):
    """Start full-charge calibration."""

    _attr_translation_key = "start_calibration"
    _attr_icon = "mdi:tune-variant"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize button."""
        super().__init__(manager, entry, "start_calibration")

    @property
    def available(self) -> bool:
        """Only available while idle."""
        return self.manager.session.mode == SESSION_IDLE

    async def async_press(self) -> None:
        """Start calibration."""
        await self.manager.async_start_calibration()


class FinishCalibrationButton(BatteryChargeManagerEntity, ButtonEntity):
    """Finish and save calibration."""

    _attr_translation_key = "finish_calibration"
    _attr_icon = "mdi:content-save-check"

    def __init__(self, manager: BatteryChargeManager, entry: ConfigEntry) -> None:
        """Initialize button."""
        super().__init__(manager, entry, "finish_calibration")

    @property
    def available(self) -> bool:
        """Only available during calibration."""
        return self.manager.session.mode == SESSION_CALIBRATING

    async def async_press(self) -> None:
        """Finish calibration."""
        await self.manager.async_finish_calibration()
