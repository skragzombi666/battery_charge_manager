const BCM_DOMAIN = "battery_charge_manager";
const BCM_PANEL_PATH = "/battery-charge-manager";

const TEXT = {
  de: {
    title: "Battery Charge Manager",
    charge: "Laden",
    batteries: "Akkus",
    setups: "Ladeanordnungen",
    idle: "Leerlaufmessung",
    calibrations: "Kalibrationen",
    settings: "Einstellungen",
    openManager: "Manager öffnen",
    setup: "Ladeanordnung",
    battery: "Akkutyp",
    quantity: "Anzahl",
    target: "Relative Ladeenergie",
    start: "Laden starten",
    stop: "Stoppen",
    status: "Status",
    phase: "Phase",
    progress: "Fortschritt",
    gross: "Bruttoenergie",
    idleEnergy: "Leerlaufenergie",
    net: "Netto-Ladeenergie",
    power: "Leistung",
    temperature: "Temperatur",
    elapsed: "Dauer",
    addBattery: "Akkutyp erfassen",
    edit: "Bearbeiten",
    delete: "Löschen",
    addSetup: "Ladeanordnung erfassen",
    automaticIdle: "Automatisch bis zuverlässig",
    fixedIdle: "Feste Dauer",
    startIdle: "Leerlaufmessung starten",
    startCalibration: "Kalibration starten",
    finishCalibration: "Manuell abschliessen",
    noBatteryIdle: "Für die Leerlaufmessung die vollständige Ladeanordnung einschalten, aber keine Akkus anschliessen.",
    calibrationHint: "Akkus mit vergleichbarem Ausgangsladezustand an die festgelegten ersten Anschlüsse anschliessen. Das tatsächliche Ladeende wird rückwirkend aus Energieplateau und – sofern vorhanden – Leistung erkannt.",
    idleRequired: "Keine zuverlässige Leerlaufmessung vorhanden. Die Kalibration wird vorläufig als Bruttomessung gespeichert und nach einer zuverlässigen Leerlaufmessung automatisch korrigiert.",
    pendingCorrection: "Leerlaufkorrektur ausstehend",
    save: "Speichern",
    cancel: "Abbrechen",
    name: "Name",
    manufacturer: "Hersteller",
    model: "Modell",
    capacity: "Nennkapazität (mAh)",
    voltage: "Nennspannung (Ausgangsspannung) (V)",
    energy: "Nennenergie (Wh)",
    technology: "Technischer Typ",
    formFactor: "Bauform",
    chargingMethod: "Ladeart",
    dischargeMethod: "Definierte Entlademethode",
    restTime: "Ruhezeit vor dem Laden (Minuten)",
    startingNotes: "Definierter Ausgangszustand / Hinweise",
    image: "Bild-URL oder /local-Pfad",
    uploadImage: "Bild hochladen",
    removeImage: "Bild entfernen",
    uploadingImage: "Bild wird hochgeladen …",
    notes: "Notizen",
    switchEntity: "Smart Plug / Switch",
    energySensor: "Kumulativer Energiesensor",
    powerSensor: "Leistungssensor (optional)",
    temperatureSensor: "Temperatursensor (optional)",
    chargerModel: "USB-Netzteil / Ladegerät",
    cable: "Kabel / Splitter",
    ports: "Anschlussbezeichnungen, kommagetrennt",
    maxPower: "Sicherheitsgrenze Leistung (W)",
    maxTemperature: "Sicherheitsgrenze Temperatur (°C, optional)",
    description: "Beschreibung",
    revision: "Revision",
    quality: "Qualität",
    measurements: "Messungen",
    reliable: "zuverlässig",
    invalid: "ungültig",
    valid: "gültig",
    durationMinutes: "Dauer (Minuten)",
    minMinutes: "Mindestdauer (Minuten)",
    maxMinutes: "Maximaldauer (Minuten)",
    baseline: "Verwendete Leerlaufleistung",
    history: "Historie",
    calibrationValue: "Median Nettoenergie",
    calibrationDuration: "Median Ladedauer",
    spread: "Streuung",
    stdev: "Standardabweichung",
    drift: "Drift letzte Messungen",
    trend: "Trend",
    detectionLimit: "unter Messgrenze",
    linearModel: "Plausibilitätsmodell 1–n Akkus",
    notAvailable: "nicht verfügbar",
    manualFallback: "Nur verwenden, wenn die automatische Erkennung nicht abschliessen kann. Die Messung wird mit niedrigerer Vertrauensstufe gespeichert.",
    maxSession: "Maximale Sitzungsdauer (Stunden)",
    saveSettings: "Einstellungen speichern",
    noSetups: "Keine Ladeanordnung vorhanden.",
    noBatteries: "Noch kein Akkutyp erfasst.",
    noCalibration: "Für diese Kombination liegt noch keine Kalibration vor.",
    active: "Aktiver Vorgang",
    portsUsed: "Verwendete Anschlüsse",
    connectTo: "Anschliessen an",
    liveMeasurement: "Laufende Messung",
    liveCalibration: "Laufende Kalibration",
    liveCharge: "Laufender Ladevorgang",
    remaining: "Verbleibende Zeit",
    plannedEnd: "Voraussichtliches Ende",
    measurementMode: "Messmodus",
    preliminaryValue: "Vorläufiger Messwert",
    stability: "Stabilität",
    minRemaining: "Bis Mindestdauer",
    maxDuration: "Maximaldauer",
    peakPower: "Spitzenleistung",
    targetEnergy: "Zielenergie",
    chargeEnergy: "Ladeenergie",
    chartBuilding: "Messkurve wird aufgebaut …",
    confidence: "Vertrauen",
    method: "Methode",
    endpoint: "Erkanntes Ladeende",
    detected: "Ende bestätigt",
    auto: "automatisch",
    fixed: "fest",
    currentRevisionOnly: "Berechnungen verwenden nur gültige Messungen der aktuellen Revision von Ladeanordnung und Akkutyp.",
    relativeNote: "Der Zielwert ist relative Ladeenergie, nicht ein behaupteter exakter Zell-Ladezustand.",
    confirmDelete: "Eintrag wirklich löschen? Historische Messdatensätze bleiben erhalten, werden aber nicht mehr für aktuelle Berechnungen verwendet.",
    error: "Fehler",
    adminOnly: "Diese Verwaltungsfunktion erfordert Administratorrechte.",
    selectRequired: "Ladeanordnung und Akkutyp auswählen.",
    automaticExplanation: "Die Messung läuft mindestens bis zur Mindestdauer und endet erst, wenn der Messwert über mehrere Zeitfenster stabil und für die Sensorauflösung ausreichend belastbar ist. Spätestens bei der Maximaldauer wird sie beendet.",
  },
  en: {
    title: "Battery Charge Manager",
    charge: "Charge",
    batteries: "Batteries",
    setups: "Charging setups",
    idle: "Idle measurement",
    calibrations: "Calibrations",
    settings: "Settings",
    openManager: "Open manager",
    setup: "Charging setup",
    battery: "Battery type",
    quantity: "Quantity",
    target: "Relative charge energy",
    start: "Start charging",
    stop: "Stop",
    status: "Status",
    phase: "Phase",
    progress: "Progress",
    gross: "Gross energy",
    idleEnergy: "Idle energy",
    net: "Net charge energy",
    power: "Power",
    temperature: "Temperature",
    elapsed: "Duration",
    addBattery: "Add battery type",
    edit: "Edit",
    delete: "Delete",
    addSetup: "Add charging setup",
    automaticIdle: "Automatic until reliable",
    fixedIdle: "Fixed duration",
    startIdle: "Start idle measurement",
    startCalibration: "Start calibration",
    finishCalibration: "Finish manually",
    noBatteryIdle: "Connect the complete charging setup, but do not connect any batteries during the idle measurement.",
    calibrationHint: "Connect batteries with comparable initial charge to the defined first ports. The actual endpoint is determined retrospectively from the energy plateau and, when available, power.",
    idleRequired: "No reliable idle measurement is available. The calibration is stored provisionally as a gross measurement and corrected automatically after a reliable idle measurement.",
    pendingCorrection: "Idle correction pending",
    save: "Save",
    cancel: "Cancel",
    name: "Name",
    manufacturer: "Manufacturer",
    model: "Model",
    capacity: "Nominal capacity (mAh)",
    voltage: "Nominal voltage (output voltage) (V)",
    energy: "Nominal energy (Wh)",
    technology: "Technology",
    formFactor: "Form factor",
    chargingMethod: "Charging method",
    dischargeMethod: "Defined discharge method",
    restTime: "Rest time before charging (minutes)",
    startingNotes: "Defined initial condition / notes",
    image: "Image URL or /local path",
    uploadImage: "Upload image",
    removeImage: "Remove image",
    uploadingImage: "Uploading image …",
    notes: "Notes",
    switchEntity: "Smart plug / switch",
    energySensor: "Cumulative energy sensor",
    powerSensor: "Power sensor (optional)",
    temperatureSensor: "Temperature sensor (optional)",
    chargerModel: "USB power supply / charger",
    cable: "Cable / splitter",
    ports: "Port labels, comma separated",
    maxPower: "Power safety limit (W)",
    maxTemperature: "Temperature safety limit (°C, optional)",
    description: "Description",
    revision: "Revision",
    quality: "Quality",
    measurements: "Measurements",
    reliable: "reliable",
    invalid: "invalid",
    valid: "valid",
    durationMinutes: "Duration (minutes)",
    minMinutes: "Minimum duration (minutes)",
    maxMinutes: "Maximum duration (minutes)",
    baseline: "Applied idle power",
    history: "History",
    calibrationValue: "Median net energy",
    calibrationDuration: "Median charge duration",
    spread: "Spread",
    stdev: "Standard deviation",
    drift: "Recent-measurement drift",
    trend: "Trend",
    detectionLimit: "below detection limit",
    linearModel: "Plausibility model for 1–n batteries",
    notAvailable: "not available",
    manualFallback: "Use only when automatic detection cannot complete. The result is stored at a lower confidence level.",
    maxSession: "Maximum session duration (hours)",
    saveSettings: "Save settings",
    noSetups: "No charging setup exists.",
    noBatteries: "No battery type has been added.",
    noCalibration: "No calibration exists for this combination.",
    active: "Active operation",
    portsUsed: "Ports used",
    connectTo: "Connect to",
    liveMeasurement: "Measurement in progress",
    liveCalibration: "Calibration in progress",
    liveCharge: "Charging in progress",
    remaining: "Time remaining",
    plannedEnd: "Expected end",
    measurementMode: "Measurement mode",
    preliminaryValue: "Preliminary value",
    stability: "Stability",
    minRemaining: "Until minimum duration",
    maxDuration: "Maximum duration",
    peakPower: "Peak power",
    targetEnergy: "Target energy",
    chargeEnergy: "Charge energy",
    chartBuilding: "Building measurement trace …",
    confidence: "Confidence",
    method: "Method",
    endpoint: "Detected charge endpoint",
    detected: "Endpoint confirmed",
    auto: "automatic",
    fixed: "fixed",
    currentRevisionOnly: "Calculations use only valid measurements from the current setup and battery revisions.",
    relativeNote: "The target is relative charge energy, not a claimed exact cell state of charge.",
    confirmDelete: "Delete this item? Historical measurement records remain retained but will no longer be used for current calculations.",
    error: "Error",
    adminOnly: "This management function requires administrator rights.",
    selectRequired: "Select a charging setup and battery type.",
    automaticExplanation: "The measurement runs at least for the minimum duration and ends only after the value is stable across several windows and sufficiently resolved by the sensors. It stops at the maximum duration at the latest.",
  },
};

