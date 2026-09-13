# Battery Charge Manager 0.3.0

## Complete measurement export

Management has one **Export all measurement data (JSON)** button for administrators.
The download is a consistent snapshot of all retained data, independent of the
selected setup, battery, quantity or history filter. It contains:

- All calibration and idle records, including invalid and historical revisions.
- Every stored sample, including parallel meter, power and electrical diagnostics.
- Original setup/battery snapshots, current definitions, revision approvals,
  validity decisions, analysis history, source comparisons and current usage status.
- Calibration comments and their edit histories.
- Retained charge history and the active/last session, with available samples.
- Export timestamp/time zone, integration/algorithm/schema versions and settings.

The export is JSON because nested histories and snapshots cannot be preserved
faithfully in a single flat CSV. It is a measurement export, not an importable
Home Assistant backup. Image references are included; image files are not embedded.
Previously compacted samples and discarded charge history cannot be recovered.
Charge history retains the latest 100 entries. From this version onward, normal
and aborted sessions also retain their stored traces and equipment snapshots;
older history entries may contain summaries only. Full historical session data
is excluded from live subscription payloads.

## Calibration comments

An optional comment is available next to the calibration start action. It is
saved before charging begins and survives restart. Completed calibration details
allow administrators to replace, extend or clear the comment, including for old
or invalid records and while another session runs. Each change records the prior
text, new text, time and actor. Concurrent edits are rejected if the saved comment
changed since opening the record. Comments do not change measurement validity,
equipment revisions, source selection or energy calculations.

Update through HACS and restart Home Assistant without an active charging session.
