# Battery Charge Manager 0.4.0

## Three measurement curves

Live and historical charts display W, Wh from the cumulative counter, and Wh
integrated from W over time. Both energy curves share a scale and, when idle
correction is available, subtract the same idle contribution. Gross views leave
both paths uncorrected.

The W/time curve can also reveal disagreements when reports are incomplete:
finite cached watt readings are held over regular sampling intervals for a
diagnostic estimate. A cumulative curve containing uncertain intervals is dashed.
Missing intervals over 120 seconds and restarts are not filled. The comparison
separately identifies energy from accepted intervals, which is only a partial sum
when coverage is incomplete. The held estimate never supplies a charge target.
It may veto a grossly inconsistent counter result; it cannot establish which
device is correct. Old traces can be estimated before chart thinning where enough
raw W samples remain. Missing samples cannot be recovered, and stored valid
parallel integrals take precedence over reconstructed estimates.

## Source setting

In **Management → Settings → Energy source**, administrators can choose:

| Mode | Behaviour |
| --- | --- |
| Automatic per calibration (default) | Each calibration compares its own data and selects the practically better-resolved usable source. No three-run prerequisite. |
| Always Wh counter | Uses the counter when its recorded positive energy passes the comparison check. |
| Always W/time | Requires a configured active-power sensor and a complete accepted integral. Can explicitly use this path despite disagreement with the counter. |

Fixed modes never fall back silently. With no usable calibration for the selected
source, charging cannot start. Both measurement paths continue to be recorded in
every mode. Voltage × RMS current remains diagnostic apparent energy only.

The comparison is a data-quality decision, not a measurement of absolute accuracy:

- Accepted W/time data require at least 99% coverage of the whole interval, at
  least two fresh reports, and no invalid integral. The existing 120-second
  maximum sample-gap/report-age limits remain in force. Repeatedly reading a
  cached Home Assistant value does not prove that the device is communicating.
- Automatic mode prefers complete W/time when the observed counter step is at
  least 5% of the run's meter energy and the W/time step is at most one quarter
  of that counter step. Otherwise it retains a usable counter.
- A disagreement exceeding the larger of two observed counter steps and 20% of
  the larger energy excludes automatic/counter use. The comparison may use a
  diagnostic hold estimate only when that estimate covers at least 99% of the
  interval. A manual W/time setting still requires complete accepted data.
- Repeat calibrations remain useful for checking variation. One usable run gives
  a provisional profile, not a stable or accuracy-certified result.

## Calibration and charging consistency

Calibration records retain their completion-time mode, chosen source and reason.
The details also show the effective source for future charge targets under the
current setting. Changing settings can re-evaluate source eligibility without
rewriting raw samples, original revisions or the recorded decision. Explicit idle
reanalysis retains the record's original mode and audits the previous analysis.

For one exact setup, battery and quantity, only values from the same chosen source
are combined into a target. High/medium-confidence usable records take precedence
over lower-confidence fallbacks. In automatic mode, the most recent calibration
in that eligible group determines the source; records choosing the other source
remain visible with a separate non-use reason. Quantities are not substituted.
Each charge freezes its source and matching target at start. Settings changes
during that charge do not change either value. Existing interruption, restart and
timeout checks remain active.

New calibrations with a power sensor confirm completion through 20 continuous
minutes of fresh net power at or below the larger of 0.12 W and 5% of peak net
power. The endpoint is the first sample of that confirmed tail. Active watt
readings above this threshold prevent completion even if the Wh counter stops
advancing. A loss of fresh reports interrupts confirmation. Calibrations without
a power sensor retain the counter-plateau method.

## Update and retained data

Update through HACS and restart Home Assistant when no charging session is active.
The panel and integration report 0.4.0; new analyses have algorithm version 0.4.0.
Existing raw data, comments, revision approvals and audit history are retained.
Old calibrations without parallel evidence remain meter-only candidates in meter
or automatic mode. Export includes the source setting, decisions, original meter
values and diagnostic estimate fields where recorded. Older traces are not
silently promoted to complete accepted W/time data.

Changes are covered by automated backend and frontend regression tests. Real
device report cadence and detection timing still need validation with new
calibrations and the USB reference meter.
