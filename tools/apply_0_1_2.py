from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS_PATH = ROOT / "custom_components/battery_charge_manager/frontend/battery-charge-manager.js"
MANAGER_PATH = ROOT / "custom_components/battery_charge_manager/manager.py"
CONST_PATH = ROOT / "custom_components/battery_charge_manager/const.py"
MANIFEST_PATH = ROOT / "custom_components/battery_charge_manager/manifest.json"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"


def replace_once(content: str, old: str, new: str, label: str) -> str:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return content.replace(old, new, 1)


def replace_between(content: str, start: str, end: str, replacement: str, label: str, *, offset: int = 0) -> str:
    start_index = content.find(start, offset)
    if start_index < 0:
        raise RuntimeError(f"{label}: start marker not found")
    end_index = content.find(end, start_index + len(start))
    if end_index < 0:
        raise RuntimeError(f"{label}: end marker not found")
    return content[:start_index] + replacement + content[end_index:]


def patch_versions() -> None:
    content = CONST_PATH.read_text(encoding="utf-8")
    content = replace_once(
        content,
        'VERSION = "0.1.1"\nALGORITHM_VERSION = "0.1.1"',
        'VERSION = "0.1.2"\nALGORITHM_VERSION = "0.1.2"',
        "const version",
    )
    CONST_PATH.write_text(content, encoding="utf-8")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("version") != "0.1.1":
        raise RuntimeError(f"manifest version is {manifest.get('version')}, expected 0.1.1")
    manifest["version"] = "0.1.2"
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def patch_manager() -> None:
    content = MANAGER_PATH.read_text(encoding="utf-8")
    old = '''        session["sample_count"] = len(self.session.samples)
        active_calibration = self.calibration_summary(
'''
    new = '''        session["sample_count"] = len(self.session.samples)
        chart_limit = 240
        raw_chart_samples = self.session.samples
        if len(raw_chart_samples) <= chart_limit:
            chart_samples = raw_chart_samples
        else:
            last_index = len(raw_chart_samples) - 1
            indices = [
                round(index * last_index / (chart_limit - 1))
                for index in range(chart_limit)
            ]
            chart_samples = [raw_chart_samples[index] for index in indices]
        session["chart_samples"] = [sample.as_dict() for sample in chart_samples]
        session["idle_live_assessment"] = (
            self._assess_idle_trace()
            if self.session.mode == SESSION_IDLE_MEASURING
            else {}
        )
        active_calibration = self.calibration_summary(
'''
    content = replace_once(content, old, new, "frontend live trace")
    MANAGER_PATH.write_text(content, encoding="utf-8")


