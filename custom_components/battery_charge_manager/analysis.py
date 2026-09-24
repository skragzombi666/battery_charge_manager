"""Evidence-based input-energy analysis, independent of nominal cell capacity.

The transition detector is a conservative, documented heuristic for a mains-side
power curve. It does not measure cell state of charge. Missing observations are
never bridged for confirmation. Reported/cached integration remains labelled.
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from datetime import datetime
import math
from typing import Any

from . import metering

CANDIDATE_SECONDS = 300
CONFIRM_SECONDS = 1200
MIN_COVERAGE = .99


def timestamp(point) -> float:
    return datetime.fromisoformat(point.timestamp.replace('Z', '+00:00')).timestamp()


def recent_samples(samples, start: float, end: float):
    """Include the held value at the left boundary without scanning the history."""
    left = max(0, bisect_right(samples, start, key=timestamp) - 1)
    right = bisect_right(samples, end, key=timestamp)
    return samples[left:right]


def intervals(samples, start: float, end: float, baseline: float = 0):
    points = recent_samples(samples, start, end)
    for previous, current in zip(points, points[1:]):
        left, right = timestamp(previous), timestamp(current)
        if not 0 < right-left <= metering.MAX_GAP_SECONDS:
            continue
        if (not previous.power_report_fresh or not current.power_report_fresh
                or not metering.finite(previous.power_w) or not metering.finite(current.power_w)):
            continue
        evidence = current.interval_quality
        if evidence and evidence.get('accepted_seconds', 0) < (right-left) * MIN_COVERAGE:
            continue
        duration = max(0, min(end, right) - max(start, left))
        if duration:
            yield (max(start, left), min(end, right), max(0, previous.power_w-baseline))


def window_statistics(samples, start: float, end: float, baseline: float = 0) -> dict:
    values = list(intervals(samples, start, end, baseline))
    covered = sum(b-a for a,b,_ in values)
    span = max(0, end-start)
    energy_ws = sum((b-a)*power for a,b,power in values)
    mean = energy_ws/covered if covered else None
    variance = (sum((b-a)*(power-mean)**2 for a,b,power in values)/covered) if covered else None
    cumulative, middle = 0.0, None
    for a,b,power in sorted(values, key=lambda value: value[2]):
        cumulative += b-a
        if cumulative >= covered/2:
            middle = power
            break
    return dict(span_seconds=span, covered_seconds=covered,
                coverage_percent=min(100, covered/span*100) if span else 0,
                mean_power_w=mean, median_power_w=middle,
                stdev_power_w=math.sqrt(variance) if variance is not None else None,
                accepted_energy_wh=energy_ws/3600, intervals=values)


def regime_transition(samples, reference: float | None, baseline: float,
                      previous: dict | None = None) -> dict:
    """Confirm a fresh, sustained low-input regime after a demonstrated main load.

    A five-minute window starts confirmation. Twenty minutes in total must be
    supported, with >=99% covered time. Mean <= max(.12 W, 8% of main); >=98% of
    time <= max(.3 W, 25% of main). Higher pulses may last <=10 s individually
    and contribute <=0.5% of the main-level energy over the window. Energy above
    the mean limit is additionally bounded to half that limit's window energy.
    These limits are independent of battery nominal energy and elapsed charge
    expectations. Return the evidence, not a cell-full assertion.
    """
    result: dict[str, Any] = {'candidate_at': None, 'confirmed': False,
                              'method': 'sustained_low_input', 'reason': 'no_main_reference'}
    if not metering.finite(reference) or reference < .5 or len(samples) < 3:
        return result
    now = timestamp(samples[-1])
    previous = previous or {}
    candidate = previous.get('candidate_at')
    start = (datetime.fromisoformat(candidate.replace('Z', '+00:00')).timestamp()
             if candidate else now - CANDIDATE_SECONDS)
    if start < timestamp(samples[0]) or now-start < CANDIDATE_SECONDS*.99:
        result['reason'] = 'insufficient_window'
        return result
    stats = window_statistics(samples, start, now, baseline)
    mean_limit = max(.12, reference*.08)
    pulse_limit = max(.3, reference*.25)
    high_seconds, high_ws, excess_ws, longest_high, continuous_high = 0., 0., 0., 0., 0.
    last_right = None
    for left, right, power in stats['intervals']:
        seconds = right-left
        excess_ws += seconds*max(0, power-mean_limit)
        if power > pulse_limit:
            high_seconds += seconds
            high_ws += seconds*power
            continuous_high = continuous_high+seconds if last_right == left else seconds
            longest_high = max(longest_high, continuous_high)
        else:
            continuous_high = 0
        last_right = right
    span = stats['span_seconds']
    result.update({key: value for key,value in stats.items() if key != 'intervals'})
    result.update(reference_power_w=reference, mean_limit_w=mean_limit,
                  pulse_limit_w=pulse_limit, high_seconds=high_seconds,
                  high_pulse_energy_wh=high_ws/3600, excess_energy_wh=excess_ws/3600,
                  longest_high_seconds=longest_high, confirmation_seconds=CONFIRM_SECONDS)
    if stats['coverage_percent'] < MIN_COVERAGE*100:
        result['reason'] = 'incomplete_tail'
        return result
    if (stats['mean_power_w'] is None or stats['mean_power_w'] > mean_limit
            or high_seconds > span*.02 or longest_high > 10
            or high_ws > reference*span*.005
            or excess_ws > mean_limit*span*.5):
        result['reason'] = 'renewed_or_substantial_load'
        return result
    if not candidate:
        # Anchor to a real stored low-power point, not an interpolated energy.
        index = bisect_left(samples, start, key=timestamp)
        while index < len(samples) and (samples[index].power_w or 0)-baseline > pulse_limit:
            index += 1
        if index >= len(samples):
            return result
        candidate = samples[index].timestamp
        start = timestamp(samples[index])
    result.update(candidate_at=candidate, confirmed=now-start >= CONFIRM_SECONDS,
                  reason='confirmed_low_input' if now-start >= CONFIRM_SECONDS else 'confirming_low_input',
                  elapsed_seconds=now-start)
    return result


def _summary(samples, endpoint, baseline, reference_at):
    result = metering.compare(samples, endpoint, baseline or 0, reference_at)
    if baseline is None:
        for key in ('meter_net_wh', 'power_net_wh', 'power_estimate_net_wh',
                    'idle_energy_wh', 'power_idle_energy_wh', 'estimate_idle_energy_wh'):
            result[key] = None
    result['idle_correction_known'] = baseline is not None
    return result


def energy_segments(samples, endpoint: str | None, baseline: float | None,
                    nominal: float | None, quantity: int = 1,
                    reference_at: str | None = None) -> dict:
    """Cumulative endpoint differences, never re-integrated compacted samples.

    Post-charge is the energy after the selected/observed boundary, not proof
    that all of it was idle waste. Unknown endpoints remain unknown. A partial
    integral's idle correction follows its own accepted time interval.
    """
    total = _summary(samples, samples[-1].timestamp if samples else None, baseline, reference_at)
    charge, post = None, None
    if samples and endpoint:
        end = datetime.fromisoformat(endpoint.replace('Z', '+00:00')).timestamp()
        if timestamp(samples[0]) <= end <= timestamp(samples[-1]):
            charge = _summary(samples, endpoint, baseline, reference_at)
            post = {}
            for source in ('meter', 'power', 'power_estimate'):
                key = source+'_gross_wh'
                a, b = total.get(key), charge.get(key)
                post[key] = max(0, a-b) if metering.finite(a) and metering.finite(b) else None
            for key in ('span_seconds', 'accepted_seconds', 'estimate_seconds', 'idle_energy_wh',
                        'power_idle_energy_wh', 'estimate_idle_energy_wh'):
                a,b = total.get(key), charge.get(key)
                post[key] = max(0,a-b) if metering.finite(a) and metering.finite(b) else None
            for source, idle in (('meter', 'idle_energy_wh'), ('power', 'power_idle_energy_wh'),
                                 ('power_estimate', 'estimate_idle_energy_wh')):
                gross, correction = post.get(source+'_gross_wh'), post.get(idle)
                post[source+'_net_wh'] = max(0,gross-correction) if metering.finite(gross) and metering.finite(correction) else None
            duration = post.get('span_seconds') or 0
            post['coverage_percent'] = min(100, (post.get('accepted_seconds') or 0)/duration*100) if duration else 0
            post['idle_correction_known'] = baseline is not None
    total_nominal = nominal*quantity if metering.finite(nominal) and nominal > 0 and quantity > 0 else None
    input_energy = charge.get('power_estimate_net_wh') if charge else None
    if input_energy is None and charge:
        input_energy = charge.get('meter_net_wh')
    ratio = input_energy/total_nominal if metering.finite(input_energy) and total_nominal else None
    return {
        'version': 1, 'basis': 'input_energy_not_cell_capacity', 'endpoint_at': endpoint,
        'total': total, 'charge': charge, 'post_charge': post,
        'nominal': {'per_battery_wh': nominal, 'quantity': quantity, 'total_wh': total_nominal,
                    'input_to_nominal_ratio': ratio, 'ratio_basis': 'selected_charge_input_not_efficiency',
                    'warning': 'unusually_high_input_ratio' if ratio is not None and ratio > 2 else None},
    }


def idle_assessment(samples, start: float, end: float, minimum_seconds: float = 1800) -> dict:
    """Time-weighted gross input mean; temporal coverage and block repeatability."""
    stats = window_statistics(samples, start+300, end)
    duration = max(0,end-start)
    length = max(0,end-start-300)
    blocks = [window_statistics(samples, start+300+i*length/3, start+300+(i+1)*length/3)
              for i in range(3)] if length else []
    means = [b['mean_power_w'] for b in blocks if b['mean_power_w'] is not None]
    complete = stats['coverage_percent'] >= 99 and all(b['coverage_percent'] >= 99 for b in blocks)
    stable = bool(len(means) == 3 and max(means)-min(means) <= max(.03, (stats['mean_power_w'] or 0)*.1))
    reliable = bool(complete and stable and duration >= minimum_seconds and len(samples) >= 12)
    return dict(average_power_w=stats['mean_power_w'] or 0,
                median_power_w=stats['median_power_w'], stdev_power_w=stats['stdev_power_w'],
                resolution_wh=None, below_detection_limit=False, upper_bound_power_w=None,
                reliable=reliable, confidence='high' if reliable else 'low', stable=stable,
                sample_count=len(samples), baseline_method='time_weighted_power',
                baseline_coverage_percent=stats['coverage_percent'], block_means_w=means)


def checkpoint_segments(raw: dict, nominal: float | None = None, quantity: int = 1) -> dict:
    """Display saved aggregate evidence without fabricating raw observations.

    For legacy stopped runs the recovery index has no hydrated curve. These
    values are a checkpoint summary, not a newly measured endpoint.
    """
    m = raw.get('metering') or {}
    baseline = raw.get('idle_baseline_power_w')
    span = m.get('total_seconds') or 0
    accepted = m.get('covered_seconds') or 0
    estimated = m.get('estimate_covered_seconds') or 0
    report = {'summary_origin': 'saved_run_checkpoint', 'span_seconds': span,
        'accepted_seconds': accepted, 'estimate_seconds': estimated,
        'coverage_percent': min(100,accepted/span*100) if span else 0,
        'power_complete': bool(m.get('power_valid') and span > 0 and accepted >= span*.99),
        'idle_correction_known': baseline is not None, 'reason': 'retained_attempt'}
    for source, field, duration, idlekey in (
        ('meter','meter_wh',span,'idle_energy_wh'),
        ('power','power_wh',accepted,'power_idle_energy_wh'),
        ('power_estimate','power_estimate_wh',estimated,'estimate_idle_energy_wh')):
        value = m.get(field)
        if source == 'meter' and value is None and raw.get('energy_source','meter') == 'meter':
            value = raw.get('gross_energy_wh')
        correction = baseline*duration/3600 if metering.finite(baseline) else None
        report[source+'_gross_wh'] = value
        report[idlekey] = correction
        report[source+'_net_wh'] = max(0,value-correction) if metering.finite(value) and correction is not None else None
    summary = energy_segments([],None,baseline,nominal,quantity)
    summary['total'] = report
    return summary
