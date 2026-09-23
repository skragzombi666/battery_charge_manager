"""Parallel metering and conservative source selection, without accuracy claims."""

from __future__ import annotations

from datetime import datetime
import math
from statistics import median
from typing import Any

MAX_GAP_SECONDS = 120
MAX_REPORT_AGE_SECONDS = 120
MIN_CALIBRATIONS = 3


def finite(value: Any) -> bool:
    """Accept finite nonnegative measurements, including zero."""
    return isinstance(value, (int, float)) and math.isfinite(value) and value >= 0


def advance(
    state: dict, timestamp: float, power: float | None,
    voltage: float | None, current: float | None, *,
    fresh: bool = True, restart: bool = False,
    reported_at: float | None = None, raw_energy: float | None = None,
) -> None:
    """Integrate held values, never interpolate across missing observations."""
    if not state:
        state.update(power_wh=0.0, apparent_vah=0.0, power_valid=True,
                     apparent_valid=True, max_gap_seconds=0.0, gaps=0,
                     covered_seconds=0.0, total_seconds=0.0,
                     estimate_covered_seconds=0.0, power_estimate_wh=0.0,
                     max_power_step_wh=0.0, meter_step_wh=None,
                     report_count=0, max_report_interval_seconds=0.0)
    previous_at = state.get('timestamp')
    good = finite(power) and fresh
    previous_report = state.get('last_report_at')
    if reported_at is not None:
        age = timestamp - reported_at
        good = good and 0 <= age <= MAX_REPORT_AGE_SECONDS
        if good and (previous_report is None or reported_at > previous_report):
            state['report_count'] += 1
            if previous_report is not None:
                interval = reported_at - previous_report
                state['max_report_interval_seconds'] = max(
                    state['max_report_interval_seconds'], interval)
                if interval > MAX_REPORT_AGE_SECONDS:
                    state['power_valid'] = False
            state['last_report_at'] = reported_at
        effective_interval = max(age, state['max_report_interval_seconds'])
        if good:
            state['max_power_step_wh'] = max(state['max_power_step_wh'],
                max(power or 0, state.get('previous_power') or 0) * effective_interval / 3600)
    if finite(raw_energy) and finite(state.get('last_counter')):
        step = raw_energy - state['last_counter']
        if step > 0:
            state['meter_step_wh'] = min(step, state['meter_step_wh'] or step)
    state['last_counter'] = raw_energy
    apparent = voltage * current if finite(voltage) and finite(current) else None
    if previous_at is not None:
        seconds = timestamp - previous_at
        state['max_gap_seconds'] = max(state['max_gap_seconds'], seconds)
        state['total_seconds'] += max(0, seconds)
        gap = seconds < 0 or seconds > MAX_GAP_SECONDS or restart
        if gap:
            state['gaps'] += 1
            state['power_valid'] = False
            state['apparent_valid'] = False
        elif seconds > 0:
            # Diagnostic hold estimate retains finite cached readings; freshness
            # remains a separate requirement for automatic/control eligibility.
            if finite(power) and finite(state.get('estimate_previous_power')):
                state['power_estimate_wh'] = state.get('power_estimate_wh', 0) + state['estimate_previous_power'] * seconds / 3600
                state['estimate_covered_seconds'] = state.get('estimate_covered_seconds', 0) + seconds
            if good and state.get('previous_good'):
                state['power_wh'] += state['previous_power'] * seconds / 3600
                state['covered_seconds'] += seconds
                state['max_power_step_wh'] = max(state['max_power_step_wh'], state['previous_power'] * seconds / 3600)
            else:
                state['power_valid'] = False
            if finite(apparent) and finite(state.get('previous_apparent')):
                state['apparent_vah'] += state['previous_apparent'] * seconds / 3600
            else:
                state['apparent_valid'] = False
    if good and not state.get('power_started') and not state['gaps']:
        # Leading stale OFF values are not charge measurements. Their uncovered
        # duration is still penalized against the full calibration interval.
        state['power_valid'] = True
        state['power_started'] = True
    if not good:
        state['power_valid'] = False
    if not finite(apparent):
        state['apparent_valid'] = False
    state.setdefault("power_estimate_wh", 0.0)
    state["estimate_previous_power"] = power
    state.update(timestamp=timestamp, previous_power=power if good else None,
                 previous_good=good, previous_apparent=apparent,
                 voltage_v=voltage, current_a=current, apparent_power_va=apparent)


