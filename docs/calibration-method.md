# Calibration method

## Measurand

Battery Charge Manager does not directly measure electrochemical cell capacity or state of charge. It measures the mains-side energy consumed by a defined charging arrangement under a defined operating method.

A calibration therefore applies only to the exact combination of:

- charging-setup revision;
- battery-type revision;
- battery quantity;
- fixed port allocation;
- defined initial battery condition.

An administrator may explicitly approve a historical record for the exact current setup/battery revisions after reviewing the differences and confirming equivalent conditions. Original snapshots and revisions remain recorded; quantity and port allocation are not reassigned.

## Idle-power correction

Let:

- `P_idle` be the aggregated idle power of the setup;
- `t` be elapsed charging time;
- `E_gross` be cumulative mains-side energy.

The estimated idle contribution is:

`E_idle = P_idle × t`

The operational calibration value is:

`E_net = E_gross − E_idle`

All hardware-dependent conversion, cable, and charging-electronics losses that occur under load remain part of the operational profile. This is intentional: normal charging uses the same physical arrangement.

## Idle measurement quality

A separate idle measurement is performed with the complete setup connected and powered but without batteries.

The automatic mode requires:

- a minimum duration;
- enough samples;
- stable estimates across sequential windows;
- enough accumulated energy relative to sensor resolution, or a sufficiently low calculated upper bound when no energy step is observed.

Valid current-revision or explicitly approved measurements are combined using their median. Reliable measured estimates take priority over below-detection results; censored results are not treated as measured zeroes. If all reliable results are below detection, zero is used as an explicitly indicated lower bound. Conflicting measurements produce an unstable aggregate and cannot supply correction.

Without a usable baseline, calibration may still record a gross trace but its idle correction remains pending and its result cannot supply a charge target. A new usable baseline automatically corrects applicable pending traces. Normal charging requires a usable baseline and an applicable corrected calibration.

## Retrospective endpoint

A calibration records the full trace beyond the first possible endpoint. Since
0.4.0, new calibrations with a power sensor require 20 continuous minutes of fresh
low-power observations. The threshold is the larger of 0.12 W and 5% of peak net
power. `charge_finished_at` is placed at the start of this low-power tail. A flat
coarse Wh counter alone cannot finish such a calibration. Missing reports interrupt
confirmation; the maximum session duration still applies. Meter-only calibrations
retain the energy-plateau method.

`end_detected_at` remains the later timestamp at which the plateau was confirmed.

This distinction prevents confirmation time and small maintenance pulses from inflating calibrated full-charge energy or charge duration.

## Repeated measurements

The operational value for an exact profile is the median of valid current-revision
or explicitly approved calibration records using the same selected source.
Pending results, records with invalid/missing idle references, unusable source
data and nonpositive energies for the selected source are excluded.
High/medium-confidence usable records take precedence over low-confidence
fallbacks. Automatic mode uses the source of the most recent eligible calibration
in that group, then combines only records choosing that source. The integration
also calculates robust spread, standard deviation, recent drift, and quality status.

See [source selection in 0.4.0](version-0.4.0.md) for fixed modes, quality gates,
and the distinction between accepted integration and diagnostic held estimates.

Invalidating an idle source excludes dependent calibrations without erasing their results. Existing corrected records are recalculated only on explicit request, preserving prior analyses. Revoking a source's revision approval only changes eligibility for future baseline aggregation; it does not invalidate that source's historical measurements or silently rewrite previous corrections.

The quantity regression model is used only to identify implausible nonlinearity or outliers. It never replaces a direct calibration for an available quantity.

## Relative energy target

Normal charging applies a percentage to the calibrated net full-charge energy. It does not claim an exact cell state of charge because charging efficiency and the relationship between supplied energy and stored cell energy can vary over the charging curve.

The method is intended to produce a repeatable intermediate storage condition that avoids deliberately storing batteries at either fully discharged or fully charged extremes.
