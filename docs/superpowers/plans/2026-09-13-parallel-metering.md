# Parallel metering (0.2.0)

Authorized: implement parallel metering, select suitable source from calibration,
merge to main and publish an update. Existing setup and battery revision rules apply.

- Retain the cumulative meter and integrate active power with a left-held sample.
- Record optional RMS voltage/current and apparent energy (VAh) for diagnostics only.
  Never use apparent energy as a charging target; no absolute accuracy claim.
- Persist integration state and per-sample parallel energies. Do not reconstruct
  missing historical data. Abort power-controlled charging after restart or gaps.
- At the retrospectively detected endpoint compare matched meter/power energies,
  observed counter steps, temporal resolution and coverage. Require three usable
  calibrations, conservative consistency and repeatability checks to select power.
- Freeze the selected source and calibration IDs at session start. Recompute the
  target median from records measured by that source, never mix Wh methods.
- Keep existing meter-only profiles operational. Reanalysis updates comparisons
  using retained accumulators; old records without them remain meter-only.
- Show comparison, eligibility/reason and selected source in live/history/profile
  UI, with optional voltage/current selectors on setup. Add focused tests first.
- Run all Python/frontend tests, independent code review, then branch/PR CI,
  merge main and verify the version-driven GitHub release.