def _time(value: str) -> float:
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()


def compare(
    samples: list, endpoint: str | None, baseline: float,
    reference_at: str | None = None,
) -> dict:
    """Use original online quality evidence, independent of trace compaction."""
    report = {'power_eligible': False, 'reason': 'no_parallel_trace',
              'meter_net_wh': None, 'power_net_wh': None,
              'apparent_energy_vah': None, 'meter_step_wh': None,
              'power_step_wh': None, 'coverage_percent': 0.0}
    if not samples or not endpoint:
        return report
    points = [p for p in samples if _time(p.timestamp) <= _time(endpoint)]
    if not points:
        return report
    first, last = points[0], points[-1]
    span = _time(last.timestamp) - _time(reference_at or first.timestamp)
    meter_gross = last.meter_energy_wh if last.meter_energy_wh is not None else last.gross_energy_wh
    report['meter_gross_wh'] = meter_gross
    report['power_gross_wh'] = last.power_energy_wh
    report['power_estimate_gross_wh'] = last.power_estimate_wh
    report['idle_energy_wh'] = max(0, baseline * span / 3600)
    report['meter_net_wh'] = max(0, meter_gross - baseline * span / 3600)
    report['power_estimate_net_wh'] = max(0, last.power_estimate_wh - baseline * span / 3600) if last.power_estimate_wh is not None else None
    report['estimate_complete'] = bool(span > 0 and (last.metering_quality.get('estimate_covered_seconds') or 0) >= span * .99)
    if last.power_energy_wh is None:
        return report
    report['power_net_wh'] = max(0, last.power_energy_wh - baseline * span / 3600)
    report['apparent_energy_vah'] = last.apparent_energy_vah
    quality = last.metering_quality
    if not quality:
        return report
    report['meter_step_wh'] = quality.get('meter_step_wh')
    covered = quality.get('covered_seconds', 0)
    report['coverage_percent'] = min(100, 100 * covered / span) if span > 0 else 0
    report['power_step_wh'] = quality.get('max_power_step_wh')
    report['max_report_interval_seconds'] = quality.get('max_report_interval_seconds')
    report['power_complete'] = bool(last.power_integral_valid and span > 0 and covered >= span * .99 and quality.get('report_count', 0) >= 2)
    if not report['power_complete']:
        report['reason'] = 'power_data_gap'
    elif report['power_net_wh'] <= 0:
        report['reason'] = 'no_power_energy'
    elif not report['meter_step_wh']:
        report['reason'] = 'counter_resolution_unknown'
    elif (quality.get('max_report_interval_seconds', float('inf')) > MAX_REPORT_AGE_SECONDS
            or not finite(report['power_step_wh'])
            or report['power_step_wh'] > report['power_net_wh'] * .05):
        report['reason'] = 'power_updates_coarse'
    else:
        report['power_eligible'] = True
        report['reason'] = 'usable'
    return report


def select_source(reports: list[dict]) -> dict:
    """Prefer a finer repeatable power path only with enough matched evidence."""
    result = {'source': 'meter', 'reason': 'insufficient_calibrations',
              'count': len(reports), 'median_net_wh': None,
              'absolute_accuracy_known': False}
    if len(reports) < MIN_CALIBRATIONS:
        return result
    # Do not silently select a favourable subset of measurements.
    if not all(r.get('power_eligible') for r in reports):
        result['reason'] = 'incomplete_power_data'
        return result
    for r in reports:
        energy, power = r.get('meter_net_wh'), r.get('power_net_wh')
        step = r.get('meter_step_wh')
        if not all(finite(v) and v > 0 for v in (energy, power, step)):
            result['reason'] = 'incomplete_power_data'
            return result
        if step / energy < .05 or r.get('power_step_wh', float('inf')) > step / 4:
            result['reason'] = 'meter_sufficiently_fine'
            return result
        if abs(power - energy) > max(2 * step, .20 * energy):
            result['reason'] = 'sources_disagree'
            return result
    values = [r['power_net_wh'] for r in reports]
    middle = median(values)
    # Full range detects outliers which MAD alone can hide in small samples.
    if (max(values) - min(values)) / middle > .15:
        result['reason'] = 'power_not_repeatable'
        return result
    result.update(source='power', reason='finer_repeatable_power', median_net_wh=middle)
    return result
