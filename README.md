# Battery Charge Manager

Home Assistant custom integration for charging removable batteries to a calibrated storage charge using a metered smart plug.

## Version

Current development version: **0.0.1**

## What 0.0.1 does

- Configures one charging smart plug/switch.
- Uses a cumulative energy sensor in Wh or kWh.
- Optionally stores a power sensor for monitoring.
- Maintains a persistent battery-type library.
- Battery types contain:
  - name
  - nominal capacity in mAh
  - technology
  - form factor
  - image
- Stores separate calibration histories for each battery type and quantity.
- Uses the median of repeated calibration samples.
- Starts a calibration from the Home Assistant UI and stores the measured full-charge energy when calibration is finished.
- Starts a storage-charge session and switches the charger off automatically when the calibrated target energy is reached.
- Restores an active session after a Home Assistant restart.
- Stops the charger if the energy sensor becomes unavailable.
- Stops the charger after a configurable safety timeout.

## Installation

Copy:

`custom_components/battery_charge_manager`

to:

`/config/custom_components/battery_charge_manager`

Restart Home Assistant.

Then open:

**Settings → Devices & services → Add integration → Battery Charge Manager**

## Initial setup

Select:

1. the smart-plug switch entity;
2. its cumulative energy sensor;
3. optionally its current power sensor;
4. the default storage-charge percentage;
5. the maximum allowed session duration.

The energy sensor must use Wh or kWh.

## Add battery types

Open:

**Settings → Devices & services → Battery Charge Manager → Configure**

Use **Add battery type**.

Each type can store a name, nominal capacity, technology, form factor and image.

## Calibration

Calibration is stored independently for every combination of battery type and quantity.

Example:

- Pale Blue AA × 1
- Pale Blue AA × 2
- Pale Blue AA × 4

are three separate calibration profiles.

To calibrate:

1. Select the battery type.
2. Select the quantity.
3. Connect batteries that are at the defined discharged starting state.
4. Press **Start calibration**.
5. Allow the batteries to reach full charge.
6. Press **Finish calibration**.

The measured Wh value is appended to the calibration history. Repeated calibrations are allowed. The integration uses the median of the stored samples.

## Normal storage charging

1. Select battery type.
2. Select quantity.
3. Set **Storage charge target**, for example 50%.
4. Press **Start charging**.

If the full-charge calibration is 12.0 Wh and the target is 50%, Battery Charge Manager switches the smart plug off after 6.0 Wh has been delivered.

## Entities

| Entity | Purpose |
|---|---|
| Battery type | Select battery profile |
| Quantity | Select number of batteries charged together |
| Storage charge target | Set target percentage |
| Status | Idle, charging or calibrating |
| Target energy | Calculated Wh target |
| Delivered energy | Wh measured in the current session |
| Progress | Charging progress |
| Battery information | Metadata and calibration history |
| Start charging | Start normal storage charging |
| Stop | Abort and switch charger off |
| Start calibration | Start full-charge calibration |
| Finish calibration | Save calibration sample and switch off |

## Safety

This integration is an automation aid, not a battery-management system. The battery's own charger/protection electronics remain responsible for electrical charging safety.

Version 0.0.1 intentionally requires the user to finish a calibration manually. Automatic full-charge detection from the power curve is not enabled yet.

## Planned

- Better calibration management, including deleting individual samples.
- Automatic end-of-charge detection using power thresholds.
- Dedicated dashboard/card.
- Multiple charger profiles.
- More validation of abnormal energy-sensor jumps.
- Diagnostics export.

## License

Battery Charge Manager is source-available under the **PolyForm Noncommercial License 1.0.0**. Noncommercial use, modification and distribution are permitted under that license. Commercial use requires a separate written commercial license from Roman Zambail.

See [LICENSE.md](LICENSE.md) and [COMMERCIAL.md](COMMERCIAL.md).

## Contributing

Contributions are welcome. By submitting a contribution, contributors retain their copyright while granting the project owner the rights necessary to distribute the contribution under the public noncommercial license and under separate commercial or proprietary licenses.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the Contributor License Agreement.
