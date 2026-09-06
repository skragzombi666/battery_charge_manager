# Battery Charge Manager 0.1.1

## Calibration workflow

- Full-charge calibration can be recorded before an idle baseline exists.
- Such records remain explicitly marked as `pending` and are excluded from normal automatic charging.
- A later reliable idle measurement automatically recalculates the stored raw trace and applies the baseline.
- The previous analysis remains retained in the record analysis history.

## Frontend

- Live Home Assistant and websocket updates no longer replace a focused input, select, or textarea.
- Deferred updates are rendered after editing leaves the control.
- Idle-measurement and settings number fields retain their draft values.
- Values below the permitted minimum are clamped to the minimum; a fixed duration of one minute therefore becomes five minutes.

## Compatibility

Existing 0.1.0 data is migrated with the previous calibration interpretation preserved. New calibrations without a baseline use the explicit pending state.