def patch_frontend() -> None:
    content = JS_PATH.read_text(encoding="utf-8")

    content = replace_once(
        content,
        '    portsUsed: "Verwendete Anschlüsse",',
        '    portsUsed: "Verwendete Anschlüsse",\n'
        '    connectTo: "Anschliessen an",\n'
        '    liveMeasurement: "Laufende Messung",\n'
        '    liveCalibration: "Laufende Kalibration",\n'
        '    liveCharge: "Laufender Ladevorgang",\n'
        '    remaining: "Verbleibende Zeit",\n'
        '    plannedEnd: "Voraussichtliches Ende",\n'
        '    measurementMode: "Messmodus",\n'
        '    preliminaryValue: "Vorläufiger Messwert",\n'
        '    stability: "Stabilität",\n'
        '    minRemaining: "Bis Mindestdauer",\n'
        '    maxDuration: "Maximaldauer",\n'
        '    peakPower: "Spitzenleistung",\n'
        '    targetEnergy: "Zielenergie",\n'
        '    chargeEnergy: "Ladeenergie",\n'
        '    chartBuilding: "Messkurve wird aufgebaut …",',
        "German live labels",
    )
    content = replace_once(
        content,
        '    portsUsed: "Ports used",',
        '    portsUsed: "Ports used",\n'
        '    connectTo: "Connect to",\n'
        '    liveMeasurement: "Measurement in progress",\n'
        '    liveCalibration: "Calibration in progress",\n'
        '    liveCharge: "Charging in progress",\n'
        '    remaining: "Time remaining",\n'
        '    plannedEnd: "Expected end",\n'
        '    measurementMode: "Measurement mode",\n'
        '    preliminaryValue: "Preliminary value",\n'
        '    stability: "Stability",\n'
        '    minRemaining: "Until minimum duration",\n'
        '    maxDuration: "Maximum duration",\n'
        '    peakPower: "Peak power",\n'
        '    targetEnergy: "Target energy",\n'
        '    chargeEnergy: "Charge energy",\n'
        '    chartBuilding: "Building measurement trace …",',
        "English live labels",
    )

    helper_marker = '''const clampNumberValue = (value, minimum, maximum, fallback) => {
  const parsed = Number(value);
  const fallbackNumber = Number(fallback);
  if (value === "" || value === null || value === undefined || !Number.isFinite(parsed)) {
    return Number.isFinite(fallbackNumber) ? fallbackNumber : minimum;
  }
  return Math.min(maximum, Math.max(minimum, parsed));
};

'''
    helpers = helper_marker + r'''const selectedPorts = (state) => {
  const setup = state?.setups?.find((item) => item.setup_id === state.selected_setup_id);
  const quantity = Math.max(0, Number(state?.selected_quantity || 0));
  return (setup?.port_labels || []).slice(0, quantity);
};

const portInstruction = (state, language = "en") => {
  const ports = selectedPorts(state);
  const quantity = Math.max(0, Number(state?.selected_quantity || ports.length));
  if (!quantity || !ports.length) return "–";
  if (language === "de") {
    const batteries = quantity === 1 ? "1 Akku" : `${quantity} Akkus`;
    const connector = ports.length === 1 ? "Anschluss" : "Anschlüsse";
    return `${batteries} → ${connector} ${ports.join(" + ")}`;
  }
  const batteries = quantity === 1 ? "1 battery" : `${quantity} batteries`;
  const connector = ports.length === 1 ? "port" : "ports";
  return `${batteries} → ${connector} ${ports.join(" + ")}`;
};

const phaseLabel = (phase, language = "en") => {
  const labels = {
    de: {
      idle: "Bereit",
      preparing: "Vorbereitung",
      waiting_for_load: "Warte auf Ladebeginn",
      main_charge: "Hauptladung",
      taper: "Abregelphase",
      confirming_end: "Ladeende wird bestätigt",
      target_reached: "Ziel erreicht",
      idle_measurement: "Leerlaufmessung",
      finished: "Abgeschlossen",
      error: "Fehler",
    },
    en: {
      idle: "Ready",
      preparing: "Preparing",
      waiting_for_load: "Waiting for charging",
      main_charge: "Main charge",
      taper: "Taper phase",
      confirming_end: "Confirming charge endpoint",
      target_reached: "Target reached",
      idle_measurement: "Idle measurement",
      finished: "Finished",
      error: "Error",
    },
  };
  return labels[language]?.[phase] || labels.en[phase] || String(phase || "–");
};

const fmtClockFromNow = (seconds, language = "en") => {
  if (seconds === null || seconds === undefined || !Number.isFinite(Number(seconds))) return "–";
  const date = new Date(Date.now() + Math.max(0, Number(seconds)) * 1000);
  return new Intl.DateTimeFormat(language === "de" ? "de-CH" : "en-GB", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

const renderSessionChart = (session, mode, language = "en", compact = false) => {
  const samples = (session?.chart_samples || [])
    .map((item) => ({ ...item, time: new Date(item.timestamp).getTime() }))
    .filter((item) => Number.isFinite(item.time));
  if (samples.length < 2) {
    return `<div class="bcm-chart-empty">${language === "de" ? "Messkurve wird aufgebaut …" : "Building measurement trace …"}</div>`;
  }
  const width = compact ? 520 : 760;
  const height = compact ? 150 : 230;
  const left = 38;
  const right = 18;
  const top = 14;
  const bottom = 28;
  const firstTime = samples[0].time;
  let lastTime = samples[samples.length - 1].time;
  if (mode === "idle" && session.idle_measurement_mode === "fixed" && session.requested_duration_minutes) {
    lastTime = Math.max(lastTime, firstTime + Number(session.requested_duration_minutes) * 60000);
  }
  const span = Math.max(1, lastTime - firstTime);
  const x = (time) => left + ((time - firstTime) / span) * (width - left - right);
  const powerKey = mode === "idle" ? "power_w" : "net_power_w";
  const energyKey = mode === "idle" ? "gross_energy_wh" : "net_energy_wh";
  const powerValues = samples.map((item) => Number(item[powerKey])).filter(Number.isFinite);
  const energyValues = samples.map((item) => Number(item[energyKey])).filter(Number.isFinite);
  const powerMax = Math.max(0.1, ...powerValues);
  const targetEnergy = mode === "charging" && Number.isFinite(Number(session.target_energy_wh))
    ? Number(session.target_energy_wh)
    : 0;
  const energyMax = Math.max(0.1, targetEnergy, ...energyValues);
  const yPower = (value) => height - bottom - (Number(value) / powerMax) * (height - top - bottom);
  const yEnergy = (value) => height - bottom - (Number(value) / energyMax) * (height - top - bottom);
  const points = (key, y) => samples
    .filter((item) => Number.isFinite(Number(item[key])))
    .map((item) => `${x(item.time).toFixed(1)},${y(item[key]).toFixed(1)}`)
    .join(" ");
  const powerPoints = points(powerKey, yPower);
  const energyPoints = points(energyKey, yEnergy);
  const markerLine = (timestamp, marker) => {
    const time = new Date(timestamp || "").getTime();
    if (!Number.isFinite(time) || time < firstTime || time > lastTime) return "";
    const position = x(time).toFixed(1);
    return `<line data-marker="${marker}" class="bcm-chart-marker" x1="${position}" y1="${top}" x2="${position}" y2="${height - bottom}" />`;
  };
  const targetLine = targetEnergy > 0
    ? `<line data-marker="target-energy" class="bcm-chart-target" x1="${left}" y1="${yEnergy(targetEnergy).toFixed(1)}" x2="${width - right}" y2="${yEnergy(targetEnergy).toFixed(1)}" />`
    : "";
  const fixedEnd = mode === "idle" && session.idle_measurement_mode === "fixed" && session.requested_duration_minutes
    ? markerLine(new Date(firstTime + Number(session.requested_duration_minutes) * 60000).toISOString(), "fixed-end")
    : "";
  const minEnd = mode === "idle" && session.idle_measurement_mode === "automatic" && session.auto_min_minutes
    ? markerLine(new Date(firstTime + Number(session.auto_min_minutes) * 60000).toISOString(), "minimum-duration")
    : "";
  const energyName = mode === "idle"
    ? (language === "de" ? "Bruttoenergie" : "Gross energy")
    : (language === "de" ? "Nettoenergie" : "Net energy");
  const powerName = language === "de" ? "Leistung" : "Power";
  return `<div class="bcm-session-chart ${compact ? "compact" : ""}">
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${language === "de" ? "Messkurve" : "Measurement trace"}">
      <line class="bcm-chart-axis" x1="${left}" y1="${height - bottom}" x2="${width - right}" y2="${height - bottom}" />
      ${targetLine}${fixedEnd}${minEnd}
      ${markerLine(session.candidate_end_at, "candidate-end")}
      ${markerLine(session.charge_finished_at, "charge-end")}
      ${markerLine(session.end_detected_at, "end-detected")}
      ${powerPoints ? `<polyline data-series="power" class="bcm-chart-power" points="${powerPoints}" />` : ""}
      ${energyPoints ? `<polyline data-series="energy" class="bcm-chart-energy" points="${energyPoints}" />` : ""}
    </svg>
    <div class="bcm-chart-legend">
      ${powerPoints ? `<span><i class="power"></i>${powerName} · max ${fmt(powerMax)} W</span>` : ""}
      ${energyPoints ? `<span><i class="energy"></i>${energyName} · max ${fmt(energyMax)} Wh</span>` : ""}
    </div>
  </div>`;
};

'''
    content = replace_once(content, helper_marker, helpers, "frontend helper insertion")

    content = replace_once(
        content,
        '  .bcm-admin { font-size:12px; color:var(--secondary-text-color); }\n'
        '  @media (max-width:600px)',
        '  .bcm-admin { font-size:12px; color:var(--secondary-text-color); }\n'
        '  .bcm-port-note { margin:10px 0; padding:11px 12px; border-radius:10px; background:color-mix(in srgb,var(--primary-color) 10%,var(--card-background-color)); font-weight:600; }\n'
        '  .bcm-session-chart { margin-top:14px; border:1px solid var(--divider-color); border-radius:12px; padding:8px 8px 5px; overflow:hidden; background:var(--card-background-color); }\n'
        '  .bcm-session-chart svg { display:block; width:100%; height:auto; min-height:150px; }\n'
        '  .bcm-session-chart.compact svg { min-height:100px; }\n'
        '  .bcm-chart-axis { stroke:var(--divider-color); stroke-width:1; }\n'
        '  .bcm-chart-power,.bcm-chart-energy { fill:none; stroke-width:2.2; stroke-linejoin:round; stroke-linecap:round; vector-effect:non-scaling-stroke; }\n'
        '  .bcm-chart-power { stroke:var(--primary-color); }\n'
        '  .bcm-chart-energy { stroke:var(--warning-color,#f9a825); }\n'
        '  .bcm-chart-marker { stroke:var(--secondary-text-color); stroke-width:1; stroke-dasharray:4 4; vector-effect:non-scaling-stroke; }\n'
        '  .bcm-chart-target { stroke:var(--success-color,#43a047); stroke-width:1.5; stroke-dasharray:7 4; vector-effect:non-scaling-stroke; }\n'
        '  .bcm-chart-legend { display:flex; flex-wrap:wrap; gap:12px; font-size:11px; color:var(--secondary-text-color); padding:2px 5px 4px; }\n'
        '  .bcm-chart-legend span { display:flex; align-items:center; gap:5px; }\n'
        '  .bcm-chart-legend i { width:14px; height:3px; border-radius:2px; display:inline-block; }\n'
        '  .bcm-chart-legend i.power { background:var(--primary-color); }\n'
        '  .bcm-chart-legend i.energy { background:var(--warning-color,#f9a825); }\n'
        '  .bcm-chart-empty { margin-top:14px; padding:18px; text-align:center; border:1px dashed var(--divider-color); border-radius:12px; color:var(--secondary-text-color); }\n'
        '  @media (max-width:600px)',
        "chart CSS",
    )

    panel_class = content.find("class BatteryChargeManagerPanel extends BcmBase")
    if panel_class < 0:
        raise RuntimeError("panel class not found")
    content = replace_once(
        content,
        '    this._draft = {};\n    this._formValues = {',
        '    this._draft = {};\n    this._tabsScrollLeft = 0;\n    this._formValues = {',
        "tabs scroll state",
    )

    panel_render = r'''  render() {
    if (!this.shadowRoot) return;
    const s = this._state;
    const admin = Boolean(this._hass?.user?.is_admin);
    const previousTabs = this.shadowRoot.querySelector(".bcm-tabs");
    const tabsScrollLeft = previousTabs?.scrollLeft ?? this._tabsScrollLeft ?? 0;
    this.shadowRoot.innerHTML = `
      <style>${BASE_STYLE}</style>
      <div class="bcm-shell">
        <div class="bcm-header">
          <div><h1 class="bcm-title">${this.t("title")}</h1><div class="bcm-version">${esc(s?.version || "")}</div></div>
          <div class="bcm-badge ${s?.session?.mode !== "idle" ? "warn" : "neutral"}">${esc(s?.session?.mode || "loading")}</div>
        </div>
        ${this._error ? `<div class="bcm-error"><strong>${this.t("error")}:</strong> ${esc(this._error)}</div>` : ""}
        <div class="bcm-tabs">
          ${this.tabButton("charge", this.t("charge"))}
          ${this.tabButton("batteries", this.t("batteries"))}
          ${this.tabButton("setups", this.t("setups"))}
          ${this.tabButton("idle", this.t("idle"))}
          ${this.tabButton("calibrations", this.t("calibrations"))}
          ${this.tabButton("settings", this.t("settings"))}
        </div>
        ${!s ? `<div class="bcm-card">Loading…</div>` : this.renderTab(admin)}
      </div>
      ${this.renderDialog(admin)}
    `;
    const tabs = this.shadowRoot.querySelector(".bcm-tabs");
    if (tabs) {
      tabs.scrollLeft = tabsScrollLeft;
      this._tabsScrollLeft = tabsScrollLeft;
      tabs.addEventListener("scroll", () => { this._tabsScrollLeft = tabs.scrollLeft; });
    }
    this.bindEvents();
  }

'''
    content = replace_between(
        content,
        "  render() {",
        "  tabButton(id, label) {",
        panel_render,
        "panel render",
        offset=panel_class,
    )

    selectors = r'''  selectors({ includeTarget = true } = {}) {
    const s = this._state;
    const setup = s.setups.find((item) => item.setup_id === s.selected_setup_id);
    const maxQuantity = setup?.port_labels?.length || 1;
    return `
      <div class="bcm-form-grid">
        <div class="bcm-field"><label>${this.t("setup")}</label><select data-select="setup" ${s.session.mode !== "idle" ? "disabled" : ""}>${s.setups.map((item) => `<option value="${esc(item.setup_id)}" ${item.setup_id === s.selected_setup_id ? "selected" : ""}>${esc(item.name)}</option>`).join("")}</select></div>
        <div class="bcm-field"><label>${this.t("battery")}</label><select data-select="battery" ${s.session.mode !== "idle" ? "disabled" : ""}>${s.batteries.map((item) => `<option value="${esc(item.battery_id)}" ${item.battery_id === s.selected_battery_id ? "selected" : ""}>${esc(item.name)}</option>`).join("")}</select></div>
      </div>
      <div class="bcm-row stack"><label><strong>${this.t("quantity")}</strong></label><div class="bcm-segment">${Array.from({ length: maxQuantity }, (_, index) => index + 1).map((n) => `<button data-quantity="${n}" class="${n === s.selected_quantity ? "active" : ""}" ${s.session.mode !== "idle" ? "disabled" : ""}>${n}</button>`).join("")}</div></div>
      <div class="bcm-port-note">${this.t("connectTo")}: ${esc(portInstruction(s, this.language))}</div>
      ${includeTarget ? `<div class="bcm-field"><label>${this.t("target")}: <strong>${s.target_percent}%</strong></label><input type="range" min="20" max="100" step="1" value="${s.target_percent}" data-target ${s.session.mode !== "idle" ? "disabled" : ""}></div>` : ""}
    `;
  }

'''
    content = replace_between(content, "  selectors() {", "  renderCharge() {", selectors, "selectors", offset=panel_class)

    render_charge = r'''  renderCharge() {
    const s = this._state;
    const session = s.session;
    const summary = s.active_calibration_summary || {};
    const progress = Math.max(0, Math.min(100, Number(session.progress_percent || 0)));
    if (session.mode === "charging") {
      const setup = s.setups.find((item) => item.setup_id === s.selected_setup_id);
      const battery = s.batteries.find((item) => item.battery_id === s.selected_battery_id);
      const ports = (session.ports?.length ? session.ports : selectedPorts(s)).join(" + ") || "–";
      return `<div class="bcm-grid">
        <section class="bcm-card">
          <h2>${this.t("liveCharge")}</h2>
          <div class="bcm-port-note">${this.t("connectTo")}: ${esc(ports)}</div>
          <div class="bcm-row"><span>${this.t("phase")}</span><strong>${esc(phaseLabel(session.phase,this.language))}</strong></div>
          <div class="bcm-progress"><div style="width:${progress}%"></div></div>
          <div class="bcm-row"><span>${this.t("progress")}</span><strong>${fmt(session.progress_percent,1)}%</strong></div>
          <div class="bcm-metrics">
            ${this.metric(this.t("elapsed"), fmtDuration(session.elapsed_seconds))}
            ${this.metric(this.t("targetEnergy"), `${fmt(session.target_energy_wh)} Wh`)}
            ${this.metric(this.t("net"), `${fmt(session.net_energy_wh)} Wh`)}
            ${this.metric(this.t("power"), `${fmt(session.current_power_w)} W`)}
            ${this.metric(this.t("gross"), `${fmt(session.gross_energy_wh)} Wh`)}
            ${this.metric(this.t("idleEnergy"), `${fmt(session.idle_energy_wh)} Wh`)}
          </div>
          ${renderSessionChart(session,"charging",this.language)}
          <div class="bcm-actions"><button class="bcm-btn danger" data-action="stop" ${this._busy ? "disabled" : ""}>${this.t("stop")}</button></div>
        </section>
        <section class="bcm-card">
          <h2>${this.t("charge")}</h2>
          <div class="bcm-row"><span>${this.t("setup")}</span><strong>${esc(setup?.name || "–")}</strong></div>
          <div class="bcm-row"><span>${this.t("battery")}</span><strong>${esc(battery?.name || "–")}</strong></div>
          <div class="bcm-row"><span>${this.t("quantity")}</span><strong>${s.selected_quantity}</strong></div>
          <div class="bcm-row"><span>${this.t("target")}</span><strong>${s.target_percent}%</strong></div>
          <div class="bcm-row"><span>${this.t("calibrationValue")}</span><strong>${fmt(summary.median_net_energy_wh)} Wh</strong></div>
          <p><span class="bcm-badge ${qualityClass(summary.quality)}">${esc(summary.quality || "none")}</span></p>
        </section>
      </div>`;
    }
    const canStart = s.setups.length && s.batteries.length && summary.median_net_energy_wh !== null && session.mode === "idle";
    return `
      <div class="bcm-grid">
        <section class="bcm-card">
          <h2>${this.t("charge")}</h2>
          ${s.setups.length && s.batteries.length ? this.selectors({ includeTarget:true }) : `<div class="bcm-note">${this.t("selectRequired")}</div>`}
          <div class="bcm-note">${this.t("relativeNote")}</div>
          <div class="bcm-actions">
            <button class="bcm-btn" data-action="start-charge" ${!canStart || this._busy ? "disabled" : ""}>${this.t("start")}</button>
            <button class="bcm-btn danger" data-action="stop" ${session.mode === "idle" || this._busy ? "disabled" : ""}>${this.t("stop")}</button>
          </div>
          ${summary.median_net_energy_wh === null ? `<p class="bcm-muted">${this.t("noCalibration")}</p>` : `<p><span class="bcm-badge ${qualityClass(summary.quality)}">${esc(summary.quality)}</span> ${this.t("calibrationValue")}: <strong>${fmt(summary.median_net_energy_wh)} Wh</strong></p>`}
        </section>
        <section class="bcm-card">
          <h2>${this.t("active")}</h2>
          <div class="bcm-row"><span>${this.t("status")}</span><strong>${esc(session.mode)}</strong></div>
          <div class="bcm-row"><span>${this.t("phase")}</span><strong>${esc(phaseLabel(session.phase,this.language))}</strong></div>
          <div class="bcm-metrics">
            ${this.metric(this.t("power"), `${fmt(session.current_power_w)} W`)}
            ${this.metric(this.t("gross"), `${fmt(session.gross_energy_wh)} Wh`)}
            ${this.metric(this.t("net"), `${fmt(session.net_energy_wh)} Wh`)}
          </div>
        </section>
      </div>
    `;
  }

'''
    content = replace_between(content, "  renderCharge() {", "  metric(label, value) {", render_charge, "renderCharge", offset=panel_class)

    render_idle = r'''  renderIdle(admin) {
    const s = this._state;
    const summary = s.active_idle_summary || {};
    const active = s.session.mode === "idle_measuring";
    const session = s.session;
    const rows = s.idle_measurements.filter((item) => item.setup_id === s.selected_setup_id);
    const baselineDisplay = summary.below_detection_count ? `&lt; ${fmt(summary.upper_bound_power_w,3)} W` : `${fmt(summary.baseline_power_w,3)} W`;
    let leftContent;
    if (active) {
      const fixed = session.idle_measurement_mode === "fixed";
      const elapsed = Math.max(0, Number(session.elapsed_seconds || 0));
      const requestedSeconds = Math.max(0, Number(session.requested_duration_minutes || 0) * 60);
      const remaining = fixed ? Math.max(0, requestedSeconds - elapsed) : null;
      const fixedProgress = fixed && requestedSeconds > 0 ? Math.min(100, elapsed / requestedSeconds * 100) : null;
      const minRemaining = !fixed ? Math.max(0, Number(session.auto_min_minutes || 0) * 60 - elapsed) : null;
      const assessment = session.idle_live_assessment || {};
      const preliminary = assessment.below_detection_limit
        ? `&lt; ${fmt(assessment.upper_bound_power_w,3)} W`
        : `${fmt(assessment.median_power_w ?? assessment.average_power_w,3)} W`;
      leftContent = `
        <h3>${this.t("liveMeasurement")}</h3>
        <div class="bcm-row"><span>${this.t("measurementMode")}</span><strong>${fixed ? this.t("fixed") : this.t("auto")}</strong></div>
        ${fixedProgress !== null ? `<div class="bcm-progress"><div style="width:${fixedProgress}%"></div></div><div class="bcm-row"><span>${this.t("progress")}</span><strong>${fmt(fixedProgress,1)}%</strong></div>` : ""}
        <div class="bcm-metrics">
          ${this.metric(this.t("elapsed"), fmtDuration(elapsed))}
          ${fixed ? this.metric(this.t("remaining"), fmtDuration(remaining)) : this.metric(this.t("minRemaining"), fmtDuration(minRemaining))}
          ${fixed ? this.metric(this.t("plannedEnd"), fmtClockFromNow(remaining,this.language)) : this.metric(this.t("maxDuration"), fmtDuration(Number(session.auto_max_minutes || 0) * 60))}
          ${this.metric(this.t("power"), `${fmt(session.current_power_w)} W`)}
          ${this.metric(this.t("gross"), `${fmt(session.gross_energy_wh)} Wh`)}
          ${this.metric(this.t("measurements"), String(session.sample_count || 0))}
          ${this.metric(this.t("preliminaryValue"), preliminary)}
          ${this.metric(this.t("stability"), assessment.stable ? this.t("reliable") : this.t("pendingCorrection"))}
        </div>
        ${renderSessionChart(session,"idle",this.language)}
        <div class="bcm-actions"><button class="bcm-btn danger" data-action="stop">${this.t("stop")}</button></div>`;
    } else {
      leftContent = `${this.selectSetupOnly()}<div class="bcm-note">${this.t("noBatteryIdle")}</div><div class="bcm-note" style="margin-top:8px">${this.t("automaticExplanation")}</div>${admin ? `<div class="bcm-form-grid"><div class="bcm-field"><label>${this.t("minMinutes")}</label><input id="idle-min" data-form-value="idleMin" type="number" min="10" max="1440" value="${esc(this._formValues.idleMin)}"></div><div class="bcm-field"><label>${this.t("maxMinutes")}</label><input id="idle-max" data-form-value="idleMax" type="number" min="30" max="1440" value="${esc(this._formValues.idleMax)}"></div><div class="bcm-field"><label>${this.t("durationMinutes")}</label><input id="idle-fixed" data-form-value="idleFixed" type="number" min="5" max="1440" value="${esc(this._formValues.idleFixed)}"></div></div><div class="bcm-actions"><button class="bcm-btn" data-action="idle-auto" ${s.session.mode !== "idle" || this._busy ? "disabled" : ""}>${this.t("automaticIdle")}</button><button class="bcm-btn secondary" data-action="idle-fixed" ${s.session.mode !== "idle" || this._busy ? "disabled" : ""}>${this.t("fixedIdle")}</button></div>` : `<p class="bcm-admin">${this.t("adminOnly")}</p>`}`;
    }
    return `<div class="bcm-grid"><section class="bcm-card"><h2>${this.t("idle")}</h2>${leftContent}</section><section class="bcm-card"><h2>${this.t("baseline")}</h2><div class="bcm-metrics">${this.metric(this.t("baseline"), baselineDisplay)}${this.metric(this.t("measurements"), String(summary.count || 0))}${this.metric(this.t("reliable"), String(summary.reliable_count || 0))}${this.metric(this.t("spread"), `${fmt(summary.spread_percent,1)}%`)}</div><p><span class="bcm-badge ${qualityClass(summary.quality)}">${esc(summary.quality || "none")}</span></p></section></div><section class="bcm-card" style="margin-top:14px"><h2>${this.t("history")}</h2>${this.idleTable(rows, admin)}</section>`;
  }

'''
    content = replace_between(content, "  renderIdle(admin) {", "  selectSetupOnly() {", render_idle, "renderIdle", offset=panel_class)

    render_calibrations = r'''  renderCalibrations(admin) {
    const s = this._state;
    const summary = s.active_calibration_summary || {};
    const idle = s.active_idle_summary || {};
    const active = s.session.mode === "calibrating";
    const session = s.session;
    const rows = s.calibrations.filter((item) => item.setup_id === s.selected_setup_id && item.battery_id === s.selected_battery_id && item.quantity === s.selected_quantity);
    let leftContent;
    if (active) {
      const battery = s.batteries.find((item) => item.battery_id === s.selected_battery_id);
      const ports = (session.ports?.length ? session.ports : selectedPorts(s)).join(" + ") || "–";
      const correction = session.idle_baseline_power_w === null || session.idle_baseline_power_w === undefined ? this.t("pendingCorrection") : this.t("valid");
      leftContent = `
        <h3>${this.t("liveCalibration")}</h3>
        <div class="bcm-row"><span>${this.t("battery")}</span><strong>${esc(battery?.name || "–")}</strong></div>
        <div class="bcm-row"><span>${this.t("quantity")}</span><strong>${session.quantity || s.selected_quantity}</strong></div>
        <div class="bcm-port-note">${this.t("connectTo")}: ${esc(ports)}</div>
        <div class="bcm-row"><span>${this.t("phase")}</span><strong>${esc(phaseLabel(session.phase,this.language))}</strong></div>
        <div class="bcm-metrics">
          ${this.metric(this.t("elapsed"), fmtDuration(session.elapsed_seconds))}
          ${this.metric(this.t("power"), `${fmt(session.current_power_w)} W`)}
          ${this.metric(this.t("peakPower"), `${fmt(session.peak_power_w)} W`)}
          ${this.metric(this.t("gross"), `${fmt(session.gross_energy_wh)} Wh`)}
          ${this.metric(this.t("idleEnergy"), `${fmt(session.idle_energy_wh)} Wh`)}
          ${this.metric(this.t("net"), `${fmt(session.net_energy_wh)} Wh`)}
          ${this.metric(this.t("measurements"), String(session.sample_count || 0))}
          ${this.metric(this.t("baseline"), correction)}
        </div>
        ${session.candidate_end_at ? `<div class="bcm-note" style="margin-top:10px"><strong>${this.t("endpoint")}</strong><br>${fmtDate(session.candidate_end_at,this.language)} · ${esc(phaseLabel("confirming_end",this.language))}</div>` : ""}
        ${renderSessionChart(session,"calibrating",this.language)}
        ${admin ? `<div class="bcm-actions"><button class="bcm-btn secondary" data-action="finish-calibration" ${this._busy ? "disabled" : ""}>${this.t("finishCalibration")}</button><button class="bcm-btn danger" data-action="stop">${this.t("stop")}</button></div><p class="bcm-muted">${this.t("manualFallback")}</p>` : ""}`;
    } else {
      leftContent = `${this.selectors({ includeTarget:false })}<div class="bcm-note">${this.t("calibrationHint")}</div>${idle.reliable_count ? "" : `<div class="bcm-note" style="margin-top:10px">${this.t("idleRequired")}</div>`}${admin ? `<div class="bcm-actions"><button class="bcm-btn" data-action="start-calibration" ${s.session.mode !== "idle" || this._busy ? "disabled" : ""}>${this.t("startCalibration")}</button></div>` : `<p class="bcm-admin">${this.t("adminOnly")}</p>`}`;
    }
    return `<div class="bcm-grid"><section class="bcm-card"><h2>${this.t("calibrations")}</h2>${leftContent}</section><section class="bcm-card"><h2>${this.t("quality")}</h2><div class="bcm-metrics">${this.metric(this.t("calibrationValue"), `${fmt(summary.median_net_energy_wh)} Wh`)}${this.metric(this.t("calibrationDuration"), fmtDuration(summary.median_charge_duration_seconds))}${this.metric(this.t("measurements"), String(summary.count || 0))}${this.metric(this.t("pendingCorrection"), String(summary.pending_count || 0))}${this.metric(this.t("spread"), `${fmt(summary.spread_percent,1)}%`)}${this.metric(this.t("stdev"), `${fmt(summary.stdev_net_energy_wh,3)} Wh`)}${this.metric(this.t("drift"), `${fmt(summary.drift_percent,1)}%`)}${this.metric(this.t("trend"), esc(summary.trend || "not_assessable"))}</div><p><span class="bcm-badge ${qualityClass(summary.quality)}">${esc(summary.quality || "none")}</span></p>${this.linearModel()}</section></div><section class="bcm-card" style="margin-top:14px"><h2>${this.t("history")}</h2>${this.calibrationTable(rows, admin)}</section>`;
  }

'''
    content = replace_between(content, "  renderCalibrations(admin) {", "  linearModel() {", render_calibrations, "renderCalibrations", offset=panel_class)

    card_class = content.find("class BatteryChargeManagerCard extends BcmBase")
    if card_class < 0:
        raise RuntimeError("card class not found")
    card_render = r'''  render() {
    if (!this.shadowRoot) return;
    const s = this._state;
    if (!s) {
      this.shadowRoot.innerHTML = `<style>${BASE_STYLE}</style><ha-card><div style="padding:16px">${this._error ? esc(this._error) : "Loading…"}</div></ha-card>`;
      return;
    }
    const session = s.session;
    const summary = s.active_calibration_summary || {};
    const setup = s.setups.find((item) => item.setup_id === s.selected_setup_id);
    const maxQuantity = setup?.port_labels?.length || 1;
    const progress = Math.max(0,Math.min(100,Number(session.progress_percent || 0)));
    const canStart = session.mode === "idle" && summary.median_net_energy_wh !== null && s.batteries.length && s.setups.length;
    const ports = (session.ports?.length ? session.ports : selectedPorts(s)).join(" + ") || "–";
    this.shadowRoot.innerHTML = `
      <style>${BASE_STYLE}:host{display:block}.compact{padding:16px}.compact h2{margin:0 0 12px;font-size:20px}</style>
      <ha-card>
        <div class="compact">
          <div class="bcm-list-head"><h2>${esc(this._config.title || this.t("title"))}</h2><button class="bcm-btn secondary" data-open>${this.t("openManager")}</button></div>
          ${this._error ? `<div class="bcm-error">${esc(this._error)}</div>` : ""}
          ${s.setups.length > 1 ? `<div class="bcm-field"><label>${this.t("setup")}</label><select data-card-select="setup" ${session.mode !== "idle" ? "disabled" : ""}>${s.setups.map((item) => `<option value="${esc(item.setup_id)}" ${item.setup_id === s.selected_setup_id ? "selected" : ""}>${esc(item.name)}</option>`).join("")}</select></div>` : ""}
          <div class="bcm-field"><label>${this.t("battery")}</label><select data-card-select="battery" ${session.mode !== "idle" ? "disabled" : ""}>${s.batteries.map((item) => `<option value="${esc(item.battery_id)}" ${item.battery_id === s.selected_battery_id ? "selected" : ""}>${esc(item.name)}</option>`).join("")}</select></div>
          <div class="bcm-row"><strong>${this.t("quantity")}</strong><div class="bcm-segment">${Array.from({length:maxQuantity},(_,i)=>i+1).map((n)=>`<button data-card-quantity="${n}" class="${n===s.selected_quantity?"active":""}" ${session.mode!=="idle"?"disabled":""}>${n}</button>`).join("")}</div></div>
          <div class="bcm-port-note">${this.t("connectTo")}: ${esc(ports)}</div>
          <div class="bcm-field"><label>${this.t("target")}: <strong>${s.target_percent}%</strong></label><input data-card-target type="range" min="20" max="100" value="${s.target_percent}" ${session.mode!=="idle"?"disabled":""}></div>
          ${session.mode === "charging" ? `<div class="bcm-progress"><div style="width:${progress}%"></div></div><div class="bcm-row"><span>${esc(phaseLabel(session.phase,this.language))}</span><strong>${fmt(session.net_energy_wh)} / ${fmt(session.target_energy_wh)} Wh</strong></div>${renderSessionChart(session,"charging",this.language,true)}` : ""}
          <div class="bcm-actions"><button class="bcm-btn" data-card-action="start" ${!canStart || this._busy ? "disabled" : ""}>${this.t("start")}</button><button class="bcm-btn danger" data-card-action="stop" ${session.mode==="idle" || this._busy ? "disabled" : ""}>${this.t("stop")}</button></div>
          ${summary.median_net_energy_wh === null ? `<p class="bcm-muted">${this.t("noCalibration")}</p>` : `<p class="bcm-muted">${this.t("calibrationValue")}: ${fmt(summary.median_net_energy_wh)} Wh · ${esc(summary.quality)}</p>`}
        </div>
      </ha-card>`;
    this.bindCardEvents();
  }

'''
    content = replace_between(content, "  render() {", "  bindCardEvents() {", card_render, "card render", offset=card_class)

    JS_PATH.write_text(content, encoding="utf-8")


