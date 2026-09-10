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

A calibration records the full trace beyond the first possible endpoint. The algorithm identifies a low-energy plateau, waits for a confirmation interval, and then places `charge_finished_at` back at the last significant charging point before the plateau.

`end_detected_at` remains the later timestamp at which the plateau was confirmed.

This distinction prevents confirmation time and small maintenance pulses from inflating calibrated full-charge energy or charge duration.

## Repeated measurements

The operational value for an exact profile is the median of valid current-revision or explicitly approved calibration records. Pending results, records with invalid/missing idle references and nonpositive net energies are excluded. High/medium-confidence records take precedence over low-confidence fallbacks. The integration also calculates robust spread, standard deviation, recent drift, and quality status.

Invalidating an idle source excludes dependent calibrations without erasing their results. Existing corrected records are recalculated only on explicit request, preserving prior analyses. Revoking a source's revision approval only changes eligibility for future baseline aggregation; it does not invalidate that source's historical measurements or silently rewrite previous corrections.

The quantity regression model is used only to identify implausible nonlinearity or outliers. It never replaces a direct calibration for an available quantity.

## Relative energy target

Normal charging applies a percentage to the calibrated net full-charge energy. It does not claim an exact cell state of charge because charging efficiency and the relationship between supplied energy and stored cell energy can vary over the charging curve.

The method is intended to produce a repeatable intermediate storage condition that avoids deliberately storing batteries at either fully discharged or fully charged extremes.