const esc = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const fmt = (value, digits = 2) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "–";
  return Number(value).toFixed(digits);
};

const fmtDuration = (seconds) => {
  if (seconds === null || seconds === undefined || Number.isNaN(Number(seconds))) return "–";
  const total = Math.max(0, Math.round(Number(seconds)));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (h) return `${h} h ${String(m).padStart(2, "0")} min`;
  if (m) return `${m} min ${String(s).padStart(2, "0")} s`;
  return `${s} s`;
};

const fmtDate = (value, language = "de") => {
  if (!value) return "–";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return esc(value);
  return new Intl.DateTimeFormat(language === "de" ? "de-CH" : "en-GB", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(date);
};

const qualityClass = (value) => {
  if (["stable", "high"].includes(value)) return "good";
  if (["limited", "provisional", "medium"].includes(value)) return "warn";
  if (["unstable", "low", "invalid", "error"].includes(value)) return "bad";
  return "neutral";
};

const imageUrl = (image) => {
  if (!image) return "";
  if (typeof image === "string") return image;
  const candidate = image.media_content_id || image.url || "";
  return candidate.startsWith("/") || candidate.startsWith("http") ? candidate : "";
};

const navigateToPanel = () => {
  try {
    window.history.pushState(null, "", BCM_PANEL_PATH);
    window.dispatchEvent(new Event("location-changed"));
  } catch (_err) {
    window.location.assign(BCM_PANEL_PATH);
  }
};

const isEditingElement = (element) => Boolean(
  element?.matches?.("input, select, textarea"),
);

const clampNumberValue = (value, minimum, maximum, fallback) => {
  const parsed = Number(value);
  const fallbackNumber = Number(fallback);
  if (value === "" || value === null || value === undefined || !Number.isFinite(parsed)) {
    return Number.isFinite(fallbackNumber) ? fallbackNumber : minimum;
  }
  return Math.min(maximum, Math.max(minimum, parsed));
};

const selectedPorts = (state) => {
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
  } else if (mode === "idle" && session.idle_measurement_mode === "automatic" && session.auto_min_minutes) {
    lastTime = Math.max(lastTime, firstTime + Number(session.auto_min_minutes) * 60000);
  }
  const span = Math.max(1, lastTime - firstTime);
  const x = (time) => left + ((time - firstTime) / span) * (width - left - right);
  const powerKey = mode === "idle" ? "power_w" : "net_power_w";
  const energyKey = mode === "idle" ? "gross_energy_wh" : "net_energy_wh";
  const hasNumber = (value) => value !== null && value !== undefined && value !== "" && Number.isFinite(Number(value));
  const powerValues = samples.map((item) => item[powerKey]).filter(hasNumber).map(Number);
  const energyValues = samples.map((item) => item[energyKey]).filter(hasNumber).map(Number);
  const powerMax = Math.max(0.1, ...powerValues);
  const targetEnergy = mode === "charging" && Number.isFinite(Number(session.target_energy_wh))
    ? Number(session.target_energy_wh)
    : 0;
  const energyMax = Math.max(0.1, targetEnergy, ...energyValues);
  const yPower = (value) => height - bottom - (Number(value) / powerMax) * (height - top - bottom);
  const yEnergy = (value) => height - bottom - (Number(value) / energyMax) * (height - top - bottom);
  const points = (key, y) => samples
    .filter((item) => hasNumber(item[key]))
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

const BASE_STYLE = `
  :host { display:block; color:var(--primary-text-color); }
  * { box-sizing:border-box; }
  button, input, select, textarea { font:inherit; }
  button { cursor:pointer; }
  .bcm-shell { max-width:1280px; margin:0 auto; padding:20px; }
  .bcm-header { display:flex; justify-content:space-between; align-items:center; gap:16px; margin-bottom:18px; }
  .bcm-title { margin:0; font-size:28px; font-weight:700; }
  .bcm-version { color:var(--secondary-text-color); font-size:12px; }
  .bcm-tabs { display:flex; gap:6px; overflow-x:auto; padding-bottom:4px; margin-bottom:18px; }
  .bcm-tab { border:0; border-radius:18px; padding:9px 14px; background:var(--secondary-background-color); color:var(--primary-text-color); white-space:nowrap; }
  .bcm-tab.active { background:var(--primary-color); color:var(--text-primary-color, white); }
  .bcm-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; }
  .bcm-card { background:var(--card-background-color); border-radius:14px; padding:16px; box-shadow:var(--ha-card-box-shadow,0 2px 8px rgba(0,0,0,.12)); }
  .bcm-card h2,.bcm-card h3 { margin:0 0 12px; }
  .bcm-card h2 { font-size:20px; }
  .bcm-card h3 { font-size:16px; }
  .bcm-row { display:flex; align-items:center; justify-content:space-between; gap:12px; margin:8px 0; }
  .bcm-row.stack { align-items:stretch; flex-direction:column; }
  .bcm-muted { color:var(--secondary-text-color); }
  .bcm-note { padding:12px; border-radius:10px; background:var(--secondary-background-color); line-height:1.45; }
  .bcm-actions { display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }
  .bcm-btn { border:0; border-radius:10px; padding:10px 14px; background:var(--primary-color); color:var(--text-primary-color,white); font-weight:600; }
  .bcm-btn.secondary { background:var(--secondary-background-color); color:var(--primary-text-color); }
  .bcm-btn.danger { background:var(--error-color,#db4437); color:white; }
  .bcm-btn:disabled { opacity:.45; cursor:not-allowed; }
  .bcm-field { display:flex; flex-direction:column; gap:5px; margin:10px 0; }
  .bcm-field label { font-size:13px; font-weight:600; }
  .bcm-field input,.bcm-field select,.bcm-field textarea { width:100%; border:1px solid var(--divider-color); background:var(--card-background-color); color:var(--primary-text-color); border-radius:9px; padding:10px; }
  .bcm-field textarea { min-height:80px; resize:vertical; }
  .bcm-form-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:0 14px; }
  .bcm-badge { display:inline-flex; align-items:center; border-radius:999px; padding:4px 9px; font-size:12px; font-weight:600; background:var(--secondary-background-color); }
  .bcm-badge.good { background:color-mix(in srgb,var(--success-color,#43a047) 20%,transparent); color:var(--success-color,#2e7d32); }
  .bcm-badge.warn { background:color-mix(in srgb,var(--warning-color,#f9a825) 22%,transparent); color:var(--warning-color,#b26a00); }
  .bcm-badge.bad { background:color-mix(in srgb,var(--error-color,#db4437) 18%,transparent); color:var(--error-color,#c62828); }
  .bcm-progress { height:10px; background:var(--secondary-background-color); border-radius:999px; overflow:hidden; }
  .bcm-progress > div { height:100%; background:var(--primary-color); transition:width .25s; }
  .bcm-metrics { display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:10px; }
  .bcm-metric { background:var(--secondary-background-color); border-radius:10px; padding:10px; }
  .bcm-metric strong { display:block; font-size:18px; margin-top:4px; }
  .bcm-list { display:flex; flex-direction:column; gap:10px; }
  .bcm-list-item { border:1px solid var(--divider-color); border-radius:12px; padding:12px; }
  .bcm-list-head { display:flex; gap:12px; align-items:center; justify-content:space-between; }
  .bcm-thumb { width:58px; height:58px; object-fit:contain; border-radius:10px; background:var(--secondary-background-color); }
  .bcm-table-wrap { overflow:auto; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th,td { text-align:left; padding:9px 8px; border-bottom:1px solid var(--divider-color); white-space:nowrap; }
  th { color:var(--secondary-text-color); }
  .bcm-error { margin-bottom:12px; padding:12px; background:color-mix(in srgb,var(--error-color,#db4437) 15%,var(--card-background-color)); border-radius:10px; color:var(--error-color,#c62828); }
  .bcm-overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); z-index:1000; display:flex; align-items:center; justify-content:center; padding:18px; }
  .bcm-dialog { width:min(760px,100%); max-height:90vh; overflow:auto; background:var(--card-background-color); border-radius:16px; padding:18px; box-shadow:0 12px 40px rgba(0,0,0,.35); }
  .bcm-dialog h2 { margin-top:0; }
  .bcm-segment { display:flex; gap:4px; flex-wrap:wrap; }
  .bcm-segment button { border:1px solid var(--divider-color); background:var(--card-background-color); color:var(--primary-text-color); border-radius:9px; min-width:42px; padding:8px 10px; }
  .bcm-segment button.active { background:var(--primary-color); color:white; border-color:var(--primary-color); }
  .bcm-admin { font-size:12px; color:var(--secondary-text-color); }
  .bcm-port-note { margin:10px 0; padding:11px 12px; border-radius:10px; background:color-mix(in srgb,var(--primary-color) 10%,var(--card-background-color)); font-weight:600; }
  .bcm-session-chart { margin-top:14px; border:1px solid var(--divider-color); border-radius:12px; padding:8px 8px 5px; overflow:hidden; background:var(--card-background-color); }
  .bcm-session-chart svg { display:block; width:100%; height:auto; min-height:150px; }
  .bcm-session-chart.compact svg { min-height:100px; }
  .bcm-chart-axis { stroke:var(--divider-color); stroke-width:1; }
  .bcm-chart-power,.bcm-chart-energy { fill:none; stroke-width:2.2; stroke-linejoin:round; stroke-linecap:round; vector-effect:non-scaling-stroke; }
  .bcm-chart-power { stroke:var(--primary-color); }
  .bcm-chart-energy { stroke:var(--warning-color,#f9a825); }
  .bcm-chart-marker { stroke:var(--secondary-text-color); stroke-width:1; stroke-dasharray:4 4; vector-effect:non-scaling-stroke; }
  .bcm-chart-target { stroke:var(--success-color,#43a047); stroke-width:1.5; stroke-dasharray:7 4; vector-effect:non-scaling-stroke; }
  .bcm-chart-legend { display:flex; flex-wrap:wrap; gap:12px; font-size:11px; color:var(--secondary-text-color); padding:2px 5px 4px; }
  .bcm-chart-legend span { display:flex; align-items:center; gap:5px; }
  .bcm-chart-legend i { width:14px; height:3px; border-radius:2px; display:inline-block; }
  .bcm-chart-legend i.power { background:var(--primary-color); }
  .bcm-chart-legend i.energy { background:var(--warning-color,#f9a825); }
  .bcm-chart-empty { margin-top:14px; padding:18px; text-align:center; border:1px dashed var(--divider-color); border-radius:12px; color:var(--secondary-text-color); }
  .bcm-image-preview { width:100%; max-height:220px; object-fit:contain; border-radius:10px; background:var(--secondary-background-color); margin-bottom:8px; }
  .bcm-file-btn { display:inline-flex; align-items:center; }
  .bcm-file-btn input { display:none; }
  @media (max-width:600px) { .bcm-shell { padding:12px; } .bcm-title { font-size:23px; } .bcm-card { padding:13px; } }
`;

class BcmBase extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._state = null;
    this._unsub = null;
    this._subscribing = false;
    this._busy = false;
    this._error = "";
    this._renderPending = false;
    this._renderLock = 0;
    this.shadowRoot.addEventListener("focusout", () => {
      queueMicrotask(() => this._flushDeferredRender());
    });
  }

  set hass(value) {
    this._hass = value;
    this._connect();
    this._requestRender();
  }

  get hass() { return this._hass; }

  connectedCallback() {
    this._connect();
    this._requestRender(true);
  }

  _requestRender(force = false) {
    if (!force && this._renderLock > 0) {
      this._renderPending = true;
      return false;
    }
    if (!force && isEditingElement(this.shadowRoot?.activeElement)) {
      this._renderPending = true;
      return false;
    }
    this._renderPending = false;
    this.render();
    return true;
  }

  _flushDeferredRender() {
    if (this._renderPending && !this.shadowRoot?.activeElement) {
      this._requestRender(true);
    }
  }

  disconnectedCallback() {
    if (this._unsub) {
      this._unsub();
      this._unsub = null;
    }
  }

  get language() {
    const code = String(this._hass?.language || "en").toLowerCase();
    return code.startsWith("de") ? "de" : "en";
  }

  t(key) { return TEXT[this.language][key] || TEXT.en[key] || key; }

  async _connect() {
    if (!this._hass || this._subscribing || this._unsub) return;
    this._subscribing = true;
    try {
      this._state = await this._hass.callWS({ type: `${BCM_DOMAIN}/get_state` });
      this._requestRender();
      this._unsub = await this._hass.connection.subscribeMessage(
        (event) => {
          this._state = event;
          this._requestRender();
        },
        { type: `${BCM_DOMAIN}/subscribe` },
      );
    } catch (err) {
      this._error = err?.message || String(err);
      this._requestRender();
    } finally {
      this._subscribing = false;
    }
  }

  async call(type, payload = {}, options = {}) {
    if (!this._hass || this._busy) return null;
    this._busy = true;
    this._error = "";
    if (options.renderBusy !== false) this._requestRender();
    try {
      const result = await this._hass.callWS({ type: `${BCM_DOMAIN}/${type}`, ...payload });
      this._state = await this._hass.callWS({ type: `${BCM_DOMAIN}/get_state` });
      return result;
    } catch (err) {
      this._error = err?.message || String(err);
      throw err;
    } finally {
      this._busy = false;
      if (options.renderDone !== false) this._requestRender();
    }
  }

  entityOptions(kind, selected = "", optional = false) {
    const states = Object.values(this._hass?.states || {});
    const filtered = states.filter((state) => {
      if (kind === "switch") return state.entity_id.startsWith("switch.");
      if (kind === "energy") return state.entity_id.startsWith("sensor.") && state.attributes?.device_class === "energy";
      if (kind === "power") return state.entity_id.startsWith("sensor.") && state.attributes?.device_class === "power";
      if (kind === "temperature") return state.entity_id.startsWith("sensor.") && state.attributes?.device_class === "temperature";
      return false;
    }).sort((a, b) => String(a.attributes?.friendly_name || a.entity_id).localeCompare(String(b.attributes?.friendly_name || b.entity_id)));
    const empty = optional ? `<option value="">–</option>` : "";
    return empty + filtered.map((state) => {
      const label = `${state.attributes?.friendly_name || state.entity_id} · ${state.entity_id}`;
      return `<option value="${esc(state.entity_id)}" ${state.entity_id === selected ? "selected" : ""}>${esc(label)}</option>`;
    }).join("");
  }
}

