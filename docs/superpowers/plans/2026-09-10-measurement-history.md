# Measurement history and revision approval implementation plan

**Goal:** Make measurement origin, validity, operational use and revision reuse explicit for idle measurements and calibrations.

**Architecture:** Keep original setup/battery snapshots and measurement revisions. Store separate, revocable approvals for an exact current revision pair. Derive operational use from the same selectors used for charging. Load historical trace details on demand.

**Tech stack:** Existing Python Home Assistant integration, native JavaScript custom elements, unittest and Node tests. No new runtime dependency.

**Spec:** User request of 10 September 2026; detailed behavior below. Implementation is already authorized and proceeds in this session.

## Required behavior

- Origin revisions and snapshots never change when an older record is approved.
- Approval requires a reason, refers to the same setup/battery identity and exact current revisions, and does not propagate to a later revision. Quantity stays fixed. The user confirms that the physical arrangement and starting conditions are equivalent after comparing metadata.
- Validity, confidence, revision eligibility and actual statistical use are separate. Invalid records are excluded; low-confidence records can remain valid but be superseded by trusted records.
- Revoke an approval independently of global record validity. Preserve decisions, timestamps and reasons.
- Invalid or missing idle references exclude dependent calibrations from operational use. Reanalysis with a reliable applicable baseline is explicit for existing corrected records. Pending records retain automatic correction behavior.
- Show original/current revisions, changed metadata, metrics, source idle records, confidence, method, timestamps, curves, prior analyses and decision history in a read-only detail dialog available to all authenticated users.
- Keep normal state messages free of historical traces. Historical details use a bounded chart. Preserve trace endpoints and signal extrema during sampling.
- Mutations require administrator rights and an idle manager. Exact expected revisions reject stale dialogs. Unknown records fail clearly.
- Labels describe actions: mark invalid, restore validity, approve for current revision, revoke approval and recalculate idle correction. Explain effects before applying them.
- Valid is green; invalid is red; confidence is separate. German and English labels are provided. Details and forms remain usable during updates and on narrow screens.

## Execution

1. Add behavior tests in `tests/test_measurement_history.py`: revision approval without origin mutation, exact-revision expiry, revocation/restore, invalid dependencies, reanalysis, persistence, historical details, old records beyond the former global 100-row cutoff. Run them before implementation.
2. Extend `models.py` with serialized approval and validity histories. Add pure revision/trace helpers in `history.py`. Integrate shared eligibility and operational-use reasons in `manager.py`; add checked approval/reanalysis methods and detail access.
3. Add authenticated read and administrator mutation endpoints in `websocket_api.py`. Test error/argument forwarding at this boundary.
4. Add frontend behavior tests, then update history tables and dialogs in `frontend/battery-charge-manager.js`. Reuse the existing chart rendering with historical/pending handling; retain focus and scroll protection.
5. Independently review the whole integration and final diff. Reproduce material findings, fix with regression tests, run all Python/JavaScript tests and syntax checks, and visually inspect desktop/mobile flows.
6. Update version/changelog/documentation and provide the verified change as a reviewable GitHub update.

## Verification commands

```sh
python -m unittest discover -s tests -v
node --test tests/*.mjs
node --check custom_components/battery_charge_manager/frontend/battery-charge-manager.js
python -m compileall -q custom_components/battery_charge_manager
git diff --check
```
