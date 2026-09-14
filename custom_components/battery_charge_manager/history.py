"""Revision applicability and bounded historical trace presentation."""

from __future__ import annotations

from math import isfinite
from copy import deepcopy
from datetime import datetime
from typing import Any

from .models import BatteryType, CalibrationRecord, ChargerSetup, IdleMeasurement, MeasurementSample

Measurement = IdleMeasurement | CalibrationRecord


def current_approval(
    record: Measurement, setup: ChargerSetup, battery: BatteryType | None = None,
) -> dict[str, Any] | None:
    """Find an unrevoked approval for this exact revision combination."""
    return next((item for item in reversed(record.revision_approvals)
                 if item.get("setup_revision") == setup.revision
                 and item.get("battery_revision") == (battery.revision if battery else None)
                 and not item.get("revoked_at")), None)


def revision_status(
    record: Measurement, setup: ChargerSetup | None, battery: BatteryType | None = None,
) -> str:
    """Classify revision eligibility independently of validity and quality."""
    if setup is None or record.setup_id != setup.setup_id:
        return "unavailable"
    if isinstance(record, CalibrationRecord):
        if battery is None or record.battery_id != battery.battery_id:
            return "unavailable"
        if not 1 <= record.quantity <= len(setup.port_labels):
            return "incompatible_quantity"
    if record.setup_revision == setup.revision and (
        not isinstance(record, CalibrationRecord)
        or (battery is not None and record.battery_revision == battery.revision)
    ):
        return "native"
    if current_approval(record, setup, battery):
        return "approved"
    return "historical"


def revision_differences(
    record: Measurement, setup: ChargerSetup | None, battery: BatteryType | None,
) -> list[dict[str, Any]]:
    """Compare original snapshots with current metadata for human review."""
    differences = []
    pairs = [("setup", record.setup_snapshot, setup)]
    if isinstance(record, CalibrationRecord):
        pairs.append(("battery", record.battery_snapshot, battery))
    for scope, original, current in pairs:
        if current is None:
            continue
        for key, value in current.as_dict().items():
            if key in {"created_at", "updated_at", "revision", "setup_id", "battery_id"}:
                continue
            if original.get(key) != value:
                differences.append({"scope": scope, "field": key,
                                    "original": original.get(key), "current": value})
    return differences


def chart_samples(samples: list[MeasurementSample], limit: int = 600) -> list[dict[str, Any]]:
    """Bound chart payload while retaining endpoints and per-bucket extrema."""
    # Reconstruct only a labelled diagnostic estimate for old records, before
    # chart thinning. Raw persisted measurements remain untouched.
    if samples and any(item.power_estimate_wh is None for item in samples):
        samples = deepcopy(samples)
        estimate = 0.0
        for i, item in enumerate(samples):
            if item.power_estimate_wh is not None:
                estimate = item.power_estimate_wh
            elif item.power_integral_valid and item.power_energy_wh is not None:
                # Trust stored cumulative evidence across chart compaction.
                estimate = item.power_energy_wh
                item.power_estimate_wh = estimate
            else:
                if i:
                    previous = samples[i - 1]
                    seconds = (datetime.fromisoformat(item.timestamp) - datetime.fromisoformat(previous.timestamp)).total_seconds()
                    if previous.power_w is not None and isfinite(previous.power_w) and previous.power_w >= 0 and 0 < seconds <= 120:
                        estimate += previous.power_w * seconds / 3600
                if item.power_w is not None:
                    item.power_estimate_wh = estimate
                    item.power_integral_valid = False
    if len(samples) <= limit:
        return [item.as_dict() for item in samples]
    keys = ("power_w", "net_power_w", "gross_energy_wh", "net_energy_wh", "temperature_c", "meter_energy_wh", "power_estimate_wh", "power_energy_wh")
    buckets = max(1, (limit - 2) // (2 * len(keys) + 2))
    indices = {0, len(samples) - 1}
    for bucket in range(buckets):
        start = bucket * len(samples) // buckets
        stop = (bucket + 1) * len(samples) // buckets
        indices.update((start, stop - 1))
        for key in keys:
            values = [(getattr(samples[i], key), i) for i in range(start, stop)
                      if getattr(samples[i], key) is not None
                      and isfinite(getattr(samples[i], key))]
            if values:
                indices.update((min(values)[1], max(values)[1]))
    return [samples[i].as_dict() for i in sorted(indices)]