class BatteryChargeManagerPanel extends BcmBase {
  constructor() {
    super();
    this._tab = "charge";
    this._dialog = null;
    this._draft = {};
    this._tabsScrollLeft = 0;
    this._dialogScrollTop = 0;
    this._formValues = {
      idleMin: 30,
      idleMax: 480,
      idleFixed: 300,
      maxSession: null,
    };
  }

  set panel(value) { this._panel = value; }

  render() {
    if (!this.shadowRoot) return;
    const s = this._state;
    const admin = Boolean(this._hass?.user?.is_admin);
    const previousTabs = this.shadowRoot.querySelector(".bcm-tabs");
    const tabsScrollLeft = previousTabs?.scrollLeft ?? this._tabsScrollLeft ?? 0;
    const previousDialog = this.shadowRoot.querySelector(".bcm-dialog");
    const dialogScrollTop = previousDialog?.scrollTop ?? this._dialogScrollTop ?? 0;
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
    const dialog = this.shadowRoot.querySelector(".bcm-dialog");
    if (dialog) {
      dialog.scrollTop = dialogScrollTop;
      this._dialogScrollTop = dialogScrollTop;
      dialog.addEventListener("scroll", () => { this._dialogScrollTop = dialog.scrollTop; });
    }
    this.bindEvents();
  }

