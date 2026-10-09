"""Pilot orchestration: reference acquisition, frozen decisions and human review."""
from copy import deepcopy
from hashlib import sha256
import json

from homeassistant.exceptions import HomeAssistantError

from . import rest_reference, metering
from .const import ALGORITHM_VERSION
from .models import CalibrationRecord, ChargeSession
from .pilot_models import RestMeasurement
from .persistence import serialized_command


class PilotWorkflow:
    @serialized_command
    async def async_set_energy_basis(self, basis):
        if basis not in ('gross', 'no_load_corrected'):
            raise HomeAssistantError('Unknown energy basis')
        self.energy_basis = basis
        await self._async_save()
        self._notify()

    def _profile(self, setup=None, battery=None, quantity=None):
        setup, battery = setup or self.active_setup, battery or self.active_battery
        quantity = self.selected_quantity if quantity is None else quantity
        if not setup or not battery:
            return None
        return rest_reference.profile_key(setup.setup_id, setup.revision,
            battery.battery_id, battery.revision, quantity, setup.ports_for_quantity(quantity))

    def _decision_fingerprint(self, record):
        setup, battery = self.setups.get(record.setup_id), self.batteries.get(record.battery_id)
        decision = dict(analysis_revision=record.analysis_revision, algorithm_version=record.algorithm_version,
            profile=self._profile(setup, battery, record.quantity) if setup and battery else None,
            record_profile=rest_reference.profile_key(record.setup_id, record.setup_revision,
                record.battery_id, record.battery_revision, record.quantity, record.ports),
            revision_approvals=record.revision_approvals)
        if isinstance(record, CalibrationRecord):
            decision.update(energy_source=record.energy_source, energy_basis=record.energy_basis,
                endpoint=record.charge_finished_at, idle_ids=record.idle_measurement_ids,
                baseline=float(round(record.idle_baseline_power_w, 6)) if record.idle_baseline_power_w is not None else None,
                net_energy_wh=float(round(record.net_energy_wh, 6)), gross_energy_wh=float(round(record.gross_energy_wh, 6)),
                source_decision=record.source_decision,
                comparison=record.metering_comparison, pilot=record.pilot)
        else:
            decision.update(confirmed_at=record.confirmed_at, statistics=record.statistics)
        return sha256(json.dumps(decision, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

    def _usage_current(self, record):
        return bool(record.valid and record.usage_approval == 'approved' and record.approval_history
                    and record.approval_history[-1].get('approved')
                    and record.approval_history[-1].get('fingerprint') == self._decision_fingerprint(record))

    def _invalidate_usage(self, record, reason):
        if not hasattr(record, 'usage_approval'):
            return
        if record.usage_approval == 'approved':
            record.approval_history.append(dict(changed_at=self._now_iso(), approved=False,
                reason=reason, actor_id=None, automatic=True))
        record.usage_approval = 'pending'
        record.usage_revision += 1

    def rest_reference_summary(self):
        profile = self._profile()
        matches = [r for r in self.rest_measurements.values()
                   if rest_reference.profile_key(r.setup_id, r.setup_revision, r.battery_id,
                        r.battery_revision, r.quantity, r.ports) == profile]
        approved = [r for r in matches if self._usage_current(r) and r.statistics.get('eligible')]
        approved.sort(key=lambda r:r.session_finished_at or '')
        reference = approved[-1].as_dict(include_samples=False) if approved else None
        return dict(reference=reference, count=len(matches), approved_count=len(approved))

    def _pilot_snapshot(self, mode, setup, battery, source_decision):
        basis = source_decision.get('energy_basis', self.energy_basis)
        if mode == 'rest_measuring':
            basis = 'gross'
        idle = source_decision.get('idle_reference') or self.idle_summary(setup.setup_id)
        if basis == 'no_load_corrected' and not idle.get('usable'):
            raise HomeAssistantError('Corrected pilot energy requires a reliable current no-load reference')
        reference = self.rest_reference_summary()['reference'] if battery else None
        known = self.calibration_summary(setup.setup_id, battery.battery_id, self.selected_quantity) if battery else {}
        from .const import DEFAULT_CALIBRATION_ABSOLUTE_MAX_WH, DEFAULT_CALIBRATION_MAX_FACTOR
        limit = (known.get("median_net_energy_wh") or 0) * DEFAULT_CALIBRATION_MAX_FACTOR or DEFAULT_CALIBRATION_ABSOLUTE_MAX_WH
        return dict(calibration_safety_limit_wh=limit, energy_basis=basis, idle_reference=deepcopy(idle) if basis == 'no_load_corrected' else {},
            rest_reference=deepcopy(reference), confirmed_at=None, proposal={},
            approval_policy='manual', algorithm_version=ALGORITHM_VERSION,
            profile=self._profile(setup, battery) if battery else None)

    @serialized_command
    async def async_prepare_rest_reference(self):
        self._ensure_idle()
        setup, battery = self._require_setup(), self._require_battery()
        if not setup.power_sensor:
            raise HomeAssistantError('Full-battery reference requires an active-power sensor')
        await self._async_begin_session(mode='rest_measuring', setup=setup, battery=battery,
            target_energy_wh=None, source_decision={'mode':'power_reported', 'source':'power_reported'})

    @serialized_command
    async def async_confirm_rest_reference(self):
        async with self._sample_lock:
            if self.session.mode != 'rest_measuring':
                raise HomeAssistantError('No full-battery reference is being prepared')
            if self.session.pilot.get('confirmed_at'):
                raise HomeAssistantError('The reference window has already started')
            self.session.pilot['confirmed_at'] = self._now_iso()
            self.session.phase = 'rest_warmup'
            await self._async_save()
            self._notify()

    async def _evaluate_pilot(self, now):
        if self.session.mode == 'rest_measuring':
            confirmed = self.session.pilot.get('confirmed_at')
            if not confirmed:
                self.session.phase = 'rest_preparing'
                return False
            seconds = self._elapsed_seconds(confirmed, now)
            self.session.phase = 'rest_warmup' if seconds < 300 else 'rest_recording'
            if seconds >= 2100:
                await self._complete_rest_reference()
                return True
            return False
        # Calibration proposals carry no switching authority. Safety checks are
        # still enforced in the shared acquisition/evaluation path.
        if self.session.mode == 'calibrating':
            reference = self.session.pilot.get('rest_reference') or {}
            proposal = rest_reference.suggest(self.session.samples, reference.get('statistics'))
            self.session.pilot['proposal'] = proposal
            if proposal['status'] == 'suggested':
                self.session.phase = 'rest_review'
            return False
        return False

    def _rest_from_session(self, session, *, completed=False):
        sid = session.session_id
        existing = next((r for r in self.rest_measurements.values() if r.origin_session_id == sid), None)
        if existing:
            return existing
        setup, battery = session.setup_snapshot, session.battery_snapshot
        stats = rest_reference.assess(session.samples, session.pilot.get('confirmed_at'), session.last_sample_at)
        record = RestMeasurement(measurement_id=f'rest_{sid}', setup_id=session.setup_id,
            setup_revision=setup.get('revision', 0), battery_id=session.battery_id,
            battery_revision=battery.get('revision', 0), quantity=session.quantity, ports=list(session.ports),
            setup_snapshot=deepcopy(setup), battery_snapshot=deepcopy(battery),
            session_started_at=session.session_started_at, confirmed_at=session.pilot.get('confirmed_at'),
            session_finished_at=session.session_finished_at,
            duration_seconds=self._seconds_between(session.session_started_at, session.session_finished_at),
            statistics=stats, origin_session_id=sid, switch_off_confirmed=bool(session.switch_off_at),
            valid=completed and bool(session.switch_off_at),
            invalid_reason='' if completed and session.switch_off_at else session.end_reason or 'Interrupted reference',
            completion_status='completed' if completed and session.switch_off_at else 'aborted',
            trace_id=session.trace_id, archived_sample_count=session.archived_sample_count,
            samples=list(session.samples))
        self.rest_measurements[record.measurement_id] = record
        return record

    async def _complete_rest_reference(self):
        self._finalizing = True
        try:
            setup = self._shutdown_setup()
            confirmed = await self._async_switch_off_checked(setup) if setup else False
            self._stop_tracking()
            self.session.session_finished_at = self._now_iso()
            self.session.switch_off_at = self.session.session_finished_at if confirmed else None
            self.session.end_reason = 'Full-battery reference retained for review' if confirmed else 'Switch OFF not confirmed'
            self.session.valid = confirmed
            self.session.phase = 'finished' if confirmed else 'error'
            record = self._rest_from_session(self.session, completed=True)
            self.session.completion_record_id = record.measurement_id
            self._append_charge_history(valid=confirmed, reason=self.session.end_reason)
            self.session.mode = 'idle'
            await self._async_save()
            self._notify()
        finally:
            self._finalizing = False

    def _rest_row(self, record):
        row = record.as_dict(include_samples=False)
        current = self._profile(self.setups.get(record.setup_id), self.batteries.get(record.battery_id), record.quantity)
        match = current == rest_reference.profile_key(record.setup_id, record.setup_revision,
            record.battery_id, record.battery_revision, record.quantity, record.ports)
        row.update(record_type='rest', used=match and self._usage_current(record),
            usage_reason='revoked' if record.usage_approval == 'revoked' else 'used' if match and self._usage_current(record) else 'pending_review' if match else 'historical',
            revision_status='native' if match else 'historical',
            sample_count=self._sample_count(record), has_trace=self._sample_count(record) > 0,
            usage_approval_current=self._usage_current(record), decision_fingerprint=self._decision_fingerprint(record),
            usage_approval_block_reason=self._usage_approval_block_reason(record),
            current_setup_revision=self.setups[record.setup_id].revision if record.setup_id in self.setups else None,
            current_battery_revision=self.batteries[record.battery_id].revision if record.battery_id in self.batteries else None)
        return row

    def _usage_approval_block_reason(self, record):
        """Use the same approval prerequisites in the UI and command handler."""
        if not record.valid:
            return 'invalid_measurement'
        if isinstance(record, RestMeasurement):
            current = self._profile(self.setups.get(record.setup_id), self.batteries.get(record.battery_id), record.quantity)
            profile = rest_reference.profile_key(record.setup_id, record.setup_revision,
                record.battery_id, record.battery_revision, record.quantity, record.ports)
            if not record.switch_off_confirmed or not record.statistics.get('eligible') or current != profile:
                return 'rest_not_usable'
        else:
            choice = self._record_source_choice(record)
            if (not record.charge_finished_at or not record.switch_off_at
                    or record.calibration_eligible is False or not choice.get('source')
                    or choice['source'] != record.energy_source
                    or self._record_revision_status(record) not in ('native', 'approved')
                    or self._invalid_idle_references(record)):
                return 'calibration_not_usable'
        return None

    @serialized_command
    async def async_set_usage_approval(self, kind, record_id, approved, reason,
                                       expected_analysis_revision, actor_id=None, *, expected_fingerprint=None, expected_usage_revision=None):
        self._ensure_idle()
        if kind not in ('calibration', 'rest'):
            raise HomeAssistantError('Only calibrations and full-battery references require use approval')
        record = self._measurement(kind, record_id)
        if record.analysis_revision != expected_analysis_revision:
            raise HomeAssistantError('Analysis changed; reopen the measurement')
        if expected_usage_revision is not None and expected_usage_revision != record.usage_revision:
            raise HomeAssistantError('Use decision changed; reopen the measurement')
        if expected_fingerprint is not None and expected_fingerprint != self._decision_fingerprint(record):
            raise HomeAssistantError('Decision or profile changed; reopen the measurement')
        if not reason.strip():
            raise HomeAssistantError('A reason for the review decision is required')
        if approved:
            blocker = self._usage_approval_block_reason(record)
            if blocker:
                raise HomeAssistantError({
                    'invalid_measurement': 'Invalid measurements cannot be approved',
                    'rest_not_usable': 'A complete, stable reference for the exact current profile is required',
                    'calibration_not_usable': 'Select a usable charge interval with confirmed switch-off before approval',
                }[blocker])
        record.usage_approval = 'approved' if approved else 'revoked'
        record.usage_revision += 1
        record.approval_history.append(dict(changed_at=self._now_iso(), actor_id=actor_id,
            reason=reason.strip(), approved=bool(approved), fingerprint=self._decision_fingerprint(record),
            analysis_revision=record.analysis_revision, algorithm_version=record.algorithm_version))
        await self._async_save()
        self._notify()

    @serialized_command
    async def async_set_usb_comparison(self, record_id, energy_wh, reason,
                                      expected_analysis_revision, actor_id=None):
        self._ensure_idle()
        record = self._measurement('calibration', record_id)
        if record.analysis_revision != expected_analysis_revision:
            raise HomeAssistantError('Analysis changed; reopen the measurement')
        if not metering.finite(energy_wh) or not reason.strip():
            raise HomeAssistantError('A finite USB end energy and comparison note are required')
        previous = deepcopy(record.usb_comparison)
        record.usb_comparison = dict(energy_wh=float(energy_wh), interval='full_run',
            reason=reason.strip(), actor_id=actor_id, changed_at=self._now_iso(), previous=previous)
        await self._async_save()
        self._notify()

    def _pilot_finish_record(self, record):
        if self.session.energy_source != 'power_reported':
            return
        record.pilot = deepcopy(self.session.pilot)
        record.energy_basis = record.pilot['energy_basis']
        record.charge_finished_at = None
        record.charge_duration_seconds = None
        record.end_detected_at = None
        record.end_method = 'pending_review'
        record.calibration_eligible = False
        record.completion_status = 'pending_review' if record.valid else 'manual_unusable'
        self.session.charge_finished_at = None
        self.session.end_detected_at = None
        record.source_decision['usable'] = False
        record.analysis_summary = {}

    def _reanalyze_pilot(self, record, actor_id):
        if self.energy_mode != 'power_reported':
            raise HomeAssistantError('Select reported-power pilot mode to reanalyze a pilot record')
        if not record.samples:
            raise HomeAssistantError('A retained power trace is required')
        idle = self.idle_summary(record.setup_id)
        if self.energy_basis == 'no_load_corrected' and not idle.get('usable'):
            raise HomeAssistantError('A reliable no-load reference is required')
        old = record.as_dict(include_samples=False)
        old.pop('analysis_history', None)
        old.update(replaced_at=self._now_iso(), replaced_by=actor_id)
        record.analysis_history.append(old)
        self._invalidate_usage(record, 'Source or energy basis reanalyzed')
        evidence = record.analysis_summary.get('endpoint_evidence', {})
        audited_endpoint = (record.end_method == 'manual_endpoint'
            and evidence.get('method') == 'manual_endpoint' and evidence.get('reason')
            and evidence.get('selected_sample_at') == record.charge_finished_at)
        if record.energy_source != 'power_reported' and not audited_endpoint:
            record.charge_finished_at = None
            record.charge_duration_seconds = None
            record.end_detected_at = None
            record.candidate_end_at = None
            record.end_method = 'pending_review'
        if record.completion_status not in ('aborted', 'recovered_unreviewed'):
            record.completion_status = 'pending_review'

        record.energy_basis = self.energy_basis
        record.idle_baseline_power_w = float(idle['baseline_power_w']) if self.energy_basis == 'no_load_corrected' else 0
        record.idle_measurement_ids = list(idle['measurement_ids']) if self.energy_basis == 'no_load_corrected' else []
        record.idle_correction_status = 'applied'
        record.pilot.update(energy_basis=self.energy_basis, idle_reference=deepcopy(idle) if record.idle_measurement_ids else {})
        record.analysis_revision += 1
        record.algorithm_version = ALGORITHM_VERSION
        record.last_analyzed_at = self._now_iso()
        record.metering_comparison = metering.compare(record.samples,
            record.charge_finished_at or record.samples[-1].timestamp, record.idle_baseline_power_w,
            record.samples[0].timestamp)
        self._select_calibration_energy(record, 'power_reported')
        record.calibration_eligible = bool(record.valid and record.switch_off_at and record.charge_finished_at
            and record.source_decision.get('usable') and record.completion_status not in ('aborted', 'recovered_unreviewed'))
        record.analysis_summary = {}
