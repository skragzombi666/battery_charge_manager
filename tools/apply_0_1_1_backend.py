from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def write(relative: str, content: str) -> None:
    (ROOT / relative).write_text(content, encoding="utf-8")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return content.replace(old, new, 1)


def patch_const() -> None:
    path = "custom_components/battery_charge_manager/const.py"
    content = read(path)
    content = replace_once(
        content,
        'VERSION = "0.1.0"\nALGORITHM_VERSION = "0.1.0"',
        'VERSION = "0.1.1"\nALGORITHM_VERSION = "0.1.1"',
        "const version",
    )
    content = replace_once(
        content,
        "DATA_SCHEMA_VERSION = 2",
        "DATA_SCHEMA_VERSION = 3",
        "data schema version",
    )
    content = replace_once(
        content,
        'IDLE_MODE_FIXED = "fixed"\nIDLE_MODE_AUTOMATIC = "automatic"',
        'IDLE_MODE_FIXED = "fixed"\nIDLE_MODE_AUTOMATIC = "automatic"\n\n'
        'IDLE_CORRECTION_PENDING = "pending"\n'
        'IDLE_CORRECTION_APPLIED = "applied"',
        "idle correction constants",
    )
    write(path, content)


def patch_manifest() -> None:
    path = "custom_components/battery_charge_manager/manifest.json"
    data = json.loads(read(path))
    if data.get("version") != "0.1.0":
        raise RuntimeError(
            f"manifest version: expected 0.1.0, got {data.get('version')}"
        )
    data["version"] = "0.1.1"
    write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def patch_models() -> None:
    path = "custom_components/battery_charge_manager/models.py"
    content = read(path)
    content = replace_once(
        content,
        "    DEFAULT_MAX_POWER_W,\n    IDLE_MODE_AUTOMATIC,",
        "    DEFAULT_MAX_POWER_W,\n    IDLE_CORRECTION_APPLIED,\n    IDLE_MODE_AUTOMATIC,",
        "models constant import",
    )
    content = replace_once(
        content,
        '    idle_baseline_power_w: float = 0.0\n'
        '    idle_measurement_ids: list[str] = field(default_factory=list)\n'
        '    idle_quality: str = "none"\n'
        '    energy_at_detection_wh: float | None = None',
        '    idle_baseline_power_w: float | None = None\n'
        '    idle_measurement_ids: list[str] = field(default_factory=list)\n'
        '    idle_quality: str = "none"\n'
        '    idle_correction_status: str = IDLE_CORRECTION_APPLIED\n'
        '    analysis_revision: int = 1\n'
        '    last_analyzed_at: str | None = None\n'
        '    analysis_history: list[dict[str, Any]] = field(default_factory=list)\n'
        '    energy_at_detection_wh: float | None = None',
        "calibration correction fields",
    )
    content = replace_once(
        content,
        '            "idle_baseline_power_w": round(self.idle_baseline_power_w, 6),\n'
        '            "idle_measurement_ids": self.idle_measurement_ids,\n'
        '            "idle_quality": self.idle_quality,\n'
        '            "energy_at_detection_wh": self.energy_at_detection_wh,',
        '            "idle_baseline_power_w": (\n'
        '                round(self.idle_baseline_power_w, 6)\n'
        '                if self.idle_baseline_power_w is not None\n'
        '                else None\n'
        '            ),\n'
        '            "idle_measurement_ids": self.idle_measurement_ids,\n'
        '            "idle_quality": self.idle_quality,\n'
        '            "idle_correction_status": self.idle_correction_status,\n'
        '            "analysis_revision": self.analysis_revision,\n'
        '            "last_analyzed_at": self.last_analyzed_at,\n'
        '            "analysis_history": self.analysis_history,\n'
        '            "energy_at_detection_wh": self.energy_at_detection_wh,',
        "calibration serialization",
    )
    content = replace_once(
        content,
        '            idle_baseline_power_w=float(\n'
        '                data.get("idle_baseline_power_w", 0.0)\n'
        '            ),\n'
        '            idle_measurement_ids=[\n'
        '                str(item) for item in data.get("idle_measurement_ids", [])\n'
        '            ],\n'
        '            idle_quality=str(data.get("idle_quality", "none")),\n'
        '            energy_at_detection_wh=_float_or_none(',
        '            idle_baseline_power_w=_float_or_none(\n'
        '                data.get("idle_baseline_power_w")\n'
        '            ),\n'
        '            idle_measurement_ids=[\n'
        '                str(item) for item in data.get("idle_measurement_ids", [])\n'
        '            ],\n'
        '            idle_quality=str(data.get("idle_quality", "none")),\n'
        '            idle_correction_status=str(\n'
        '                data.get("idle_correction_status", IDLE_CORRECTION_APPLIED)\n'
        '            ),\n'
        '            analysis_revision=_int_or(data.get("analysis_revision"), 1),\n'
        '            last_analyzed_at=data.get("last_analyzed_at"),\n'
        '            analysis_history=[\n'
        '                dict(item) for item in data.get("analysis_history", [])\n'
        '            ],\n'
        '            energy_at_detection_wh=_float_or_none(',
        "calibration deserialization",
    )
    content = replace_once(
        content,
        '    idle_baseline_power_w: float = 0.0\n'
        '    idle_measurement_ids: list[str] = field(default_factory=list)',
        '    idle_baseline_power_w: float | None = None\n'
        '    idle_measurement_ids: list[str] = field(default_factory=list)',
        "session nullable baseline",
    )
    content = replace_once(
        content,
        '            idle_baseline_power_w=float(\n'
        '                data.get("idle_baseline_power_w", 0.0)\n'
        '            ),\n'
        '            idle_measurement_ids=[',
        '            idle_baseline_power_w=_float_or_none(\n'
        '                data.get("idle_baseline_power_w")\n'
        '            ),\n'
        '            idle_measurement_ids=[',
        "session baseline deserialization",
    )
    write(path, content)


