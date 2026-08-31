# Battery Charge Manager

Battery Charge Manager is a Home Assistant custom integration for repeatable, energy-based charging of removable batteries through a metered smart plug.

It is designed for batteries with their own charging electronics, such as USB-C rechargeable AA/AAA batteries connected to a USB power supply. The integration measures the complete charging arrangement at the mains side, learns full-charge energy profiles, and switches the charger off after a selected share of the calibrated net energy has been delivered.

> Battery Charge Manager is an automation and measurement aid. It is not a battery-management system or a substitute for the battery's charger, protection electronics, manufacturer limits, or supervision appropriate to the battery chemistry.

## Current version

**0.1.0**

## Main interface

Version 0.1.0 provides two complementary interfaces:

- a full **Battery Charge Manager panel** for setup management, battery profiles, idle measurements, calibrations, history, quality assessment, and settings;
- a compact **Battery Charge Manager dashboard card** for daily charging.

The dashboard card contains an **Open manager** button that navigates directly to `/battery-charge-manager`. The sidebar entry can therefore be hidden in a user's Home Assistant profile without losing access to the full panel.

The integration also creates regular Home Assistant entities for automations, notifications, and custom dashboards.

## Features

### Charging setups

A charging setup represents the complete physical arrangement used for a measurement:

- smart plug or charge switch;
- cumulative energy sensor in Wh or kWh;
- optional power sensor;
- optional temperature sensor;
- USB power supply or charger description;
- cable, splitter, and adapter description;
- ordered port labels;
- maximum permitted power;
- optional maximum permitted temperature.

The port order is operationally significant. With ports `A, B, C, D`, charging two batteries always means ports `A + B`; charging three means `A + B + C`.

Technical changes create a new setup revision. Existing measurements remain in the audit history but are excluded from calculations for the new revision.

### Battery profiles

Each battery type can store:

- name, manufacturer, and model;
- nominal capacity in mAh;
- optional nominal voltage and Wh value;
- chemistry or technical type;
- form factor;
- charging method;
- image URL or `/local` path;
- defined discharge method;
- expected rest time before charging;
- notes describing the repeatable starting condition.

Technical changes create a new battery revision. Previous measurements remain retained but become historical for current calculations.

### Independent idle-power measurements

Idle power is measured for the complete setup with the charger, power supply, splitter, and cables connected, but with no batteries attached.

Two modes are available:

- **Fixed duration**: run for a selected number of minutes.
- **Automatic until reliable**: run until the value is stable over several time windows and sufficiently resolved by the available sensors, subject to a maximum duration.

Multiple measurements are retained. Current valid and reliable measurements are combined using robust median-based statistics; a new measurement never silently replaces an older result.

For coarse cumulative energy sensors, the integration evaluates the inferred measurement resolution. If no energy step is observed, the result is reported as being below a calculated detection limit instead of claiming an exact zero.

### Full-charge calibration

Calibrations are specific to the exact combination of:

- charging setup and setup revision;
- battery type and battery revision;
- battery quantity;
- fixed port allocation.

A reliable idle measurement is required before starting a new calibration.

During calibration the integration records a raw trace containing timestamps, cumulative energy, gross energy, calculated idle energy, net charge energy, power, optional temperature, and switch state.

The integration detects:

- the beginning of significant charging;
- the main charging phase;
- tapering power;
- a candidate end-of-charge plateau;
- a confirmed endpoint after a stability window.

The actual `charge_finished_at` timestamp and calibrated energy are assigned retrospectively to the beginning of the confirmed plateau. The later `end_detected_at` timestamp records when enough evidence existed to confirm that endpoint. Small maintenance or top-up activity after the true endpoint is therefore not automatically counted as full-charge energy or charge duration.

Manual completion remains available as a low-confidence fallback. It is clearly marked in the calibration record.

### Repeated calibrations and quality

Every calibration remains an immutable record. Records can be invalidated and restored without deleting the audit trail.

For each exact setup/battery/quantity profile the integration calculates:

