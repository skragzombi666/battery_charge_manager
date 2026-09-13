# Battery Charge Manager 0.2.1

Fixes the header reporting 0.1.7 after installing 0.2.0. The frontend receives
its version from a backend constant that was not updated with the manifest.
Both now report 0.2.1. The parallel metering implementation was already present
in 0.2.0; this patch does not change charging calculations.

New calibration analysis uses algorithm identifier 0.2.0, reflecting the
parallel metering implementation. Existing historical identifiers are preserved.
Regression tests check display/manifest agreement and the algorithm identifier.

Install the update and restart Home Assistant with no active charging session.
