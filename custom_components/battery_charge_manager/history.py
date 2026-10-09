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
    """Preserve per-channel segment boundaries before choosing display extrema.

    Dense transitions use time-bucket envelopes with time-weighted quality. The
    overview is explicitly marked and never pretends adjacent retained points
    establish continuous observations. Raw paging remains the detailed view.
    """
    if not samples:
        return []
    limit = max(24, limit)
    keys = ('power_w', 'net_power_w', 'gross_energy_wh', 'net_energy_wh',
            'temperature_c', 'meter_energy_wh', 'power_estimate_wh', 'power_energy_wh')
    valid = lambda value: isinstance(value, (int, float)) and isfinite(value) and value >= 0
    times = [datetime.fromisoformat(p.timestamp).timestamp() for p in samples]
    flags, estimates, durations, boundaries = [], [], [], {0, len(samples)-1}
    estimate = 0.0
    for i, point in enumerate(samples):
        before = samples[i-1] if i else point
        seconds = times[i]-times[i-1] if i else 0
        actual_gap = bool(i and (seconds < 0 or seconds > 120 or point.interval_quality.get('reason') in ('restart','clock_reversal','sample_gap')))
        power_gap = actual_gap or not valid(point.power_w) or not valid(before.power_w)
        held = not (point.power_report_fresh and before.power_report_fresh)
        meter_gap = actual_gap or (i and not valid(point.raw_energy_wh) and point.metering_quality.get('counter_discontinuous', False))
        if i and valid(point.raw_energy_wh) and valid(before.raw_energy_wh) and point.raw_energy_wh < before.raw_energy_wh:
            meter_gap = True
        channels = {'power': {'gap_before': bool(i and power_gap), 'held': held},
                    'meter': {'gap_before': bool(i and meter_gap), 'held': False},
                    'integration': {'gap_before': bool(i and power_gap), 'held': held}}
        flags.append(channels)
        durations.append(max(0, seconds))
        if i and (channels != flags[i-1] or point.power_report_fresh != before.power_report_fresh):
            boundaries.update((i-1,i))
        if point.power_estimate_wh is not None:
            estimate = point.power_estimate_wh
        elif point.power_integral_valid and point.power_energy_wh is not None:
            estimate = point.power_energy_wh
        elif i and not power_gap and seconds > 0:
            estimate += before.power_w*seconds/3600
        estimates.append(estimate)

    def extrema(start, stop):
        selected = {start, stop-1}
        for key in keys:
            values = [(getattr(samples[i], key), i) for i in range(start, stop) if valid(getattr(samples[i], key))]
            if values:
                selected.update((min(values)[1], max(values)[1]))
        return selected

    overview = len(boundaries) > limit//2
    indices, buckets = set(), {}
    if len(samples) <= limit:
        indices.update(range(len(samples)))
        overview = False
    else:
        if not overview:
            indices.update(boundaries)
        bucket_count = max(1, (limit-len(indices))//(2*len(keys)+2))
        # Buckets are uniform in elapsed time, not report/event count.
        span = max(1, times[-1]-times[0])
        groups = {}
        for i, value in enumerate(times):
            group = min(bucket_count-1, max(0, int((value-times[0])/span*bucket_count)))
            groups.setdefault(group, []).append(i)
        for group, members in groups.items():
            start, stop = members[0], members[-1]+1
            chosen = extrema(start, stop)
            indices.update(chosen)
            if overview:
                bucket = dict(id=group, start_at=samples[start].timestamp, end_at=samples[stop-1].timestamp,
                    fresh_seconds=0.0, held_seconds=0.0, unknown_seconds=0.0, sample_count=stop-start)
                for key in keys:
                    values = [getattr(samples[i],key) for i in range(start,stop) if valid(getattr(samples[i],key))]
                    if values:
                        bucket[key] = {'min':min(values), 'max':max(values)}
                for i in range(start,stop):
                    quality = 'unknown_seconds' if flags[i]['power']['gap_before'] else 'held_seconds' if flags[i]['power']['held'] else 'fresh_seconds'
                    bucket[quality] += durations[i]
                for i in chosen:
                    buckets[i] = bucket
    result = []
    for i in sorted(indices):
        item = samples[i]
        point = {key:value for key,value in item.as_dict().items() if key != 'provenance'}
        point['provenance'] = {key:item.provenance[key] for key in
            ('received_at','source','event_type','event_at','trigger_entity_id','new_report') if key in item.provenance}
        point.update(raw_index=i, chart_channels=flags[i],
                     chart_gap_before=flags[i]['power']['gap_before'], chart_overview=overview)
        if i in buckets:
            point['chart_bucket'] = buckets[i]
        if item.power_estimate_wh is None and item.power_w is not None:
            point['power_estimate_wh'] = estimates[i]
        result.append(point)
    return result
