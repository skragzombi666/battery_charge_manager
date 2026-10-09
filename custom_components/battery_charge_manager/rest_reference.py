"""Time-weighted full-battery references and review-only endpoint proposals.

The supplied power is held on [previous, current). Staleness is disclosed;
missing observations and restart intervals are never bridged.
"""
from datetime import datetime
from .metering import MAX_GAP_SECONDS, finite

WARMUP_SECONDS = 300
REFERENCE_SECONDS = 1800
WINDOW_SECONDS = 300


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()


def profile_key(setup_id, setup_revision, battery_id, battery_revision, quantity, ports):
    return [setup_id, setup_revision, battery_id, battery_revision, quantity, list(ports)]


def intervals(samples):
    for before, after in zip(samples, samples[1:]):
        start, end = timestamp(before.timestamp), timestamp(after.timestamp)
        valid = (0 < end-start <= MAX_GAP_SECONDS and finite(before.power_w)
                 and finite(after.power_w) and after.interval_quality.get('reason') not in
                 ('restart', 'clock_reversal', 'sample_gap', 'invalid_power'))
        yield start, end, before.power_w, valid, before.power_report_fresh and after.power_report_fresh


def window(observations, start, end):
    covered = fresh = energy = 0.0
    distribution = {}
    invalid = False
    for a, b, power, valid, accepted in observations:
        seconds = min(b, end) - max(a, start)
        if b < a and start <= a <= end:
            invalid = True
        if seconds <= 0:
            continue
        if not valid:
            invalid = True
            continue
        covered += seconds
        fresh += seconds if accepted else 0
        energy += power * seconds
        distribution[power] = distribution.get(power, 0) + seconds
    return dict(complete=not invalid and abs(covered-(end-start)) < 1e-5,
                mean_power_w=energy/covered if covered else None,
                covered_seconds=covered, fresh_seconds=fresh,
                held_seconds=covered-fresh, distribution=distribution)


def assess(samples, confirmed_at, end_at):
    report = dict(eligible=False, reason='not_confirmed')
    if not confirmed_at or not end_at:
        return report
    start = timestamp(confirmed_at) + WARMUP_SECONDS
    end = start + REFERENCE_SECONDS
    report.update(analysis_start_at=datetime.fromtimestamp(start, tz=datetime.fromisoformat(confirmed_at).tzinfo).isoformat(),
                  analysis_end_at=datetime.fromtimestamp(end, tz=datetime.fromisoformat(confirmed_at).tzinfo).isoformat())
    if timestamp(end_at) < end:
        return {**report, 'reason': 'window_incomplete'}
    observations = list(intervals(samples))
    whole = window(observations, start, end)
    report.update({k:v for k,v in whole.items() if k not in ('distribution', 'complete')})
    if not whole['complete']:
        return {**report, 'reason': 'recording_gap'}
    block_means = [window(observations, start+i*600, start+(i+1)*600)['mean_power_w'] for i in range(3)]
    levels = sorted(whole['distribution'])
    steps = [b-a for a,b in zip(levels, levels[1:]) if b-a > 1e-9]
    step = min(steps) if steps else None
    tolerance = max(.03, step/2 if step else .03)
    cumulative = 0
    median = levels[-1]
    for power in levels:
        cumulative += whole['distribution'][power]
        if cumulative >= REFERENCE_SECONDS/2:
            median = power
            break
    stable = max(block_means)-min(block_means) <= 2*tolerance + 1e-9
    report.update(eligible=stable, reason='usable' if stable else 'unstable_blocks',
                  block_means_w=block_means, observed_step_w=step,
                  resolution_known=bool(step), tolerance_w=tolerance,
                  upper_power_w=max(block_means)+tolerance, median_power_w=median,
                  power_distribution=[{'power_w':p, 'seconds':whole['distribution'][p]} for p in levels])
    return report


def suggest(samples, reference, previous=None):
    """Require an observed load, then four non-overlapping low 5-minute windows.

    The proposal stays provisional; later load or an invalid window withdraws it.
    Window boundaries are original stored observations, never invented timestamps.
    """
    result = dict(status='no_reference', endpoint_at=None, confirmed_windows=0)
    if not reference or not reference.get('eligible') or len(samples) < 2:
        return result
    observations = list(intervals(samples))
    upper, tolerance = reference['upper_power_w'], reference['tolerance_w']
    high_seen, lows, anchor, start_point = False, 0, None, samples[0]
    result['status'] = 'waiting_for_load'
    last_end = timestamp(start_point.timestamp)
    for point in samples[1:]:
        end = timestamp(point.timestamp)
        if end-last_end < WINDOW_SECONDS:
            continue
        block = window(observations, last_end, end)
        if not block['complete']:
            high_seen, lows, anchor = False, 0, None
        elif block['mean_power_w'] > upper+tolerance:
            high_seen, lows, anchor = True, 0, None
        elif high_seen and block['mean_power_w'] <= upper:
            if not lows:
                anchor = start_point.timestamp
            lows += 1
        else:
            lows, anchor = 0, None
        start_point, last_end = point, end
    # A renewed instantaneous high must also withdraw a pending proposal before
    # the next complete window. Normal residual pulses remain below upper+tol.
    if result is not None and lows and finite(samples[-1].power_w) and samples[-1].power_w > upper+tolerance:
        # Evaluate partial-window mean; one short pulse is not a new charge.
        partial = window(observations, last_end, timestamp(samples[-1].timestamp))
        if partial['covered_seconds'] and (not partial['complete'] or partial['mean_power_w'] > upper+tolerance):
            lows, anchor = 0, None
    result.update(status='suggested' if lows >= 4 else 'candidate' if lows else 'waiting_for_rest' if high_seen else 'waiting_for_load',
                  endpoint_at=anchor, confirmed_windows=lows,
                  upper_power_w=upper, tolerance_w=tolerance)
    return result