def patch_manager() -> None:
    path = "custom_components/battery_charge_manager/manager.py"
    content = read(path)
    content = replace_once(
        content,
        "    IDLE_MODE_AUTOMATIC,\n    IDLE_MODE_FIXED,",
        "    IDLE_CORRECTION_APPLIED,\n    IDLE_CORRECTION_PENDING,\n"
        "    IDLE_MODE_AUTOMATIC,\n    IDLE_MODE_FIXED,",
        "manager correction constant imports",
    )
    content = replace_once(
        content,
        '    async def async_start_calibration(self) -> None:\n'
        '        """Start automatic full-charge calibration."""\n'
        '        self._ensure_idle()\n'
        '        setup = self._require_setup()\n'
        '        battery = self._require_battery()\n'
        '        idle = self.idle_summary(setup.setup_id)\n'
        '        if idle["reliable_count"] == 0:\n'
        '            raise HomeAssistantError(\n'
        '                "A reliable idle measurement is required before calibration"\n'
        '            )\n'
        '        await self._async_begin_session(',
        '    async def async_start_calibration(self) -> None:\n'
        '        """Start automatic full-charge calibration with deferred correction."""\n'
        '        self._ensure_idle()\n'
        '        setup = self._require_setup()\n'
        '        battery = self._require_battery()\n'
        '        await self._async_begin_session(',
        "allow calibration without idle measurement",
    )
    content = replace_once(
        content,
        '        if mode == IDLE_MODE_FIXED:\n'
        '            duration_minutes = float(duration_minutes or DEFAULT_IDLE_FIXED_MINUTES)\n'
        '            if duration_minutes < 5 or duration_minutes > 24 * 60:\n'
        '                raise HomeAssistantError("Fixed duration must be 5 to 1440 minutes")',
        '        if mode == IDLE_MODE_FIXED:\n'
        '            duration_minutes = max(\n'
        '                5.0,\n'
        '                float(duration_minutes or DEFAULT_IDLE_FIXED_MINUTES),\n'
        '            )\n'
        '            if duration_minutes > 24 * 60:\n'
        '                raise HomeAssistantError("Fixed duration must be at most 1440 minutes")',
        "clamp fixed idle duration",
    )
    content = replace_once(
        content,
        '        idle_summary = (\n'
        '            self._empty_idle_summary()\n'
        '            if mode == SESSION_IDLE_MEASURING\n'
        '            else self.idle_summary(setup.setup_id)\n'
        '        )\n'
        '        phase = (',
        '        idle_summary = (\n'
        '            self._empty_idle_summary()\n'
        '            if mode == SESSION_IDLE_MEASURING\n'
        '            else self.idle_summary(setup.setup_id)\n'
        '        )\n'
        '        has_reliable_idle = bool(idle_summary.get("reliable_count"))\n'
        '        idle_baseline = (\n'
        '            float(idle_summary["baseline_power_w"])\n'
        '            if has_reliable_idle\n'
        '            and idle_summary.get("baseline_power_w") is not None\n'
        '            else None\n'
        '        )\n'
        '        phase = (',
        "session reliable baseline selection",
    )
    content = replace_once(
        content,
        '            idle_baseline_power_w=float(\n'
        '                idle_summary.get("baseline_power_w") or 0.0\n'
        '            ),\n'
        '            idle_measurement_ids=list(\n'
        '                idle_summary.get("measurement_ids") or []\n'
        '            ),\n'
        '            idle_quality=str(idle_summary.get("quality") or QUALITY_NONE),',
        '            idle_baseline_power_w=idle_baseline,\n'
        '            idle_measurement_ids=(\n'
        '                list(idle_summary.get("measurement_ids") or [])\n'
        '                if has_reliable_idle\n'
        '                else []\n'
        '            ),\n'
        '            idle_quality=(\n'
        '                str(idle_summary.get("quality") or QUALITY_NONE)\n'
        '                if has_reliable_idle\n'
        '                else QUALITY_NONE\n'
        '            ),',
        "session baseline persistence",
    )
    content = replace_once(
        content,
        '            baseline = (\n'
        '                0.0\n'
        '                if self.session.mode == SESSION_IDLE_MEASURING\n'
        '                else self.session.idle_baseline_power_w\n'
        '            )',
        '            baseline = (\n'
        '                0.0\n'
        '                if self.session.mode == SESSION_IDLE_MEASURING\n'
        '                else (self.session.idle_baseline_power_w or 0.0)\n'
        '            )',
        "nullable sampling baseline",
    )
    content = replace_once(
        content,
        '            idle_baseline = self.session.idle_baseline_power_w\n'
        '            endpoint_idle = idle_baseline * max(\n',
        '            idle_baseline = self.session.idle_baseline_power_w\n'
        '            baseline_for_math = idle_baseline or 0.0\n'
        '            endpoint_idle = baseline_for_math * max(\n',
        "nullable endpoint baseline",
    )
    content = replace_once(
        content,
        '                idle_quality=self.session.idle_quality,\n'
        '                energy_at_detection_wh=self.session.net_energy_wh,',
        '                idle_quality=self.session.idle_quality,\n'
        '                idle_correction_status=(\n'
        '                    IDLE_CORRECTION_APPLIED\n'
        '                    if idle_baseline is not None\n'
        '                    else IDLE_CORRECTION_PENDING\n'
        '                ),\n'
        '                analysis_revision=1,\n'
        '                last_analyzed_at=detected_at,\n'
        '                energy_at_detection_wh=self.session.net_energy_wh,',
        "calibration correction metadata",
    )
    content = replace_once(
        content,
        '                confidence=confidence,\n'
        '                synchrony=self._estimate_synchrony(charge_duration),',
        '                confidence=(\n'
        '                    confidence\n'
        '                    if idle_baseline is not None\n'
        '                    else CONFIDENCE_LOW\n'
        '                ),\n'
        '                synchrony=self._estimate_synchrony(charge_duration),',
        "pending calibration confidence",
    )
    content = replace_once(
        content,
        '            self.idle_measurements[record.measurement_id] = record\n'
        '            self.session.switch_off_at = switch_off_at',
        '            self.idle_measurements[record.measurement_id] = record\n'
        '            if record.valid and record.reliable:\n'
        '                self._reprocess_pending_calibrations(setup.setup_id)\n'
        '            self.session.switch_off_at = switch_off_at',
        "automatic pending recalculation",
    )
    content = replace_once(
        content,
        '        records = [\n'
        '            item\n'
        '            for item in self.calibrations.values()\n'
        '            if item.setup_id == setup_id\n'
        '            and item.setup_revision == setup.revision\n'
        '            and item.battery_id == battery_id\n'
        '            and item.battery_revision == battery.revision\n'
        '            and item.quantity == quantity\n'
        '            and item.valid\n'
        '            and item.net_energy_wh > 0\n'
        '        ]\n'
        '        records.sort(key=lambda item: item.session_started_at or "")\n'
        '        trusted = [',
        '        all_records = [\n'
        '            item\n'
        '            for item in self.calibrations.values()\n'
        '            if item.setup_id == setup_id\n'
        '            and item.setup_revision == setup.revision\n'
        '            and item.battery_id == battery_id\n'
        '            and item.battery_revision == battery.revision\n'
        '            and item.quantity == quantity\n'
        '            and item.valid\n'
        '            and item.net_energy_wh > 0\n'
        '        ]\n'
        '        all_records.sort(key=lambda item: item.session_started_at or "")\n'
        '        pending = [\n'
        '            item\n'
        '            for item in all_records\n'
        '            if item.idle_correction_status != IDLE_CORRECTION_APPLIED\n'
        '        ]\n'
        '        records = [\n'
        '            item\n'
        '            for item in all_records\n'
        '            if item.idle_correction_status == IDLE_CORRECTION_APPLIED\n'
        '        ]\n'
        '        trusted = [',
        "exclude pending calibrations from operation",
    )
    content = replace_once(
        content,
        '            "count": len(used),\n'
        '            "total_current_count": len(records),\n'
        '            "trusted_count": len(trusted),',
        '            "count": len(used),\n'
        '            "total_current_count": len(all_records),\n'
        '            "pending_count": len(pending),\n'
        '            "applied_count": len(records),\n'
        '            "trusted_count": len(trusted),',
        "calibration summary counts",
    )
    content = replace_once(
        content,
        '            "all_current_record_ids": [item.calibration_id for item in records],\n'
        '            "confidence_counts": {\n'
        '                level: sum(1 for item in records if item.confidence == level)',
        '            "all_current_record_ids": [\n'
        '                item.calibration_id for item in all_records\n'
        '            ],\n'
        '            "confidence_counts": {\n'
        '                level: sum(1 for item in all_records if item.confidence == level)',
        "calibration summary all records",
    )
    content = replace_once(
        content,
        '            "total_current_count": 0,\n'
        '            "trusted_count": 0,',
        '            "total_current_count": 0,\n'
        '            "pending_count": 0,\n'
        '            "applied_count": 0,\n'
        '            "trusted_count": 0,',
        "empty calibration correction counts",
    )

    marker = (
        '            auto_max_minutes=auto_max_minutes,\n'
        '        )\n\n'
        '    async def _async_begin_session(\n'
    )
    methods = """            auto_max_minutes=auto_max_minutes,
        )

    async def async_reprocess_pending_calibrations(self, setup_id: str) -> int:
        \"\"\"Apply a newly available reliable baseline to pending records.\"\"\"
        corrected = self._reprocess_pending_calibrations(setup_id)
        if corrected:
            await self._async_save()
            self._notify()
        return corrected

    def _reprocess_pending_calibrations(self, setup_id: str) -> int:
        \"\"\"Recalculate trace-backed pending calibrations for one revision.\"\"\"
        setup = self.setups.get(setup_id)
        if setup is None:
            return 0
        idle = self.idle_summary(setup_id)
        if not idle.get(\"reliable_count\") or idle.get(\"baseline_power_w\") is None:
            return 0
        baseline = float(idle[\"baseline_power_w\"])
        measurement_ids = list(idle.get(\"measurement_ids\") or [])
        quality = str(idle.get(\"quality\") or QUALITY_NONE)
        corrected = 0
        for record in self.calibrations.values():
            if (
                record.setup_id != setup_id
                or record.setup_revision != setup.revision
                or record.idle_correction_status != IDLE_CORRECTION_PENDING
                or not record.valid
                or not record.samples
            ):
                continue
            self._apply_idle_correction(
                record,
                baseline=baseline,
                measurement_ids=measurement_ids,
                quality=quality,
            )
            corrected += 1
        return corrected

    def _apply_idle_correction(
        self,
        record: CalibrationRecord,
        *,
        baseline: float,
        measurement_ids: list[str],
        quality: str,
    ) -> None:
        \"\"\"Recalculate derived values while retaining the raw trace.\"\"\"
        record.analysis_history.append(
            {
                \"analysis_revision\": record.analysis_revision,
                \"analyzed_at\": record.last_analyzed_at,
                \"idle_correction_status\": record.idle_correction_status,
                \"idle_baseline_power_w\": record.idle_baseline_power_w,
                \"idle_measurement_ids\": list(record.idle_measurement_ids),
                \"gross_energy_wh\": record.gross_energy_wh,
                \"idle_energy_wh\": record.idle_energy_wh,
                \"net_energy_wh\": record.net_energy_wh,
                \"charge_started_at\": record.charge_started_at,
                \"charge_finished_at\": record.charge_finished_at,
                \"charge_duration_seconds\": record.charge_duration_seconds,
                \"end_method\": record.end_method,
                \"confidence\": record.confidence,
                \"algorithm_version\": record.algorithm_version,
            }
        )
        record.analysis_history = record.analysis_history[-10:]
        samples = sorted(record.samples, key=lambda item: item.timestamp)
        reference_at = record.switch_on_at or record.session_started_at
        peak_net = 0.0
        for sample in samples:
            elapsed = self._seconds_between(reference_at, sample.timestamp)
            sample.idle_energy_wh = max(0.0, baseline * elapsed / 3600.0)
            sample.net_energy_wh = max(
                0.0,
                sample.gross_energy_wh - sample.idle_energy_wh,
            )
            sample.net_power_w = (
                max(0.0, sample.power_w - baseline)
                if sample.power_w is not None
                else None
            )
            peak_net = max(peak_net, sample.net_power_w or 0.0)
        record.samples = samples
        start_sample = next(
            (
                item
                for item in samples
                if item.net_power_w is not None and item.net_power_w >= 0.35
            ),
            None,
        )
        if start_sample is None:
            start_sample = next(
                (item for item in samples if item.net_energy_wh >= 0.02),
                samples[0],
            )
        charge_started_at = start_sample.timestamp
        significance = max(0.15, peak_net * 0.05)
        significant = [
            item
            for item in samples
            if item.net_power_w is not None and item.net_power_w > significance
        ]
        endpoint = significant[-1] if significant else samples[-1]
        endpoint_dt = self._parse_dt(endpoint.timestamp)
        last_dt = self._parse_dt(samples[-1].timestamp)
        confirmed = False
        if endpoint_dt is not None and last_dt is not None and last_dt > endpoint_dt:
            tail = [
                item
                for item in samples
                if (self._parse_dt(item.timestamp) or endpoint_dt) >= endpoint_dt
            ]
            span = self._seconds_between(endpoint.timestamp, tail[-1].timestamp)
            gain = max(0.0, tail[-1].net_energy_wh - endpoint.net_energy_wh)
            average_power = gain / (span / 3600.0) if span > 0 else float(\"inf\")
            tolerance = max(0.05, endpoint.net_energy_wh * 0.01)
            plateau_threshold = max(0.12, peak_net * 0.05)
            confirmed = bool(
                span >= DEFAULT_END_CONFIRM_MINUTES * 60
                and gain <= tolerance
                and average_power <= plateau_threshold
            )
        if not confirmed:
            endpoint = self._record_sample_at_or_before(
                samples,
                record.charge_finished_at
                or record.session_finished_at
                or samples[-1].timestamp,
            ) or samples[-1]
        record.charge_started_at = charge_started_at
        record.charge_finished_at = endpoint.timestamp
        record.charge_duration_seconds = self._seconds_between(
            charge_started_at,
            endpoint.timestamp,
        )
        record.gross_energy_wh = endpoint.gross_energy_wh
        record.idle_energy_wh = max(0.0, endpoint.idle_energy_wh)
        record.net_energy_wh = max(0.0, endpoint.net_energy_wh)
        record.idle_baseline_power_w = baseline
        record.idle_measurement_ids = measurement_ids
        record.idle_quality = quality
        record.idle_correction_status = IDLE_CORRECTION_APPLIED
        record.energy_at_detection_wh = samples[-1].net_energy_wh
        record.peak_net_power_w = peak_net if peak_net > 0 else None
        if confirmed:
            record.candidate_end_at = endpoint.timestamp
            record.end_method = \"retrospective_idle_reanalysis\"
            record.confidence = (
                CONFIDENCE_HIGH
                if any(item.power_w is not None for item in samples)
                else CONFIDENCE_MEDIUM
            )
        record.analysis_revision += 1
        record.last_analyzed_at = self._now_iso()
        record.algorithm_version = ALGORITHM_VERSION

    @staticmethod
    def _record_sample_at_or_before(
        samples: list[MeasurementSample],
        timestamp: str | None,
    ) -> MeasurementSample | None:
        \"\"\"Return the last supplied trace point at or before a timestamp.\"\"\"
        target = BatteryChargeManager._parse_dt(timestamp)
        if target is None:
            return None
        found = None
        for sample in samples:
            parsed = BatteryChargeManager._parse_dt(sample.timestamp)
            if parsed is not None and parsed <= target:
                found = sample
        return found

    async def _async_begin_session(
"""
    content = replace_once(
        content,
        marker,
        methods,
        "pending calibration reprocessing methods",
    )
    write(path, content)


