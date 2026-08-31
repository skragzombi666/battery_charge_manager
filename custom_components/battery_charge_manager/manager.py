"""Professional measurement and charge manager for Battery Charge Manager."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
import logging
import math
from statistics import median, pstdev
from typing import Any
from uuid import uuid4

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower, UnitOfTemperature
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    ALGORITHM_VERSION,
    CONF_DEFAULT_TARGET,
    CONF_ENERGY_SENSOR,
    CONF_MAX_SESSION_HOURS,
    CONF_POWER_SENSOR,
    CONF_SETUP_NAME,
    CONF_SWITCH_ENTITY,
    CONF_TEMPERATURE_SENSOR,
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    DATA_SCHEMA_VERSION,
    DEFAULT_CALIBRATION_ABSOLUTE_MAX_WH,
    DEFAULT_CALIBRATION_DRIFT_WARN_PERCENT,
    DEFAULT_CALIBRATION_MAX_FACTOR,
    DEFAULT_CHARGE_START_TIMEOUT_MINUTES,
    DEFAULT_END_CONFIRM_MINUTES,
    DEFAULT_END_WINDOW_MINUTES,
    DEFAULT_HEARTBEAT_SECONDS,
    DEFAULT_IDLE_AUTO_MAX_HOURS,
    DEFAULT_IDLE_AUTO_MIN_MINUTES,
    DEFAULT_IDLE_FIXED_MINUTES,
    DEFAULT_IDLE_RELIABLE_UPPER_BOUND_W,
    DEFAULT_IDLE_RESOLUTION_MULTIPLIER,
    DEFAULT_IDLE_WARMUP_MINUTES,
    DEFAULT_MAX_POWER_W,
    DEFAULT_MAX_SESSION_HOURS,
    DEFAULT_MIN_CHARGE_MINUTES,
    DEFAULT_SETUP_NAME,
    DEFAULT_TARGET,
    DOMAIN,
    IDLE_MODE_AUTOMATIC,
    IDLE_MODE_FIXED,
    PHASE_CONFIRMING_END,
    PHASE_ERROR,
    PHASE_FINISHED,
    PHASE_IDLE_MEASUREMENT,
    PHASE_MAIN_CHARGE,
    PHASE_PREPARING,
    PHASE_TAPER,
    PHASE_TARGET_REACHED,
    PHASE_WAITING_FOR_LOAD,
    QUALITY_LIMITED,
    QUALITY_NONE,
    QUALITY_PROVISIONAL,
    QUALITY_STABLE,
    QUALITY_UNSTABLE,
    SESSION_CALIBRATING,
    SESSION_CHARGING,
    SESSION_IDLE,
    SESSION_IDLE_MEASURING,
    SIGNAL_UPDATE,
    STORAGE_KEY,
    STORAGE_VERSION,
    VERSION,
)
from .models import (
    BatteryType,
    CalibrationRecord,
    ChargerSetup,
    ChargeSession,
    IdleMeasurement,
    MeasurementSample,
)

_LOGGER = logging.getLogger(__name__)


class BatteryChargeManager:
    """Manage setups, batteries, measurements, calibrations, and charging."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize manager."""
        self.hass = hass
        self.entry = entry
        self.store = Store[dict[str, Any]](
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY}.{entry.entry_id}",
        )
        self.setups: dict[str, ChargerSetup] = {}
        self.batteries: dict[str, BatteryType] = {}
        self.idle_measurements: dict[str, IdleMeasurement] = {}
        self.calibrations: dict[str, CalibrationRecord] = {}
        self.charge_history: list[dict[str, Any]] = []
        self.session = ChargeSession()
        self.selected_setup_id: str | None = None
        self.selected_battery_id: str | None = None
        self.selected_quantity = 1
        self.target_percent = int(
            entry.options.get(CONF_DEFAULT_TARGET, DEFAULT_TARGET)
        )
        self.max_session_hours = float(
            entry.options.get(CONF_MAX_SESSION_HOURS, DEFAULT_MAX_SESSION_HOURS)
        )
        self._remove_energy_listener: Callable[[], None] | None = None
        self._remove_power_listener: Callable[[], None] | None = None
        self._remove_temperature_listener: Callable[[], None] | None = None
        self._remove_switch_listener: Callable[[], None] | None = None
        self._remove_heartbeat: Callable[[], None] | None = None
        self._cancel_timeout: Callable[[], None] | None = None
        self._sample_lock = asyncio.Lock()
        self._commanding_switch = False
        self._finalizing = False

    @property
    def signal(self) -> str:
        """Return dispatcher signal for this config entry."""
        return f"{SIGNAL_UPDATE}_{self.entry.entry_id}"

    @property
    def active_setup(self) -> ChargerSetup | None:
        """Return selected setup."""
        if not self.selected_setup_id:
            return None
        return self.setups.get(self.selected_setup_id)

    @property
    def active_battery(self) -> BatteryType | None:
        """Return selected battery."""
        if not self.selected_battery_id:
            return None
        return self.batteries.get(self.selected_battery_id)

    @property
    def switch_entity(self) -> str | None:
        """Return selected setup switch entity."""
        return self.active_setup.switch_entity if self.active_setup else None

    @property
    def energy_sensor(self) -> str | None:
        """Return selected setup energy sensor."""
        return self.active_setup.energy_sensor if self.active_setup else None

    @property
    def power_sensor(self) -> str | None:
        """Return selected setup power sensor."""
        return self.active_setup.power_sensor if self.active_setup else None

    @property
    def progress_percent(self) -> float | None:
        """Return current target progress."""
        target = self.session.target_energy_wh
        if not target or target <= 0:
            return None
        return min(100.0, self.session.net_energy_wh / target * 100.0)

    async def async_load(self) -> None:
        """Load, migrate, and normalize persistent data."""
        data = await self.store.async_load() or {}
        raw_batteries = list(data.get("batteries", []))
        self.batteries = {
            item["battery_id"]: BatteryType.from_dict(item)
            for item in raw_batteries
            if item.get("battery_id")
        }
        self.setups = {
            item["setup_id"]: ChargerSetup.from_dict(item)
            for item in data.get("setups", [])
            if item.get("setup_id")
        }
        created_default_setup = False
        if not self.setups:
            setup = self._setup_from_entry_options()
            self.setups[setup.setup_id] = setup
            created_default_setup = True

        self.idle_measurements = {
            item["measurement_id"]: IdleMeasurement.from_dict(item)
            for item in data.get("idle_measurements", [])
            if item.get("measurement_id")
        }
        self.calibrations = {
            item["calibration_id"]: CalibrationRecord.from_dict(item)
            for item in data.get("calibrations", [])
            if item.get("calibration_id")
        }
        self.charge_history = [dict(item) for item in data.get("charge_history", [])]
        self.session = ChargeSession.from_dict(data.get("session"))
        self.selected_setup_id = data.get("selected_setup_id")
        if self.selected_setup_id not in self.setups:
            self.selected_setup_id = next(iter(self.setups), None)
        self.selected_battery_id = data.get("selected_battery_id")
        if self.selected_battery_id not in self.batteries:
            self.selected_battery_id = next(iter(self.batteries), None)
        self.selected_quantity = max(1, int(data.get("selected_quantity", 1)))
        self.target_percent = int(data.get("target_percent", self.target_percent))
        self.max_session_hours = float(
            data.get("max_session_hours", self.max_session_hours)
        )

        migrated = self._migrate_legacy_calibrations(raw_batteries)
        resumed_or_closed = False
        if self.session.active:
            await self._async_resume_session()
            resumed_or_closed = True
        if (
            created_default_setup
            or migrated
            or resumed_or_closed
            or data.get("schema_version") != DATA_SCHEMA_VERSION
        ):
            await self._async_save()
        self._notify()

    def _setup_from_entry_options(self) -> ChargerSetup:
        """Create the initial setup from the original config flow."""
        now = self._now_iso()
        options = self.entry.options
        return ChargerSetup(
            setup_id=uuid4().hex,
            name=str(options.get(CONF_SETUP_NAME, DEFAULT_SETUP_NAME)),
            switch_entity=str(options.get(CONF_SWITCH_ENTITY, "")),
            energy_sensor=str(options.get(CONF_ENERGY_SENSOR, "")),
            power_sensor=options.get(CONF_POWER_SENSOR) or None,
            temperature_sensor=options.get(CONF_TEMPERATURE_SENSOR) or None,
            port_labels=["A", "B", "C", "D"],
            max_power_w=DEFAULT_MAX_POWER_W,
            created_at=now,
            updated_at=now,
        )

    def _migrate_legacy_calibrations(self, raw_batteries: list[dict[str, Any]]) -> bool:
        """Convert 0.0.x Wh-only calibration lists into immutable records."""
        if self.calibrations:
            return False
        setup = self.active_setup or next(iter(self.setups.values()), None)
        if setup is None:
            return False
        migrated = False
        for raw in raw_batteries:
            battery = self.batteries.get(str(raw.get("battery_id", "")))
            if battery is None:
                continue
            for quantity_raw, values in raw.get("calibrations", {}).items():
                try:
                    quantity = int(quantity_raw)
                except (TypeError, ValueError):
                    continue
                for value in values:
                    try:
                        energy = float(value)
                    except (TypeError, ValueError):
                        continue
                    record = CalibrationRecord(
                        calibration_id=uuid4().hex,
                        setup_id=setup.setup_id,
                        setup_revision=setup.revision,
                        setup_snapshot=setup.snapshot(),
                        battery_id=battery.battery_id,
                        battery_revision=battery.revision,
                        battery_snapshot=battery.snapshot(),
                        quantity=quantity,
                        ports=setup.ports_for_quantity(quantity),
                        gross_energy_wh=energy,
                        net_energy_wh=energy,
                        end_method="legacy_import",
                        confidence=CONFIDENCE_LOW,
                        legacy=True,
                        algorithm_version="0.0.x",
                    )
                    self.calibrations[record.calibration_id] = record
                    migrated = True
        return migrated

    async def _async_resume_session(self) -> None:
        """Resume an active session after Home Assistant restart."""
        setup = self.setups.get(self.session.setup_id or "")
        if setup is None:
            self.session.mode = SESSION_IDLE
            self.session.phase = PHASE_ERROR
            self.session.valid = False
            self.session.end_reason = "Charging setup missing after restart"
            self.session.session_finished_at = self._now_iso()
            return
        switch_state = self.hass.states.get(setup.switch_entity)
        if switch_state is None or switch_state.state != "on":
            self.session.mode = SESSION_IDLE
            self.session.phase = PHASE_ERROR
            self.session.valid = False
            self.session.end_reason = "Charging switch was not on after restart"
            self.session.session_finished_at = self._now_iso()
            return
        self.session.restart_count += 1
        self.selected_setup_id = setup.setup_id
        if self.session.battery_id in self.batteries:
            self.selected_battery_id = self.session.battery_id
        self.selected_quantity = self.session.quantity
        self._start_tracking()
        self._schedule_timeout()
        await self._async_sample("restart")

    async def async_shutdown(self) -> None:
        """Detach listeners without changing the physical charge state."""
        self._stop_tracking()

    async def _async_save(self) -> None:
        """Persist all manager data."""
        await self.store.async_save(
            {
                "schema_version": DATA_SCHEMA_VERSION,
                "setups": [setup.as_dict() for setup in self.setups.values()],
                "batteries": [battery.as_dict() for battery in self.batteries.values()],
                "idle_measurements": [
                    item.as_dict() for item in self.idle_measurements.values()
                ],
                "calibrations": [
                    item.as_dict() for item in self.calibrations.values()
                ],
                "charge_history": self.charge_history[-100:],
                "session": self.session.as_dict(),
                "selected_setup_id": self.selected_setup_id,
                "selected_battery_id": self.selected_battery_id,
                "selected_quantity": self.selected_quantity,
                "target_percent": self.target_percent,
                "max_session_hours": self.max_session_hours,
            }
        )

    @callback
    def _notify(self) -> None:
        """Notify entities and frontend subscribers."""
        async_dispatcher_send(self.hass, self.signal)

    async def async_add_or_update_setup(self, data: dict[str, Any]) -> ChargerSetup:
        """Create or update a versioned charging setup."""
        self._ensure_idle()
        setup_id = str(data.get("setup_id") or uuid4().hex)
        existing = self.setups.get(setup_id)
        now = self._now_iso()
        labels = self._normalize_port_labels(data.get("port_labels"))
        switch_entity = str(data.get("switch_entity", "")).strip()
        energy_sensor = str(data.get("energy_sensor", "")).strip()
        power_sensor = str(data.get("power_sensor", "")).strip() or None
        temperature_sensor = (
            str(data.get("temperature_sensor", "")).strip() or None
        )
        self._validate_setup_entities(
            switch_entity,
            energy_sensor,
            power_sensor,
            temperature_sensor,
        )
        if existing is None:
            setup = ChargerSetup(
                setup_id=setup_id,
                name=str(data.get("name") or "Charging setup").strip(),
                switch_entity=switch_entity,
                energy_sensor=energy_sensor,
                power_sensor=power_sensor,
                temperature_sensor=temperature_sensor,
                charger_model=str(data.get("charger_model", "")).strip(),
                cable_description=str(data.get("cable_description", "")).strip(),
                description=str(data.get("description", "")).strip(),
                port_labels=labels,
                max_power_w=max(
                    1.0, float(data.get("max_power_w", DEFAULT_MAX_POWER_W))
                ),
                max_temperature_c=self._optional_positive_float(
                    data.get("max_temperature_c")
                ),
                created_at=now,
                updated_at=now,
            )
            self.setups[setup.setup_id] = setup
        else:
            technical_before = (
                existing.switch_entity,
                existing.energy_sensor,
                existing.power_sensor,
                existing.temperature_sensor,
                existing.charger_model,
                existing.cable_description,
                tuple(existing.port_labels),
            )
            technical_after = (
                switch_entity,
                energy_sensor,
                power_sensor,
                temperature_sensor,
                str(data.get("charger_model", "")).strip(),
                str(data.get("cable_description", "")).strip(),
                tuple(labels),
            )
            if technical_before != technical_after:
                existing.revision += 1
            existing.name = str(data.get("name") or existing.name).strip()
            existing.switch_entity = switch_entity
            existing.energy_sensor = energy_sensor
            existing.power_sensor = power_sensor
            existing.temperature_sensor = temperature_sensor
            existing.charger_model = technical_after[4]
            existing.cable_description = technical_after[5]
            existing.description = str(data.get("description", "")).strip()
            existing.port_labels = labels
            existing.max_power_w = max(
                1.0, float(data.get("max_power_w", existing.max_power_w))
            )
            existing.max_temperature_c = self._optional_positive_float(
                data.get("max_temperature_c")
            )
            existing.updated_at = now
            setup = existing
        self.selected_setup_id = setup.setup_id
        self.selected_quantity = min(self.selected_quantity, len(setup.port_labels))
        await self._async_save()
        self._notify()
        return setup

    async def async_delete_setup(self, setup_id: str) -> None:
        """Delete a setup while retaining historical measurement snapshots."""
        self._ensure_idle()
        if len(self.setups) <= 1:
            raise HomeAssistantError("At least one charging setup must remain")
        self.setups.pop(setup_id, None)
        if self.selected_setup_id == setup_id:
            self.selected_setup_id = next(iter(self.setups), None)
        await self._async_save()
        self._notify()

    async def async_add_or_update_battery(self, data: dict[str, Any]) -> BatteryType:
        """Create or update a versioned battery type."""
        self._ensure_idle()
        battery_id = str(data.get("battery_id") or uuid4().hex)
        existing = self.batteries.get(battery_id)
        now = self._now_iso()
        name = str(data.get("name") or "Battery").strip()
        if any(
            item.battery_id != battery_id and item.name.casefold() == name.casefold()
            for item in self.batteries.values()
        ):
            raise HomeAssistantError("A battery type with this name already exists")
        nominal_capacity_mah = max(1, int(float(data.get("nominal_capacity_mah", 1000))))
        nominal_voltage_v = self._optional_positive_float(data.get("nominal_voltage_v"))
        nominal_energy_wh = self._optional_positive_float(data.get("nominal_energy_wh"))
        if existing is None:
            battery = BatteryType(
                battery_id=battery_id,
                name=name,
                manufacturer=str(data.get("manufacturer", "")).strip(),
                model=str(data.get("model", "")).strip(),
                nominal_capacity_mah=nominal_capacity_mah,
                nominal_voltage_v=nominal_voltage_v,
                nominal_energy_wh=nominal_energy_wh,
                technology=str(data.get("technology", "Other")),
                form_factor=str(data.get("form_factor", "Other")),
                charging_method=str(
                    data.get("charging_method", "Integrated USB-C charger")
                ),
                discharge_method=str(data.get("discharge_method", "")).strip(),
                rest_time_minutes=(
                    max(0, int(float(data.get("rest_time_minutes", 0))))
                    if data.get("rest_time_minutes") not in {None, ""}
                    else None
                ),
                starting_condition_notes=str(
                    data.get("starting_condition_notes", "")
                ).strip(),
                image=data.get("image") or None,
                notes=str(data.get("notes", "")).strip(),
                created_at=now,
                updated_at=now,
            )
            self.batteries[battery.battery_id] = battery
        else:
            technical_before = (
                existing.manufacturer,
                existing.model,
                existing.nominal_capacity_mah,
                existing.nominal_voltage_v,
                existing.nominal_energy_wh,
                existing.technology,
                existing.form_factor,
                existing.charging_method,
                existing.discharge_method,
                existing.rest_time_minutes,
                existing.starting_condition_notes,
            )
            technical_after = (
                str(data.get("manufacturer", "")).strip(),
                str(data.get("model", "")).strip(),
                nominal_capacity_mah,
                nominal_voltage_v,
                nominal_energy_wh,
                str(data.get("technology", existing.technology)),
                str(data.get("form_factor", existing.form_factor)),
                str(data.get("charging_method", existing.charging_method)),
                str(data.get("discharge_method", "")).strip(),
                (
                    max(0, int(float(data.get("rest_time_minutes", 0))))
                    if data.get("rest_time_minutes") not in {None, ""}
                    else None
                ),
                str(data.get("starting_condition_notes", "")).strip(),
            )
            if technical_before != technical_after:
                existing.revision += 1
            existing.name = name
            existing.manufacturer = technical_after[0]
            existing.model = technical_after[1]
            existing.nominal_capacity_mah = technical_after[2]
            existing.nominal_voltage_v = technical_after[3]
            existing.nominal_energy_wh = technical_after[4]
            existing.technology = technical_after[5]
            existing.form_factor = technical_after[6]
            existing.charging_method = technical_after[7]
            existing.discharge_method = technical_after[8]
            existing.rest_time_minutes = technical_after[9]
            existing.starting_condition_notes = technical_after[10]
            existing.image = data.get("image") or None
            existing.notes = str(data.get("notes", "")).strip()
            existing.updated_at = now
            battery = existing
        self.selected_battery_id = battery.battery_id
        await self._async_save()
        self._notify()
        return battery

    async def async_delete_battery(self, battery_id: str) -> None:
        """Delete a battery type while retaining historical snapshots."""
        self._ensure_idle()
        self.batteries.pop(battery_id, None)
        if self.selected_battery_id == battery_id:
            self.selected_battery_id = next(iter(self.batteries), None)
        await self._async_save()
        self._notify()

    async def async_select_setup(self, setup_id: str) -> None:
        """Select active setup."""
        self._ensure_idle()
        if setup_id not in self.setups:
            raise HomeAssistantError("Unknown charging setup")
        self.selected_setup_id = setup_id
        setup = self.setups[setup_id]
        self.selected_quantity = min(self.selected_quantity, len(setup.port_labels))
        await self._async_save()
        self._notify()

    async def async_select_battery(self, battery_id: str) -> None:
        """Select active battery."""
        self._ensure_idle()
        if battery_id not in self.batteries:
            raise HomeAssistantError("Unknown battery type")
        self.selected_battery_id = battery_id
        await self._async_save()
        self._notify()

    async def async_select_quantity(self, quantity: int) -> None:
        """Select a fixed first-N port quantity."""
        self._ensure_idle()
        setup = self._require_setup()
        if quantity < 1 or quantity > len(setup.port_labels):
            raise HomeAssistantError(
                f"Quantity must be between 1 and {len(setup.port_labels)}"
            )
        self.selected_quantity = quantity
        await self._async_save()
        self._notify()

    async def async_set_target_percent(self, value: int) -> None:
        """Set relative target energy percentage."""
        self._ensure_idle()
        value = int(value)
        if value < 20 or value > 100:
            raise HomeAssistantError("Target must be between 20 and 100 percent")
        self.target_percent = value
        await self._async_save()
        self._notify()

    async def async_set_max_session_hours(self, value: float) -> None:
        """Set global safety timeout."""
        value = float(value)
        if value < 1 or value > 48:
            raise HomeAssistantError("Maximum session duration must be 1 to 48 hours")
        self.max_session_hours = value
        await self._async_save()
        self._notify()

    async def async_set_measurement_validity(
        self, record_type: str, record_id: str, valid: bool, reason: str = ""
    ) -> None:
        """Mark a measurement valid or invalid without deleting its audit trail."""
        self._ensure_idle()
        if record_type == "idle":
            record = self.idle_measurements.get(record_id)
        elif record_type == "calibration":
            record = self.calibrations.get(record_id)
        else:
            raise HomeAssistantError("Unknown record type")
        if record is None:
            raise HomeAssistantError("Measurement record not found")
        record.valid = bool(valid)
        record.invalid_reason = "" if valid else reason.strip()
        await self._async_save()
        self._notify()

    async def async_start_charge(self) -> None:
        """Start a normal relative-energy charge."""
        self._ensure_idle()
        setup = self._require_setup()
        battery = self._require_battery()
        summary = self.calibration_summary(
            setup.setup_id, battery.battery_id, self.selected_quantity
        )
        median_wh = summary.get("median_net_energy_wh")
        if median_wh is None:
            raise HomeAssistantError(
                "No current calibration exists for this battery, setup, and quantity"
            )
        target_energy_wh = float(median_wh) * self.target_percent / 100.0
        await self._async_begin_session(
            mode=SESSION_CHARGING,
            setup=setup,
            battery=battery,
            target_energy_wh=target_energy_wh,
        )

    async def async_start_calibration(self) -> None:
        """Start automatic full-charge calibration."""
        self._ensure_idle()
        setup = self._require_setup()
        battery = self._require_battery()
        idle = self.idle_summary(setup.setup_id)
        if idle["reliable_count"] == 0:
            raise HomeAssistantError(
                "A reliable idle measurement is required before calibration"
            )
        await self._async_begin_session(
            mode=SESSION_CALIBRATING,
            setup=setup,
            battery=battery,
            target_energy_wh=None,
        )

    async def async_start_idle_measurement(
        self,
        *,
        mode: str = IDLE_MODE_AUTOMATIC,
        duration_minutes: float | None = None,
        auto_min_minutes: float = DEFAULT_IDLE_AUTO_MIN_MINUTES,
        auto_max_minutes: float = DEFAULT_IDLE_AUTO_MAX_HOURS * 60,
    ) -> None:
        """Start an independent no-battery idle measurement."""
        self._ensure_idle()
        setup = self._require_setup()
        if mode not in {IDLE_MODE_FIXED, IDLE_MODE_AUTOMATIC}:
            raise HomeAssistantError("Invalid idle measurement mode")
        if mode == IDLE_MODE_FIXED:
            duration_minutes = float(duration_minutes or DEFAULT_IDLE_FIXED_MINUTES)
            if duration_minutes < 5 or duration_minutes > 24 * 60:
                raise HomeAssistantError("Fixed duration must be 5 to 1440 minutes")
        auto_min_minutes = max(10.0, float(auto_min_minutes))
        auto_max_minutes = max(auto_min_minutes, float(auto_max_minutes))
        await self._async_begin_session(
            mode=SESSION_IDLE_MEASURING,
            setup=setup,
            battery=None,
            target_energy_wh=None,
            idle_mode=mode,
            duration_minutes=duration_minutes,
            auto_min_minutes=auto_min_minutes,
            auto_max_minutes=auto_max_minutes,
        )

    async def _async_begin_session(
        self,
        *,
        mode: str,
        setup: ChargerSetup,
        battery: BatteryType | None,
        target_energy_wh: float | None,
        idle_mode: str | None = None,
        duration_minutes: float | None = None,
        auto_min_minutes: float | None = None,
        auto_max_minutes: float | None = None,
    ) -> None:
        """Validate hardware, create a persistent session, and switch on."""
        self._validate_runtime_setup(setup)
        energy_state = self.hass.states.get(setup.energy_sensor)
        raw_energy = self._energy_state_to_wh(energy_state)
        if raw_energy is None:
            raise HomeAssistantError("Configured energy sensor has no usable value")
        now = self._now_iso()
        idle_summary = (
            self._empty_idle_summary()
            if mode == SESSION_IDLE_MEASURING
            else self.idle_summary(setup.setup_id)
        )
        phase = (
            PHASE_IDLE_MEASUREMENT
            if mode == SESSION_IDLE_MEASURING
            else PHASE_PREPARING
        )
        self.session = ChargeSession(
            session_id=uuid4().hex,
            mode=mode,
            phase=phase,
            setup_id=setup.setup_id,
            battery_id=battery.battery_id if battery else None,
            quantity=self.selected_quantity if battery else 0,
            ports=(
                setup.ports_for_quantity(self.selected_quantity) if battery else []
            ),
            target_percent=self.target_percent,
            target_energy_wh=target_energy_wh,
            last_raw_energy_wh=raw_energy,
            idle_baseline_power_w=float(
                idle_summary.get("baseline_power_w") or 0.0
            ),
            idle_measurement_ids=list(
                idle_summary.get("measurement_ids") or []
            ),
            idle_quality=str(idle_summary.get("quality") or QUALITY_NONE),
            session_started_at=now,
            last_sample_at=now,
            idle_measurement_mode=idle_mode,
            requested_duration_minutes=duration_minutes,
            auto_min_minutes=auto_min_minutes,
            auto_max_minutes=auto_max_minutes,
        )
        await self._async_save()
        self._start_tracking()
        self._schedule_timeout()
        try:
            await self._async_switch_on_checked(setup)
        except Exception:
            self._stop_tracking()
            self.session.phase = PHASE_ERROR
            self.session.valid = False
            self.session.end_reason = "Could not switch charging setup on"
            self.session.session_finished_at = self._now_iso()
            self.session.mode = SESSION_IDLE
            await self._async_save()
            self._notify()
            raise
        self.session.switch_on_at = self._now_iso()
        self.session.phase = (
            PHASE_IDLE_MEASUREMENT
            if mode == SESSION_IDLE_MEASURING
            else PHASE_WAITING_FOR_LOAD
        )
        await self._async_sample("start")

    async def async_finish_calibration(self) -> float:
        """Manually finish and retain an active calibration."""
        if self.session.mode != SESSION_CALIBRATING:
            raise HomeAssistantError("No calibration session is active")
        if self.session.net_energy_wh <= 0:
            raise HomeAssistantError("Calibration measured no net energy")
        record = await self._async_complete_calibration(
            automatic=False, reason="Calibration manually completed"
        )
        return record.net_energy_wh

    async def async_stop(self, reason: str = "Stopped by user") -> None:
        """Abort an active session without treating it as a calibration."""
        if not self.session.active:
            return
        await self._async_abort_session(reason)

    async def _async_abort_session(self, reason: str) -> None:
        """Safely abort the current session and retain an audit summary."""
        if self._finalizing:
            return
        self._finalizing = True
        try:
            setup = self.setups.get(self.session.setup_id or "")
            switch_off_confirmed = True
            if setup:
                switch_off_confirmed = await self._async_switch_off_checked(setup)
            self._stop_tracking()
            now = self._now_iso()
            self.session.switch_off_at = now
            self.session.session_finished_at = now
            self.session.phase = PHASE_ERROR
            self.session.valid = False
            if not switch_off_confirmed:
                reason = f"{reason}; smart plug OFF state not confirmed"
            self.session.end_reason = reason
            self._append_charge_history(valid=False, reason=reason)
            self.session.mode = SESSION_IDLE
            await self._async_save()
            self._notify()
        finally:
            self._finalizing = False

    def _start_tracking(self) -> None:
        """Attach all sensor, switch, and heartbeat listeners."""
        self._stop_tracking()
        setup = self.setups.get(self.session.setup_id or "")
        if setup is None:
            return
        self._remove_energy_listener = async_track_state_change_event(
            self.hass, [setup.energy_sensor], self._async_state_changed
        )
        if setup.power_sensor:
            self._remove_power_listener = async_track_state_change_event(
                self.hass, [setup.power_sensor], self._async_state_changed
            )
        if setup.temperature_sensor:
            self._remove_temperature_listener = async_track_state_change_event(
                self.hass,
                [setup.temperature_sensor],
                self._async_state_changed,
            )
        self._remove_switch_listener = async_track_state_change_event(
            self.hass, [setup.switch_entity], self._async_switch_changed
        )
        self._remove_heartbeat = async_track_time_interval(
            self.hass,
            self._async_heartbeat,
            timedelta(seconds=DEFAULT_HEARTBEAT_SECONDS),
        )

    def _schedule_timeout(self) -> None:
        """Schedule a hard safety timeout."""
        if self._cancel_timeout:
            self._cancel_timeout()
        hours = self.max_session_hours
        if self.session.mode == SESSION_IDLE_MEASURING:
            if self.session.idle_measurement_mode == IDLE_MODE_FIXED:
                requested = self.session.requested_duration_minutes or 0
                hours = max(hours, requested / 60.0 + 0.25)
            elif self.session.auto_max_minutes:
                hours = max(hours, self.session.auto_max_minutes / 60.0 + 0.25)
        elapsed = self._elapsed_seconds(
            self.session.session_started_at,
            dt_util.utcnow(),
        )
        remaining = max(1.0, hours * 3600.0 - elapsed)
        self._cancel_timeout = async_call_later(
            self.hass,
            timedelta(seconds=remaining),
            self._async_timeout,
        )

    def _stop_tracking(self) -> None:
        """Detach active-session listeners."""
        for attr in (
            "_remove_energy_listener",
            "_remove_power_listener",
            "_remove_temperature_listener",
            "_remove_switch_listener",
            "_remove_heartbeat",
            "_cancel_timeout",
        ):
            remove = getattr(self, attr)
            if remove:
                remove()
                setattr(self, attr, None)

    async def _async_timeout(self, _now: Any) -> None:
        """Handle hard session timeout."""
        await self._async_abort_session("Maximum session duration reached")

    async def _async_heartbeat(self, _now: datetime) -> None:
        """Record plateau periods even when sensors do not change."""
        await self._async_sample("heartbeat")

    async def _async_state_changed(self, _event: Event) -> None:
        """Record an energy or power sensor change."""
        await self._async_sample("state_change")

    async def _async_switch_changed(self, event: Event) -> None:
        """Detect external switch changes and unavailable hardware."""
        if not self.session.active or self._commanding_switch or self._finalizing:
            return
        new_state: State | None = event.data.get("new_state")
        if new_state is None or new_state.state in {"unknown", "unavailable"}:
            await self._async_abort_session("Charging switch became unavailable")
            return
        if new_state.state == "off":
            await self._async_abort_session("Charging switch was turned off externally")

    async def _async_sample(self, source: str) -> None:
        """Read all configured signals, update trace, and evaluate the session."""
        if not self.session.active or self._finalizing:
            return
        async with self._sample_lock:
            if not self.session.active or self._finalizing:
                return
            setup = self.setups.get(self.session.setup_id or "")
            if setup is None:
                await self._async_abort_session("Charging setup no longer exists")
                return
            energy_state = self.hass.states.get(setup.energy_sensor)
            raw_energy = self._energy_state_to_wh(energy_state)
            if raw_energy is None:
                await self._async_abort_session("Energy sensor became unavailable or invalid")
                return
            switch_state = self.hass.states.get(setup.switch_entity)
            if switch_state is None or switch_state.state in {"unknown", "unavailable"}:
                await self._async_abort_session("Charging switch became unavailable")
                return
            if switch_state.state != "on" and not self._commanding_switch:
                await self._async_abort_session("Charging switch is not on")
                return
            power_w = self._power_state_to_w(
                self.hass.states.get(setup.power_sensor)
                if setup.power_sensor
                else None
            )
            if setup.power_sensor and power_w is None:
                await self._async_abort_session(
                    "Configured power sensor became unavailable or invalid"
                )
                return
            temperature_c = self._temperature_state_to_c(
                self.hass.states.get(setup.temperature_sensor)
                if setup.temperature_sensor
                else None
            )
            if setup.temperature_sensor and temperature_c is None:
                await self._async_abort_session(
                    "Configured temperature sensor became unavailable or invalid"
                )
                return
            now = dt_util.utcnow()
            now_iso = now.isoformat()
            previous_raw = self.session.last_raw_energy_wh
            if previous_raw is None:
                delta_wh = 0.0
            elif raw_energy >= previous_raw:
                delta_wh = raw_energy - previous_raw
            else:
                delta_wh = raw_energy
            if delta_wh < -1e-9 or not math.isfinite(delta_wh):
                await self._async_abort_session("Energy sensor moved backwards unexpectedly")
                return
            self.session.gross_energy_wh += max(0.0, delta_wh)
            self.session.last_raw_energy_wh = raw_energy
            baseline = (
                0.0
                if self.session.mode == SESSION_IDLE_MEASURING
                else self.session.idle_baseline_power_w
            )
            elapsed_from_switch = self._elapsed_seconds(
                self.session.switch_on_at or self.session.session_started_at,
                now,
            )
            self.session.idle_energy_wh = max(
                0.0, baseline * elapsed_from_switch / 3600.0
            )
            self.session.net_energy_wh = max(
                0.0,
                self.session.gross_energy_wh - self.session.idle_energy_wh,
            )
            net_power_w = None if power_w is None else max(0.0, power_w - baseline)
            self.session.current_power_w = power_w
            self.session.current_net_power_w = net_power_w
            self.session.current_temperature_c = temperature_c
            if power_w is not None:
                self.session.peak_power_w = max(
                    power_w, self.session.peak_power_w or power_w
                )
            if net_power_w is not None:
                self.session.peak_net_power_w = max(
                    net_power_w, self.session.peak_net_power_w or net_power_w
                )
            if temperature_c is not None:
                self.session.peak_temperature_c = max(
                    temperature_c,
                    self.session.peak_temperature_c or temperature_c,
                )
            sample = MeasurementSample(
                timestamp=now_iso,
                raw_energy_wh=raw_energy,
                gross_energy_wh=self.session.gross_energy_wh,
                idle_energy_wh=self.session.idle_energy_wh,
                net_energy_wh=self.session.net_energy_wh,
                power_w=power_w,
                net_power_w=net_power_w,
                temperature_c=temperature_c,
                switch_state=switch_state.state,
            )
            self._append_sample(sample, source)
            self.session.last_sample_at = now_iso
            if power_w is not None and power_w > setup.max_power_w:
                await self._async_abort_session(
                    f"Measured power {power_w:.1f} W exceeded setup limit"
                )
                return
            if (
                temperature_c is not None
                and setup.max_temperature_c is not None
                and temperature_c > setup.max_temperature_c
            ):
                await self._async_abort_session(
                    f"Measured temperature {temperature_c:.1f} °C exceeded setup limit"
                )
                return
            completed = await self._async_evaluate_session(now)
            if completed:
                return
            await self._async_save()
            self._notify()

    async def _async_evaluate_session(self, now: datetime) -> bool:
        """Evaluate mode-specific start, target, reliability, and end conditions."""
        if self.session.mode == SESSION_IDLE_MEASURING:
            return await self._async_evaluate_idle_measurement(now)
        self._detect_charge_start(now)
        if self.session.charge_started_at is None:
            if self._elapsed_seconds(self.session.switch_on_at, now) >= (
                DEFAULT_CHARGE_START_TIMEOUT_MINUTES * 60
            ):
                await self._async_abort_session(
                    "No significant charging load was detected"
                )
                return True
            return False
        self._update_significant_and_taper(now)
        if self.session.mode == SESSION_CHARGING:
            target = self.session.target_energy_wh
            if target is not None and self.session.net_energy_wh >= target:
                self.session.phase = PHASE_TARGET_REACHED
                await self._async_complete_normal_charge("Target energy reached")
                return True
            return False
        if self.session.mode == SESSION_CALIBRATING:
            if self._calibration_exceeds_safety_limit():
                await self._async_abort_session("Calibration energy exceeded safety limit")
                return True
            if self._detect_calibration_end(now):
                await self._async_complete_calibration(
                    automatic=True,
                    reason="Full charge automatically detected",
                )
                return True
        return False

    async def _async_evaluate_idle_measurement(self, now: datetime) -> bool:
        """Complete fixed or reliability-driven idle measurement."""
        elapsed_minutes = self._elapsed_seconds(self.session.switch_on_at, now) / 60.0
        assessment = self._assess_idle_trace()
        mode = self.session.idle_measurement_mode
        if mode == IDLE_MODE_FIXED:
            if elapsed_minutes >= float(self.session.requested_duration_minutes or 0):
                await self._async_complete_idle_measurement(
                    assessment,
                    reason="Requested idle measurement duration reached",
                )
                return True
            return False
        min_minutes = float(
            self.session.auto_min_minutes or DEFAULT_IDLE_AUTO_MIN_MINUTES
        )
        max_minutes = float(
            self.session.auto_max_minutes or DEFAULT_IDLE_AUTO_MAX_HOURS * 60
        )
        if elapsed_minutes >= min_minutes and assessment["reliable"]:
            await self._async_complete_idle_measurement(
                assessment,
                reason="Reliable idle value established automatically",
            )
            return True
        if elapsed_minutes >= max_minutes:
            await self._async_complete_idle_measurement(
                assessment,
                reason="Automatic idle measurement maximum duration reached",
            )
            return True
        return False

    def _detect_charge_start(self, now: datetime) -> None:
        """Recognize the first sustained relevant load."""
        if self.session.charge_started_at is not None:
            return
        recent = self._samples_since(now - timedelta(minutes=3))
        power_hits = [
            item
            for item in recent
            if item.net_power_w is not None and item.net_power_w >= 0.35
        ]
        energy_started = self.session.net_energy_wh >= 0.02
        if len(power_hits) >= 2 or (
            power_hits and (power_hits[-1].net_power_w or 0) >= 1.0
        ) or energy_started:
            first = (
                power_hits[0].timestamp
                if power_hits
                else self.session.switch_on_at or recent[0].timestamp
            )
            self.session.charge_started_at = first
            self.session.last_significant_at = first
            self.session.last_significant_net_energy_wh = 0.0
            self.session.phase = PHASE_MAIN_CHARGE

    def _update_significant_and_taper(self, now: datetime) -> None:
        """Track relevant charging and the onset of the taper phase."""
        peak = self.session.peak_net_power_w or 0.0
        significance = max(0.15, peak * 0.05)
        current = self.session.current_net_power_w
        if current is not None and current > significance:
            sustained = True
            if self.session.candidate_end_at:
                recent = self._samples_since(now - timedelta(minutes=2))
                recent_powers = [
                    item.net_power_w
                    for item in recent
                    if item.net_power_w is not None
                ]
                recent_gain = (
                    max(0.0, recent[-1].net_energy_wh - recent[0].net_energy_wh)
                    if len(recent) >= 2
                    else 0.0
                )
                restart_threshold = max(significance * 1.5, peak * 0.10, 0.25)
                sustained = bool(
                    len(recent_powers) >= 2
                    and median(recent_powers) > restart_threshold
                    and recent_gain > 0.01
                )
                if sustained:
                    self._reset_end_candidate()
            if sustained:
                self.session.last_significant_at = self.session.last_sample_at
                self.session.last_significant_net_energy_wh = self.session.net_energy_wh
        elif current is None and len(self.session.samples) >= 2:
            previous = self.session.samples[-2]
            current_sample = self.session.samples[-1]
            elapsed = self._seconds_between(previous.timestamp, current_sample.timestamp)
            if elapsed > 0:
                slope_w = (
                    current_sample.net_energy_wh - previous.net_energy_wh
                ) / (elapsed / 3600.0)
                if slope_w > significance:
                    self.session.last_significant_at = current_sample.timestamp
                    self.session.last_significant_net_energy_wh = (
                        current_sample.net_energy_wh
                    )
        if self.session.taper_started_at is None and peak >= 0.5:
            recent = self._samples_since(now - timedelta(minutes=5))
            powers = [
                item.net_power_w
                for item in recent
                if item.net_power_w is not None
            ]
            if powers and median(powers) <= peak * 0.6:
                self.session.taper_started_at = recent[0].timestamp
                self.session.phase = PHASE_TAPER

    def _detect_calibration_end(self, now: datetime) -> bool:
        """Recognize and retrospectively anchor a stable end-of-charge plateau."""
        if self._elapsed_seconds(self.session.charge_started_at, now) < (
            DEFAULT_MIN_CHARGE_MINUTES * 60
        ):
            return False
        if self.session.net_energy_wh < 0.1:
            return False
        window_start = now - timedelta(minutes=DEFAULT_END_WINDOW_MINUTES)
        window = self._samples_since(window_start)
        if len(window) < 3:
            return False
        span = self._seconds_between(window[0].timestamp, window[-1].timestamp)
        if span < DEFAULT_END_WINDOW_MINUTES * 60 * 0.75:
            return False
        gain = max(0.0, window[-1].net_energy_wh - window[0].net_energy_wh)
        avg_net_power = gain / (span / 3600.0) if span > 0 else float("inf")
        peak = self.session.peak_net_power_w or max(avg_net_power, 0.1)
        plateau_threshold_w = max(0.12, peak * 0.05)
        plateau = avg_net_power <= plateau_threshold_w
        if not plateau:
            if avg_net_power > plateau_threshold_w * 1.5:
                self._reset_end_candidate()
            return False
        if self.session.candidate_end_at is None:
            endpoint = self._candidate_endpoint(window)
            self.session.candidate_end_at = endpoint.timestamp
            self.session.candidate_end_net_energy_wh = endpoint.net_energy_wh
            self.session.candidate_end_gross_energy_wh = endpoint.gross_energy_wh
            self.session.phase = PHASE_CONFIRMING_END
            return False
        candidate_dt = self._parse_dt(self.session.candidate_end_at)
        if candidate_dt is None:
            self._reset_end_candidate()
            return False
        candidate_elapsed = (now - candidate_dt).total_seconds()
        if candidate_elapsed < DEFAULT_END_CONFIRM_MINUTES * 60:
            return False
        candidate_energy = self.session.candidate_end_net_energy_wh or 0.0
        later_gain = max(0.0, self.session.net_energy_wh - candidate_energy)
        tolerance = max(0.05, candidate_energy * 0.01)
        if later_gain > tolerance:
            self._reset_end_candidate()
            return False
        self.session.charge_finished_at = self.session.candidate_end_at
        self.session.end_detected_at = now.isoformat()
        return True

    def _candidate_endpoint(
        self, window: list[MeasurementSample]
    ) -> MeasurementSample:
        """Choose the last significant point before the confirmed plateau."""
        if self.session.last_significant_at:
            last_sig = self._parse_dt(self.session.last_significant_at)
            if last_sig:
                candidates = [
                    item
                    for item in self.session.samples
                    if (self._parse_dt(item.timestamp) or last_sig) <= last_sig
                ]
                if candidates:
                    return candidates[-1]
        return window[0]

    def _reset_end_candidate(self) -> None:
        """Clear a plateau candidate after renewed significant charging."""
        self.session.candidate_end_at = None
        self.session.candidate_end_net_energy_wh = None
        self.session.candidate_end_gross_energy_wh = None
        if self.session.taper_started_at:
            self.session.phase = PHASE_TAPER
        elif self.session.charge_started_at:
            self.session.phase = PHASE_MAIN_CHARGE

    def _calibration_exceeds_safety_limit(self) -> bool:
        """Stop grossly implausible calibration energy."""
        setup_id = self.session.setup_id or ""
        battery_id = self.session.battery_id or ""
        summary = self.calibration_summary(
            setup_id, battery_id, self.session.quantity
        )
        known = summary.get("median_net_energy_wh")
        limit = (
            float(known) * DEFAULT_CALIBRATION_MAX_FACTOR
            if known
            else DEFAULT_CALIBRATION_ABSOLUTE_MAX_WH
        )
        return self.session.net_energy_wh > limit

    async def _async_complete_normal_charge(self, reason: str) -> None:
        """Safely finish a normal relative-energy charge."""
        if self._finalizing:
            return
        self._finalizing = True
        try:
            setup = self._require_session_setup()
            now = self._now_iso()
            self.session.charge_finished_at = now
            self.session.end_detected_at = now
            switch_off_confirmed = await self._async_switch_off_checked(setup)
            self._stop_tracking()
            self.session.switch_off_at = self._now_iso()
            self.session.session_finished_at = self.session.switch_off_at
            self.session.phase = (
                PHASE_FINISHED if switch_off_confirmed else PHASE_ERROR
            )
            if not switch_off_confirmed:
                reason = f"{reason}; smart plug OFF state not confirmed"
            self.session.end_reason = reason
            self.session.valid = switch_off_confirmed
            self._append_charge_history(
                valid=switch_off_confirmed,
                reason=reason,
            )
            self.session.mode = SESSION_IDLE
            await self._async_save()
            self._notify()
        finally:
            self._finalizing = False

    async def _async_complete_calibration(
        self, *, automatic: bool, reason: str
    ) -> CalibrationRecord:
        """Store a full calibration using the retrospective endpoint."""
        if self._finalizing:
            raise HomeAssistantError("Session is already being finalized")
        self._finalizing = True
        try:
            setup = self._require_session_setup()
            battery = self.batteries.get(self.session.battery_id or "")
            if battery is None:
                raise HomeAssistantError("Battery type no longer exists")
            detected_at = self._now_iso()
            if automatic and self.session.candidate_end_at:
                endpoint_at = self.session.candidate_end_at
                endpoint_net = float(
                    self.session.candidate_end_net_energy_wh
                    if self.session.candidate_end_net_energy_wh is not None
                    else self.session.net_energy_wh
                )
                endpoint_gross = float(
                    self.session.candidate_end_gross_energy_wh
                    if self.session.candidate_end_gross_energy_wh is not None
                    else self.session.gross_energy_wh
                )
                method = (
                    "energy_plateau_and_low_power"
                    if setup.power_sensor
                    else "energy_plateau"
                )
                confidence = (
                    CONFIDENCE_HIGH if setup.power_sensor else CONFIDENCE_MEDIUM
                )
            else:
                endpoint_at = (
                    self.session.last_significant_at
                    or self.session.last_sample_at
                    or detected_at
                )
                endpoint_sample = self._sample_at_or_before(endpoint_at)
                endpoint_net = (
                    endpoint_sample.net_energy_wh
                    if endpoint_sample
                    else self.session.net_energy_wh
                )
                endpoint_gross = (
                    endpoint_sample.gross_energy_wh
                    if endpoint_sample
                    else self.session.gross_energy_wh
                )
                method = "manual"
                confidence = CONFIDENCE_LOW
            self.session.charge_finished_at = endpoint_at
            self.session.end_detected_at = detected_at
            switch_off_confirmed = await self._async_switch_off_checked(setup)
            self._stop_tracking()
            switch_off_at = self._now_iso()
            self.session.switch_off_at = switch_off_at
            self.session.session_finished_at = switch_off_at
            session_duration = self._seconds_between(
                self.session.session_started_at, switch_off_at
            )
            charge_duration = self._seconds_between(
                self.session.charge_started_at, endpoint_at
            )
            idle_baseline = self.session.idle_baseline_power_w
            endpoint_idle = idle_baseline * max(
                0.0,
                self._seconds_between(self.session.switch_on_at, endpoint_at),
            ) / 3600.0
            record = CalibrationRecord(
                calibration_id=uuid4().hex,
                setup_id=setup.setup_id,
                setup_revision=setup.revision,
                setup_snapshot=setup.snapshot(),
                battery_id=battery.battery_id,
                battery_revision=battery.revision,
                battery_snapshot=battery.snapshot(),
                quantity=self.session.quantity,
                ports=list(self.session.ports),
                session_started_at=self.session.session_started_at,
                switch_on_at=self.session.switch_on_at,
                charge_started_at=self.session.charge_started_at,
                taper_started_at=self.session.taper_started_at,
                candidate_end_at=self.session.candidate_end_at,
                charge_finished_at=endpoint_at,
                end_detected_at=detected_at,
                switch_off_at=switch_off_at,
                session_finished_at=switch_off_at,
                session_duration_seconds=session_duration,
                charge_duration_seconds=charge_duration,
                gross_energy_wh=endpoint_gross,
                idle_energy_wh=endpoint_idle,
                net_energy_wh=max(0.0, endpoint_net),
                idle_baseline_power_w=idle_baseline,
                idle_measurement_ids=list(self.session.idle_measurement_ids),
                idle_quality=self.session.idle_quality,
                energy_at_detection_wh=self.session.net_energy_wh,
                peak_power_w=self.session.peak_power_w,
                peak_net_power_w=self.session.peak_net_power_w,
                peak_temperature_c=self.session.peak_temperature_c,
                end_method=method,
                confidence=confidence,
                synchrony=self._estimate_synchrony(charge_duration),
                valid=switch_off_confirmed,
                invalid_reason=(
                    "Smart plug OFF state was not confirmed"
                    if not switch_off_confirmed
                    else ""
                ),
                manual_override=not automatic,
                algorithm_version=ALGORITHM_VERSION,
                samples=list(self.session.samples),
            )
            if record.net_energy_wh <= 0:
                raise HomeAssistantError("Calibration endpoint contains no net energy")
            self.calibrations[record.calibration_id] = record
            self.session.phase = (
                PHASE_FINISHED if switch_off_confirmed else PHASE_ERROR
            )
            if not switch_off_confirmed:
                reason = f"{reason}; smart plug OFF state not confirmed"
            self.session.end_reason = reason
            self.session.valid = switch_off_confirmed
            self._append_charge_history(
                valid=switch_off_confirmed,
                reason=reason,
            )
            self.session.mode = SESSION_IDLE
            await self._async_save()
            self._notify()
            return record
        finally:
            self._finalizing = False

    async def _async_complete_idle_measurement(
        self, assessment: dict[str, Any], *, reason: str
    ) -> IdleMeasurement:
        """Store one independent idle measurement and safely switch off."""
        if self._finalizing:
            raise HomeAssistantError("Session is already being finalized")
        self._finalizing = True
        try:
            setup = self._require_session_setup()
            finished_at = self._now_iso()
            switch_off_confirmed = await self._async_switch_off_checked(setup)
            self._stop_tracking()
            switch_off_at = self._now_iso()
            duration = self._seconds_between(
                self.session.switch_on_at, finished_at
            )
            record = IdleMeasurement(
                measurement_id=uuid4().hex,
                setup_id=setup.setup_id,
                setup_revision=setup.revision,
                setup_snapshot=setup.snapshot(),
                mode=self.session.idle_measurement_mode or IDLE_MODE_AUTOMATIC,
                requested_duration_minutes=self.session.requested_duration_minutes,
                started_at=self.session.switch_on_at,
                finished_at=finished_at,
                duration_seconds=duration,
                gross_energy_wh=self.session.gross_energy_wh,
                average_power_w=float(assessment["average_power_w"]),
                median_power_w=assessment.get("median_power_w"),
                stdev_power_w=assessment.get("stdev_power_w"),
                resolution_wh=assessment.get("resolution_wh"),
                below_detection_limit=bool(
                    assessment.get("below_detection_limit", False)
                ),
                upper_bound_power_w=assessment.get("upper_bound_power_w"),
                sample_count=len(self.session.samples),
                reliable=bool(assessment["reliable"]),
                confidence=str(assessment["confidence"]),
                valid=switch_off_confirmed,
                end_reason=reason,
                algorithm_version=ALGORITHM_VERSION,
                samples=list(self.session.samples),
            )
            self.idle_measurements[record.measurement_id] = record
            self.session.switch_off_at = switch_off_at
            self.session.session_finished_at = switch_off_at
            self.session.phase = (
                PHASE_FINISHED if switch_off_confirmed else PHASE_ERROR
            )
            if not switch_off_confirmed:
                reason = f"{reason}; smart plug OFF state not confirmed"
                record.end_reason = reason
            self.session.end_reason = reason
            self.session.valid = record.reliable and switch_off_confirmed
            self.session.mode = SESSION_IDLE
            await self._async_save()
            self._notify()
            return record
        finally:
            self._finalizing = False

    def _assess_idle_trace(self) -> dict[str, Any]:
        """Assess precision, stability, and reliability of the active idle trace."""
        samples = self.session.samples
        duration = self._seconds_between(
            self.session.switch_on_at,
            self.session.last_sample_at,
        )
        average = (
            self.session.gross_energy_wh / (duration / 3600.0)
            if duration > 0
            else 0.0
        )
        start_dt = self._parse_dt(self.session.switch_on_at)
        warmed: list[MeasurementSample] = []
        if start_dt:
            cutoff = start_dt + timedelta(minutes=DEFAULT_IDLE_WARMUP_MINUTES)
            warmed = [
                sample
                for sample in samples
                if (self._parse_dt(sample.timestamp) or cutoff) >= cutoff
            ]
        powers = [
            float(item.power_w)
            for item in warmed
            if item.power_w is not None and math.isfinite(item.power_w)
        ]
        interval_powers = self._interval_power_values(warmed)
        block_powers = self._block_energy_powers(warmed)
        values = powers if powers else block_powers
        median_power = median(values) if values else (average if duration > 0 else None)
        stdev_power = pstdev(values) if len(values) >= 2 else None
        observed_resolution = self._energy_resolution(samples)
        setup = self.setups.get(self.session.setup_id or "")
        inferred_resolution = self._state_resolution_wh(
            self.hass.states.get(setup.energy_sensor) if setup else None
        )
        resolution = observed_resolution or inferred_resolution
        stable = (
            self._series_stable(values)
            if powers
            else self._block_values_stable(block_powers)
        )
        enough_samples = (
            len(powers) >= 12
            if powers
            else len(warmed) >= 12 and len(block_powers) == 3
        )
        duration_hours = duration / 3600.0 if duration > 0 else 0.0
        below_detection_limit = bool(
            not powers
            and observed_resolution is None
            and self.session.gross_energy_wh <= 1e-9
            and resolution is not None
            and duration_hours > 0
        )
        upper_bound_power_w = (
            resolution / duration_hours
            if below_detection_limit and duration_hours > 0 and resolution
            else None
        )
        enough_energy = True
        if resolution and not powers and not below_detection_limit:
            enough_energy = self.session.gross_energy_wh >= max(
                0.05,
                resolution * DEFAULT_IDLE_RESOLUTION_MULTIPLIER,
            )
        near_zero_with_power_sensor = bool(
            powers and median_power is not None and median_power <= 0.05 and stable
        )
        below_detection_reliable = bool(
            below_detection_limit
            and upper_bound_power_w is not None
            and upper_bound_power_w <= DEFAULT_IDLE_RELIABLE_UPPER_BOUND_W
        )
        reliable = bool(
            duration >= DEFAULT_IDLE_AUTO_MIN_MINUTES * 60
            and enough_samples
            and stable
            and (
                enough_energy
                or near_zero_with_power_sensor
                or below_detection_reliable
            )
        )
        confidence = (
            CONFIDENCE_HIGH
            if reliable and powers
            else CONFIDENCE_MEDIUM if reliable
            else CONFIDENCE_LOW
        )
        return {
            "average_power_w": max(0.0, average),
            "median_power_w": (
                max(0.0, median_power) if median_power is not None else None
            ),
            "stdev_power_w": stdev_power,
            "resolution_wh": resolution,
            "below_detection_limit": below_detection_limit,
            "upper_bound_power_w": upper_bound_power_w,
            "reliable": reliable,
            "confidence": confidence,
            "stable": stable,
            "sample_count": len(values),
        }

    def idle_summary(self, setup_id: str) -> dict[str, Any]:
        """Combine all current valid idle measurements robustly."""
        setup = self.setups.get(setup_id)
        if setup is None:
            return self._empty_idle_summary()
        current = [
            item
            for item in self.idle_measurements.values()
            if item.setup_id == setup_id
            and item.setup_revision == setup.revision
            and item.valid
        ]
        reliable = [item for item in current if item.reliable]
        used = reliable or current
        values = [item.baseline_power_w for item in used]
        baseline = median(values) if values else None
        upper_bounds = [
            item.upper_bound_power_w
            for item in used
            if item.upper_bound_power_w is not None
        ]
        spread = self._relative_mad_percent(values)
        if not values:
            quality = QUALITY_NONE
        elif len(values) == 1:
            quality = QUALITY_PROVISIONAL
        elif spread is not None and spread <= 10:
            quality = QUALITY_STABLE
        else:
            quality = QUALITY_UNSTABLE
        outdated = sum(
            1
            for item in self.idle_measurements.values()
            if item.setup_id == setup_id and item.setup_revision != setup.revision
        )
        return {
            "baseline_power_w": baseline,
            "count": len(current),
            "reliable_count": len(reliable),
            "used_count": len(used),
            "spread_percent": spread,
            "quality": quality,
            "outdated_count": outdated,
            "measurement_ids": [item.measurement_id for item in used],
            "below_detection_count": sum(
                1 for item in used if item.below_detection_limit
            ),
            "upper_bound_power_w": (
                median(upper_bounds) if upper_bounds else None
            ),
        }

    def calibration_summary(
        self, setup_id: str, battery_id: str, quantity: int
    ) -> dict[str, Any]:
        """Combine current calibration records for one exact profile."""
        setup = self.setups.get(setup_id)
        battery = self.batteries.get(battery_id)
        if setup is None or battery is None:
            return self._empty_calibration_summary()
        records = [
            item
            for item in self.calibrations.values()
            if item.setup_id == setup_id
            and item.setup_revision == setup.revision
            and item.battery_id == battery_id
            and item.battery_revision == battery.revision
            and item.quantity == quantity
            and item.valid
            and item.net_energy_wh > 0
        ]
        records.sort(key=lambda item: item.session_started_at or "")
        trusted = [
            item
            for item in records
            if item.confidence in {CONFIDENCE_HIGH, CONFIDENCE_MEDIUM}
            and not item.legacy
        ]
        used = trusted or records
        values = [item.net_energy_wh for item in used]
        durations = [
            item.charge_duration_seconds
            for item in used
            if item.charge_duration_seconds is not None
            and item.charge_duration_seconds > 0
        ]
        spread = self._relative_mad_percent(values)
        stdev = pstdev(values) if len(values) >= 2 else None
        recent_values = values[-5:]
        recent_median = median(recent_values) if recent_values else None
        overall_median = median(values) if values else None
        drift_percent = (
            (recent_median - overall_median) / overall_median * 100.0
            if recent_median is not None
            and overall_median is not None
            and overall_median > 0
            and len(values) >= 4
            else None
        )
        if drift_percent is None:
            trend = "not_assessable"
        elif abs(drift_percent) < DEFAULT_CALIBRATION_DRIFT_WARN_PERCENT:
            trend = "stable"
        elif drift_percent > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        if not values:
            quality = QUALITY_NONE
        elif len(values) == 1:
            quality = QUALITY_PROVISIONAL
        elif len(values) == 2:
            quality = QUALITY_LIMITED if (spread or 0) <= 10 else QUALITY_UNSTABLE
        elif spread is not None and spread <= 5:
            quality = QUALITY_STABLE
        elif spread is not None and spread <= 10:
            quality = QUALITY_LIMITED
        else:
            quality = QUALITY_UNSTABLE
        if (
            drift_percent is not None
            and abs(drift_percent) >= DEFAULT_CALIBRATION_DRIFT_WARN_PERCENT
        ):
            quality = QUALITY_UNSTABLE
        outdated = sum(
            1
            for item in self.calibrations.values()
            if item.setup_id == setup_id
            and item.battery_id == battery_id
            and item.quantity == quantity
            and (
                item.setup_revision != setup.revision
                or item.battery_revision != battery.revision
            )
        )
        return {
            "count": len(used),
            "total_current_count": len(records),
            "trusted_count": len(trusted),
            "excluded_low_confidence_count": len(records) - len(used),
            "median_net_energy_wh": overall_median,
            "recent_median_net_energy_wh": recent_median,
            "median_charge_duration_seconds": median(durations) if durations else None,
            "min_net_energy_wh": min(values) if values else None,
            "max_net_energy_wh": max(values) if values else None,
            "stdev_net_energy_wh": stdev,
            "spread_percent": spread,
            "drift_percent": drift_percent,
            "trend": trend,
            "quality": quality,
            "outdated_count": outdated,
            "record_ids": [item.calibration_id for item in used],
            "all_current_record_ids": [item.calibration_id for item in records],
            "confidence_counts": {
                level: sum(1 for item in records if item.confidence == level)
                for level in (CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW)
            },
        }

    def linear_profile_model(self, setup_id: str, battery_id: str) -> dict[str, Any]:
        """Fit E = intercept + slope * quantity for plausibility only."""
        setup = self.setups.get(setup_id)
        if setup is None:
            return {"available": False}
        points: list[tuple[float, float]] = []
        for quantity in range(1, len(setup.port_labels) + 1):
            summary = self.calibration_summary(setup_id, battery_id, quantity)
            value = summary.get("median_net_energy_wh")
            if value is not None:
                points.append((float(quantity), float(value)))
        if len(points) < 2:
            return {"available": False, "points": points}
        mean_x = sum(x for x, _ in points) / len(points)
        mean_y = sum(y for _, y in points) / len(points)
        denominator = sum((x - mean_x) ** 2 for x, _ in points)
        if denominator <= 0:
            return {"available": False, "points": points}
        slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / denominator
        intercept = mean_y - slope * mean_x
        predicted = [intercept + slope * x for x, _ in points]
        ss_res = sum((y - p) ** 2 for (_, y), p in zip(points, predicted, strict=True))
        ss_tot = sum((y - mean_y) ** 2 for _, y in points)
        r_squared = 1.0 if ss_tot <= 0 else max(0.0, 1.0 - ss_res / ss_tot)
        return {
            "available": True,
            "intercept_wh": intercept,
            "per_battery_wh": slope,
            "r_squared": r_squared,
            "points": [{"quantity": int(x), "energy_wh": y} for x, y in points],
            "operational_use": False,
        }

    def frontend_state(self) -> dict[str, Any]:
        """Return a sample-light complete state for panel and card."""
        setup_id = self.selected_setup_id or ""
        battery_id = self.selected_battery_id or ""
        setup_rows = []
        for setup in sorted(self.setups.values(), key=lambda item: item.name.casefold()):
            row = setup.as_dict()
            row["idle_summary"] = self.idle_summary(setup.setup_id)
            setup_rows.append(row)
        battery_rows = []
        for battery in sorted(
            self.batteries.values(), key=lambda item: item.name.casefold()
        ):
            row = battery.as_dict()
            row["calibration_summaries"] = {
                str(quantity): self.calibration_summary(
                    setup_id, battery.battery_id, quantity
                )
                for quantity in range(
                    1,
                    len(self.active_setup.port_labels) + 1
                    if self.active_setup
                    else 1,
                )
            }
            battery_rows.append(row)
        session = self.session.as_dict(include_samples=False)
        session["progress_percent"] = self.progress_percent
        session["elapsed_seconds"] = self._elapsed_seconds(
            self.session.session_started_at,
            dt_util.utcnow(),
        ) if self.session.session_started_at else 0.0
        session["sample_count"] = len(self.session.samples)
        active_calibration = self.calibration_summary(
            setup_id, battery_id, self.selected_quantity
        )
        return {
            "version": VERSION,
            "entry_id": self.entry.entry_id,
            "selected_setup_id": self.selected_setup_id,
            "selected_battery_id": self.selected_battery_id,
            "selected_quantity": self.selected_quantity,
            "target_percent": self.target_percent,
            "max_session_hours": self.max_session_hours,
            "setups": setup_rows,
            "batteries": battery_rows,
            "idle_measurements": [
                item.as_dict(include_samples=False)
                for item in sorted(
                    self.idle_measurements.values(),
                    key=lambda value: value.started_at or "",
                    reverse=True,
                )[:100]
            ],
            "calibrations": [
                item.as_dict(include_samples=False)
                for item in sorted(
                    self.calibrations.values(),
                    key=lambda value: value.session_started_at or "",
                    reverse=True,
                )[:100]
            ],
            "charge_history": list(reversed(self.charge_history[-50:])),
            "session": session,
            "active_idle_summary": self.idle_summary(setup_id),
            "active_calibration_summary": active_calibration,
            "linear_model": self.linear_profile_model(setup_id, battery_id),
            "target_label": "relative_energy_percent",
        }

    def _append_charge_history(self, *, valid: bool, reason: str) -> None:
        """Retain compact normal/aborted session audit information."""
        self.charge_history.append(
            {
                "session_id": self.session.session_id,
                "mode": self.session.mode,
                "setup_id": self.session.setup_id,
                "battery_id": self.session.battery_id,
                "quantity": self.session.quantity,
                "target_percent": self.session.target_percent,
                "target_energy_wh": self.session.target_energy_wh,
                "gross_energy_wh": self.session.gross_energy_wh,
                "idle_energy_wh": self.session.idle_energy_wh,
                "net_energy_wh": self.session.net_energy_wh,
                "started_at": self.session.session_started_at,
                "finished_at": self.session.session_finished_at or self._now_iso(),
                "valid": valid,
                "reason": reason,
            }
        )
        self.charge_history = self.charge_history[-100:]

    async def _async_switch_on_checked(self, setup: ChargerSetup) -> None:
        """Turn on and verify the configured smart plug."""
        self._commanding_switch = True
        try:
            await self.hass.services.async_call(
                "switch",
                "turn_on",
                {"entity_id": setup.switch_entity},
                blocking=True,
            )
            if not await self._async_wait_for_switch_state(
                setup.switch_entity,
                "on",
                timeout_seconds=5.0,
            ):
                raise HomeAssistantError("Smart plug did not confirm the ON state")
        finally:
            self._commanding_switch = False

    async def _async_switch_off_checked(self, setup: ChargerSetup) -> bool:
        """Turn off, verify, retry once, and create a persistent warning if needed."""
        self._commanding_switch = True
        try:
            for attempt in range(2):
                try:
                    await self.hass.services.async_call(
                        "switch",
                        "turn_off",
                        {"entity_id": setup.switch_entity},
                        blocking=True,
                    )
                except Exception as err:  # noqa: BLE001
                    _LOGGER.error(
                        "Could not switch off %s: %s",
                        setup.switch_entity,
                        err,
                    )
                if await self._async_wait_for_switch_state(
                    setup.switch_entity,
                    "off",
                    timeout_seconds=5.0,
                ):
                    return True
                _LOGGER.warning(
                    "Smart plug %s remained on after attempt %s",
                    setup.switch_entity,
                    attempt + 1,
                )
            persistent_notification.async_create(
                self.hass,
                (
                    f"The charging switch {setup.switch_entity} still reports ON after "
                    "two shutdown attempts. Disconnect the charger manually."
                ),
                title="Battery Charge Manager safety warning",
                notification_id=f"{DOMAIN}_switch_off_failed",
            )
            return False
        finally:
            self._commanding_switch = False

    async def _async_wait_for_switch_state(
        self,
        entity_id: str,
        expected_state: str,
        *,
        timeout_seconds: float,
    ) -> bool:
        """Wait for a switch state without assuming immediate entity propagation."""
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_seconds
        while True:
            state = self.hass.states.get(entity_id)
            if state is not None and state.state == expected_state:
                return True
            if loop.time() >= deadline:
                return False
            await asyncio.sleep(0.25)

    def _append_sample(self, sample: MeasurementSample, source: str) -> None:
        """Append trace sample while suppressing event bursts and limiting storage."""
        samples = self.session.samples
        if samples:
            previous = samples[-1]
            seconds = self._seconds_between(previous.timestamp, sample.timestamp)
            materially_changed = (
                abs(sample.gross_energy_wh - previous.gross_energy_wh) >= 0.0001
                or (
                    sample.power_w is not None
                    and previous.power_w is not None
                    and abs(sample.power_w - previous.power_w) >= 0.02
                )
                or sample.switch_state != previous.switch_state
            )
            if source == "state_change" and seconds < 2 and not materially_changed:
                return
        samples.append(sample)
        if len(samples) > 1600:
            self.session.samples = samples[::2]
            if self.session.samples[-1].timestamp != sample.timestamp:
                self.session.samples.append(sample)

    def _estimate_synchrony(self, charge_duration: float | None) -> str:
        """Return an explicitly indicative multi-battery synchrony assessment."""
        if self.session.quantity <= 1:
            return "single_battery"
        if not self.active_setup or not self.active_setup.power_sensor:
            return "not_assessable"
        if not charge_duration or not self.session.taper_started_at or not self.session.charge_finished_at:
            return "not_assessable"
        taper = self._seconds_between(
            self.session.taper_started_at, self.session.charge_finished_at
        )
        ratio = taper / charge_duration if charge_duration > 0 else 1.0
        if ratio <= 0.15:
            return "indicatively_close"
        if ratio <= 0.35:
            return "indicatively_moderate"
        return "indicatively_spread"

    def _samples_since(self, start: datetime) -> list[MeasurementSample]:
        """Return samples at or after a UTC timestamp."""
        result = []
        for sample in self.session.samples:
            parsed = self._parse_dt(sample.timestamp)
            if parsed and parsed >= start:
                result.append(sample)
        return result

    def _sample_at_or_before(self, timestamp: str) -> MeasurementSample | None:
        """Return the last sample at or before a timestamp."""
        target = self._parse_dt(timestamp)
        if target is None:
            return None
        found = None
        for sample in self.session.samples:
            parsed = self._parse_dt(sample.timestamp)
            if parsed and parsed <= target:
                found = sample
        return found

    def _interval_power_values(
        self, samples: list[MeasurementSample]
    ) -> list[float]:
        """Derive average interval powers from cumulative energy."""
        values: list[float] = []
        for previous, current in zip(samples, samples[1:], strict=False):
            seconds = self._seconds_between(previous.timestamp, current.timestamp)
            if seconds <= 0:
                continue
            delta = current.gross_energy_wh - previous.gross_energy_wh
            if delta < 0:
                continue
            values.append(delta / (seconds / 3600.0))
        return values

    def _block_energy_powers(
        self, samples: list[MeasurementSample]
    ) -> list[float]:
        """Derive three long-window powers robust to quantized energy sensors."""
        if len(samples) < 6:
            return []
        start = self._parse_dt(samples[0].timestamp)
        end = self._parse_dt(samples[-1].timestamp)
        if start is None or end is None or end <= start:
            return []
        total = (end - start).total_seconds()
        powers: list[float] = []
        for index in range(3):
            block_start = start + timedelta(seconds=total * index / 3)
            block_end = start + timedelta(seconds=total * (index + 1) / 3)
            before = None
            after = None
            for sample in samples:
                parsed = self._parse_dt(sample.timestamp)
                if parsed is None:
                    continue
                if parsed <= block_start:
                    before = sample
                if parsed >= block_start and before is None:
                    before = sample
                if parsed <= block_end:
                    after = sample
                elif after is None:
                    after = sample
                    break
            if before is None or after is None:
                return []
            seconds = self._seconds_between(before.timestamp, after.timestamp)
            if seconds <= 0:
                return []
            delta = max(0.0, after.gross_energy_wh - before.gross_energy_wh)
            powers.append(delta / (seconds / 3600.0))
        return powers

    @staticmethod
    def _block_values_stable(values: list[float]) -> bool:
        """Check agreement of three long-window estimates."""
        if len(values) != 3:
            return False
        center = median(values)
        tolerance = max(0.03, abs(center) * 0.10)
        return max(values) - min(values) <= tolerance

    @staticmethod
    def _series_stable(values: list[float]) -> bool:
        """Check whether three sequential blocks agree within robust limits."""
        if len(values) < 9:
            return False
        block = len(values) // 3
        medians = [
            median(values[index * block : (index + 1) * block])
            for index in range(3)
        ]
        center = median(medians)
        tolerance = max(0.03, abs(center) * 0.10)
        return max(medians) - min(medians) <= tolerance

    @staticmethod
    def _energy_resolution(samples: list[MeasurementSample]) -> float | None:
        """Infer smallest positive cumulative energy step."""
        raw = [
            sample.raw_energy_wh
            for sample in samples
            if sample.raw_energy_wh is not None
        ]
        deltas = [
            current - previous
            for previous, current in zip(raw, raw[1:], strict=False)
            if current > previous
        ]
        return min(deltas) if deltas else None

    @staticmethod
    def _state_resolution_wh(state: State | None) -> float | None:
        """Infer an upper-bound display resolution from the sensor state string."""
        if state is None or state.state in {"unknown", "unavailable"}:
            return None
        try:
            exponent = Decimal(str(state.state)).as_tuple().exponent
        except (InvalidOperation, ValueError):
            return None
        step = float(Decimal(10) ** exponent)
        unit = state.attributes.get("unit_of_measurement")
        if unit == UnitOfEnergy.KILO_WATT_HOUR:
            return abs(step * 1000.0)
        if unit == UnitOfEnergy.WATT_HOUR:
            return abs(step)
        if unit == "MWh":
            return abs(step * 1_000_000.0)
        return None

    @staticmethod
    def _relative_mad_percent(values: list[float]) -> float | None:
        """Return relative median absolute deviation in percent."""
        if len(values) < 2:
            return None
        center = median(values)
        if center == 0:
            return 0.0 if all(value == 0 for value in values) else None
        mad = median([abs(value - center) for value in values])
        return abs(mad / center) * 100.0

    @staticmethod
    def _normalize_port_labels(value: Any) -> list[str]:
        """Normalize comma-separated or list port labels."""
        if isinstance(value, str):
            labels = [item.strip() for item in value.split(",") if item.strip()]
        elif isinstance(value, list):
            labels = [str(item).strip() for item in value if str(item).strip()]
        else:
            labels = ["A", "B", "C", "D"]
        if not labels:
            labels = ["A", "B", "C", "D"]
        if len(labels) > 8:
            labels = labels[:8]
        if len(set(labels)) != len(labels):
            raise HomeAssistantError("Port labels must be unique")
        return labels

    @staticmethod
    def _optional_positive_float(value: Any) -> float | None:
        """Parse an optional positive float."""
        if value in {None, ""}:
            return None
        parsed = float(value)
        if parsed <= 0:
            raise HomeAssistantError("Value must be greater than zero")
        return parsed

    @staticmethod
    def _validate_setup_entities(
        switch_entity: str,
        energy_sensor: str,
        power_sensor: str | None,
        temperature_sensor: str | None = None,
    ) -> None:
        """Validate entity domains before persisting a setup."""
        if not switch_entity.startswith("switch."):
            raise HomeAssistantError("Charge switch must be a switch entity")
        if not energy_sensor.startswith("sensor."):
            raise HomeAssistantError("Energy sensor must be a sensor entity")
        if power_sensor and not power_sensor.startswith("sensor."):
            raise HomeAssistantError("Power sensor must be a sensor entity")
        if temperature_sensor and not temperature_sensor.startswith("sensor."):
            raise HomeAssistantError("Temperature sensor must be a sensor entity")

    def _validate_runtime_setup(self, setup: ChargerSetup) -> None:
        """Validate current entity availability and units."""
        self._validate_setup_entities(
            setup.switch_entity,
            setup.energy_sensor,
            setup.power_sensor,
            setup.temperature_sensor,
        )
        energy_state = self.hass.states.get(setup.energy_sensor)
        if self._energy_state_to_wh(energy_state) is None:
            raise HomeAssistantError("Energy sensor is unavailable or has no energy unit")
        switch_state = self.hass.states.get(setup.switch_entity)
        if switch_state is None or switch_state.state in {"unknown", "unavailable"}:
            raise HomeAssistantError("Charge switch is unavailable")
        if switch_state.state != "off":
            raise HomeAssistantError(
                "Charge switch must report OFF before a new session can start"
            )
        if setup.power_sensor:
            power_state = self.hass.states.get(setup.power_sensor)
            if self._power_state_to_w(power_state) is None:
                raise HomeAssistantError("Power sensor is unavailable or has no power unit")
        if setup.temperature_sensor:
            temperature_state = self.hass.states.get(setup.temperature_sensor)
            if self._temperature_state_to_c(temperature_state) is None:
                raise HomeAssistantError(
                    "Temperature sensor is unavailable or has no temperature unit"
                )

    def _ensure_idle(self) -> None:
        """Require no active measurement or charge."""
        if self.session.active:
            raise HomeAssistantError("A charge or measurement session is already active")

    def _require_setup(self) -> ChargerSetup:
        """Return selected setup or raise."""
        setup = self.active_setup
        if setup is None:
            raise HomeAssistantError("No charging setup is selected")
        return setup

    def _require_battery(self) -> BatteryType:
        """Return selected battery or raise."""
        battery = self.active_battery
        if battery is None:
            raise HomeAssistantError("No battery type is selected")
        return battery

    def _require_session_setup(self) -> ChargerSetup:
        """Return setup used by active session."""
        setup = self.setups.get(self.session.setup_id or "")
        if setup is None:
            raise HomeAssistantError("Session charging setup no longer exists")
        return setup

    @staticmethod
    def _empty_idle_summary() -> dict[str, Any]:
        return {
            "baseline_power_w": None,
            "count": 0,
            "reliable_count": 0,
            "used_count": 0,
            "spread_percent": None,
            "quality": QUALITY_NONE,
            "outdated_count": 0,
            "measurement_ids": [],
            "below_detection_count": 0,
            "upper_bound_power_w": None,
        }

    @staticmethod
    def _empty_calibration_summary() -> dict[str, Any]:
        return {
            "count": 0,
            "total_current_count": 0,
            "trusted_count": 0,
            "excluded_low_confidence_count": 0,
            "median_net_energy_wh": None,
            "recent_median_net_energy_wh": None,
            "median_charge_duration_seconds": None,
            "min_net_energy_wh": None,
            "max_net_energy_wh": None,
            "stdev_net_energy_wh": None,
            "spread_percent": None,
            "drift_percent": None,
            "trend": "not_assessable",
            "quality": QUALITY_NONE,
            "outdated_count": 0,
            "record_ids": [],
            "all_current_record_ids": [],
            "confidence_counts": {
                CONFIDENCE_HIGH: 0,
                CONFIDENCE_MEDIUM: 0,
                CONFIDENCE_LOW: 0,
            },
        }

    @staticmethod
    def _now_iso() -> str:
        return dt_util.utcnow().isoformat()

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        return dt_util.parse_datetime(value)

    @classmethod
    def _seconds_between(cls, start: str | None, end: str | None) -> float:
        start_dt = cls._parse_dt(start)
        end_dt = cls._parse_dt(end)
        if start_dt is None or end_dt is None:
            return 0.0
        return max(0.0, (end_dt - start_dt).total_seconds())

    @classmethod
    def _elapsed_seconds(cls, start: str | None, end: datetime) -> float:
        start_dt = cls._parse_dt(start)
        if start_dt is None:
            return 0.0
        return max(0.0, (end - start_dt).total_seconds())

    @staticmethod
    def _energy_state_to_wh(state: State | None) -> float | None:
        """Convert a cumulative energy sensor state to Wh."""
        if state is None or state.state in {"unknown", "unavailable"}:
            return None
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(value):
            return None
        unit = state.attributes.get("unit_of_measurement")
        if unit == UnitOfEnergy.KILO_WATT_HOUR:
            return value * 1000.0
        if unit == UnitOfEnergy.WATT_HOUR:
            return value
        if unit == "MWh":
            return value * 1_000_000.0
        return None

    @staticmethod
    def _power_state_to_w(state: State | None) -> float | None:
        """Convert a power sensor state to W."""
        if state is None or state.state in {"unknown", "unavailable"}:
            return None
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(value):
            return None
        unit = state.attributes.get("unit_of_measurement")
        if unit == UnitOfPower.WATT:
            return value
        if unit == UnitOfPower.KILO_WATT:
            return value * 1000.0
        if unit == "mW":
            return value / 1000.0
        return None

    @staticmethod
    def _temperature_state_to_c(state: State | None) -> float | None:
        """Convert a temperature sensor state to degrees Celsius."""
        if state is None or state.state in {"unknown", "unavailable"}:
            return None
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(value):
            return None
        unit = state.attributes.get("unit_of_measurement")
        if unit == UnitOfTemperature.CELSIUS:
            return value
        if unit == UnitOfTemperature.FAHRENHEIT:
            return (value - 32.0) * 5.0 / 9.0
        if unit == UnitOfTemperature.KELVIN:
            return value - 273.15
        return None
