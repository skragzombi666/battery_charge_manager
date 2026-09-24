"""Archive integration and visible retained attempts; no charger decision logic."""
from __future__ import annotations

import asyncio
from copy import deepcopy
from functools import partial, wraps
import logging
import sqlite3
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.exceptions import HomeAssistantError

from .archive import RawArchive
from .const import ALGORITHM_VERSION, DATA_SCHEMA_VERSION, DOMAIN
from .models import CalibrationRecord, ChargerSetup, IdleMeasurement, MeasurementSample

_LOGGER = logging.getLogger(__name__)


def serialized_command(function):
    """Serialize user commands across executor awaits; sample safety stays independent."""
    @wraps(function)
    async def guarded(self, *args, **kwargs):
        async with self._command_lock:
            return await function(self, *args, **kwargs)
    return guarded


class ArchivePersistence:
    """Persistence helpers consumed by BatteryChargeManager.

    SQLite is called only from an executor. A failed write never removes the
    in-memory trace or replaces the last good persisted checkpoint with zeroes.
    """

    async def _io(self, function, *args):
        executor = getattr(self.hass, 'async_add_executor_job', None)
        return await executor(function, *args) if executor else await asyncio.to_thread(function, *args)

    def _shutdown_setup(self):
        setup = self.setups.get(self.session.setup_id or '')
        if setup is not None:
            return setup
        try:
            return ChargerSetup.from_dict(self.session.setup_snapshot) if self.session.setup_snapshot else None
        except (KeyError, TypeError, ValueError):
            return None

    @staticmethod
    def _sample_count(record) -> int:
        return max(record.archived_sample_count, len(record.samples))

    async def _async_open_archive(self, legacy: dict) -> dict:
        config = getattr(self.hass, 'config', None)
        if config is None or not callable(getattr(config, 'path', None)):
            # Embedded users/tests without HA's filesystem keep the unlimited
            # Store representation. Actual HA always supplies config.path.
            return legacy
        archive = RawArchive(config.path('.storage', f'{DOMAIN}.{self.entry.entry_id}.sqlite3'))
        try:
            result = await self._io(archive.initialize, legacy)
        except (OSError, sqlite3.Error, ValueError) as err:
            self._archive_error = str(err)
            _LOGGER.exception('Raw archive could not be opened; original Store remains untouched')
            raise HomeAssistantError('Raw archive could not be opened. Original data were not changed.') from err
        self.archive = archive
        return result

    async def _async_restore_session_trace(self) -> None:
        if self.archive and self.session.trace_id and not self.session.samples:
            points = await self._io(self.archive.read_samples, self.session.trace_id)
            self.session.samples = [MeasurementSample.from_dict(p) for p in points]
            self.session.archived_sample_count = len(points)

    async def _async_archive_failure(self, err: Exception) -> None:
        self._archive_error = str(err)
        _LOGGER.error('Raw archive write failed; no observations were purged: %s', err)
        # Do not recurse through the regular completion/save path on disk failure.
        if self.session.active:
            setup = self._shutdown_setup()
            confirmed = await self._async_switch_off_checked(setup) if setup else False
            self._stop_tracking()
            self.session.session_finished_at = self._now_iso()
            self.session.switch_off_at = self.session.session_finished_at if confirmed else None
            self.session.end_reason = 'Archive write failed; latest observations remain in memory'
            self.session.phase = 'error'
            self.session.valid = False
            self._append_charge_history(valid=False, reason=self.session.end_reason)
            self.session.mode = 'idle'
        persistent_notification.async_create(
            self.hass,
            'The measurement archive could not be written. No old data were deleted. '
            'Charging was stopped where possible. Export the in-memory data and check storage before starting again.',
            title='Battery Charge Manager storage error', notification_id=f'{DOMAIN}_archive_error')
        self._notify()

    async def _async_sync_sample_archive(self) -> None:
        if not self.archive or not self.session.session_id:
            return
        self.session.trace_id = self.session.trace_id or f'session:{self.session.session_id}'
        offset = self.session.archived_sample_count
        points = [p.as_dict() for p in self.session.samples[offset:]]
        try:
            count = await self._io(partial(
                self.archive.append_samples, self.session.trace_id, points,
                start=offset, checkpoint=self.session.as_dict(include_samples=False)))
        except (OSError, sqlite3.Error, ValueError) as err:
            await self._async_archive_failure(err)
            raise HomeAssistantError('Measurement could not be saved; charging stopped. Check storage.') from err
        self.session.archived_sample_count = count

    def _metadata_state(self, *, include_samples: bool) -> dict[str, Any]:
        return {
            'schema_version': DATA_SCHEMA_VERSION,
            'setups': [s.as_dict() for s in self.setups.values()],
            'batteries': [b.as_dict() for b in self.batteries.values()],
            'idle_measurements': [r.as_dict(include_samples=include_samples) for r in self.idle_measurements.values()],
            'calibrations': [r.as_dict(include_samples=include_samples) for r in self.calibrations.values()],
            'charge_history': self.charge_history,
            'session': self.session.as_dict(include_samples=include_samples),
            'selected_setup_id': self.selected_setup_id,
            'selected_battery_id': self.selected_battery_id,
            'selected_quantity': self.selected_quantity,
            'target_percent': self.target_percent,
            'max_session_hours': self.max_session_hours,
            'energy_mode': self.energy_mode,
        }

    async def _async_persist(self) -> None:
        if not self.archive:
            await self.store.async_save(self._metadata_state(include_samples=True))
            return
        await self._async_sync_sample_archive()
        # New records share the run's immutable trace; legacy imported records
        # already have their own immutable trace. No historical reread/rewrite.
        try:
            for records, prefix in ((self.idle_measurements, 'idle'), (self.calibrations, 'calibration')):
                for key, record in records.items():
                    if not record.trace_id:
                        record.trace_id = f'{prefix}:{key}'
                        record.archived_sample_count = await self._io(
                            self.archive.append_samples, record.trace_id,
                            [p.as_dict() for p in record.samples])
                    elif record.trace_id == self.session.trace_id:
                        record.archived_sample_count = self.session.archived_sample_count
            state = deepcopy(self._metadata_state(include_samples=False))
            await self._io(self.archive.save_state, state)
        except (OSError, sqlite3.Error, ValueError) as err:
            await self._async_archive_failure(err)
            raise HomeAssistantError('Measurement metadata could not be saved. Check storage.') from err
        # Release completed historical curves. The current/last run remains a
        # separate cache; its existence is never the only retained copy.
        for record in (*self.calibrations.values(), *self.idle_measurements.values()):
            if record.trace_id and record.archived_sample_count:
                record.samples = []

    def _recover_attempt(self, history: dict) -> CalibrationRecord | None:
        """Add an excluded view of a retained calibration; never alter history."""
        if history.get('mode') == 'idle_measuring':
            self._recover_idle_attempt(history)
            return None
        if history.get('mode') != 'calibrating':
            return None
        raw = history.get('session') or {}
        session_id = history.get('session_id') or raw.get('session_id')
        if not session_id:
            return None
        for record in self.calibrations.values():
            if (record.origin_session_id == session_id or
                    (record.session_started_at == history.get('started_at')
                     and record.setup_id == history.get('setup_id')
                     and record.battery_id == history.get('battery_id')
                     and record.quantity == history.get('quantity', 1))):
                return record
        setup = history.get('setup_snapshot') or raw.get('setup_snapshot') or {}
        battery = history.get('battery_snapshot') or raw.get('battery_snapshot') or {}
        reason = history.get('reason') or raw.get('end_reason') or 'Legacy operation retained without a calibration record'
        # Never create current-revision provenance for a legacy summary that did
        # not record it. Revision zero remains historical/unavailable.
        record = CalibrationRecord(
            calibration_id=f'attempt_{session_id}', origin_session_id=session_id,
            setup_id=history.get('setup_id') or raw.get('setup_id') or '',
            setup_revision=int(setup.get('revision') or 0), setup_snapshot=deepcopy(setup),
            battery_id=history.get('battery_id') or raw.get('battery_id') or '',
            battery_revision=int(battery.get('revision') or 0), battery_snapshot=deepcopy(battery),
            quantity=int(history.get('quantity') or raw.get('quantity') or 1),
            ports=list(raw.get('ports', [])), comment=raw.get('comment', history.get('comment', '')),
            comment_history=deepcopy(raw.get('comment_history', history.get('comment_history', []))),
            session_started_at=raw.get('session_started_at', history.get('started_at')),
            switch_on_at=raw.get('switch_on_at'), charge_started_at=raw.get('charge_started_at'),
            session_finished_at=history.get('finished_at') or raw.get('session_finished_at'),
            switch_off_at=raw.get('switch_off_at'),
            gross_energy_wh=float(raw.get('gross_energy_wh') or 0),
            net_energy_wh=float(raw.get('net_energy_wh') or 0),
            idle_energy_wh=float(raw.get('idle_energy_wh') or 0),
            idle_baseline_power_w=raw.get('idle_baseline_power_w'),
            idle_measurement_ids=list(raw.get('idle_measurement_ids', [])),
            idle_quality=raw.get('idle_quality', 'none'),
            idle_correction_status='applied' if raw.get('idle_baseline_power_w') is not None else 'pending',
            peak_power_w=raw.get('peak_power_w'), peak_net_power_w=raw.get('peak_net_power_w'),
            trace_id=raw.get('trace_id'), archived_sample_count=raw.get('archived_sample_count', 0),
            samples=[MeasurementSample.from_dict(p) for p in raw.get('samples', [])],
            valid=False, invalid_reason=reason, confidence='low',
            completion_status='aborted' if not history.get('valid') else 'recovered_unreviewed', calibration_eligible=False,
            end_method='aborted', source_decision={'source': None, 'usable': False, 'reason': 'aborted'},
            algorithm_version=ALGORITHM_VERSION,
        )
        record.session_duration_seconds = self._seconds_between(record.session_started_at, record.session_finished_at)
        from .analysis import checkpoint_segments
        record.analysis_summary = checkpoint_segments(raw, battery.get('nominal_energy_wh'), record.quantity)
        record.metering_comparison = deepcopy(record.analysis_summary['total'])
        self.calibrations[record.calibration_id] = record
        return record

    def _recover_idle_attempt(self, history: dict) -> None:
        raw = history.get('session') or {}
        sid = history.get('session_id') or raw.get('session_id')
        if not sid:
            return
        if any(r.origin_session_id == sid or
               (r.started_at == history.get('started_at') and r.setup_id == history.get('setup_id'))
               for r in self.idle_measurements.values()):
            return
        context = history.get('setup_snapshot') or raw.get('setup_snapshot') or {}
        reason = history.get('reason') or raw.get('end_reason') or 'Idle measurement interrupted'
        r = IdleMeasurement(measurement_id=f'attempt_{sid}', origin_session_id=sid,
            setup_id=history.get('setup_id') or raw.get('setup_id') or '',
            setup_revision=int(context.get('revision') or 0), setup_snapshot=deepcopy(context),
            mode=raw.get('idle_measurement_mode') or 'fixed',
            started_at=raw.get('session_started_at') or history.get('started_at'),
            finished_at=history.get('finished_at') or raw.get('session_finished_at'),
            gross_energy_wh=float(raw.get('gross_energy_wh') or 0),
            valid=False, reliable=False, confidence='low', invalid_reason=reason, end_reason=reason,
            completion_status='aborted', baseline_method='unavailable',
            trace_id=raw.get('trace_id'), archived_sample_count=raw.get('archived_sample_count',0),
            samples=[MeasurementSample.from_dict(p) for p in raw.get('samples',[])])
        r.duration_seconds = self._seconds_between(r.started_at,r.finished_at)
        r.sample_count = self._sample_count(r)
        self.idle_measurements[r.measurement_id] = r

    def _recover_attempts(self) -> bool:
        before = len(self.calibrations)+len(self.idle_measurements)
        for history in self.charge_history:
            self._recover_attempt(history)
        return len(self.calibrations)+len(self.idle_measurements) != before

    async def async_measurement_details(self, record_type: str, record_id: str) -> dict:
        record = self._measurement(record_type, record_id)
        if not self.archive or not record.trace_id:
            return self.measurement_details(record_type, record_id)
        points = await self._io(self.archive.read_samples, record.trace_id)
        # No await while a temporary hydrated representation is visible.
        previous = record.samples
        try:
            record.samples = [MeasurementSample.from_dict(p) for p in points]
            detail = self.measurement_details(record_type, record_id)
            detail['raw_archive'] = {'trace_id': record.trace_id, 'sample_count': len(points)}
            return detail
        finally:
            record.samples = previous

    async def _async_hydrate(self, record):
        if self.archive and record.trace_id and not record.samples:
            points = await self._io(self.archive.read_samples, record.trace_id)
            record.samples = [MeasurementSample.from_dict(p) for p in points]

    async def _async_correct_pending(self, setup_id: str) -> int:
        """Hydrate one pending curve at a time; keep old raw and analysis history."""
        if not self.archive:
            return self._reprocess_pending_calibrations(setup_id)
        count = 0
        idle = self.idle_summary(setup_id)
        if not idle['usable']:
            return count
        for record in list(self.calibrations.values()):
            if (record.setup_id != setup_id or not record.valid
                    or record.idle_correction_status != 'pending'
                    or self._record_revision_status(record) not in {'native', 'approved'}):
                continue
            await self._async_hydrate(record)
            try:
                if record.samples:
                    self._apply_idle_correction(record, baseline=float(idle['baseline_power_w']),
                                                measurement_ids=idle['measurement_ids'], quality=idle['quality'])
                    count += 1
            finally:
                record.samples = []
        return count

    @serialized_command
    async def async_set_calibration_endpoint(self, record_id: str, endpoint_at: str, *,
                                             reason: str, expected_analysis_revision: int,
                                             actor_id: str | None = None) -> None:
        """Explicit human boundary revision; raw evidence and eligibility are not upgraded."""
        from . import analysis, metering
        async with self._sample_lock:
            self._ensure_idle()
            record = self._measurement('calibration', record_id)
            if record.analysis_revision != expected_analysis_revision:
                raise HomeAssistantError('Analysis changed elsewhere; reopen the measurement.')
            if not reason.strip():
                raise HomeAssistantError('A reason for the endpoint selection is required.')
            target = self._parse_dt(endpoint_at)
            if target is None or target.tzinfo is None:
                raise HomeAssistantError('Endpoint must include a valid date, time and timezone.')
            await self._async_hydrate(record)
            try:
                points = record.samples
                if (not points or target < self._parse_dt(points[0].timestamp)
                        or target > self._parse_dt(points[-1].timestamp)):
                    raise HomeAssistantError('Endpoint must be within the retained measurement.')
                endpoint = self._record_sample_at_or_before(points, endpoint_at)
                old = {key: deepcopy(value) for key,value in record.as_dict(include_samples=False).items()
                       if key not in {'analysis_history', 'validity_history', 'revision_approvals', 'comment_history'}}
                old.update(endpoint_reason=reason.strip(), endpoint_actor=actor_id,
                           replaced_at=self._now_iso(), requested_endpoint_at=endpoint_at)
                record.analysis_history.append(old)
                record.charge_finished_at = endpoint.timestamp
                record.charge_duration_seconds = self._seconds_between(record.charge_started_at or record.switch_on_at,
                                                                         endpoint.timestamp)
                record.end_detected_at = None  # a manual boundary is not automatically detected
                record.end_method = 'manual_endpoint'
                record.manual_override = True
                record.confidence = 'low'
                record.analysis_revision += 1
                record.last_analyzed_at = self._now_iso()
                record.algorithm_version = ALGORITHM_VERSION
                record.metering_comparison = metering.compare(points, endpoint.timestamp,
                    record.idle_baseline_power_w or 0, record.switch_on_at or record.session_started_at)
                self._select_calibration_energy(record, record.source_decision.get('mode', self.energy_mode))
                if record.calibration_eligible is False:
                    record.source_decision['usable'] = False
                record.analysis_summary = analysis.energy_segments(points, endpoint.timestamp,
                    record.idle_baseline_power_w, record.battery_snapshot.get('nominal_energy_wh'),
                    record.quantity, record.switch_on_at or record.session_started_at)
                record.analysis_summary['endpoint_evidence'] = {'method': 'manual_endpoint', 'confirmed': False,
                    'reason': reason.strip(), 'actor_id': actor_id, 'requested_at': endpoint_at,
                    'selected_sample_at': endpoint.timestamp}
                await self._async_save()
            finally:
                if self.archive:
                    record.samples = []
            self._notify()


    @serialized_command
    async def async_archive_export(self):
        """Open a stable full export; iterator must be consumed in an executor.

        The first chunk opens a WAL snapshot while the sample lock is held.
        Later observations continue in separate write transactions.
        """
        from .archive import encoded
        from .const import VERSION
        async with self._sample_lock:
            if not self.archive:
                return iter([encoded(self.export_measurements())])
            if not self._archive_error:
                await self._async_save()
            metadata = deepcopy(self._metadata_state(include_samples=False))
            metadata.update(export_format='battery_charge_manager.measurements',
                export_schema_version=2, exported_at=self._now_iso(),
                integration_version=VERSION, algorithm_version=ALGORITHM_VERSION,
                time_zone=getattr(getattr(self.hass,'config',None),'time_zone','UTC'),
                retention={'automatic_deletion':False, 'charge_history_limit':None,
                    'scope':'all_retained_data', 'raw_archive_required':True,
                    'trace_note':'All received data since 0.4.2; older compaction cannot be reversed.'})
            if self._archive_error or self._pending_observations:
                metadata['uncommitted_memory'] = {
                    'storage_error':self._archive_error,
                    'trace_id':self.session.trace_id,
                    'sample_offset':self.session.archived_sample_count,
                    'samples':[p.as_dict() for p in self.session.samples[self.session.archived_sample_count:]],
                    'observations':deepcopy(self._pending_observations)}
            generator = self.archive.iter_export(metadata)
            first = await self._io(next, generator)
            # A wrapper with finally ensures reader connection cleanup on disconnect.
            def stream():
                try:
                    yield first
                    yield from generator
                finally:
                    generator.close()
            return stream()

    async def async_raw_measurement_page(self, kind: str, record_id: str, offset: int = 0, limit: int = 500) -> dict:
        """Read original full-precision observations, independently of chart thinning."""
        if offset < 0 or not 1 <= limit <= 1000:
            raise HomeAssistantError('Invalid raw data page (maximum 1000 observations).')
        if kind == 'session':
            if record_id != self.session.session_id:
                raise HomeAssistantError('Unknown session')
            record = self.session
        else:
            record = self._measurement(kind,record_id)
        total = self._sample_count(record)
        if self.archive and record.trace_id:
            points = await self._io(self.archive.read_samples, record.trace_id, offset, limit)
        else:
            points = [p.as_dict() for p in record.samples[offset:offset+limit]]
        return {'trace_id':record.trace_id, 'sample_count':total, 'offset':offset,
                'next_offset':offset+len(points) if offset+len(points)<total else None, 'samples':points}