- median net full-charge energy;
- median charge duration;
- minimum and maximum energy;
- standard deviation;
- robust relative spread;
- recent median and drift;
- confidence counts;
- quality state: none, provisional, limited, stable, or unstable.

A linear `E(n) = intercept + energy_per_battery × n` model is calculated across calibrated quantities as a plausibility check only. Direct measurements for the selected quantity remain the operational values.

### Normal charging

Normal charging uses:

`target net energy = median calibrated net full-charge energy × selected percentage`

The smart plug is switched off when that target is reached.

The percentage is intentionally described as **relative charge energy**, not as an exact electrochemical state of charge. A 50% energy target is a repeatable operational midpoint, but it does not prove that the cell is at exactly 50% SoC.

### Safety and fault handling

The integration includes:

- verified smart-plug ON and OFF commands;
- a second OFF attempt if the first is not confirmed;
- a persistent Home Assistant warning if OFF cannot be confirmed;
- prevention of a new session while the plug does not report OFF;
- hard maximum session duration, preserved across Home Assistant restarts;
- session continuation after restart when the physical switch remains on;
- abort on energy-sensor failure;
- abort on configured power- or temperature-sensor failure;
- configurable maximum power;
- optional maximum temperature;
- abort when no significant charging load is detected;
- calibration energy plausibility limits;
- detection of external switch-off events;
- retained audit summaries for successful and aborted sessions.

## Installation with HACS

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu and select **Custom repositories**.
3. Add:

   `https://github.com/skragzombi666/battery_charge_manager`

4. Select category **Integration**.
5. Open **Battery Charge Manager** in HACS and install the latest release.
6. Restart Home Assistant.
7. Open **Settings → Devices & services → Add integration**.
8. Select **Battery Charge Manager** and configure the first charging setup.

Further setup and battery management is performed in the Battery Charge Manager panel.

## Dashboard card

The frontend module is registered automatically by the integration. No manual Lovelace resource entry is required.

Add the card through the dashboard card picker by selecting **Battery Charge Manager**, or use YAML:

```yaml
type: custom:battery-charge-manager-card
title: Battery charging
```

The card provides:

- charging-setup selection when more than one setup exists;
- battery-type selection;
- quantity selection;
- relative energy target;
- progress and current net energy;
- start and stop controls;
- direct navigation to the full manager panel.

## Recommended operating method

For repeatable results:

1. Use batteries of the same model and similar age and cycle history.
2. Discharge them using the same defined device or procedure until its normal cutoff.
3. Do not repeatedly force additional discharge after cutoff.
4. Apply the same rest time before charging.
5. Use the same setup, cables, splitter, ports, and environmental conditions.
6. Calibrate each quantity that will be used: 1, 2, 3, and 4 batteries where applicable.
7. Obtain at least three consistent calibrations before treating a profile as stable.
8. Re-measure idle power after changing any part of the charging arrangement.

See [Calibration method](docs/calibration-method.md) for the measurement model and interpretation.

## Entities

The integration exposes entities for:

- selected charging setup;
- selected battery type;
- selected quantity;
- relative energy target;
- session status and phase;
- target, gross, idle, and net energy;
- progress;
- current and peak power;
- current and peak temperature;
- elapsed time;
- aggregated idle-power baseline;
- calibration quality;
- battery information;
- start charge, stop, start calibration, manual calibration completion, and automatic idle measurement.

## Data retention and migration

Version 0.1.0 migrates 0.0.x battery profiles and Wh-only calibration samples. Legacy calibration samples remain usable but are marked as legacy, have low confidence, and do not contain a raw trace or measured duration.

Measurement records retain snapshots of the battery and charging-setup metadata used at the time of measurement. Later edits do not rewrite historical results.

## Licensing

Battery Charge Manager is source-available under the **PolyForm Noncommercial License 1.0.0**. Noncommercial use, modification, distribution, and contribution are permitted under its terms. Commercial use requires a separate written license from Roman Zambail.

See:

- [LICENSE.md](LICENSE.md)
- [COMMERCIAL.md](COMMERCIAL.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
