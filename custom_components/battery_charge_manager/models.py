"""Persistent data models for Battery Charge Manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median
from typing import Any

from .const import (
    ALGORITHM_VERSION,
    CONFIDENCE_UNKNOWN,
    DEFAULT_MAX_POWER_W,
    IDLE_MODE_AUTOMATIC,
    PHASE_IDLE,
    SESSION_IDLE,
)


def _float_or_none(value: Any) -> float | None:
    """Convert a stored value to float when possible."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or(value: Any, default: int) -> int:
    """Convert a stored value to int with a fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class MeasurementSample:
    """One point in an idle, calibration, or charge trace."""

    timestamp: str
    raw_energy_wh: float | None = None
    gross_energy_wh: float = 0.0
    idle_energy_wh: float = 0.0
    net_energy_wh: float = 0.0
    power_w: float | None = None
    net_power_w: float | None = None
    temperature_c: float | None = None
    switch_state: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize sample."""
        return {
            "timestamp": self.timestamp,
            "raw_energy_wh": self.raw_energy_wh,
            "gross_energy_wh": round(self.gross_energy_wh, 6),
            "idle_energy_wh": round(self.idle_energy_wh, 6),
            "net_energy_wh": round(self.net_energy_wh, 6),
            "power_w": self.power_w,
            "net_power_w": self.net_power_w,
            "temperature_c": self.temperature_c,
            "switch_state": self.switch_state,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MeasurementSample":
        """Deserialize sample."""
        return cls(
            timestamp=str(data.get("timestamp", "")),
            raw_energy_wh=_float_or_none(data.get("raw_energy_wh")),
            gross_energy_wh=float(data.get("gross_energy_wh", 0.0)),
            idle_energy_wh=float(data.get("idle_energy_wh", 0.0)),
            net_energy_wh=float(data.get("net_energy_wh", 0.0)),
            power_w=_float_or_none(data.get("power_w")),
            net_power_w=_float_or_none(data.get("net_power_w")),
            temperature_c=_float_or_none(data.get("temperature_c")),
            switch_state=data.get("switch_state"),
        )


@dataclass(slots=True)
class BatteryType:
    """A battery type and its versioned technical metadata."""

    battery_id: str
    name: str
    nominal_capacity_mah: int
    technology: str
    form_factor: str
    manufacturer: str = ""
    model: str = ""
    nominal_voltage_v: float | None = None
    nominal_energy_wh: float | None = None
    charging_method: str = "Integrated USB-C charger"
    discharge_method: str = ""
    rest_time_minutes: int | None = None
    starting_condition_notes: str = ""
    image: dict[str, Any] | str | None = None
    notes: str = ""
    revision: int = 1
    created_at: str | None = None
    updated_at: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize battery type."""
        return {
            "battery_id": self.battery_id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "nominal_capacity_mah": self.nominal_capacity_mah,
            "nominal_voltage_v": self.nominal_voltage_v,
            "nominal_energy_wh": self.nominal_energy_wh,
            "technology": self.technology,
            "form_factor": self.form_factor,
            "charging_method": self.charging_method,
            "discharge_method": self.discharge_method,
            "rest_time_minutes": self.rest_time_minutes,
            "starting_condition_notes": self.starting_condition_notes,
            "image": self.image,
            "notes": self.notes,
            "revision": self.revision,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def snapshot(self) -> dict[str, Any]:
        """Return immutable metadata for a measurement record."""
        return self.as_dict()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BatteryType":
        """Deserialize battery type, including legacy records."""
        return cls(
            battery_id=str(data["battery_id"]),
            name=str(data.get("name", "Battery")),
            manufacturer=str(data.get("manufacturer", "")),
            model=str(data.get("model", "")),
            nominal_capacity_mah=_int_or(data.get("nominal_capacity_mah"), 1000),
            nominal_voltage_v=_float_or_none(data.get("nominal_voltage_v")),
            nominal_energy_wh=_float_or_none(data.get("nominal_energy_wh")),
            technology=str(data.get("technology", "Other")),
            form_factor=str(data.get("form_factor", "Other")),
            charging_method=str(
                data.get("charging_method", "Integrated USB-C charger")
            ),
            discharge_method=str(data.get("discharge_method", "")),
            rest_time_minutes=(
                _int_or(data.get("rest_time_minutes"), 0)
                if data.get("rest_time_minutes") not in {None, ""}
                else None
            ),
            starting_condition_notes=str(
                data.get("starting_condition_notes", "")
            ),
            image=data.get("image"),
            notes=str(data.get("notes", "")),
            revision=_int_or(data.get("revision"), 1),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass(slots=True)
class ChargerSetup:
    """Versioned physical charging arrangement."""

    setup_id: str
    name: str
    switch_entity: str
    energy_sensor: str
    power_sensor: str | None = None
    temperature_sensor: str | None = None
    charger_model: str = ""
    cable_description: str = ""
    description: str = ""
    port_labels: list[str] = field(default_factory=lambda: ["A", "B", "C", "D"])
    max_power_w: float = DEFAULT_MAX_POWER_W
    max_temperature_c: float | None = None
    revision: int = 1
    created_at: str | None = None
    updated_at: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize setup."""
        return {
            "setup_id": self.setup_id,
            "name": self.name,
            "switch_entity": self.switch_entity,
            "energy_sensor": self.energy_sensor,
            "power_sensor": self.power_sensor,
            "temperature_sensor": self.temperature_sensor,
            "charger_model": self.charger_model,
            "cable_description": self.cable_description,
            "description": self.description,
            "port_labels": self.port_labels,
            "max_power_w": self.max_power_w,
            "max_temperature_c": self.max_temperature_c,
            "revision": self.revision,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def snapshot(self) -> dict[str, Any]:
        """Return immutable setup metadata for a measurement record."""
        return self.as_dict()

    def ports_for_quantity(self, quantity: int) -> list[str]:
        """Return the fixed first-N port allocation."""
        return self.port_labels[:quantity]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChargerSetup":
        """Deserialize setup."""
        labels = [str(item) for item in data.get("port_labels", ["A", "B", "C", "D"])]
        if not labels:
            labels = ["A", "B", "C", "D"]
        return cls(
            setup_id=str(data["setup_id"]),
            name=str(data.get("name", "Charging setup")),
            switch_entity=str(data.get("switch_entity", "")),
            energy_sensor=str(data.get("energy_sensor", "")),
            power_sensor=data.get("power_sensor") or None,
            temperature_sensor=data.get("temperature_sensor") or None,
            charger_model=str(data.get("charger_model", "")),
            cable_description=str(data.get("cable_description", "")),
            description=str(data.get("description", "")),
            port_labels=labels,
            max_power_w=float(data.get("max_power_w", DEFAULT_MAX_POWER_W)),
            max_temperature_c=_float_or_none(data.get("max_temperature_c")),
            revision=_int_or(data.get("revision"), 1),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass(slots=True)
class IdleMeasurement:
    """Independent no-battery measurement for one setup revision."""

    measurement_id: str
    setup_id: str
    setup_revision: int
    setup_snapshot: dict[str, Any]
    mode: str = IDLE_MODE_AUTOMATIC
    requested_duration_minutes: float | None = None
    started_at: str | None = None
    finished_at: str | None = None
    duration_seconds: float = 0.0
    gross_energy_wh: float = 0.0
    average_power_w: float = 0.0
    median_power_w: float | None = None
    stdev_power_w: float | None = None
    resolution_wh: float | None = None
    below_detection_limit: bool = False
    upper_bound_power_w: float | None = None
    sample_count: int = 0
    reliable: bool = False
    confidence: str = CONFIDENCE_UNKNOWN
    valid: bool = True
    invalid_reason: str = ""
    end_reason: str = ""
    algorithm_version: str = ALGORITHM_VERSION
    samples: list[MeasurementSample] = field(default_factory=list)

    @property
    def baseline_power_w(self) -> float:
        """Return the preferred baseline estimate."""
        if self.median_power_w is not None:
            return max(0.0, self.median_power_w)
        return max(0.0, self.average_power_w)

    def as_dict(self, *, include_samples: bool = True) -> dict[str, Any]:
        """Serialize measurement."""
        data: dict[str, Any] = {
            "measurement_id": self.measurement_id,
            "setup_id": self.setup_id,
            "setup_revision": self.setup_revision,
            "setup_snapshot": self.setup_snapshot,
            "mode": self.mode,
            "requested_duration_minutes": self.requested_duration_minutes,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": round(self.duration_seconds, 3),
            "gross_energy_wh": round(self.gross_energy_wh, 6),
            "average_power_w": round(self.average_power_w, 6),
            "median_power_w": self.median_power_w,
            "stdev_power_w": self.stdev_power_w,
            "resolution_wh": self.resolution_wh,
            "below_detection_limit": self.below_detection_limit,
            "upper_bound_power_w": self.upper_bound_power_w,
            "sample_count": self.sample_count,
            "reliable": self.reliable,
            "confidence": self.confidence,
            "valid": self.valid,
            "invalid_reason": self.invalid_reason,
            "end_reason": self.end_reason,
            "algorithm_version": self.algorithm_version,
        }
        if include_samples:
            data["samples"] = [sample.as_dict() for sample in self.samples]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IdleMeasurement":
        """Deserialize measurement."""
        return cls(
            measurement_id=str(data["measurement_id"]),
            setup_id=str(data["setup_id"]),
            setup_revision=_int_or(data.get("setup_revision"), 1),
            setup_snapshot=dict(data.get("setup_snapshot", {})),
            mode=str(data.get("mode", IDLE_MODE_AUTOMATIC)),
            requested_duration_minutes=_float_or_none(
                data.get("requested_duration_minutes")
            ),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            duration_seconds=float(data.get("duration_seconds", 0.0)),
            gross_energy_wh=float(data.get("gross_energy_wh", 0.0)),
            average_power_w=float(data.get("average_power_w", 0.0)),
            median_power_w=_float_or_none(data.get("median_power_w")),
            stdev_power_w=_float_or_none(data.get("stdev_power_w")),
            resolution_wh=_float_or_none(data.get("resolution_wh")),
            below_detection_limit=bool(
                data.get("below_detection_limit", False)
            ),
            upper_bound_power_w=_float_or_none(
                data.get("upper_bound_power_w")
            ),
            sample_count=_int_or(data.get("sample_count"), 0),
            reliable=bool(data.get("reliable", False)),
            confidence=str(data.get("confidence", CONFIDENCE_UNKNOWN)),
            valid=bool(data.get("valid", True)),
            invalid_reason=str(data.get("invalid_reason", "")),
            end_reason=str(data.get("end_reason", "")),
            algorithm_version=str(data.get("algorithm_version", ALGORITHM_VERSION)),
            samples=[
                MeasurementSample.from_dict(item)
                for item in data.get("samples", [])
            ],
        )


@dataclass(slots=True)
class CalibrationRecord:
    """One immutable full-charge calibration result."""

    calibration_id: str
    setup_id: str
    setup_revision: int
    setup_snapshot: dict[str, Any]
    battery_id: str
    battery_revision: int
    battery_snapshot: dict[str, Any]
    quantity: int
    ports: list[str]
    session_started_at: str | None = None
    switch_on_at: str | None = None
    charge_started_at: str | None = None
    taper_started_at: str | None = None
    candidate_end_at: str | None = None
    charge_finished_at: str | None = None
    end_detected_at: str | None = None
    switch_off_at: str | None = None
    session_finished_at: str | None = None
    session_duration_seconds: float | None = None
    charge_duration_seconds: float | None = None
    gross_energy_wh: float = 0.0
    idle_energy_wh: float = 0.0
    net_energy_wh: float = 0.0
    idle_baseline_power_w: float = 0.0
    idle_measurement_ids: list[str] = field(default_factory=list)
    idle_quality: str = "none"
    energy_at_detection_wh: float | None = None
    peak_power_w: float | None = None
    peak_net_power_w: float | None = None
    peak_temperature_c: float | None = None
    end_method: str = "manual"
    confidence: str = CONFIDENCE_UNKNOWN
    synchrony: str = "not_assessable"
    valid: bool = True
    invalid_reason: str = ""
    manual_override: bool = False
    legacy: bool = False
    algorithm_version: str = ALGORITHM_VERSION
    samples: list[MeasurementSample] = field(default_factory=list)

    def as_dict(self, *, include_samples: bool = True) -> dict[str, Any]:
        """Serialize calibration."""
        data: dict[str, Any] = {
            "calibration_id": self.calibration_id,
            "setup_id": self.setup_id,
            "setup_revision": self.setup_revision,
            "setup_snapshot": self.setup_snapshot,
            "battery_id": self.battery_id,
            "battery_revision": self.battery_revision,
            "battery_snapshot": self.battery_snapshot,
            "quantity": self.quantity,
            "ports": self.ports,
            "session_started_at": self.session_started_at,
            "switch_on_at": self.switch_on_at,
            "charge_started_at": self.charge_started_at,
            "taper_started_at": self.taper_started_at,
            "candidate_end_at": self.candidate_end_at,
            "charge_finished_at": self.charge_finished_at,
            "end_detected_at": self.end_detected_at,
            "switch_off_at": self.switch_off_at,
            "session_finished_at": self.session_finished_at,
            "session_duration_seconds": self.session_duration_seconds,
            "charge_duration_seconds": self.charge_duration_seconds,
            "gross_energy_wh": round(self.gross_energy_wh, 6),
            "idle_energy_wh": round(self.idle_energy_wh, 6),
            "net_energy_wh": round(self.net_energy_wh, 6),
            "idle_baseline_power_w": round(self.idle_baseline_power_w, 6),
            "idle_measurement_ids": self.idle_measurement_ids,
            "idle_quality": self.idle_quality,
            "energy_at_detection_wh": self.energy_at_detection_wh,
            "peak_power_w": self.peak_power_w,
            "peak_net_power_w": self.peak_net_power_w,
            "peak_temperature_c": self.peak_temperature_c,
            "end_method": self.end_method,
            "confidence": self.confidence,
            "synchrony": self.synchrony,
            "valid": self.valid,
            "invalid_reason": self.invalid_reason,
            "manual_override": self.manual_override,
            "legacy": self.legacy,
            "algorithm_version": self.algorithm_version,
        }
        if include_samples:
            data["samples"] = [sample.as_dict() for sample in self.samples]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CalibrationRecord":
        """Deserialize calibration."""
        return cls(
            calibration_id=str(data["calibration_id"]),
            setup_id=str(data.get("setup_id", "")),
            setup_revision=_int_or(data.get("setup_revision"), 1),
            setup_snapshot=dict(data.get("setup_snapshot", {})),
            battery_id=str(data.get("battery_id", "")),
            battery_revision=_int_or(data.get("battery_revision"), 1),
            battery_snapshot=dict(data.get("battery_snapshot", {})),
            quantity=_int_or(data.get("quantity"), 1),
            ports=[str(item) for item in data.get("ports", [])],
            session_started_at=data.get("session_started_at"),
            switch_on_at=data.get("switch_on_at"),
            charge_started_at=data.get("charge_started_at"),
            taper_started_at=data.get("taper_started_at"),
            candidate_end_at=data.get("candidate_end_at"),
            charge_finished_at=data.get("charge_finished_at"),
            end_detected_at=data.get("end_detected_at"),
            switch_off_at=data.get("switch_off_at"),
            session_finished_at=data.get("session_finished_at"),
            session_duration_seconds=_float_or_none(
                data.get("session_duration_seconds")
            ),
            charge_duration_seconds=_float_or_none(
                data.get("charge_duration_seconds")
            ),
            gross_energy_wh=float(data.get("gross_energy_wh", 0.0)),
            idle_energy_wh=float(data.get("idle_energy_wh", 0.0)),
            net_energy_wh=float(data.get("net_energy_wh", 0.0)),
            idle_baseline_power_w=float(
                data.get("idle_baseline_power_w", 0.0)
            ),
            idle_measurement_ids=[
                str(item) for item in data.get("idle_measurement_ids", [])
            ],
            idle_quality=str(data.get("idle_quality", "none")),
            energy_at_detection_wh=_float_or_none(
                data.get("energy_at_detection_wh")
            ),
            peak_power_w=_float_or_none(data.get("peak_power_w")),
            peak_net_power_w=_float_or_none(data.get("peak_net_power_w")),
            peak_temperature_c=_float_or_none(
                data.get("peak_temperature_c")
            ),
            end_method=str(data.get("end_method", "manual")),
            confidence=str(data.get("confidence", CONFIDENCE_UNKNOWN)),
            synchrony=str(data.get("synchrony", "not_assessable")),
            valid=bool(data.get("valid", True)),
            invalid_reason=str(data.get("invalid_reason", "")),
            manual_override=bool(data.get("manual_override", False)),
            legacy=bool(data.get("legacy", False)),
            algorithm_version=str(data.get("algorithm_version", ALGORITHM_VERSION)),
            samples=[
                MeasurementSample.from_dict(item)
                for item in data.get("samples", [])
            ],
        )


@dataclass(slots=True)
class ChargeSession:
    """Runtime and persistent state for the active or last session."""

    session_id: str | None = None
    mode: str = SESSION_IDLE
    phase: str = PHASE_IDLE
    setup_id: str | None = None
    battery_id: str | None = None
    quantity: int = 1
    ports: list[str] = field(default_factory=list)
    target_percent: int = 50
    target_energy_wh: float | None = None
    gross_energy_wh: float = 0.0
    idle_energy_wh: float = 0.0
    net_energy_wh: float = 0.0
    last_raw_energy_wh: float | None = None
    current_power_w: float | None = None
    current_net_power_w: float | None = None
    current_temperature_c: float | None = None
    peak_power_w: float | None = None
    peak_net_power_w: float | None = None
    peak_temperature_c: float | None = None
    idle_baseline_power_w: float = 0.0
    idle_measurement_ids: list[str] = field(default_factory=list)
    idle_quality: str = "none"
    session_started_at: str | None = None
    switch_on_at: str | None = None
    charge_started_at: str | None = None
    taper_started_at: str | None = None
    candidate_end_at: str | None = None
    candidate_end_net_energy_wh: float | None = None
    candidate_end_gross_energy_wh: float | None = None
    charge_finished_at: str | None = None
    end_detected_at: str | None = None
    switch_off_at: str | None = None
    session_finished_at: str | None = None
    last_sample_at: str | None = None
    last_significant_at: str | None = None
    last_significant_net_energy_wh: float | None = None
    end_reason: str | None = None
    valid: bool = True
    restart_count: int = 0
    idle_measurement_mode: str | None = None
    requested_duration_minutes: float | None = None
    auto_min_minutes: float | None = None
    auto_max_minutes: float | None = None
    samples: list[MeasurementSample] = field(default_factory=list)

    @property
    def active(self) -> bool:
        """Return whether a session is active."""
        return self.mode != SESSION_IDLE

    def as_dict(self, *, include_samples: bool = True) -> dict[str, Any]:
        """Serialize session."""
        data: dict[str, Any] = {
            "session_id": self.session_id,
            "mode": self.mode,
            "phase": self.phase,
            "setup_id": self.setup_id,
            "battery_id": self.battery_id,
            "quantity": self.quantity,
            "ports": self.ports,
            "target_percent": self.target_percent,
            "target_energy_wh": self.target_energy_wh,
            "gross_energy_wh": round(self.gross_energy_wh, 6),
            "idle_energy_wh": round(self.idle_energy_wh, 6),
            "net_energy_wh": round(self.net_energy_wh, 6),
            "last_raw_energy_wh": self.last_raw_energy_wh,
            "current_power_w": self.current_power_w,
            "current_net_power_w": self.current_net_power_w,
            "current_temperature_c": self.current_temperature_c,
            "peak_power_w": self.peak_power_w,
            "peak_net_power_w": self.peak_net_power_w,
            "peak_temperature_c": self.peak_temperature_c,
            "idle_baseline_power_w": self.idle_baseline_power_w,
            "idle_measurement_ids": self.idle_measurement_ids,
            "idle_quality": self.idle_quality,
            "session_started_at": self.session_started_at,
            "switch_on_at": self.switch_on_at,
            "charge_started_at": self.charge_started_at,
            "taper_started_at": self.taper_started_at,
            "candidate_end_at": self.candidate_end_at,
            "candidate_end_net_energy_wh": self.candidate_end_net_energy_wh,
            "candidate_end_gross_energy_wh": self.candidate_end_gross_energy_wh,
            "charge_finished_at": self.charge_finished_at,
            "end_detected_at": self.end_detected_at,
            "switch_off_at": self.switch_off_at,
            "session_finished_at": self.session_finished_at,
            "last_sample_at": self.last_sample_at,
            "last_significant_at": self.last_significant_at,
            "last_significant_net_energy_wh": self.last_significant_net_energy_wh,
            "end_reason": self.end_reason,
            "valid": self.valid,
            "restart_count": self.restart_count,
            "idle_measurement_mode": self.idle_measurement_mode,
            "requested_duration_minutes": self.requested_duration_minutes,
            "auto_min_minutes": self.auto_min_minutes,
            "auto_max_minutes": self.auto_max_minutes,
        }
        if include_samples:
            data["samples"] = [sample.as_dict() for sample in self.samples]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ChargeSession":
        """Deserialize session, including the original 0.0.x fields."""
        if not data:
            return cls()
        legacy_started = data.get("session_started_at") or data.get("started_at")
        legacy_finished = data.get("session_finished_at") or data.get("finished_at")
        legacy_delivered = float(
            data.get("gross_energy_wh", data.get("delivered_energy_wh", 0.0))
        )
        return cls(
            session_id=data.get("session_id"),
            mode=str(data.get("mode", SESSION_IDLE)),
            phase=str(data.get("phase", PHASE_IDLE)),
            setup_id=data.get("setup_id"),
            battery_id=data.get("battery_id"),
            quantity=_int_or(data.get("quantity"), 1),
            ports=[str(item) for item in data.get("ports", [])],
            target_percent=_int_or(data.get("target_percent"), 50),
            target_energy_wh=_float_or_none(data.get("target_energy_wh")),
            gross_energy_wh=legacy_delivered,
            idle_energy_wh=float(data.get("idle_energy_wh", 0.0)),
            net_energy_wh=float(data.get("net_energy_wh", legacy_delivered)),
            last_raw_energy_wh=_float_or_none(
                data.get("last_raw_energy_wh", data.get("last_energy_wh"))
            ),
            current_power_w=_float_or_none(data.get("current_power_w")),
            current_net_power_w=_float_or_none(data.get("current_net_power_w")),
            current_temperature_c=_float_or_none(
                data.get("current_temperature_c")
            ),
            peak_power_w=_float_or_none(data.get("peak_power_w")),
            peak_net_power_w=_float_or_none(data.get("peak_net_power_w")),
            peak_temperature_c=_float_or_none(
                data.get("peak_temperature_c")
            ),
            idle_baseline_power_w=float(
                data.get("idle_baseline_power_w", 0.0)
            ),
            idle_measurement_ids=[
                str(item) for item in data.get("idle_measurement_ids", [])
            ],
            idle_quality=str(data.get("idle_quality", "none")),
            session_started_at=legacy_started,
            switch_on_at=data.get("switch_on_at"),
            charge_started_at=data.get("charge_started_at"),
            taper_started_at=data.get("taper_started_at"),
            candidate_end_at=data.get("candidate_end_at"),
            candidate_end_net_energy_wh=_float_or_none(
                data.get("candidate_end_net_energy_wh")
            ),
            candidate_end_gross_energy_wh=_float_or_none(
                data.get("candidate_end_gross_energy_wh")
            ),
            charge_finished_at=data.get("charge_finished_at"),
            end_detected_at=data.get("end_detected_at"),
            switch_off_at=data.get("switch_off_at"),
            session_finished_at=legacy_finished,
            last_sample_at=data.get("last_sample_at"),
            last_significant_at=data.get("last_significant_at"),
            last_significant_net_energy_wh=_float_or_none(
                data.get("last_significant_net_energy_wh")
            ),
            end_reason=data.get("end_reason"),
            valid=bool(data.get("valid", True)),
            restart_count=_int_or(data.get("restart_count"), 0),
            idle_measurement_mode=data.get("idle_measurement_mode"),
            requested_duration_minutes=_float_or_none(
                data.get("requested_duration_minutes")
            ),
            auto_min_minutes=_float_or_none(data.get("auto_min_minutes")),
            auto_max_minutes=_float_or_none(data.get("auto_max_minutes")),
            samples=[
                MeasurementSample.from_dict(item)
                for item in data.get("samples", [])
            ],
        )


def median_or_none(values: list[float]) -> float | None:
    """Return median or None."""
    return median(values) if values else None
