# Battery Charge Manager 0.4.2

## Data ownership and durable retention

The application never automatically deletes raw samples, received state reports,
operations or analysis revisions. The old 1,600-point repeated halving, 100-run
history cap and suppression of short event bursts are removed. There is no raw
measurement deletion operation in this release. Deleting a battery/setup profile
still requires the existing explicit user action; historic metadata and measured
traces remain in the archive. No data are normalized to nominal battery energy.

New persistent storage is a per-entry SQLite archive at
`.storage/battery_charge_manager.<entry-id>.sqlite3`. It uses WAL transactions and
FULL synchronization. Raw samples, received observations and metadata/analysis
snapshots are append-only; database triggers reject replacement/deletion of raw
rows. A chained SHA-256 hash identifies each exact sample sequence. Mutable
checkpoints and counts are recovery indexes, not original observations.

Home Assistant's executor performs SQLite I/O. Historical curves load on demand;
only the active/last session remains cached. Display updates may be throttled and
charts may be reduced, but the raw archive is not. There is no configured maximum
sample count or automatic age expiry. Available disk space and hardware still
bound storage: a write failure causes a checked stop where possible, a visible
notification and blocked new starts, not purging of older records. Unsaved
observations are retained in memory and included separately in an emergency
export while that process is still running. Software cannot retain RAM-only data
through power loss when persistent storage has failed.

## Migration and update

Install 0.4.2 through HACS and restart Home Assistant after ending the active
operation. No integration reconfiguration is needed. On the first load, all
remaining original Store records, raw fields, histories and analyses are imported
in a transaction. The unmodified legacy Store is also retained, and an exact JSON
snapshot is stored in the archive. Import is idempotent. Divergent historical
snapshots of the same session are retained as separate trace versions rather than
overwritten. Earlier compaction/deletion cannot be reversed.

A stopped calibration previously hidden in the operation log now appears as an
excluded calibration attempt. Stopped idle runs likewise appear as invalid,
unreliable idle measurements, not as a usable baseline. Missing legacy metadata
is not fabricated from the current hardware revision.

**Downgrade warning:** after migration, the SQLite archive is authoritative; the
old Store is an unchanged pre-migration snapshot, not a continuously updated
mirror. An older integration version cannot read the new archive. Preserve a full
export/backup before downgrading; a downgrade is not a supported way to continue
new measurements with all current data visible. Keep the SQLite database and any
associated WAL/SHM files together when making filesystem copies while HA runs;
the authenticated export is a consistent snapshot.

## Ending a measurement is not approval of a calibration

Manual finish always requests and verifies switch-off before assessing energy.
Zero-counter/estimate-only runs are saved with `manual_unusable` status rather than
left running. Stop, timeout, external switch changes and analysis errors retain a
visible excluded attempt and its reason. Repeated finish/stop commands do not
create duplicate completed records. User commands are serialized across disk
awaits; incoming sample/safety processing remains independent.

Validity, completion status, revision applicability, endpoint evidence and energy
source usability are separate. A retained estimate or a user-restored validity
flag does not silently authorize charge targets. Explicit fixed-source selection,
maximum duration, temperature, power and checked-switch safeguards remain.

## Actual reports and interval evidence

The application captures each state event before queueing work, including raw
state strings, attributes/units, receive time, event time, reporting timestamps,
trigger entity, old state and receipt sequence. It subscribes to both indexed HA
state-change and state-report events. Unchanged reported values are distinguishable
from a heartbeat reading the previously stored value. Invalid observations are
archived before the corresponding stop. Non-JSON values are explicitly represented
rather than silently omitted. Original numeric precision is not rounded in the
raw archive.

HA's `state_reported` is evidence that its integration wrote a state, not independent
proof that the physical device performed a new measurement. Unknown timestamps,
reports older than 120 seconds and gaps/restarts remain unsupported for automatic
control. No heartbeat makes an old reading artificially fresh.

Every interval records supported time, estimated time, accepted energy, estimated
energy and the reason for exclusion. An accepted partial integral subtracts idle
energy for its accepted duration only, not for the whole session. Estimates have
their own supported duration. Overall coverage is not evidence that the high-power
charging period was captured: source decisions use the selected endpoint's
cumulative evidence, and unknown earlier intervals do not become valid because a
later tail was measured well.

New idle measurements use the time-weighted mean active input power after a
five-minute warm-up. At least 99% fresh temporal coverage and agreement of three
time blocks are required for a reliable reference. A zero median amid positive
pulses is not assumed to imply zero consumption. Old baseline summaries are kept
with their original `legacy_median` method, not silently promoted/recalculated.

## Charge phases and pulsating residual input

