"""Explicitly reviewed fixture state for tests of subsequent selection behavior.

Workflow tests exercise the approval API itself. Older statistics/source tests
construct reviewed records so their existing subject remains independently tested.
"""
def reviewed(manager, record, *, select=True):
    if select and record.metering_comparison:
        confidence = record.confidence
        manager._select_calibration_energy(record, manager.energy_mode)
        record.confidence = confidence
    record.usage_approval = 'approved'
    record.approval_history.append({'approved': True, 'reason': 'Reviewed fixture',
        'fingerprint': manager._decision_fingerprint(record)})
    return record
