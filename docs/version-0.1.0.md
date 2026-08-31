# Battery Charge Manager 0.1.0

Version 0.1.0 replaces the original helper-only prototype with a complete measurement and operating system for repeatable energy-based battery charging.

## User interface

- Full Battery Charge Manager side panel for daily charging, battery profiles, charging setups, idle measurements, calibrations, history, quality assessment, and settings.
- Compact Lovelace card for setup, battery, quantity, target, start/stop, progress, and direct navigation to the full panel.
- The card module is registered automatically; no manual Lovelace resource entry is required.

## Professional measurement model

- Versioned physical charging setups with fixed port order, smart plug, energy sensor, optional power and temperature sensors, hardware description, and safety limits.
- Versioned battery profiles with nominal electrical data, chemistry, form factor, charging method, image, defined discharge method, rest time, and starting-condition notes.
- Independent idle-power measurements with fixed-duration and automatic-until-reliable modes.
- Multiple retained idle measurements combined through robust current-revision statistics.
- Gross, idle, and net energy accounting.
- Immutable calibration records with full setup and battery snapshots.
- Separate timestamps for session start, switch-on, detected charge start, taper, candidate endpoint, retrospective charge endpoint, endpoint confirmation, switch-off, and session completion.
- Automatic charge-end detection from a confirmed energy plateau and, when available, low power.
- Retrospective endpoint energy and charge duration that exclude the later confirmation period and minor maintenance activity.
- Repeated-calibration statistics, confidence, quality, drift, and a non-operational quantity plausibility model.

## Operation and safety

- Exact setup/battery/quantity profiles remain the operational source; the quantity model never replaces a direct calibration.
- Charging targets are explicitly relative charge energy rather than a claimed exact cell state of charge.
- Verified smart-plug ON/OFF commands, OFF retry, persistent warning, restart-safe timeout, external-switch detection, sensor-failure shutdown, power and temperature limits, no-load timeout, and calibration-energy plausibility checks.
- Existing 0.0.x Wh-only calibrations are retained as low-confidence legacy records.