Phase interpretation remains distinct from source selection and charge-end
confirmation. Without a supported main-load reference, phase can be
**Undetermined / Nicht bestimmbar**, not a fabricated main/taper phase. The 0.4.1
five-minute time-weighted main reference and reversible taper hysteresis remain.

For a supported main input of at least 0.5 W, a five-minute low-input window starts
an endpoint candidate. Confirmation requires 20 minutes in total with at least
99% fresh covered time:

- Mean net power at most `max(0.12 W, 8% of sustained main input)`.
- At least 98% of window time below `max(0.30 W, 25% of main input)`.
- Above-threshold pulses at most 10 seconds each and at most 0.5% of the energy a
  main-level input would use over that window.
- Excess energy above the mean threshold at most half that threshold's window
  energy.

Renewed substantial input or missing tail evidence rejects the candidate. The
candidate is a retained sample timestamp, not an interpolated raw value. The
thresholds are documented conservative input-curve heuristics, not proof of cell
state of charge. They do not use a nominal-Wh target or a hard-coded expected
charging time. Without a supported main reference, the separate strict fresh
low-power confirmation fallback remains; no unchanged cumulative counter alone
confirms a power-sensor-equipped setup's endpoint. Hard safety timeout remains the
upper bound if no endpoint can be established.

## Results and retrospective boundaries

Gross and net energy always show both **Energy meter / Energiezähler** and
**Power integration / Leistungsintegration**. The source setting and actual
selection remain separate. Total operation, selected charging interval and
post-end interval are separate summaries. The post-end interval is not assumed to
be pure idle waste; it can include residual draw or top-up pulses.

An administrator may select an endpoint in local time and supply a reason. The
last retained sample at or before the requested time is used; no missing raw point
is reconstructed. The prior analysis, actor, reason, requested timestamp and actual
sample timestamp are retained. This action never approves an excluded/incomplete
calibration. On sparse legacy data it cannot establish an exact endpoint between
surviving samples. Unknown boundaries remain unknown until supported or explicitly
set, not automatically inferred from nominal capacity.

Nominal battery energy is displayed as a reference, with an input/nominal ratio
where an interval is selected. Supply-side input includes conversion losses and
is not directly measured cell capacity. The ratio is not a measured efficiency.
A ratio above two is a review warning only, never a rescaling or charge cutoff.
Numerical integration cannot independently correct a biased input power sensor.
A physical reference measurement remains separate from software verification.

## Viewing and exporting all retained data

History includes completed and excluded attempts. Its filter and paging never
delete anything. Detail charts retain bucket extrema, label unsupported gaps and
do not connect absent raw power into a fictitious continuous trace. Raw observations
are separately pageable in the detail view, including provenance and full numeric
precision. Reanalysis changes only derived views, not archived samples.

The administrator's **Export all measurement data (JSON)** downloads via an
HA-authenticated, short-lived signed GET, not a giant WebSocket payload or browser
Blob. Export schema 2 includes all current metadata, trace references, the full
`raw_archive.traces[].samples`, received `events`, and immutable original/analysis
`documents`. Trace IDs and counts tie records to their original rows. The legacy
WebSocket exporter explicitly rejects an incomplete metadata-only export when the
SQLite archive is active. Readers hold one consistent WAL snapshot; new recording
can continue. A failed read aborts the download rather than reporting truncated
JSON as a successful archive. Uncommitted RAM data after storage failure are marked
separately, not described as durable.

## Verification and limits

Regression coverage includes over 100,000 original samples, over 100 retained
operations, reopen/import idempotence, raw hash equality, divergent legacy
snapshots, manual and repeated stop, storage failures, missing metadata, unchanged
reports, stale reads, accepted-time idle correction, pulsed tails, load recovery,
nominal independence, explicit boundary auditing, authenticated HTTP streaming
and UI behaviour. Tests use synthetic public fixtures. A separate local migration
check can exercise a user export without publishing it.

No firmware update is applied to any plug. Software tests and browser checks do
not establish the absolute accuracy or reporting reliability of a physical
GRILLPLATS/charger combination. Incomplete device data remain marked as such.

Local release verification: **157 Python tests and 70 JavaScript tests passed**.
An offline Chromium check at 360, 412 and 1024 pixels exercised the history/detail
layouts, local-time endpoint input, reason and optimistic-revision payload, raw
paging and signed-download link creation without JavaScript errors. Browser
network transfer was not exercised; the HTTP stream has separate aiohttp tests.
The local private-export migration check retained 6,558 original points across
records, exposed the stopped 1,432-point example without approving its estimate,
and verified original JSON equality, stable hashes and repeatable reopening.
The private export is not included in this repository.
