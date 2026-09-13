# Battery Charge Manager 0.2.0

## Parallel measurement and automatic source selection

Every new calibration records three parallel paths where sensors are available:

1. The existing cumulative energy meter (Wh).
2. Active-power integration (Wh), using the last observed W value over time.
3. Voltage × RMS current integrated as apparent energy (VAh), diagnostic only.

The third path is not real energy and is never selected for charging. Display
resolution, repeatability and coverage are measurable; absolute accuracy and
actual electrochemical state of charge are not established by this comparison.

### Updating and using existing data

Install 0.2.0 via HACS and restart Home Assistant with no charge in progress.
Existing meter-based calibrations and history remain intact. They continue to
work. Older traces are not retroactively treated as complete power recordings.
Three new qualifying calibrations for an exact setup/battery revision, quantity
and fixed port allocation are required before automatic power selection.

Configured power sensors are used automatically. Optional voltage/current
selectors are available under charging setups. When blank, available unambiguous
RMS voltage/current sensors belonging to the same HA device as the energy sensor
are selected at session start. Their IDs are retained in the session audit.
Disabled or ambiguous entities are not guessed. Enable and explicitly select the
appropriate diagnostic entities if automatic detection does not resolve them.
Adding/changing explicit diagnostic sensors creates a setup revision, as other
technical setup changes do. No extra hardware or diagnostics are required to
compare the cumulative meter and active-power paths.

### Selection policy

Selection operates on the same eligible/trusted profile records as calibration.
Older records without parallel evidence remain meter-only. All parallel records
in that candidate set must qualify; failed coverage records are not silently
removed to manufacture a favourable comparison.

Power integration is selected only when:

- at least three matching parallel calibrations are available;
- original online records show >=99% temporal coverage to the endpoint;
- sampling gaps and power-report intervals/ages do not exceed 120 seconds;
- at least two actual power reports were observed, and the largest temporal
  energy increment is <=5% of calibrated power energy;
- the smallest observed positive counter increment is >=5% of meter energy,
  and the power temporal increment is at most one quarter of that counter step;
- the paths differ by no more than the larger of two observed counter steps or
  20% of meter energy;
- the full range of integrated calibration energies is <=15% of their median.

These are conservative operational heuristics, not certified uncertainty bounds.
A positive counter increment is an observed step, not proof of internal hardware
resolution. The meter remains selected when evidence is insufficient or conflicting.

The selected source, reference IDs and target are frozen at charge start. Power
control uses the median of power-derived calibration energies, with the same idle
subtraction window as live power integration. It never uses a meter-derived target
for a power-derived live count. Quantity models are hidden when their profiles use
mixed sources. There is no automatic source switch during an active charge.

### Reliability

An old OFF-state power report may wait up to 120 seconds for the first fresh report;
this leading uncovered interval remains part of the coverage assessment. After
power integration starts, stale/missing power data or a sampling gap abort a
power-controlled charge. A Home Assistant restart aborts power-controlled charging
because power during downtime is unknown; meter-controlled sessions retain their
existing restart accounting. Calibration can resume on the meter, but its interrupted
power path cannot qualify. Counter rollback and the existing safety checks still abort.

Coverage, report cadence and observed counter resolution are accumulated online
and retained per sample. Thinning a long chart does not create artificial gaps or
change these quality facts. Idle reanalysis preserves the prior comparison in its
audit record and applies the same switch-on reference to both paths.

### Interface

Live measurements have an expandable comparison showing meter Wh, integrated W
in Wh and diagnostic VAh. Calibration details show same-endpoint net energies,
observed counter step, coverage and eligibility reason. The calibration quality
panel identifies the chosen source and explains why it was selected. Live charging
shows its frozen source. Individual historical sample readouts include the extra
measurements. Missing older data are explicitly labelled.

## Validation

Python regression tests cover integration math, coarse-meter selection, mismatched
sources, repeated-calibration quality, stale sensors, startup, restart/gap shutdown,
source-matched targets, rollback, diagnostic units, persistence, endpoint handling,
idle correction and compaction invariance. Frontend tests cover comparison labels,
source reasons and optional diagnostic selectors. Live GRILLPLATS/HA hardware has
not been exercised by the development environment.
