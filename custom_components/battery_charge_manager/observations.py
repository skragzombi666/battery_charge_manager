"""Capture HA state reports before queueing. A receipt is not a hardware sample claim."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import math
from types import SimpleNamespace
from typing import Any


def json_value(value: Any) -> Any:
    """Keep JSON values exact; label values JSON cannot represent instead of dropping them."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else {'nonfinite': repr(value)}
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [json_value(v) for v in value]
    return {'type': type(value).__name__, 'representation': repr(value)}


def snapshot(state, *, reported_at: datetime | None = None) -> dict | None:
    if state is None:
        return None
    return {
        'state': str(state.state), 'attributes': json_value(dict(state.attributes)),
        'last_reported': json_value(reported_at or getattr(state, 'last_reported', None)),
        'last_updated': json_value(getattr(state, 'last_updated', None)),
        'last_changed': json_value(getattr(state, 'last_changed', None)),
    }


def parse_time(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return result if result.tzinfo else None
    except ValueError:
        return None


def state_value(data: dict | None):
    """Adapter for existing unit conversion; no reads of mutable HA state."""
    if data is None:
        return None
    return SimpleNamespace(state=data['state'], attributes=data.get('attributes', {}),
                           last_reported=parse_time(data.get('last_reported')),
                           last_updated=parse_time(data.get('last_updated')))


def capture(hass, setup, session, now: datetime, source: str, event=None,
            *, sequence: int = 0, command_in_progress: bool = False) -> dict:
    data = getattr(event, 'data', {}) or {}
    trigger = data.get('entity_id')
    ids = {setup.energy_sensor, setup.power_sensor, setup.temperature_sensor,
           setup.switch_entity, setup.voltage_sensor, setup.current_sensor,
           *session.source_decision.get('diagnostic_sensors', [])}
    states = {entity: snapshot(hass.states.get(entity)) for entity in ids if entity}
    if trigger and 'new_state' in data:
        states[trigger] = snapshot(data['new_state'], reported_at=data.get('last_reported'))
    kind = getattr(event, 'event_type', source) if event is not None else source
    return {
        'received_at': now.isoformat(), 'receipt_sequence': sequence,
        'event_type': kind, 'event_time': json_value(getattr(event, 'time_fired', None)),
        'trigger_entity_id': trigger, 'new_report': event is not None,
        'command_in_progress': command_in_progress,
        'session_id': session.session_id, 'trace_id': session.trace_id or f'session:{session.session_id}',
        'states': states, 'old_state': snapshot(data.get('old_state')),
        'old_last_reported': json_value(data.get('old_last_reported')),
        'evidence_scope': 'home_assistant_report_not_independent_hardware_timestamp',
    }
