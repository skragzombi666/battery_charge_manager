"""Data models for Battery Charge Manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median
from typing import Any


@dataclass(slots=True)
class BatteryType:
    """A battery type stored in the battery library."""

    battery_id: str
    name: str
    nominal_capacity_mah: int
    technology: str
    form_factor: str
    image: dict[str, Any] | None = None
    calibrations: dict[str, list[float]] = field(default_factory=dict)

    def calibration_value(self, quantity: int) -> float | None:
        """Return the median full-charge energy for a quantity."""
        samples = self.calibrations.get(str(quantity), [])
        return median(samples) if samples else None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the battery type."""
        return {
            "battery_id": self.battery_id,
            "name": self.name,
            "nominal_capacity_mah": self.nominal_capacity_mah,
            "technology": self.technology,
            "form_factor": self.form_factor,
            "image": self.image,
            "calibrations": self.calibrations,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BatteryType":
        """Deserialize the battery type."""
        return cls(
            battery_id=data["battery_id"],
            name=data["name"],
            nominal_capacity_mah=int(data["nominal_capacity_mah"]),
            technology=data["technology"],
            form_factor=data["form_factor"],
            image=data.get("image"),
            calibrations={
                str(key): [float(value) for value in values]
                for key, values in data.get("calibrations", {}).items()
            },
        )


@dataclass(slots=True)
class ChargeSession:
    """Runtime and persistent charge session state."""

    mode: str = "idle"
    battery_id: str | None = None
    quantity: int = 1
    target_percent: int = 50
    target_energy_wh: float | None = None
    delivered_energy_wh: float = 0.0
    last_energy_wh: float | None = None
    started_at: str | None = None
    finished_at: str | None = None
    end_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize session."""
        return {
            "mode": self.mode,
            "battery_id": self.battery_id,
            "quantity": self.quantity,
            "target_percent": self.target_percent,
            "target_energy_wh": self.target_energy_wh,
            "delivered_energy_wh": self.delivered_energy_wh,
            "last_energy_wh": self.last_energy_wh,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "end_reason": self.end_reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ChargeSession":
        """Deserialize session."""
        if not data:
            return cls()
        return cls(
            mode=data.get("mode", "idle"),
            battery_id=data.get("battery_id"),
            quantity=int(data.get("quantity", 1)),
            target_percent=int(data.get("target_percent", 50)),
            target_energy_wh=data.get("target_energy_wh"),
            delivered_energy_wh=float(data.get("delivered_energy_wh", 0.0)),
            last_energy_wh=data.get("last_energy_wh"),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            end_reason=data.get("end_reason"),
        )
