# Battery Charge Manager 0.1.2

## Operational UI

The calibration screen no longer shows the relative-charge-energy target. Both charging and calibration show the exact configured first-N ports to use. Horizontal tab navigation retains its scroll position during live updates.

## Live process views

Active idle measurements, calibrations, and charging sessions replace setup controls with a live process view. Fixed idle measurements show elapsed time, remaining time, expected end, current power, accumulated energy, sample count, a preliminary baseline estimate, and a progress bar. Automatic idle measurements show time until the minimum duration, maximum duration, and live reliability information.

Calibration shows the selected battery, exact ports, detected phase, duration, power, peak power, gross/idle/net energy, sample count, correction state, and endpoint-candidate information without presenting a fabricated percent complete value.

Normal charging shows actual percent progress because a calibrated target energy exists.

## Charts

A shared lightweight SVG chart renders the session power and energy trace. Idle measurement charts use gross power/energy, calibration charts use net power/energy with endpoint markers, and charging charts use net power/energy with a target-energy line. The dashboard card shows a compact chart while charging. The backend downsamples long sessions to at most 240 evenly distributed points while retaining the first and last sample.
