"""Power-curve phase hints; independent of energy totals and charge termination."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from .const import PHASE_MAIN_CHARGE, PHASE_TAPER
from .metering import MAX_GAP_SECONDS, finite

MAIN_WINDOW_SECONDS = 300
RECOVERY_WINDOW_SECONDS = 120
TAPER_RATIO = 0.60
RECOVERY_RATIO = 0.80
TRACKING_VERSION = 1


def _window(samples: list, start: datetime, end: datetime) -> list[tuple[float, float]]:
    """Weight fresh held values by elapsed seconds, not by event counts."""
    result = []
    for previous, current in zip(samples, samples[1:]):
        left = datetime.fromisoformat(previous.timestamp.replace('Z', '+00:00'))
        right = datetime.fromisoformat(current.timestamp.replace('Z', '+00:00'))
        if right < start or left > end:
            continue
        if (not 0 < (right - left).total_seconds() <= MAX_GAP_SECONDS
                or not previous.power_report_fresh or not current.power_report_fresh
                or not finite(previous.net_power_w) or not finite(current.net_power_w)):
            continue
        seconds = (min(right, end) - max(left, start)).total_seconds()
        if seconds > 0:
            result.append((previous.net_power_w, seconds))
    return result


def _median(values: list[tuple[float, float]]) -> float:
    halfway = sum(seconds for _, seconds in values) / 2
    cumulative = 0.0
    for power, seconds in sorted(values):
        cumulative += seconds
        if cumulative >= halfway:
            return power
    return 0.0


def update(session: Any, now: datetime) -> None:
    """Learn a sustained load and use hysteresis for reversible taper hints.

    Five minutes of fresh main-load evidence precede a sustained reduction.
    Individual inrush peaks, pre-start zeros and bursts of events are not a
    reference. This does not infer cell voltage, state of charge or charge end.
    """
    if not session.charge_started_at:
        return
    state = session.phase_tracking
    if state.get('version') != TRACKING_VERSION:
        # A v0.4.0 startup latch is not evidence of an actual taper. Historical
        # calibration records are untouched; only an active session is repaired.
        state.clear()
        state['version'] = TRACKING_VERSION
        session.taper_started_at = None
        if session.phase == PHASE_TAPER and not session.candidate_end_at:
            session.phase = PHASE_MAIN_CHARGE
    started = datetime.fromisoformat(session.charge_started_at.replace('Z', '+00:00'))
    if (now - started).total_seconds() < MAIN_WINDOW_SECONDS:
        return
    start = now - timedelta(seconds=MAIN_WINDOW_SECONDS)
    # Do not include the off/initialization samples before detected charge start.
    samples = [s for s in session.samples
               if started <= datetime.fromisoformat(s.timestamp.replace('Z', '+00:00')) <= now]
    values = _window(samples, start, now)
    covered = sum(seconds for _, seconds in values)
    current = session.current_net_power_w
    if covered < MAIN_WINDOW_SECONDS * .99 or not finite(current):
        return
    level = _median(values)
    stable = sum(seconds for power, seconds in values
                 if level * .8 <= power <= level * 1.2) >= covered * .8
    reference = state.get('reference_power_w', 0.0)
    if stable and level >= .5:
        reference = max(reference, level)
        state['reference_power_w'] = reference
    if reference < .5:
        return
    if session.taper_started_at:
        recovery = _window(samples, now - timedelta(seconds=RECOVERY_WINDOW_SECONDS), now)
        duration = sum(seconds for _, seconds in recovery)
        high = sum(seconds for power, seconds in recovery if power >= reference * RECOVERY_RATIO)
        if (duration >= RECOVERY_WINDOW_SECONDS * .99
                and high >= duration * .8 and current >= reference * RECOVERY_RATIO):
            session.taper_started_at = None
            if session.phase == PHASE_TAPER and not session.candidate_end_at:
                session.phase = PHASE_MAIN_CHARGE
    elif (current <= reference * TAPER_RATIO
          and sum(seconds for power, seconds in values
                  if power <= reference * TAPER_RATIO) >= covered * .8):
        session.taper_started_at = start.isoformat()
        if not session.candidate_end_at:
            session.phase = PHASE_TAPER