  tabButton(id, label) {
    return `<button class="bcm-tab ${this._tab === id ? "active" : ""}" data-tab="${id}">${label}</button>`;
  }

  renderTab(admin) {
    if (this._tab === "batteries") return this.renderBatteries(admin);
    if (this._tab === "setups") return this.renderSetups(admin);
    if (this._tab === "idle") return this.renderIdle(admin);
    if (this._tab === "calibrations") return this.renderCalibrations(admin);
    if (this._tab === "settings") return this.renderSettings(admin);
    return this.renderCharge();
  }

  selectors({ includeTarget = true } = {}) {
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

  renderCharge() {
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

  metric(label, value) { return `<div class="bcm-metric"><span class="bcm-muted">${label}</span><strong>${value}</strong></div>`; }

  renderBatteries(admin) {
    const s = this._state;
    return `<section class="bcm-card"><div class="bcm-list-head"><h2>${this.t("batteries")}</h2>${admin ? `<button class="bcm-btn" data-action="new-battery">${this.t("addBattery")}</button>` : `<span class="bcm-admin">${this.t("adminOnly")}</span>`}</div><p class="bcm-muted">${this.t("currentRevisionOnly")}</p><div class="bcm-list">${s.batteries.length ? s.batteries.map((battery) => this.batteryItem(battery, admin)).join("") : `<div class="bcm-note">${this.t("noBatteries")}</div>`}</div></section>`;
  }

  batteryItem(battery, admin) {
    const img = imageUrl(battery.image);
    return `<div class="bcm-list-item"><div class="bcm-list-head"><div style="display:flex;gap:12px;align-items:center">${img ? `<img class="bcm-thumb" src="${esc(img)}">` : ""}<div><strong>${esc(battery.name)}</strong><div class="bcm-muted">${esc([battery.manufacturer,battery.model].filter(Boolean).join(" "))}</div><div class="bcm-muted">${esc(battery.technology)} · ${esc(battery.form_factor)} · ${battery.nominal_capacity_mah} mAh</div></div></div><span class="bcm-badge">${this.t("revision")} ${battery.revision}</span></div>${admin ? `<div class="bcm-actions"><button class="bcm-btn secondary" data-edit-battery="${esc(battery.battery_id)}">${this.t("edit")}</button><button class="bcm-btn danger" data-delete-battery="${esc(battery.battery_id)}">${this.t("delete")}</button></div>` : ""}</div>`;
  }

  renderSetups(admin) {
    const s = this._state;
    return `<section class="bcm-card"><div class="bcm-list-head"><h2>${this.t("setups")}</h2>${admin ? `<button class="bcm-btn" data-action="new-setup">${this.t("addSetup")}</button>` : `<span class="bcm-admin">${this.t("adminOnly")}</span>`}</div><p class="bcm-muted">${this.t("currentRevisionOnly")}</p><div class="bcm-list">${s.setups.length ? s.setups.map((setup) => this.setupItem(setup, admin)).join("") : `<div class="bcm-note">${this.t("noSetups")}</div>`}</div></section>`;
  }

  setupItem(setup, admin) {
    const idle = setup.idle_summary || {};
    const img = imageUrl(setup.image);
    return `<div class="bcm-list-item"><div class="bcm-list-head"><div style="display:flex;gap:12px;align-items:center">${img ? `<img class="bcm-thumb" src="${esc(img)}">` : ""}<div><strong>${esc(setup.name)}</strong><div class="bcm-muted">${esc(setup.switch_entity)} · ${esc(setup.energy_sensor)}${setup.power_sensor ? ` · ${esc(setup.power_sensor)}` : ""}${setup.temperature_sensor ? ` · ${esc(setup.temperature_sensor)}` : ""}</div><div class="bcm-muted">${esc((setup.port_labels || []).join(" / "))}</div></div></div><span class="bcm-badge">${this.t("revision")} ${setup.revision}</span></div><div class="bcm-row"><span>${this.t("baseline")}</span><strong>${idle.below_detection_count ? `&lt; ${fmt(idle.upper_bound_power_w,3)} W` : `${fmt(idle.baseline_power_w,3)} W`} <span class="bcm-badge ${qualityClass(idle.quality)}">${esc(idle.quality || "none")}</span></strong></div>${admin ? `<div class="bcm-actions"><button class="bcm-btn secondary" data-edit-setup="${esc(setup.setup_id)}">${this.t("edit")}</button><button class="bcm-btn danger" data-delete-setup="${esc(setup.setup_id)}" ${this._state.setups.length <= 1 ? "disabled" : ""}>${this.t("delete")}</button></div>` : ""}</div>`;
  }

  renderIdle(admin) {
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

  selectSetupOnly() {
    const s = this._state;
    return `<div class="bcm-field"><label>${this.t("setup")}</label><select data-select="setup" ${s.session.mode !== "idle" ? "disabled" : ""}>${s.setups.map((item) => `<option value="${esc(item.setup_id)}" ${item.setup_id === s.selected_setup_id ? "selected" : ""}>${esc(item.name)}</option>`).join("")}</select></div>`;
  }

  idleTable(rows, admin) {
    if (!rows.length) return `<div class="bcm-note">–</div>`;
    return `<div class="bcm-table-wrap"><table><thead><tr><th>${this.t("status")}</th><th>${this.t("auto")}/${this.t("fixed")}</th><th>${this.t("baseline")}</th><th>${this.t("elapsed")}</th><th>${this.t("confidence")}</th><th>${this.t("detected")}</th><th></th></tr></thead><tbody>${rows.map((item) => `<tr><td><span class="bcm-badge ${item.valid ? qualityClass(item.confidence) : "bad"}">${item.valid ? (item.reliable ? this.t("reliable") : this.t("valid")) : this.t("invalid")}</span></td><td>${esc(item.mode)}</td><td>${item.below_detection_limit ? `&lt; ${fmt(item.upper_bound_power_w,3)} W` : `${fmt(item.median_power_w ?? item.average_power_w,3)} W`}</td><td>${fmtDuration(item.duration_seconds)}</td><td>${esc(item.confidence)}</td><td>${fmtDate(item.finished_at,this.language)}</td><td>${admin ? `<button class="bcm-btn secondary" data-validity="idle" data-record="${esc(item.measurement_id)}" data-valid="${item.valid ? "false" : "true"}">${item.valid ? this.t("invalid") : this.t("valid")}</button>` : ""}</td></tr>`).join("")}</tbody></table></div>`;
  }

  renderCalibrations(admin) {
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

  linearModel() {
    const model = this._state.linear_model || {};
    if (!model.available) return `<p class="bcm-muted">${this.t("linearModel")}: ${this.t("notAvailable")}</p>`;
    return `<div class="bcm-note"><strong>${this.t("linearModel")}</strong><br>E(n) = ${fmt(model.intercept_wh,3)} Wh + ${fmt(model.per_battery_wh,3)} Wh × n<br>R² = ${fmt(model.r_squared,3)}<br><span class="bcm-muted">Plausibilisierung; nicht als primärer Abschaltwert verwendet.</span></div>`;
  }

  calibrationTable(rows, admin) {
    if (!rows.length) return `<div class="bcm-note">${this.t("noCalibration")}</div>`;
    return `<div class="bcm-table-wrap"><table><thead><tr><th>${this.t("status")}</th><th>${this.t("net")}</th><th>${this.t("elapsed")}</th><th>${this.t("endpoint")}</th><th>${this.t("detected")}</th><th>${this.t("confidence")}</th><th>${this.t("method")}</th><th></th></tr></thead><tbody>${rows.map((item) => `<tr><td><span class="bcm-badge ${item.valid ? qualityClass(item.confidence) : "bad"}">${item.valid ? (item.idle_correction_status === "pending" ? this.t("pendingCorrection") : this.t("valid")) : this.t("invalid")}</span></td><td>${fmt(item.net_energy_wh)} Wh</td><td>${fmtDuration(item.charge_duration_seconds)}</td><td>${fmtDate(item.charge_finished_at,this.language)}</td><td>${fmtDate(item.end_detected_at,this.language)}</td><td>${esc(item.confidence)}</td><td>${esc(item.end_method)}</td><td>${admin ? `<button class="bcm-btn secondary" data-validity="calibration" data-record="${esc(item.calibration_id)}" data-valid="${item.valid ? "false" : "true"}">${item.valid ? this.t("invalid") : this.t("valid")}</button>` : ""}</td></tr>`).join("")}</tbody></table></div>`;
  }

  renderSettings(admin) {
    const s = this._state;
    return `<section class="bcm-card"><h2>${this.t("settings")}</h2><div class="bcm-note">${this.t("currentRevisionOnly")}</div>${admin ? `<div class="bcm-field"><label>${this.t("maxSession")}</label><input id="max-session" data-form-value="maxSession" type="number" min="1" max="48" step="0.5" value="${esc(this._formValues.maxSession ?? s.max_session_hours)}"></div><button class="bcm-btn" data-action="save-settings">${this.t("saveSettings")}</button>` : `<p class="bcm-admin">${this.t("adminOnly")}</p>`}</section>`;
  }

  renderDialog(admin) {
    if (!this._dialog || !admin) return "";
    const d = this._draft;
    const dialogError = this._error ? `<div class="bcm-error bcm-dialog-error"><strong>${this.t("error")}:</strong> ${esc(this._error)}</div>` : "";
    if (this._dialog === "battery") {
      return `<div class="bcm-overlay"><div class="bcm-dialog"><h2>${d.battery_id ? this.t("edit") : this.t("addBattery")}</h2>${dialogError}<div class="bcm-form-grid">${this.input("name",this.t("name"),d.name,true)}${this.input("manufacturer",this.t("manufacturer"),d.manufacturer)}${this.input("model",this.t("model"),d.model)}${this.input("nominal_capacity_mah",this.t("capacity"),d.nominal_capacity_mah ?? "",true,"number")}${this.input("nominal_voltage_v",this.t("voltage"),d.nominal_voltage_v,"", "number", "0.01")}${this.input("nominal_energy_wh",this.t("energy"),d.nominal_energy_wh,"", "number", "0.01")}${this.selectField("technology",this.t("technology"),["Li-Ion USB-C","Li-Ion","LiFePO4","NiMH","NiCd","Other"],d.technology || "Li-Ion USB-C")}${this.selectField("form_factor",this.t("formFactor"),["AAA","AA","C","D","9V","18650","21700","Proprietary","Other"],d.form_factor || "AA")}${this.selectField("charging_method",this.t("chargingMethod"),["Integrated USB-C charger","External USB charger","Dedicated charger","Other"],d.charging_method || "Integrated USB-C charger")}${this.input("discharge_method",this.t("dischargeMethod"),d.discharge_method)}${this.input("rest_time_minutes",this.t("restTime"),d.rest_time_minutes ?? "","", "number", "1")}${this.imageField("battery",d.image)}</div>${this.textarea("starting_condition_notes",this.t("startingNotes"),d.starting_condition_notes)}${this.textarea("notes",this.t("notes"),d.notes)}<div class="bcm-actions"><button class="bcm-btn" data-action="save-battery">${this.t("save")}</button><button class="bcm-btn secondary" data-action="close-dialog">${this.t("cancel")}</button></div></div></div>`;
    }
    if (this._dialog === "setup") {
      return `<div class="bcm-overlay"><div class="bcm-dialog"><h2>${d.setup_id ? this.t("edit") : this.t("addSetup")}</h2>${dialogError}<div class="bcm-form-grid">${this.input("name",this.t("name"),d.name,true)}<div class="bcm-field"><label>${this.t("switchEntity")}</label><select data-draft="switch_entity" required>${this.entityOptions("switch",d.switch_entity)}</select></div><div class="bcm-field"><label>${this.t("energySensor")}</label><select data-draft="energy_sensor" required>${this.entityOptions("energy",d.energy_sensor)}</select></div><div class="bcm-field"><label>${this.t("powerSensor")}</label><select data-draft="power_sensor">${this.entityOptions("power",d.power_sensor,true)}</select></div><div class="bcm-field"><label>${this.t("temperatureSensor")}</label><select data-draft="temperature_sensor">${this.entityOptions("temperature",d.temperature_sensor,true)}</select></div>${this.input("charger_model",this.t("chargerModel"),d.charger_model)}${this.input("cable_description",this.t("cable"),d.cable_description)}${this.input("port_labels",this.t("ports"),Array.isArray(d.port_labels) ? d.port_labels.join(", ") : (d.port_labels || "A, B, C, D"),true)}${this.input("max_power_w",this.t("maxPower"),d.max_power_w ?? 100,true,"number","0.1")}${this.input("max_temperature_c",this.t("maxTemperature"),d.max_temperature_c,"", "number", "0.1")}${this.imageField("setup",d.image)}</div>${this.textarea("description",this.t("description"),d.description)}<div class="bcm-actions"><button class="bcm-btn" data-action="save-setup">${this.t("save")}</button><button class="bcm-btn secondary" data-action="close-dialog">${this.t("cancel")}</button></div></div></div>`;
    }
    return "";
  }

  input(key, label, value = "", required = false, type = "text", step = "1") {
    return `<div class="bcm-field"><label>${label}</label><input data-draft="${key}" type="${type}" step="${step}" value="${esc(value ?? "")}" ${required ? "required" : ""}></div>`;
  }
  imageField(kind, image) {
    const url = imageUrl(image);
    const textValue = typeof image === "string" ? image : (image?.url || image?.media_content_id || "");
    return `<div class="bcm-field"><label>${this.t("image")}</label>${url ? `<img class="bcm-image-preview" src="${esc(url)}">` : ""}<input data-draft="image" type="text" value="${esc(textValue)}"><div class="bcm-actions"><label class="bcm-btn secondary bcm-file-btn">${this.t("uploadImage")}<input data-image-upload="${kind}" type="file" accept="image/jpeg,image/png,image/webp"></label>${url ? `<button type="button" class="bcm-btn secondary" data-remove-image>${this.t("removeImage")}</button>` : ""}</div></div>`;
  }
  textarea(key,label,value="") { return `<div class="bcm-field"><label>${label}</label><textarea data-draft="${key}">${esc(value || "")}</textarea></div>`; }
  selectField(key,label,options,value) { return `<div class="bcm-field"><label>${label}</label><select data-draft="${key}">${options.map((item) => `<option value="${esc(item)}" ${item === value ? "selected" : ""}>${esc(item)}</option>`).join("")}</select></div>`; }

  bindEvents() {
    this.shadowRoot.querySelectorAll("[data-tab]").forEach((el) => el.addEventListener("click", () => { this._tab = el.dataset.tab; this.render(); }));
    this.shadowRoot.querySelectorAll("[data-draft]").forEach((el) => el.addEventListener("input", () => { this._draft[el.dataset.draft] = el.value; }));
    this.shadowRoot.querySelectorAll("[data-image-upload]").forEach((el) => el.addEventListener("change", () => this.handleImageUpload(el)));
    this.shadowRoot.querySelectorAll("[data-remove-image]").forEach((el) => el.addEventListener("click", () => { this._draft.image = ""; this._dialogScrollTop = this.shadowRoot.querySelector(".bcm-dialog")?.scrollTop || 0; this.render(); }));
    this.shadowRoot.querySelectorAll("[data-form-value]").forEach((el) => {
      el.addEventListener("input", () => {
        this._formValues[el.dataset.formValue] = el.value;
      });
      el.addEventListener("change", () => this.commitNumberInput(el));
    });
    this.shadowRoot.querySelectorAll("[data-select]").forEach((el) => el.addEventListener("change", async () => {
      const key = el.dataset.select;
      const payload = key === "setup" ? { setup_id: el.value } : { battery_id: el.value };
      try { await this.call("select", payload); } catch (_err) {}
    }));
    this.shadowRoot.querySelectorAll("[data-quantity]").forEach((el) => el.addEventListener("click", async () => { try { await this.call("select", { quantity: Number(el.dataset.quantity) }); } catch (_err) {} }));
    const target = this.shadowRoot.querySelector("[data-target]");
    if (target) target.addEventListener("change", async () => { try { await this.call("select", { target_percent: Number(target.value) }); } catch (_err) {} });
    this.shadowRoot.querySelectorAll("[data-edit-battery]").forEach((el) => el.addEventListener("click", () => { const item = this._state.batteries.find((x) => x.battery_id === el.dataset.editBattery); this._draft = structuredClone(item || {}); this._dialog = "battery"; this._dialogScrollTop = 0; this.render(); }));
    this.shadowRoot.querySelectorAll("[data-edit-setup]").forEach((el) => el.addEventListener("click", () => { const item = this._state.setups.find((x) => x.setup_id === el.dataset.editSetup); this._draft = structuredClone(item || {}); this._dialog = "setup"; this._dialogScrollTop = 0; this.render(); }));
    this.shadowRoot.querySelectorAll("[data-delete-battery]").forEach((el) => el.addEventListener("click", async () => { if (confirm(this.t("confirmDelete"))) { try { await this.call("delete_battery", { battery_id: el.dataset.deleteBattery }); } catch (_err) {} } }));
    this.shadowRoot.querySelectorAll("[data-delete-setup]").forEach((el) => el.addEventListener("click", async () => { if (confirm(this.t("confirmDelete"))) { try { await this.call("delete_setup", { setup_id: el.dataset.deleteSetup }); } catch (_err) {} } }));
    this.shadowRoot.querySelectorAll("[data-validity]").forEach((el) => el.addEventListener("click", async () => { try { await this.call("set_measurement_validity", { record_type: el.dataset.validity, record_id: el.dataset.record, valid: el.dataset.valid === "true", reason: el.dataset.valid === "true" ? "" : "Invalidated in panel" }); } catch (_err) {} }));
    this.shadowRoot.querySelectorAll("[data-action]").forEach((el) => el.addEventListener("click", () => this.handleAction(el.dataset.action)));
  }

  async handleAction(action) {
    try {
      if (action === "new-battery") { this._draft = {}; this._dialog = "battery"; this._dialogScrollTop = 0; this.render(); return; }
      if (action === "new-setup") { this._draft = { port_labels:["A","B","C","D"], max_power_w:100 }; this._dialog = "setup"; this._dialogScrollTop = 0; this.render(); return; }
      if (action === "close-dialog") { this._dialog = null; this._draft = {}; this._dialogScrollTop = 0; this.render(); return; }
      if (action === "save-battery") { await this.saveDialog("battery", "save_battery"); return; }
      if (action === "save-setup") { await this.saveDialog("setup", "save_setup"); return; }
      if (action === "start-charge") await this.call("start_charge");
      if (action === "stop") await this.call("stop", { reason:"Stopped by user" });
      if (action === "start-calibration") await this.call("start_calibration");
      if (action === "finish-calibration") await this.call("finish_calibration");
      if (action === "idle-auto") {
        const minimum = this.readNumberInput("idle-min", 30);
        let maximum = this.readNumberInput("idle-max", 480);
        if (maximum < minimum) {
          maximum = minimum;
          this._formValues.idleMax = maximum;
          const field = this.shadowRoot.getElementById("idle-max");
          if (field) field.value = String(maximum);
        }
        await this.call("start_idle_measurement", {
          mode: "automatic",
          auto_min_minutes: minimum,
          auto_max_minutes: maximum,
        });
      }
      if (action === "idle-fixed") await this.call("start_idle_measurement", {
        mode: "fixed",
        duration_minutes: this.readNumberInput("idle-fixed", 300),
      });
      if (action === "save-settings") await this.call("set_settings", {
        max_session_hours: this.readNumberInput("max-session", 12),
      });
    } catch (_err) {}
  }

  async saveDialog(kind, command) {
    this._renderLock += 1;
    const button = this.shadowRoot.querySelector(`[data-action="save-${kind}"]`);
    if (button) button.disabled = true;
    try {
      await this.call(command, { data: this.normalizeDraft(kind) }, { renderBusy:false, renderDone:false });
      this._dialog = null;
      this._draft = {};
      this._dialogScrollTop = 0;
    } finally {
      this._renderLock = Math.max(0, this._renderLock - 1);
      this._requestRender(true);
    }
  }

  async handleImageUpload(input) {
    const file = input.files?.[0];
    if (!file) return;
    this._renderLock += 1;
    try {
      const prepared = await this.prepareImageFile(file);
      const data = await this.fileToBase64(prepared);
      const result = await this.call("upload_image", {
        filename: prepared.name || file.name || "image",
        mime_type: prepared.type,
        data,
      }, { renderBusy:false, renderDone:false });
      if (result?.path) this._draft.image = result.path;
    } catch (err) {
      this._error = err?.message || String(err);
    } finally {
      this._renderLock = Math.max(0, this._renderLock - 1);
      this._requestRender(true);
    }
  }

  async prepareImageFile(file) {
    const allowed = ["image/jpeg", "image/png", "image/webp"];
    if (!allowed.includes(file.type)) throw new Error("Unsupported image type");
    if (file.size <= 1800000) return file;
    if (typeof createImageBitmap !== "function" || typeof document === "undefined") {
      throw new Error("Image is too large; choose an image below 2 MB");
    }
    const bitmap = await createImageBitmap(file);
    const maxSide = 1600;
    const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(bitmap.width * scale));
    canvas.height = Math.max(1, Math.round(bitmap.height * scale));
    canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close?.();
    const blob = await new Promise((resolve, reject) => canvas.toBlob((value) => value ? resolve(value) : reject(new Error("Could not resize image")), "image/webp", 0.85));
    if (blob.size > 2000000) throw new Error("Image is too large after resizing");
    return new File([blob], "upload.webp", { type:"image/webp" });
  }

  fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || "").split(",", 2)[1] || "");
      reader.onerror = () => reject(new Error("Could not read image"));
      reader.readAsDataURL(file);
    });
  }

  commitNumberInput(input, fallbackValue = undefined) {
    const minimum = Number(input.min || Number.NEGATIVE_INFINITY);
    const maximum = Number(input.max || Number.POSITIVE_INFINITY);
    const key = input.dataset.formValue;
    const stored = this._formValues[key];
    const fallback = fallbackValue ?? (stored === "" || stored === null ? minimum : stored);
    const value = clampNumberValue(input.value, minimum, maximum, fallback);
    input.value = String(value);
    this._formValues[key] = value;
    return value;
  }

  readNumberInput(id, fallback) {
    const input = this.shadowRoot.getElementById(id);
    if (!input) return fallback;
    return this.commitNumberInput(input, fallback);
  }

  normalizeDraft(type) {
    const d = { ...this._draft };
    if (type === "battery") {
      d.nominal_capacity_mah = d.nominal_capacity_mah === "" || d.nominal_capacity_mah === null || d.nominal_capacity_mah === undefined ? null : Number(d.nominal_capacity_mah);
      d.nominal_voltage_v = d.nominal_voltage_v === "" || d.nominal_voltage_v === undefined ? null : Number(d.nominal_voltage_v);
      d.nominal_energy_wh = d.nominal_energy_wh === "" || d.nominal_energy_wh === undefined ? null : Number(d.nominal_energy_wh);
      d.rest_time_minutes = d.rest_time_minutes === "" || d.rest_time_minutes === undefined ? null : Number(d.rest_time_minutes);
    } else {
      d.power_sensor = d.power_sensor || null;
      d.temperature_sensor = d.temperature_sensor || null;
      d.max_power_w = Number(d.max_power_w || 100);
      d.max_temperature_c = d.max_temperature_c === "" || d.max_temperature_c === null || d.max_temperature_c === undefined ? null : Number(d.max_temperature_c);
      d.port_labels = String(d.port_labels || "A,B,C,D").split(",").map((item) => item.trim()).filter(Boolean);
    }
    return d;
  }
}

