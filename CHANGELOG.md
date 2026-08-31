# Changelog

## 0.1.0

Major measurement, calibration, and user-interface release.

### User interface

- Added a complete Battery Charge Manager side panel.
- Added a compact Lovelace dashboard card with setup, battery, quantity, target, start/stop, progress, and a direct link to the full panel.
- Registered the card frontend automatically; no manual Lovelace resource is required.
- Added German and English panel/card text.
- Added graphical battery and charging-setup management.

### Charging setups and battery profiles

- Added multiple versioned charging setups.
- Added switch, cumulative energy, optional power, and optional temperature sensors.
- Added charger, cable/splitter, ordered port, power-limit, and temperature-limit metadata.
- Added versioned battery profiles with manufacturer, model, nominal electrical data, chemistry, form factor, charging method, image, discharge method, rest time, and starting-condition notes.
- Added first-N fixed port allocation for quantities 1–8.
- Technical edits now retain old measurements but exclude them from current-revision calculations.

### Idle measurements

- Added independent fixed-duration idle-power measurement.
- Added automatic measurement until a statistically reliable result is obtained.
- Added warm-up exclusion, stability windows, inferred energy resolution, and below-detection-limit reporting.
- Added multiple retained idle measurements per setup revision.
- Added robust aggregation, quality, spread, and reliable-measurement counts.

### Calibration

- Added automatic charge-start, main-phase, taper, plateau, and endpoint detection.
- Added retrospective `charge_finished_at` and separate `end_detected_at` timestamps.
- Excluded post-charge idle/maintenance energy from the calibrated endpoint.
- Added gross, idle, and net energy.
- Added raw timestamped measurement traces.
- Added charge duration, session duration, peak power, optional peak temperature, end method, confidence, and indicative multi-battery synchrony.
- Added immutable calibration records and reversible validity controls.
- Added median, standard deviation, robust spread, recent drift, confidence counts, and quality states.
- Added a linear quantity model for plausibility checking only.
- Retained manual completion as a clearly marked low-confidence fallback.

### Operation and safety

- Normal charging now uses current-revision median net energy for the exact setup, battery, and quantity.
- Clarified that target percentage represents relative charge energy rather than exact cell SoC.
- Added verified switch ON/OFF, retry, and persistent warning on unconfirmed OFF.
- Added prevention of new sessions while the switch is not confirmed OFF.
- Added restart-safe remaining timeout calculation.
- Added energy-, power-, temperature-, switch-, no-load-, excessive-energy-, and maximum-duration fault handling.
- Added compact retained charge history.

### Migration

- Added storage schema migration from 0.0.x.
- Converted legacy Wh-only samples to retained low-confidence calibration records.

## 0.0.2

HACS packaging and validation fixes.

- Added integration issue-tracker metadata.
- Added local brand assets.
- Added automatic GitHub release workflow.
- Added HACS and hassfest validation workflow.

## 0.0.1

Initial development version.

- Added Home Assistant UI config flow.
- Added smart-plug, energy-sensor and optional power-sensor configuration.
- Added persistent battery-type library.
- Added separate Wh calibration histories by battery type and quantity.
- Added median calibration calculation.
- Added manual calibration start/finish workflow.
- Added energy-target cutoff, restart persistence, sensor-failure shutdown, and safety timeout.