def patch_docs() -> None:
    changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
    changelog = replace_once(
        changelog,
        "# Changelog\n\n",
        "# Changelog\n\n"
        "## 0.1.2\n\n"
        "- Removed the relative-charge-energy control from calibration because it does not affect full-charge calibration.\n"
        "- Added explicit first-N charging-port instructions for charging and calibration.\n"
        "- Preserved horizontal tab navigation position across live frontend rerenders.\n"
        "- Added live process views for fixed/automatic idle measurements, calibration, and normal charging.\n"
        "- Added remaining time and expected end for fixed-duration idle measurements.\n"
        "- Added lightweight SVG live charts for power and energy in the panel and a compact charging chart in the dashboard card.\n"
        "- Added live idle-assessment data and bounded full-session chart downsampling to the frontend state.\n\n",
        "changelog 0.1.2",
    )
    CHANGELOG_PATH.write_text(changelog, encoding="utf-8")
    (ROOT / "docs/version-0.1.2.md").write_text(
        "# Battery Charge Manager 0.1.2\n\n"
        "## Operational UI\n\n"
        "The calibration screen no longer shows the relative-charge-energy target. Both charging and calibration show the exact configured first-N ports to use. Horizontal tab navigation retains its scroll position during live updates.\n\n"
        "## Live process views\n\n"
        "Active idle measurements, calibrations, and charging sessions replace setup controls with a live process view. Fixed idle measurements show elapsed time, remaining time, expected end, current power, accumulated energy, sample count, a preliminary baseline estimate, and a progress bar. Automatic idle measurements show time until the minimum duration, maximum duration, and live reliability information.\n\n"
        "Calibration shows the selected battery, exact ports, detected phase, duration, power, peak power, gross/idle/net energy, sample count, correction state, and endpoint-candidate information without presenting a fabricated percent complete value.\n\n"
        "Normal charging shows actual percent progress because a calibrated target energy exists.\n\n"
        "## Charts\n\n"
        "A shared lightweight SVG chart renders the session power and energy trace. Idle measurement charts use gross power/energy, calibration charts use net power/energy with endpoint markers, and charging charts use net power/energy with a target-energy line. The dashboard card shows a compact chart while charging. The backend downsamples long sessions to at most 240 evenly distributed points while retaining the first and last sample.\n",
        encoding="utf-8",
    )


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("version") == "0.1.2":
        print("0.1.2 implementation already applied")
        return
    patch_versions()
    patch_manager()
    patch_frontend()
    patch_docs()
    print("Applied Battery Charge Manager 0.1.2")


if __name__ == "__main__":
    main()