class BatteryChargeManagerCard extends BcmBase {
  constructor() {
    super();
    this._config = {};
  }

  setConfig(config) { this._config = config || {}; this.render(); }
  static getStubConfig() { return {}; }
  static getConfigForm() {
    return {
      schema: [{ name: "title", selector: { text: {} } }],
      computeLabel: (schema) => schema.name === "title" ? "Title" : undefined,
    };
  }
  getCardSize() { return 4; }
  getGridOptions() {
    return { rows: 7, min_rows: 5, columns: 6, min_columns: 3 };
  }

  render() {
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

  bindCardEvents() {
    this.shadowRoot.querySelector("[data-open]")?.addEventListener("click", navigateToPanel);
    this.shadowRoot.querySelectorAll("[data-card-select]").forEach((el) => el.addEventListener("change", async () => { const payload = el.dataset.cardSelect === "setup" ? {setup_id:el.value}:{battery_id:el.value}; try{await this.call("select",payload);}catch(_err){} }));
    this.shadowRoot.querySelectorAll("[data-card-quantity]").forEach((el) => el.addEventListener("click", async () => { try{await this.call("select",{quantity:Number(el.dataset.cardQuantity)});}catch(_err){} }));
    this.shadowRoot.querySelector("[data-card-target]")?.addEventListener("change", async (event) => { try{await this.call("select",{target_percent:Number(event.target.value)});}catch(_err){} });
    this.shadowRoot.querySelector("[data-card-action='start']")?.addEventListener("click", async () => { try{await this.call("start_charge");}catch(_err){} });
    this.shadowRoot.querySelector("[data-card-action='stop']")?.addEventListener("click", async () => { try{await this.call("stop",{reason:"Stopped from dashboard card"});}catch(_err){} });
  }
}

const requestedPanelElement = (() => {
  try {
    const value = new URL(import.meta.url).searchParams.get("panel") || "";
    return /^battery-charge-manager-panel-r[a-f0-9]{12}$/.test(value)
      ? value
      : "battery-charge-manager-panel";
  } catch (_err) {
    return "battery-charge-manager-panel";
  }
})();
if (!customElements.get(requestedPanelElement)) customElements.define(requestedPanelElement, BatteryChargeManagerPanel);
if (!customElements.get("battery-charge-manager-card")) customElements.define("battery-charge-manager-card", BatteryChargeManagerCard);
window.customCards = window.customCards || [];
if (!window.customCards.some((item) => item.type === "battery-charge-manager-card")) {
  window.customCards.push({
    type: "battery-charge-manager-card",
    name: "Battery Charge Manager",
    description: "Compact battery charging control with a direct link to the full manager panel.",
    preview: true,
  });
}

export { BcmBase, clampNumberValue, isEditingElement };
