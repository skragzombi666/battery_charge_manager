"""Per-calibration energy decisions and independently observed charge endpoints."""
from datetime import datetime
from .metering import finite, MAX_GAP_SECONDS

MODES = ('auto', 'meter', 'power')


def choose(report: dict, mode: str) -> dict:
    """Choose within one run. Resolution does not establish absolute accuracy."""
    if mode not in MODES:
        raise ValueError('Unknown energy source mode')
    meter, power = report.get('meter_net_wh'), report.get('power_net_wh')
    good_meter = finite(meter) and meter > 0
    good_power = (report.get('power_complete', report.get('power_eligible', False))
                  and finite(power) and power > 0)
    result = dict(mode=mode, source=None, reason='incomplete_power_data',
                  absolute_accuracy_known=False)
    if mode == 'power':
        if good_power:
            result.update(source='power', reason='forced_power')
        return result
    # No observed counter increment is not contradictory positive evidence.
    # Automatic fallback still requires full fresh coverage and useful time
    # resolution; held estimates never qualify. A forced meter stays forced.
    meter_gross = report.get('meter_gross_wh', meter)
    power_step = report.get('power_step_wh')
    report_interval = report.get('max_report_interval_seconds', 0)
    if (mode == 'auto' and finite(meter_gross) and meter_gross == 0
            and good_power and finite(power_step) and power_step <= power * .05
            and finite(report_interval) and report_interval <= MAX_GAP_SECONDS):
        result.update(source='power', reason='counter_not_advancing')
        return result
    # A fresh, complete disagreement or a strongly conflicting held estimate
    # excludes meter/automatic use. An explicit power choice may ignore the meter.
    step = report.get('meter_step_wh') or 0
    estimate = report.get('power_estimate_net_wh')
    comparison = power if good_power else estimate if report.get('estimate_complete') else None
    if finite(comparison) and comparison > 0 and finite(meter):
        if abs(comparison - meter) > max(2 * step, .20 * max(meter, comparison)):
            result['reason'] = 'sources_disagree'
            return result
    if not good_meter:
        result['reason'] = 'no_meter_energy'
        return result
    result.update(source='meter', reason='forced_meter' if mode == 'meter' else 'incomplete_power_data')
    if mode == 'meter':
        return result
    power_step = report.get('power_step_wh')
    if (good_power and step > 0 and step / meter >= .05
            and finite(power_step) and power_step <= step / 4):
        result.update(source='power', reason='finer_power_single_run')
    elif good_power:
        result['reason'] = 'meter_sufficiently_fine'
    return result


def time(value: str) -> float:
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()


def power_endpoint(samples: list, baseline: float, threshold: float,
                   confirmation_seconds: float) -> tuple:
    """Find the start of an uninterrupted fresh low-power tail; never a counter step."""
    if not samples:
        return None, False
    tail = []
    later = None
    for sample in reversed(samples):
        if (not finite(sample.power_w) or not sample.power_report_fresh
                or max(0, sample.power_w - baseline) > threshold):
            break
        if later is not None and not 0 < time(later.timestamp) - time(sample.timestamp) <= MAX_GAP_SECONDS:
            break
        tail.append(sample)
        later = sample
    if not tail:
        return None, False
    endpoint = tail[-1]
    span = time(samples[-1].timestamp) - time(endpoint.timestamp)
    return endpoint, len(tail) >= 3 and span >= confirmation_seconds
