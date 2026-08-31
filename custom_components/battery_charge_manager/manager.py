"""Charge manager for Battery Charge Manager."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging
from statistics import median
from typing import Any
from uuid import uuid4

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DEFAULT_TARGET,
    CONF_ENERGY_SENSOR,
    CONF_MAX_SESSION_HOURS,
    CONF_POWER_SENSOR,
    CONF_SWITCH_ENTITY,
    DEFAULT_MAX_SESSION_HOURS,
    DEFAULT_TARGET,
    DOMAIN,
    SESSION_CALIBRATING,
    SESSION_CHARGING,
    SESSION_IDLE,
    SIGNAL_UPDATE,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .models import BatteryType, ChargeSession

_LOGGER = logging.getLogger(__name__)


class BatteryChargeManager:
    """Manage battery profiles, calibrations, and charge sessions."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize manager."""
        self.hass = hass
        self.entry = entry
        self.store = Store[dict[str, Any]](
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY}.{entry.entry_id}",
        )
        self.batteries: dict[str, BatteryType] = {}
        self.session = ChargeSession()
        self.selected_battery_id: str | None = None
        self.selected_quantity = 1
        self.target_percent = int(
            entry.options.get(CONF_DEFAULT_TARGET, DEFAULT_TARGET)
        )
        self._remove_energy_listener: Callable[[], None] | None = None
        self._cancel_timeout: Callable[[], None] | None = None

    @property
    def switch_entity(self) -> str:
        """Configured charge switch."""
        return self.entry.options[CONF_SWITCH_ENTITY]

    @property
    def energy_sensor(self) -> str:
        """Configured cumulative energy sensor."""
        return self.entry.options[CONF_ENERGY_SENSOR]

    @property
    def power_sensor(self) -> str | None:
        """Optional configured power sensor."""
        return self.entry.options.get(CONF_POWER_SENSOR)

    @property
    def max_session_hours(self) -> float:
        """Maximum session duration."""
        return float(
            self.entry.options.get(
                CONF_MAX_SESSION_HOURS, DEFAULT_MAX_SESSION_HOURS
            )
        )

    @property
    def active_battery(self) -> BatteryType | None:
        """Return selected battery."""
        if not self.selected_battery_id:
            return None
        return self.batteries.get(self.selected_battery_id)

    @property
    def progress_percent(self) -> float | None:
        """Return session progress."""
        if (
            not self.session.target_energy_wh
            or self.session.target_energy_wh <= 0
        ):
            return None
        return min(
            100.0,
            self.session.delivered_energy_wh
            / self.session.target_energy_wh
            * 100.0,
        )

    async def async_load(self) -> None:
        """Load persistent library and session state."""
        data = await self.store.async_load() or {}
        self.batteries = {
            item["battery_id"]: BatteryType.from_dict(item)
            for item in data.get("batteries", [])
        }
        self.session = ChargeSession.from_dict(data.get("session"))
        self.selected_battery_id = data.get("selected_battery_id")
        if self.selected_battery_id not in self.batteries:
            self.selected_battery_id = next(iter(self.batteries), None)
        self.selected_quantity = int(data.get("selected_quantity", 1))
        self.target_percent = int(
            data.get(
                "target_percent",
                self.entry.options.get(CONF_DEFAULT_TARGET, DEFAULT_TARGET),
            )
        )

        if self.session.mode != SESSION_IDLE:
            state = self.hass.states.get(self.energy_sensor)
            if state is None or state.state in {"unknown", "unavailable"}:
                await self.async_stop("Energy sensor unavailable after restart")
            else:
                current = self._energy_state_to_wh(state)
                if current is None:
                    await self.async_stop("Energy sensor invalid after restart")
                else:
                    previous = self.session.last_energy_wh
                    if previous is not None:
                        if current >= previous:
                            self.session.delivered_energy_wh += current - previous
                        else:
                            self.session.delivered_energy_wh += current
                    self.session.last_energy_wh = current
                    if (
                        self.session.mode == SESSION_CHARGING
                        and self.session.target_energy_wh is not None
                        and self.session.delivered_energy_wh
                        >= self.session.target_energy_wh
                    ):
                        await self.async_stop(
                            "Target energy reached while Home Assistant was unavailable"
                        )
                    else:
                        self._start_tracking()
                        self._schedule_timeout()
                        await self._async_save()
                        self._notify()

    async def async_shutdown(self) -> None:
        """Stop listeners without interrupting a running physical charge."""
        self._stop_tracking()

    async def _async_save(self) -> None:
        """Persist manager data."""
        await self.store.async_save(
            {
                "batteries": [
                    battery.as_dict() for battery in self.batteries.values()
                ],
                "session": self.session.as_dict(),
                "selected_battery_id": self.selected_battery_id,
                "selected_quantity": self.selected_quantity,
                "target_percent": self.target_percent,
            }
        )

    @callback
    def _notify(self) -> None:
        """Notify entities about state changes."""
        async_dispatcher_send(
            self.hass, f"{SIGNAL_UPDATE}_{self.entry.entry_id}"
        )

    async def async_add_battery(
        self,
        *,
        name: str,
        nominal_capacity_mah: int,
        technology: str,
        form_factor: str,
        image: dict[str, Any] | None,
    ) -> BatteryType:
        """Add a battery type."""
        battery = BatteryType(
            battery_id=uuid4().hex,
            name=name.strip(),
            nominal_capacity_mah=int(nominal_capacity_mah),
            technology=technology,
            form_factor=form_factor,
            image=image,
        )
        self.batteries[battery.battery_id] = battery
        if self.selected_battery_id is None:
            self.selected_battery_id = battery.battery_id
        await self._async_save()
        self._notify()
        return battery

    async def async_update_battery(
        self,
        battery_id: str,
        *,
        name: str,
        nominal_capacity_mah: int,
        technology: str,
        form_factor: str,
        image: dict[str, Any] | None,
    ) -> None:
        """Update a battery type without touching calibration history."""
        battery = self.batteries[battery_id]
        battery.name = name.strip()
        battery.nominal_capacity_mah = int(nominal_capacity_mah)
        battery.technology = technology
        battery.form_factor = form_factor
        battery.image = image
        await self._async_save()
        self._notify()

    async def async_delete_battery(self, battery_id: str) -> None:
        """Delete a battery type."""
        if self.session.mode != SESSION_IDLE and self.session.battery_id == battery_id:
            raise HomeAssistantError("Cannot delete the battery type used by an active session")
        self.batteries.pop(battery_id, None)
        if self.selected_battery_id == battery_id:
            self.selected_battery_id = next(iter(self.batteries), None)
        await self._async_save()
        self._notify()

    async def async_select_battery(self, battery_id: str) -> None:
        """Select battery."""
        if battery_id not in self.batteries:
            raise HomeAssistantError("Unknown battery type")
        self.selected_battery_id = battery_id
        await self._async_save()
        self._notify()

    async def async_select_quantity(self, quantity: int) -> None:
        """Select battery quantity."""
        if quantity < 1 or quantity > 8:
            raise HomeAssistantError("Quantity must be between 1 and 8")
        self.selected_quantity = quantity
        await self._async_save()
        self._notify()

    async def async_set_target_percent(self, value: int) -> None:
        """Set storage charge target."""
        value = int(value)
        if value < 20 or value > 100:
            raise HomeAssistantError("Target charge must be between 20 and 100 percent")
        self.target_percent = value
        await self._async_save()
        self._notify()

    async def async_start_charge(self) -> None:
        """Start a storage-charge session."""
        self._ensure_idle()
        battery = self._require_selected_battery()
        full_energy_wh = battery.calibration_value(self.selected_quantity)
        if full_energy_wh is None:
            raise HomeAssistantError(
                "No calibration exists for this battery type and quantity"
            )
        target_energy_wh = full_energy_wh * self.target_percent / 100.0
        await self._async_begin_session(
            mode=SESSION_CHARGING,
            battery=battery,
            target_energy_wh=target_energy_wh,
        )

    async def async_start_calibration(self) -> None:
        """Start a full-charge calibration session."""
        self._ensure_idle()
        battery = self._require_selected_battery()
        await self._async_begin_session(
            mode=SESSION_CALIBRATING,
            battery=battery,
            target_energy_wh=None,
        )

    async def async_finish_calibration(self) -> float:
        """Finish calibration, store sample, and switch off."""
        if self.session.mode != SESSION_CALIBRATING:
            raise HomeAssistantError("No calibration session is active")
        if self.session.delivered_energy_wh <= 0:
            raise HomeAssistantError("Calibration measured no energy")
        battery = self.batteries.get(self.session.battery_id or "")
        if battery is None:
            raise HomeAssistantError("Battery type no longer exists")
        quantity_key = str(self.session.quantity)
        samples = battery.calibrations.setdefault(quantity_key, [])
        sample = round(self.session.delivered_energy_wh, 4)
        samples.append(sample)
        await self._switch_off()
        self._stop_tracking()
        self.session.mode = SESSION_IDLE
        self.session.finished_at = dt_util.utcnow().isoformat()
        self.session.end_reason = "Calibration saved"
        await self._async_save()
        self._notify()
        return sample

    async def async_stop(self, reason: str = "Stopped") -> None:
        """Stop active session and switch off."""
        was_active = self.session.mode != SESSION_IDLE
        if was_active:
            _LOGGER.info("Stopping Battery Charge Manager session: %s", reason)
        await self._switch_off()
        self._stop_tracking()
        if was_active:
            self.session.mode = SESSION_IDLE
            self.session.finished_at = dt_util.utcnow().isoformat()
            self.session.end_reason = reason
        await self._async_save()
        self._notify()

    def calibration_summary(self, battery: BatteryType) -> dict[str, Any]:
        """Return calibration details."""
        result: dict[str, Any] = {}
        for quantity, samples in sorted(
            battery.calibrations.items(), key=lambda item: int(item[0])
        ):
            result[quantity] = {
                "samples_wh": [round(value, 4) for value in samples],
                "median_wh": round(median(samples), 4) if samples else None,
            }
        return result

    async def _async_begin_session(
        self,
        *,
        mode: str,
        battery: BatteryType,
        target_energy_wh: float | None,
    ) -> None:
        state = self.hass.states.get(self.energy_sensor)
        if state is None or state.state in {"unknown", "unavailable"}:
            raise HomeAssistantError("Configured energy sensor is unavailable")
        current_wh = self._energy_state_to_wh(state)
        if current_wh is None:
            raise HomeAssistantError("Configured energy sensor has no usable energy value")

        self.session = ChargeSession(
            mode=mode,
            battery_id=battery.battery_id,
            quantity=self.selected_quantity,
            target_percent=self.target_percent,
            target_energy_wh=target_energy_wh,
            delivered_energy_wh=0.0,
            last_energy_wh=current_wh,
            started_at=dt_util.utcnow().isoformat(),
        )
        await self._async_save()
        self._start_tracking()
        self._schedule_timeout()

        try:
            await self.hass.services.async_call(
                "switch",
                "turn_on",
                {"entity_id": self.switch_entity},
                blocking=True,
            )
        except Exception:
            self._stop_tracking()
            self.session = ChargeSession()
            await self._async_save()
            self._notify()
            raise

        self._notify()

    @callback
    def _start_tracking(self) -> None:
        """Start energy sensor tracking."""
        self._stop_tracking()
        self._remove_energy_listener = async_track_state_change_event(
            self.hass,
            [self.energy_sensor],
            self._async_energy_changed,
        )

    @callback
    def _schedule_timeout(self) -> None:
        """Schedule a session timeout."""
        if self._cancel_timeout:
            self._cancel_timeout()
        self._cancel_timeout = async_call_later(
            self.hass,
            timedelta(hours=self.max_session_hours),
            self._async_timeout,
        )

    @callback
    def _stop_tracking(self) -> None:
        """Stop session listeners."""
        if self._remove_energy_listener:
            self._remove_energy_listener()
            self._remove_energy_listener = None
        if self._cancel_timeout:
            self._cancel_timeout()
            self._cancel_timeout = None

    async def _async_timeout(self, _now: Any) -> None:
        """Handle timeout."""
        await self.async_stop("Maximum session time reached")

    async def _async_energy_changed(self, event: Event) -> None:
        """Track energy delivered during the active session."""
        if self.session.mode == SESSION_IDLE:
            return
        new_state: State | None = event.data.get("new_state")
        if new_state is None or new_state.state in {"unknown", "unavailable"}:
            await self.async_stop("Energy sensor became unavailable")
            return

        current_wh = self._energy_state_to_wh(new_state)
        if current_wh is None:
            await self.async_stop("Energy sensor returned an invalid value")
            return

        previous_wh = self.session.last_energy_wh
        if previous_wh is None:
            self.session.last_energy_wh = current_wh
            await self._async_save()
            return

        if current_wh >= previous_wh:
            delta_wh = current_wh - previous_wh
        else:
            # A cumulative energy sensor may reset to zero. Count the post-reset
            # value instead of treating the reset as negative consumption.
            delta_wh = current_wh

        if delta_wh < 0:
            await self.async_stop("Energy sensor moved backwards unexpectedly")
            return

        self.session.delivered_energy_wh += delta_wh
        self.session.last_energy_wh = current_wh
        await self._async_save()
        self._notify()

        if (
            self.session.mode == SESSION_CHARGING
            and self.session.target_energy_wh is not None
            and self.session.delivered_energy_wh >= self.session.target_energy_wh
        ):
            await self.async_stop("Target energy reached")

    async def _switch_off(self) -> None:
        """Switch charger off."""
        try:
            await self.hass.services.async_call(
                "switch",
                "turn_off",
                {"entity_id": self.switch_entity},
                blocking=True,
            )
        except Exception as err:
            _LOGGER.error("Could not switch off %s: %s", self.switch_entity, err)

    def _ensure_idle(self) -> None:
        """Ensure no session is active."""
        if self.session.mode != SESSION_IDLE:
            raise HomeAssistantError("A charge or calibration session is already active")

    def _require_selected_battery(self) -> BatteryType:
        """Return selected battery or raise."""
        battery = self.active_battery
        if battery is None:
            raise HomeAssistantError("No battery type is selected")
        return battery

    @staticmethod
    def _energy_state_to_wh(state: State) -> float | None:
        """Convert an energy sensor state to Wh."""
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        unit = state.attributes.get("unit_of_measurement")
        if unit == UnitOfEnergy.KILO_WATT_HOUR:
            return value * 1000.0
        if unit == UnitOfEnergy.WATT_HOUR:
            return value
        if unit == "MWh":
            return value * 1_000_000.0
        return None
