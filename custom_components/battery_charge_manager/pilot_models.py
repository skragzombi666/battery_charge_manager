"""Versioned metadata for full-battery references, separate from no-load baselines."""
from dataclasses import dataclass, field, fields
from copy import deepcopy
from .const import ALGORITHM_VERSION
from .models import MeasurementSample


@dataclass(slots=True)
class RestMeasurement:
    measurement_id: str
    setup_id: str
    setup_revision: int
    battery_id: str
    battery_revision: int
    quantity: int
    ports: list[str]
    setup_snapshot: dict = field(default_factory=dict)
    battery_snapshot: dict = field(default_factory=dict)
    session_started_at: str | None = None
    confirmed_at: str | None = None
    session_finished_at: str | None = None
    duration_seconds: float = 0.0
    statistics: dict = field(default_factory=dict)
    valid: bool = True
    invalid_reason: str = ''
    completion_status: str = 'completed'
    origin_session_id: str | None = None
    switch_off_confirmed: bool = False
    analysis_revision: int = 1
    algorithm_version: str = ALGORITHM_VERSION
    usage_approval: str = 'pending'
    usage_revision: int = 0
    approval_history: list[dict] = field(default_factory=list)
    validity_history: list[dict] = field(default_factory=list)
    revision_approvals: list[dict] = field(default_factory=list)
    comment: str = ''
    comment_history: list[dict] = field(default_factory=list)
    trace_id: str | None = None
    archived_sample_count: int = 0
    samples: list[MeasurementSample] = field(default_factory=list)

    def as_dict(self, *, include_samples=True):
        result = {f.name: deepcopy(getattr(self, f.name)) for f in fields(self) if f.name != 'samples'}
        if include_samples:
            result['samples'] = [s.as_dict() for s in self.samples]
        return result

    @classmethod
    def from_dict(cls, data):
        values = {f.name: deepcopy(data[f.name]) for f in fields(cls) if f.name in data and f.name != 'samples'}
        values['samples'] = [MeasurementSample.from_dict(s) for s in data.get('samples', [])]
        return cls(**values)
