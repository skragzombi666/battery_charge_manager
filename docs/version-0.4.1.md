# Battery Charge Manager 0.4.1

## Correct phase indications for small batteries

The phase is an interpretation of the measured mains-side power curve, not a
measurement of cell state of charge. It neither regulates the battery's charging
current nor replaces its charging electronics. The expected duration of a
particular battery is not hard-coded.

Version 0.4.0 could interpret the initial zero readings followed by the first
charging reading as a reduction relative to the peak and latch the taper phase.
Version 0.4.1 replaces that single-peak comparison with elapsed-time evidence:

- Only samples at or after the detected charging start are considered.
- A five-minute window must have at least 99% fresh coverage. Intervals over
  120 seconds, stale reports and invalid power values are not phase evidence.
- The reference is the highest sustained five-minute weighted median at or above
  0.5 W. At least 80% of the covered time must be within 20% of that median to
  establish or raise the reference. Individual inrush spikes do not establish it.
- Taper requires current net power at or below 60% of the reference and at least
  80% of a covered five-minute window below that threshold.
- Recovery to main charging requires current power at or above 80% of the
  reference and at least 80% of a covered two-minute window above that threshold.
- Samples are weighted by elapsed time, so bursts of sensor events cannot outvote
  several minutes of stable charging. Tracking state survives serialization.

An active legacy session's unverified taper latch is cleared before learning
current evidence. Historical calibration records and their phase timestamps are
not rewritten. An existing end-confirmation candidate is not overwritten by a
phase hint. The established end-detection rules remain separate: a configured
power sensor must provide the fresh, low-power confirmation tail, not merely an
unchanging energy counter. See [the endpoint method](calibration-method.md).

## Two measurement paths in both energy tiles

**Gross energy** and **Net charge energy** always show both **Energy meter** and
**Power integration**, regardless of the selected source mode. In German the
labels are **Bruttoenergie**, **Netto-Ladeenergie**, **Energiezähler** and
**Leistungsintegration**. The latter is the time integral of active power,
`E = integral(P dt)`, expressed in Wh; it is not watts divided by time.

Each net value subtracts the same applicable idle contribution from its own gross
value. An unknown idle reference is displayed as pending correction, not as a
measured zero or an apparently valid net value. The chart then shows gross
energy. Missing power measurements are shown as unavailable rather than 0 Wh.
The idle-power tile shows the numeric value and identifies a lower-bound estimate
when applicable.

Cards and charts use the same displayed integrated estimate. If all accepted
intervals support that value it is labelled complete; otherwise it is explicitly
an estimate or partial value. The expanded comparison retains the accepted
partial integral separately. Displaying an estimate does not authorize its use
for charge targets. Complete coverage is not proof of absolute measurement
accuracy or of the battery's electrochemical capacity.

The source setting is shown separately from the measurement values. During an
automatic calibration the UI states that the decision is made at completion.
Normal charging identifies its frozen operational source; displaying both paths
never changes the running target or source. An unchanged counter alongside a
positive integrated estimate is called out as **no counter increment**, not as a
proven hardware diagnosis.

New calibration comparisons retain both gross values and the idle contribution
at the same endpoint. This also prevents a zero counter gross value from being
reconstructed as positive idle energy after net energy was clamped to zero.
Older reports without these fields remain readable; missing data are not invented.

## Usable integration when the cumulative counter does not advance

In automatic mode, an exactly zero gross counter increment no longer vetoes an
otherwise complete, sufficiently resolved active-power integral. The fallback
requires a positive accepted net integral, the existing complete-coverage checks
(at least 99%, at least two fresh reports, no invalid integral), a largest
integration contribution at most 5% of net energy and report intervals at most
120 seconds. The saved selection reason is `counter_not_advancing`.

This is an explicit fallback from an unusable zero-increment counter, not proof
that its firmware is defective. Estimates with stale reports, gaps or insufficient
time resolution cannot trigger this automatic fallback. Positive conflicting
counter values are still subject to the existing disagreement rejection. A fixed
**Energy meter** setting never switches silently. A fixed **Power integration**
setting retains its existing requirement for a complete accepted integral.

Manual completion can now retain a usable power-based calibration even when the
live counter-based net total is zero. It still produces a lower-confidence manual
record and still requires confirmed switch-off. An estimate-only zero-counter
run is rejected without switching off or silently treating the estimate as usable.
Automatic completion continues to require independently confirmed low power.

The calibration energy safety check also observes the accepted integral, so a
stalled counter cannot conceal measured energy above the limit. Its reference
comes from the same eligible source-matched calibration summary used for charge
targets. No timeout, power, temperature, switch-off or restart protection is removed.

## Update and retained data

Update through HACS and restart Home Assistant after the active operation has
finished. Integration and analysis versions are 0.4.1. The normal versioned frontend
registration also refreshes the panel code after the update.

No runtime dependencies are added. Raw samples, comments, revisions, validity
history and prior analyses are retained. Old complete parallel evidence can be
re-evaluated under the current source setting without altering the original
completion-time decision. Missing historical measurements cannot be recovered.

This release fixes the integration's phase logic, presentation and handling of a
non-advancing counter; it does not update or repair smart-plug firmware. Regression
traces cover the reported low-power scenario. End-to-end validation on a physical
GRILLPLATS and the user's charger remains distinct from automated software tests.