def patch_docs() -> None:
    path = "CHANGELOG.md"
    content = read(path)
    content = replace_once(
        content,
        "# Changelog\n\n",
        "# Changelog\n\n"
        "## 0.1.1\n\n"
        "- Calibrations can start without a reliable idle measurement and are stored with pending idle correction.\n"
        "- Pending trace-backed calibrations are recalculated automatically after a reliable idle measurement becomes available.\n"
        "- Focused form fields are no longer replaced by background Home Assistant or websocket updates.\n"
        "- Idle-measurement and settings number fields retain their draft values.\n"
        "- Fixed idle durations below five minutes are clamped to five minutes instead of being rejected or reset.\n\n",
        "changelog 0.1.1",
    )
    write(path, content)
    (ROOT / "docs/version-0.1.1.md").write_text(
        "# Battery Charge Manager 0.1.1\n\n"
        "## Calibration workflow\n\n"
        "- Full-charge calibration can be recorded before an idle baseline exists.\n"
        "- Such records remain explicitly marked as `pending` and are excluded from normal automatic charging.\n"
        "- A later reliable idle measurement automatically recalculates the stored raw trace and applies the baseline.\n"
        "- The previous analysis remains retained in the record analysis history.\n\n"
        "## Frontend\n\n"
        "- Live Home Assistant and websocket updates no longer replace a focused input, select, or textarea.\n"
        "- Deferred updates are rendered after editing leaves the control.\n"
        "- Idle-measurement and settings number fields retain their draft values.\n"
        "- Values below the permitted minimum are clamped to the minimum; a fixed duration of one minute therefore becomes five minutes.\n\n"
        "## Compatibility\n\n"
        "Existing 0.1.0 data is migrated with the previous calibration interpretation preserved. New calibrations without a baseline use the explicit pending state.\n",
        encoding="utf-8",
    )


def main() -> None:
    manifest = json.loads(
        read("custom_components/battery_charge_manager/manifest.json")
    )
    if manifest.get("version") == "0.1.1":
        print("0.1.1 backend implementation already applied")
        return
    patch_const()
    patch_manifest()
    patch_models()
    patch_manager()
    patch_docs()
    print("Applied Battery Charge Manager 0.1.1 backend implementation")


if __name__ == "__main__":
    main()
