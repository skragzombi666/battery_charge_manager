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
    home: "Startseite",
    manage: "Verwaltung",
    haMenu: "Home Assistant Seitenleiste öffnen",
    change: "Ändern",
    chargeOptions: "Ladeoptionen",
    calibrate: "Kalibrieren",
    calibrationHomeHint: "Bei Bedarf aufklappen · dieses Gerät merkt sich den Zustand",
    calibrationSelection: "Verwendet die oben gewählte Anzahl, den Akkutyp und die Ladeanordnung.",
    noActive: "Kein Vorgang aktiv",
    lastOperation: "Letzter Vorgang",
    viewActive: "Zum laufenden Vorgang",
    activeFirst: "Der laufende Vorgang muss zuerst beendet werden.",
    readiness: "Ladebereitschaft",
    readyToCharge: "Bereit zum Laden",
    calibrationHistory: "Kalibrationen und Historie",
    manageIntro: "Akkutypen und Ladeanordnungen einrichten, Messungen prüfen und Einstellungen anpassen.",
    batteriesHelp: "Akkutypen erfassen und ihre Eigenschaften bearbeiten.",
    setupsHelp: "Ladegerät, Anschlüsse, Sensoren und Sicherheitsgrenzen einrichten.",
    idleHelp: "Leerlauf messen, Kurven ansehen und verwendete Messungen verwalten.",
    calibrationsHelp: "Kalibrieren, Kurven prüfen und Messungen für Revisionen freigeben.",
    settingsHelp: "Die maximale Laufzeit für Vorgänge festlegen.",
    setupFirst: "Ladeanordnung einrichten",
    batteryFirst: "Akkutyp erfassen",
    loading: "Wird geladen …",
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
    energy: "Nennenergie (mWh)",
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
    currentRevisionOnly: "Berechnungen verwenden gültige Messungen der aktuellen Revision sowie ausdrücklich dafür freigegebene ältere Messungen. Messqualität und gültige Leerlaufreferenzen bestimmen zusätzlich die tatsächliche Verwendung.",
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
    home: "Home",
    manage: "Management",
    haMenu: "Open Home Assistant sidebar",
    change: "Change",
    chargeOptions: "Charging options",
    calibrate: "Calibrate",
    calibrationHomeHint: "Expand when needed · this device remembers your choice",
    calibrationSelection: "Uses the quantity, battery type and charging setup selected above.",
    noActive: "No operation running",
    lastOperation: "Last operation",
    viewActive: "View running operation",
    activeFirst: "Finish the running operation first.",
    readiness: "Charging readiness",
    readyToCharge: "Ready to charge",
    calibrationHistory: "Calibrations and history",
    manageIntro: "Set up battery types and charging arrangements, review measurements and adjust settings.",
    batteriesHelp: "Add battery types and edit their properties.",
    setupsHelp: "Configure chargers, ports, sensors and safety limits.",
    idleHelp: "Measure idle power, inspect curves and manage the measurements in use.",
    calibrationsHelp: "Calibrate, inspect curves and approve measurements for revisions.",
    settingsHelp: "Set the maximum duration of an operation.",
    setupFirst: "Configure charging setup",
    batteryFirst: "Add battery type",
    loading: "Loading …",
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
    energy: "Nominal energy (mWh)",
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
    currentRevisionOnly: "Calculations use valid current-revision measurements and older records explicitly approved for them. Measurement quality and valid idle references also determine actual use.",
    relativeNote: "The target is relative charge energy, not a claimed exact cell state of charge.",
    confirmDelete: "Delete this item? Historical measurement records remain retained but will no longer be used for current calculations.",
    error: "Error",
    adminOnly: "This management function requires administrator rights.",
    selectRequired: "Select a charging setup and battery type.",
    automaticExplanation: "The measurement runs at least for the minimum duration and ends only after the value is stable across several windows and sufficiently resolved by the sensors. It stops at the maximum duration at the latest.",
  },
};

const HISTORY_TEXT = {
  de: {
    details: "Details", close: "Schliessen", refresh: "Aktualisieren", loading: "Messung wird geladen …",
    originRevision: "Ursprüngliche Revision", currentRevision: "Aktuelle Revision", usage: "Verwendung",
    validity: "Gültigkeit", result: "Messwert", recorded: "Gemessen am", actions: "Aktionen",
    usedCount: "Einbezogen", allRecords: "Alle Messungen", usedRecords: "Einbezogene Messungen",
    excludedRecords: "Nicht einbezogen", historicalRecords: "Andere Revisionen", moreRecords: "Weitere anzeigen",
    revision_native: "Aktuelle Revision", revision_approved: "Für aktuelle Revision freigegeben",
    revision_historical: "Andere Revision", revision_unavailable: "Zuordnung gelöscht",
    revision_incompatible_quantity: "Anzahl nicht kompatibel",
    usage_used: "Wird verwendet", usage_invalid: "Nicht verwendet: ungültig",
    usage_historical: "Nicht verwendet: Freigabe für aktuelle Revision fehlt",
    usage_unavailable: "Nicht verwendet: Ladeanordnung oder Akkutyp gelöscht",
    usage_incompatible_quantity: "Nicht verwendet: Anzahl passt nicht zur Ladeanordnung",
    usage_pending_correction: "Nicht verwendet: Leerlaufkorrektur ausstehend",
    usage_invalid_idle_reference: "Nicht verwendet: zugrunde liegende Leerlaufmessung ungültig oder fehlt",
    usage_no_net_energy: "Nicht verwendet: keine verwertbare Nettoenergie",
    usage_lower_confidence: "Nicht verwendet: Messungen mit höherem Vertrauen vorhanden",
    usage_unreliable: "Nicht verwendet: zuverlässige Messungen haben Vorrang",
    usage_provisional_baseline: "Nur vorläufiger Wert; keine Leerlaufkorrektur",
    confidence_high: "hoch", confidence_medium: "mittel", confidence_low: "niedrig", confidence_unknown: "unbekannt",
    invalidate: "Als ungültig markieren", restore: "Gültigkeit wiederherstellen",
    approve: "Für aktuelle Revision freigeben", revoke: "Revisionsfreigabe widerrufen",
    reanalyze: "Leerlaufkorrektur neu berechnen", decisionReason: "Begründung",
    reasonRequired: "Eine Begründung ist erforderlich.", equivalentRequired: "Die Gleichwertigkeit der Messbedingungen muss bestätigt sein.",
    equivalent: "Die physische Ladeanordnung und – bei Kalibrationen – Akkutyp, Anschlussbelegung und Ausgangszustand sind unverändert bzw. messtechnisch gleichwertig. Die Unterschiede sind nur formeller Natur.",
    approveHint: "Die ursprüngliche Revision bleibt erhalten. Diese Freigabe gilt nur für die unten angezeigte aktuelle Revision. Gültigkeit und Messqualität werden weiterhin separat geprüft. Ausstehende Leerlaufkorrekturen können danach automatisch berechnet werden.",
    revokeHint: "Die Messung bleibt gültig und in der Historie erhalten. Sie wird für diese aktuelle Revision nicht mehr berücksichtigt. Bereits gespeicherte Kalibrationsauswertungen behalten ihre damaligen Leerlaufwerte; ein Widerruf ist keine Ungültigerklärung der Messung.",
    invalidateIdleHint: "Diese Messung wird aus der Leerlaufberechnung ausgeschlossen. Kalibrationen, deren Korrektur auf ihr beruht, werden ebenfalls nicht mehr für Ladeziele verwendet. Wiederherstellen oder eine gezielte Neuberechnung mit gültigen Leerlaufdaten macht sie wieder nutzbar. Messkurven und Historie bleiben erhalten.",
    invalidateCalibrationHint: "Diese Kalibration wird aus der Berechnung der Ladeenergie ausgeschlossen. Median, Qualität und künftige Ladeziele werden aus den verbleibenden nutzbaren Kalibrationen berechnet. Messkurve und Historie bleiben erhalten.",
    restoreHint: "Die Messung wird wieder als gültig bewertet. Ihre Revision und Messqualität entscheiden weiterhin über die tatsächliche Verwendung. Eine frühere Revisionsfreigabe wird nicht automatisch erneuert. Ausstehende Leerlaufkorrekturen können automatisch berechnet werden.",
    reanalyzeHint: "Die gespeicherte Kurve wird mit der aktuell verwendeten zuverlässigen Leerlaufleistung neu ausgewertet. Nettoenergie, erkanntes Ladeende und künftige Ladeziele können sich ändern. Die bisherige Auswertung bleibt in der Auswertungshistorie erhalten.",
    noTrace: "Keine Messkurve gespeichert. Für diese ältere Messung sind nur die vorhandenen Ergebnisdaten verfügbar.",
    trace: "Messkurve", traceSummary: "Die Kurve zeigt den gespeicherten Verlauf. Lange Messreihen werden für die Anzeige verdichtet; Spitzenwerte bleiben berücksichtigt.",
    point: "Messpunkt", rawEnergy: "Zählerstand", sourceMeasurements: "Zugrunde liegende Leerlaufmessungen",
    noSources: "Keine Leerlaufreferenzen gespeichert.", missingSource: "Messung nicht mehr vorhanden",
    dependentRecords: "Davon abhängige Kalibrationen", changes: "Änderungen seit der Messung",
    noChanges: "Keine Unterschiede in den gespeicherten Beschreibungen. Die Revisionsnummern unterscheiden sich gegebenenfalls trotzdem.",
    field: "Angabe", original: "Bei der Messung", current: "Heute", snapshots: "Ursprüngliche Messbedingungen",
    decisions: "Freigabe- und Gültigkeitshistorie", noDecisions: "Noch keine nachträglichen Entscheidungen protokolliert.",
    priorAnalyses: "Auswertungshistorie", analysisRevision: "Auswertung", priorResult: "Frühere Auswertung",
    firstRecorded: "Ursprünglich gespeichert", activeSessionHint: "Änderungen sind erst nach Ende des laufenden Vorgangs möglich.",
    staleDetail: "Status oder Revision haben sich geändert. Details aktualisieren, bevor eine Entscheidung getroffen wird.",
    historyHint: "Gültigkeit und tatsächliche Verwendung sind getrennt. Ein gültiger Datensatz kann wegen Revision, Leerlaufkorrektur oder Messqualität ausgeschlossen sein. Änderungen wirken auf die Berechnung künftiger Ladevorgänge.",
    method_manual: "Manuell abgeschlossen", method_energy_plateau: "Energieplateau",
    method_energy_plateau_and_low_power: "Energieplateau und niedrige Leistung",
    method_retrospective_idle_reanalysis: "Nachträgliche Leerlaufkorrektur", method_legacy_import: "Übernommene Altdaten",
    unreliableLabel: "nicht zuverlässig", measuredBaseline: "Gemessene Leerlaufleistung", confirmation: "Entscheidung prüfen",
    usage_unstable_baseline: "Nicht verwendet: Leerlaufmessungen widersprechen sich",
    usage_below_detection: "Nur Messgrenze; genauer gemessene Werte haben Vorrang",
    lowerBoundHint: "Unter der Messgrenze: 0 W ist nur die rechnerische Untergrenze, kein exakt gemessener Nullverbrauch. Dadurch wird die Leerlaufenergie nicht überschätzt.",
    idleChargeRequired: "Für das Laden fehlt eine nutzbare Leerlaufmessung der aktuellen Revision. Eine passende Messung freigeben oder neu messen; widersprüchliche Messungen prüfen.",
    method_idle_reanalysis_unconfirmed: "Leerlaufkorrektur neu berechnet; Ladeende nicht erneut bestätigt",
  },
  en: {
    details: "Details", close: "Close", refresh: "Refresh", loading: "Loading measurement …",
    originRevision: "Original revision", currentRevision: "Current revision", usage: "Use",
    validity: "Validity", result: "Measured value", recorded: "Measured on", actions: "Actions",
    usedCount: "Included", allRecords: "All measurements", usedRecords: "Included measurements",
    excludedRecords: "Not included", historicalRecords: "Other revisions", moreRecords: "Show more",
    revision_native: "Current revision", revision_approved: "Approved for current revision",
    revision_historical: "Other revision", revision_unavailable: "Assignment deleted",
    revision_incompatible_quantity: "Incompatible quantity",
    usage_used: "Used in calculation", usage_invalid: "Not used: invalid",
    usage_historical: "Not used: approval for current revision missing",
    usage_unavailable: "Not used: setup or battery deleted",
    usage_incompatible_quantity: "Not used: quantity does not fit the setup",
    usage_pending_correction: "Not used: idle correction pending",
    usage_invalid_idle_reference: "Not used: underlying idle measurement invalid or missing",
    usage_no_net_energy: "Not used: no usable net energy",
    usage_lower_confidence: "Not used: higher-confidence measurements available",
    usage_unreliable: "Not used: reliable measurements take precedence",
    usage_provisional_baseline: "Provisional value only; no idle correction",
    confidence_high: "high", confidence_medium: "medium", confidence_low: "low", confidence_unknown: "unknown",
    invalidate: "Mark as invalid", restore: "Restore validity",
    approve: "Approve for current revision", revoke: "Revoke revision approval",
    reanalyze: "Recalculate idle correction", decisionReason: "Reason",
    reasonRequired: "A reason is required.", equivalentRequired: "Confirm equivalent measurement conditions first.",
    equivalent: "The physical setup and, for calibrations, battery type, port allocation and initial condition are unchanged or equivalent for measurement. The differences are formal only.",
    approveHint: "The original revision is retained. Approval applies only to the current revision shown below. Validity and measurement quality are still checked separately. Pending idle corrections may then be calculated automatically.",
    revokeHint: "The measurement remains valid and retained in history but is excluded for this current revision. Existing calibration analyses retain their original idle values; revoking reuse does not invalidate the measurement itself.",
    invalidateIdleHint: "This measurement is excluded from the idle baseline. Calibrations corrected with it are also excluded from charge targets until the source is restored or the calibration is explicitly recalculated with valid idle data. Curves and history are retained.",
    invalidateCalibrationHint: "This calibration is excluded from charge-energy calculations. Median, quality and future targets use the remaining usable calibrations. The curve and history are retained.",
    restoreHint: "The measurement becomes valid again. Revision and measurement quality still determine actual use. Previous revision approvals are not automatically renewed. Pending idle corrections may be calculated automatically.",
    reanalyzeHint: "The stored curve is reanalysed with the currently used reliable idle baseline. Net energy, detected endpoint and future charge targets may change. The previous analysis remains in the analysis history.",
    noTrace: "No measurement trace stored. Only the available result data can be shown for this older measurement.",
    trace: "Measurement curve", traceSummary: "The curve shows the stored trace. Long traces are reduced for display, retaining signal extrema.",
    point: "Sample", rawEnergy: "Meter reading", sourceMeasurements: "Underlying idle measurements",
    noSources: "No idle references stored.", missingSource: "Measurement no longer available",
    dependentRecords: "Dependent calibrations", changes: "Changes since measurement",
    noChanges: "No differences in the stored descriptions. Revision numbers may still differ.",
    field: "Field", original: "At measurement", current: "Today", snapshots: "Original measurement conditions",
    decisions: "Approval and validity history", noDecisions: "No subsequent decisions recorded yet.",
    priorAnalyses: "Analysis history", analysisRevision: "Analysis", priorResult: "Previous analysis",
    firstRecorded: "Originally recorded", activeSessionHint: "Changes are available after the active session ends.",
    staleDetail: "Status or revision changed. Refresh details before making a decision.",
    historyHint: "Validity and actual use are separate. Valid records may be excluded due to revision, idle correction or measurement quality. Changes affect future charge calculations.",
    method_manual: "Manually completed", method_energy_plateau: "Energy plateau",
    method_energy_plateau_and_low_power: "Energy plateau and low power",
    method_retrospective_idle_reanalysis: "Retrospective idle correction", method_legacy_import: "Imported legacy data",
    unreliableLabel: "not reliable", measuredBaseline: "Measured idle power", confirmation: "Review decision",
    usage_unstable_baseline: "Not used: idle measurements conflict",
    usage_below_detection: "Detection bound only; measured values take precedence",
    lowerBoundHint: "Below detection: 0 W is a calculation lower bound, not an exact measurement of zero consumption. This avoids overestimating idle energy.",
    idleChargeRequired: "Charging requires a usable idle measurement for the current revision. Approve a matching measurement or measure again; review conflicting measurements.",
    method_idle_reanalysis_unconfirmed: "Idle correction recalculated; endpoint not reconfirmed",
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

const fmtTime = (value, language) => new Intl.DateTimeFormat(language === "de" ? "de-CH" : "en-GB", {
  hour: "2-digit", minute: "2-digit",
}).format(new Date(value));

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
  const grossOnly = mode === "idle" || mode === "gross_calibration";
  const powerKey = grossOnly ? "power_w" : "net_power_w";
  const energyKey = grossOnly ? "gross_energy_wh" : "net_energy_wh";
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
  const energyName = grossOnly
    ? (language === "de" ? "Bruttoenergie" : "Gross energy")
    : (language === "de" ? "Nettoenergie" : "Net energy");
  const powerName = language === "de" ? (grossOnly ? "Leistung" : "Nettoleistung") : (grossOnly ? "Power" : "Net power");
  return `<div class="bcm-session-chart ${compact ? "compact" : ""}">
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${language === "de" ? "Messkurve" : "Measurement trace"}">
      <line class="bcm-chart-axis" x1="${left}" y1="${height - bottom}" x2="${width - right}" y2="${height - bottom}" />
      ${[0,0.5,1].map((fraction) => `<text x="${x(firstTime + span * fraction)}" y="${height - 6}" text-anchor="${fraction === 0 ? "start" : fraction === 1 ? "end" : "middle"}" class="bcm-chart-tick">${fmtTime(new Date(firstTime + span * fraction).toISOString(),language)}</text>`).join("")}
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
  .bcm-header { display:flex; justify-content:space-between; align-items:center; gap:12px; min-height:64px; padding:8px 16px; border-bottom:1px solid var(--divider-color); background:var(--primary-background-color); }
  .bcm-heading { display:flex; align-items:center; gap:8px; min-width:0; }
  .bcm-heading ha-icon-button { flex:none; }
  .bcm-title { margin:0; font-size:24px; font-weight:700; overflow-wrap:anywhere; }
  .bcm-version { color:var(--secondary-text-color); font-size:12px; }
  .bcm-breadcrumbs { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:16px; }
  .bcm-nav-link { color:var(--primary-color); border:0; background:transparent; padding:8px 0; text-align:start; }
  .bcm-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr)); gap:14px; }
  .bcm-grid > * { min-width:0; }
  .bcm-management-link { display:block; width:100%; text-align:start; color:inherit; border:1px solid var(--divider-color); }
  .bcm-management-link strong { display:block; font-size:18px; margin-bottom:8px; }
  .bcm-management-link span { display:block; line-height:1.5; }
  .bcm-active-link { display:flex; width:100%; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; text-align:start; border:1px solid var(--primary-color); color:inherit; margin-bottom:16px; }
  .bcm-home-status { margin-bottom:14px; }
  .bcm-home-status p { margin:6px 0 0; overflow-wrap:anywhere; }
  .bcm-calibration-home { margin-top:18px; }
  .bcm-calibration-home > summary { font-size:18px; font-weight:600; cursor:pointer; padding:4px 0; }
  .bcm-calibration-home > summary span { display:block; font-size:13px; font-weight:400; color:var(--secondary-text-color); margin:6px 0 0; }
  .bcm-calibration-home[open] > summary { margin-bottom:14px; }
  .bcm-charge-options { border-top:1px solid var(--divider-color); margin-top:14px; padding-top:12px; }
  .bcm-charge-options > summary { cursor:pointer; line-height:1.6; overflow-wrap:anywhere; }
  .bcm-charge-options > summary .bcm-change { color:var(--primary-color); font-weight:600; margin-inline-start:8px; }
  .bcm-start-charge { min-width:180px; min-height:48px; }
  button:focus-visible,summary:focus-visible { outline:2px solid var(--primary-color); outline-offset:3px; }
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
  .bcm-segment button { border:1px solid var(--divider-color); background:var(--card-background-color); color:var(--primary-text-color); border-radius:9px; min-width:48px; min-height:44px; padding:8px 10px; }
  .bcm-segment button:disabled { opacity:.45; cursor:not-allowed; }
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
  .bcm-chart-tick { fill:var(--secondary-text-color); font-size:11px; }
  .bcm-history-toolbar { display:flex; flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:center; margin:14px 0; }
  .bcm-history-toolbar select { padding:8px; border:1px solid var(--divider-color); border-radius:8px; background:var(--card-background-color); color:var(--primary-text-color); max-width:100%; }
  .bcm-history-table td { white-space:normal; vertical-align:top; line-height:1.5; }
  .bcm-history-table .bcm-muted { margin-top:4px; font-size:12px; }
  .bcm-history-table .bcm-use-cell { min-width:150px; max-width:260px; }
  .bcm-history-table .bcm-actions { margin:0; gap:6px; }
  .bcm-history-table .bcm-btn { padding:8px 10px; font-size:12px; text-align:left; }
  .bcm-detail-header { position:sticky; top:-18px; display:flex; gap:12px; justify-content:space-between; align-items:center; padding:12px 0; background:var(--card-background-color); z-index:1; }
  .bcm-detail-header h2 { margin:0; font-size:20px; }
  .bcm-detail-status { display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
  .bcm-dialog section { margin:18px 0; }
  .bcm-dialog h3 { margin:14px 0 8px; }
  .bcm-dialog .bcm-row { flex-wrap:wrap; }
  .bcm-decision { padding:14px; border:2px solid var(--primary-color); border-radius:12px; }
  .bcm-equivalence { display:flex; align-items:flex-start; gap:10px; margin-top:16px; line-height:1.5; }
  .bcm-equivalence input { flex:none; margin-top:5px; width:18px; height:18px; }
  .bcm-detail-table th,.bcm-detail-table td { white-space:normal; overflow-wrap:anywhere; vertical-align:top; }
  .bcm-detail-table { table-layout:fixed; }
  .bcm-dialog details { border-top:1px solid var(--divider-color); padding:12px 0; }
  .bcm-dialog summary { cursor:pointer; font-weight:600; }
  .bcm-dialog details .bcm-note { margin-top:10px; }
  .bcm-source-row { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin:8px 0; }
  .bcm-sample-label { display:flex; align-items:center; gap:12px; margin:12px 0; }
  .bcm-sample-label input { flex:1; min-width:0; }
  .bcm-sample-values { display:flex; flex-wrap:wrap; gap:8px 16px; margin-top:8px; font-size:13px; }
  .bcm-record-id { font-size:11px; overflow-wrap:anywhere; }
  @media(max-width:700px) {
    .bcm-history-table thead { display:none; }
    .bcm-history-table tbody { display:grid; gap:12px; }
    .bcm-history-table tr { display:grid; grid-template-columns:1fr 1fr; border:1px solid var(--divider-color); border-radius:12px; overflow:hidden; }
    .bcm-history-table td { min-width:0; border:0; padding:10px; }
    .bcm-history-table td::before { content:attr(data-label); display:block; color:var(--secondary-text-color); font-size:11px; font-weight:600; margin-bottom:5px; }
    .bcm-history-table .bcm-use-cell,.bcm-history-table .bcm-record-actions { grid-column:1 / -1; max-width:none; }
    .bcm-history-table .bcm-btn { min-height:40px; }
    .bcm-dialog { padding:14px; }
    .bcm-overlay { padding:8px; }
    .bcm-detail-header { top:-14px; }
    .bcm-dialog .bcm-form-grid { grid-template-columns:1fr; gap:8px; }
  }
  .bcm-image-preview { width:100%; max-height:220px; object-fit:contain; border-radius:10px; background:var(--secondary-background-color); margin-bottom:8px; }
  .bcm-file-btn { display:inline-flex; align-items:center; }
  .bcm-file-btn input { display:none; }
  @media (max-width:600px) { .bcm-shell { padding:12px; } .bcm-title { font-size:18px; } .bcm-header { gap:8px; } .bcm-header > .bcm-btn { padding:10px; font-size:13px; } .bcm-card { padding:13px; } .bcm-start-charge { width:100%; } .bcm-form-grid { grid-template-columns:1fr; } }
`;

class BcmBase extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._state = null;
    this._unsub = null;
    this._subscribing = false;
    this._connectionGeneration = 0;
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
    this._connectionGeneration += 1;
    this._subscribing = false;
    if (this._unsub) {
      this._unsub();
      this._unsub = null;
    }
  }

  get language() {
    const code = String(this._hass?.language || "en").toLowerCase();
    return code.startsWith("de") ? "de" : "en";
  }

  t(key) { return HISTORY_TEXT[this.language]?.[key] || TEXT[this.language][key] || HISTORY_TEXT.en[key] || TEXT.en[key] || key; }

  async _connect() {
    if (!this._hass || this._subscribing || this._unsub || this.isConnected === false) return;
    const generation = this._connectionGeneration;
    const current = () => generation === this._connectionGeneration && this.isConnected !== false;
    this._subscribing = true;
    try {
      const state = await this._hass.callWS({ type: `${BCM_DOMAIN}/get_state` });
      if (!current()) return;
      this._state = state;
      this._error = "";
      this._requestRender();
      const unsubscribe = await this._hass.connection.subscribeMessage(
        (event) => {
          if (!current()) return;
          this._state = event;
          this._requestRender();
        },
        { type: `${BCM_DOMAIN}/subscribe` },
      );
      if (!current()) unsubscribe();
      else this._unsub = unsubscribe;
    } catch (err) {
      if (!current()) return;
      this._error = err?.message || String(err);
      this._requestRender();
    } finally {
      if (generation === this._connectionGeneration) this._subscribing = false;
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
    this._chargeOptionsOpen = false;
    this._calibrationOpen = false;
    this._preferencesUser = null;
    this._dialogScrollTop = 0;
    this._historyFilters = {};
    this._historyLimits = {};
    this._detailsRequest = 0;
    this._openDisclosures = [];
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
    this.loadHomePreferences();
    const previousDialog = this.shadowRoot.querySelector(".bcm-dialog");
    const dialogScrollTop = previousDialog?.scrollTop ?? this._dialogScrollTop ?? 0;
    this.shadowRoot.innerHTML = `
      <style>${BASE_STYLE}</style>
      <header class="bcm-header">
          <div class="bcm-heading"><ha-icon-button data-ha-menu></ha-icon-button><div><h1 class="bcm-title">${this.t("title")}</h1><div class="bcm-version">${esc(s?.version || "")}</div></div></div>
          ${this.navButton(this._tab === "charge" ? "manage" : "charge", this.t(this._tab === "charge" ? "manage" : "home"))}
      </header>
      <div class="bcm-shell">
        ${this._error ? `<div class="bcm-error"><strong>${this.t("error")}:</strong> ${esc(this._error)}</div>` : ""}
        ${this.renderBreadcrumbs()}
        ${s && this._tab !== "charge" ? this.renderActiveLink() : ""}
        <main tabindex="-1">${!s ? `<div class="bcm-card">${this.t("loading")}</div>` : this.renderTab(admin)}</main>
      </div>
      ${this.renderDialog(admin)}
    `;
    const dialog = this.shadowRoot.querySelector(".bcm-dialog");
    if (dialog) {
      dialog.scrollTop = dialogScrollTop;
      this._dialogScrollTop = dialogScrollTop;
      dialog.addEventListener("scroll", () => { this._dialogScrollTop = dialog.scrollTop; });
    }
    this.shadowRoot.querySelectorAll("[data-disclosure]").forEach((el) => {
      el.open = this._openDisclosures.includes(el.dataset.disclosure);
      el.addEventListener("toggle", () => {
        this._openDisclosures = [...this.shadowRoot.querySelectorAll("[data-disclosure]")].filter((item) => item.open).map((item) => item.dataset.disclosure);
      });
    });
    this.bindEvents();
  }

  navButton(id, label) {
    return `<button class="bcm-btn secondary" data-tab="${id}">${label}</button>`;
  }

  navigate(tab) {
    this._tab = ["charge","manage","batteries","setups","idle","calibrations","settings"].includes(tab) ? tab : "charge";
    this.render();
    this.shadowRoot.querySelector("main")?.focus({preventScroll:true});
    this.shadowRoot.querySelector(".bcm-header")?.scrollIntoView({block:"start"});
  }

  renderBreadcrumbs() {
    if (this._tab === "charge") return "";
    return `<nav class="bcm-breadcrumbs" aria-label="${this.t("manage")}">${this._tab === "manage" ? `<span aria-current="page">${this.t("manage")}</span>` : `<button class="bcm-nav-link" data-tab="manage">${this.t("manage")}</button><span aria-hidden="true">›</span><span aria-current="page">${this.t(this._tab)}</span>`}</nav>`;
  }

  loadHomePreferences() {
    const user = this._hass?.user?.id || "default";
    if (this._preferencesUser === user) return;
    this._preferencesUser = user;
    this._chargeOptionsOpen = false;
    this._calibrationOpen = false;
    try {
      this._calibrationOpen = globalThis.localStorage?.getItem(`${BCM_DOMAIN}:home:calibration:${user}`) === "true";
    } catch (_err) { /* Browser storage may be unavailable. Keep in-memory preferences. */ }
  }

  setHomeDisclosure(name, open) {
    this.loadHomePreferences();
    if (name === "charge-options") { this._chargeOptionsOpen = open; return; }
    if (name !== "calibration" || this._calibrationOpen === open) return;
    this._calibrationOpen = open;
    try {
      globalThis.localStorage?.setItem(`${BCM_DOMAIN}:home:calibration:${this._preferencesUser}`, String(open));
    } catch (_err) { /* The current view still remembers the choice. */ }
  }

  sessionActive() { return Boolean(this._state?.session?.mode && this._state.session.mode !== "idle"); }

  sessionTitle() {
    return this.t({ charging:"liveCharge", calibrating:"liveCalibration", idle_measuring:"liveMeasurement" }[this._state.session.mode] || "active");
  }

  renderActiveLink() {
    if (!this.sessionActive()) return "";
    const session = this._state.session;
    return `<button class="bcm-note bcm-active-link" data-tab="charge" data-active-link><span><strong>${this.sessionTitle()}</strong> · ${esc(phaseLabel(session.phase,this.language))} · ${fmtDuration(session.elapsed_seconds)}</span><span>${this.t("viewActive")} →</span></button>`;
  }

  renderHome(admin) {
    this.loadHomePreferences();
    const session = this._state.session;
    let operation;
    if (session.mode === "charging") operation = this.renderChargeSession();
    else if (session.mode === "calibrating") operation = `<section class="bcm-card">${this.renderCalibrationSession(admin)}</section>`;
    else if (session.mode === "idle_measuring") operation = `<section class="bcm-card"><h2>${this.t("idle")}</h2>${this.renderIdleSession()}</section>`;
    else operation = `<div class="bcm-note bcm-home-status"><strong>${this.t("noActive")}</strong>${session.session_finished_at ? `<p>${this.t("lastOperation")}: ${esc(phaseLabel(session.phase,this.language))} · ${fmtDate(session.session_finished_at,this.language)}${session.end_reason ? `<br>${esc(session.end_reason)}` : ""}</p>` : ""}</div>${this.renderCharge()}`;
    return `${operation}<details class="bcm-calibration-home bcm-card" data-home-disclosure="calibration"${this._calibrationOpen ? " open" : ""}><summary>${this.t("calibrate")}<span>${this.t("calibrationHomeHint")}</span></summary>${this.sessionActive() ? `<p class="bcm-note">${this.t("activeFirst")}</p>` : this.renderCalibrationStart(admin, false)}<div class="bcm-actions">${this.navButton("calibrations",this.t("calibrationHistory"))}</div></details>`;
  }

  renderManagement() {
    return `<p class="bcm-muted">${this.t("manageIntro")}</p><div class="bcm-grid">${["batteries","setups","idle","calibrations","settings"].map(id => `<button class="bcm-card bcm-management-link" data-tab="${id}"><strong>${this.t(id)}</strong><span class="bcm-muted">${this.t(`${id}Help`)}</span></button>`).join("")}</div>`;
  }

  renderTab(admin) {
    if (this._tab === "manage") return this.renderManagement();
    if (this._tab === "batteries") return this.renderBatteries(admin);
    if (this._tab === "setups") return this.renderSetups(admin);
    if (this._tab === "idle") return this.renderIdle(admin);
    if (this._tab === "calibrations") return this.renderCalibrations(admin);
    if (this._tab === "settings") return this.renderSettings(admin);
    return this.renderHome(admin);
  }

  selectors({ includeTarget = true } = {}) {
    return `<div class="bcm-form-grid">${this.selectSetupOnly()}${this.batterySelector()}</div>${this.quantitySelector()}${includeTarget ? this.targetSelector() : ""}`;
  }

  batterySelector() {
    const s = this._state;
    return `<div class="bcm-field"><label for="bcm-battery">${this.t("battery")}</label><select id="bcm-battery" data-select="battery" ${this.sessionActive() || this._busy ? "disabled" : ""}>${s.batteries.map(item => `<option value="${esc(item.battery_id)}" ${item.battery_id === s.selected_battery_id ? "selected" : ""}>${esc(item.name)}</option>`).join("")}</select></div>`;
  }

  quantitySelector() {
    const s = this._state;
    const setup = s.setups.find(item => item.setup_id === s.selected_setup_id);
    const maxQuantity = setup?.port_labels?.length || 1;
    return `<div class="bcm-row stack"><strong id="bcm-quantity-label">${this.t("quantity")}</strong><div class="bcm-segment" role="group" aria-labelledby="bcm-quantity-label">${Array.from({length:maxQuantity}, (_, i) => i + 1).map(n => `<button data-quantity="${n}" class="${n === s.selected_quantity ? "active" : ""}" aria-pressed="${n === s.selected_quantity}" ${this.sessionActive() || this._busy ? "disabled" : ""}>${n}</button>`).join("")}</div></div><div class="bcm-port-note">${this.t("connectTo")}: ${esc(portInstruction(s,this.language))}</div>`;
  }

  targetSelector() {
    const s = this._state;
    return `<div class="bcm-field"><label for="bcm-target">${this.t("target")}: <strong data-target-value>${s.target_percent}%</strong></label><input id="bcm-target" type="range" min="20" max="100" step="1" value="${s.target_percent}" data-target ${this.sessionActive() || this._busy ? "disabled" : ""}></div>`;
  }

  renderChargeSession() {
    const s = this._state;
    const session = s.session;
    const summary = s.active_calibration_summary || {};
    const progress = Math.max(0, Math.min(100, Number(session.progress_percent || 0)));
    const setup = s.setups.find((item) => item.setup_id === (session.setup_id || s.selected_setup_id));
    const battery = s.batteries.find((item) => item.battery_id === (session.battery_id || s.selected_battery_id));
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
        <div class="bcm-row"><span>${this.t("quantity")}</span><strong>${session.quantity ?? s.selected_quantity}</strong></div>
        <div class="bcm-row"><span>${this.t("target")}</span><strong>${session.target_percent ?? s.target_percent}%</strong></div>
        <div class="bcm-row"><span>${this.t("calibrationValue")}</span><strong>${fmt(summary.median_net_energy_wh)} Wh</strong></div>
        <p><span class="bcm-badge ${qualityClass(summary.quality)}">${esc(summary.quality || "none")}</span></p>
      </section>
    </div>`;
  }

  renderCharge() {
    const s = this._state;
    if (s.session.mode === "charging") return this.renderChargeSession();
    const summary = s.active_calibration_summary || {};
    const setup = s.setups.find(item => item.setup_id === s.selected_setup_id);
    const battery = s.batteries.find(item => item.battery_id === s.selected_battery_id);
    const hasSelection = Boolean(setup && battery);
    const canStart = hasSelection && summary.median_net_energy_wh != null && s.active_idle_summary?.usable !== false && !this.sessionActive();
    return `<div class="bcm-grid">
      <section class="bcm-card">
        <h2>${this.t("charge")}</h2>
        ${hasSelection ? `${this.quantitySelector()}${this.batterySelector()}
          <details class="bcm-charge-options" data-home-disclosure="charge-options"${this._chargeOptionsOpen ? " open" : ""}>
            <summary><span class="bcm-muted">${this.t("chargeOptions")}</span><br>${esc(setup.name)} · ${this.t("target")}: ${s.target_percent}% <span class="bcm-change">${this.t("change")}</span></summary>
            ${this.selectSetupOnly()}${this.targetSelector()}<div class="bcm-note">${this.t("relativeNote")}</div>
          </details>` : `<div class="bcm-note">${this.t("selectRequired")}</div><div class="bcm-actions">${this.navButton(!setup ? "setups" : "batteries",this.t(!setup ? "setupFirst" : "batteryFirst"))}</div>`}
        <div class="bcm-actions"><button class="bcm-btn bcm-start-charge" data-action="start-charge" ${!canStart || this._busy ? "disabled" : ""}>${this.t("start")}</button></div>
      </section>
      <section class="bcm-card">
        <h2>${this.t("readiness")}</h2>
        ${canStart ? `<p><span class="bcm-badge good">${this.t("readyToCharge")}</span></p>` : ""}
        ${summary.median_net_energy_wh == null ? `<p class="bcm-note">${this.t("noCalibration")}</p><div class="bcm-actions">${this.navButton("calibrations",this.t("calibrationHistory"))}</div>` : `<div class="bcm-row"><span>${this.t("calibrationValue")}</span><strong>${fmt(summary.median_net_energy_wh)} Wh</strong></div><p><span class="bcm-badge ${qualityClass(summary.quality)}">${esc(summary.quality || "none")}</span></p>`}
        ${s.active_idle_summary?.usable === false ? `<p class="bcm-note">${this.t("idleChargeRequired")}</p><div class="bcm-actions">${this.navButton("idle",this.t("idle"))}</div>` : ""}
      </section>
    </div>`;
  }

  metric(label, value) { return `<div class="bcm-metric"><span class="bcm-muted">${label}</span><strong>${value}</strong></div>`; }

  renderBatteries(admin) {
    const s = this._state;
    return `<section class="bcm-card"><div class="bcm-list-head"><h2>${this.t("batteries")}</h2>${admin ? `<button class="bcm-btn" data-action="new-battery">${this.t("addBattery")}</button>` : `<span class="bcm-admin">${this.t("adminOnly")}</span>`}</div><p class="bcm-muted">${this.t("currentRevisionOnly")}</p><div class="bcm-list">${s.batteries.length ? s.batteries.map((battery) => this.batteryItem(battery, admin)).join("") : `<div class="bcm-note">${this.t("noBatteries")}</div>`}</div></section>`;
  }

  batteryItem(battery, admin) {
    const img = imageUrl(battery.image);
    const nominalSpecs = [
      battery.nominal_capacity_mah !== null && battery.nominal_capacity_mah !== undefined ? `${battery.nominal_capacity_mah} mAh` : "",
      battery.nominal_energy_wh !== null && battery.nominal_energy_wh !== undefined ? `${fmt(Number(battery.nominal_energy_wh) * 1000,0)} mWh` : "",
    ].filter(Boolean).join(" · ") || "–";
    return `<div class="bcm-list-item"><div class="bcm-list-head"><div style="display:flex;gap:12px;align-items:center">${img ? `<img class="bcm-thumb" src="${esc(img)}">` : ""}<div><strong>${esc(battery.name)}</strong><div class="bcm-muted">${esc([battery.manufacturer,battery.model].filter(Boolean).join(" "))}</div><div class="bcm-muted">${esc(battery.technology)} · ${esc(battery.form_factor)} · ${esc(nominalSpecs)}</div></div></div><span class="bcm-badge">${this.t("revision")} ${battery.revision}</span></div>${admin ? `<div class="bcm-actions"><button class="bcm-btn secondary" data-edit-battery="${esc(battery.battery_id)}">${this.t("edit")}</button><button class="bcm-btn danger" data-delete-battery="${esc(battery.battery_id)}">${this.t("delete")}</button></div>` : ""}</div>`;
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

  renderIdleSession() {
    const s = this._state;
    const session = s.session;
    const setup = s.setups.find(item => item.setup_id === (session.setup_id || s.selected_setup_id));
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
    return `
      <h3>${this.t("liveMeasurement")}</h3><div class="bcm-row"><span>${this.t("setup")}</span><strong>${esc(setup?.name || "–")}</strong></div>
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
      <div class="bcm-actions"><button class="bcm-btn danger" data-action="stop" ${this._busy ? "disabled" : ""}>${this.t("stop")}</button></div>`;
  }

  renderIdle(admin) {
    const s = this._state;
    const summary = s.active_idle_summary || {};
    const active = s.session.mode === "idle_measuring";
    const rows = s.idle_measurements.filter((item) => item.setup_id === s.selected_setup_id);
    const baselineDisplay = summary.below_detection_count ? `&lt; ${fmt(summary.upper_bound_power_w,3)} W` : `${fmt(summary.baseline_power_w,3)} W`;
    let leftContent;
    if (active) {
      leftContent = this.renderIdleSession();
    } else {
      leftContent = `${this.selectSetupOnly()}<div class="bcm-note">${this.t("noBatteryIdle")}</div><div class="bcm-note" style="margin-top:8px">${this.t("automaticExplanation")}</div>${admin ? `<div class="bcm-form-grid"><div class="bcm-field"><label>${this.t("minMinutes")}</label><input id="idle-min" data-form-value="idleMin" type="number" min="10" max="1440" value="${esc(this._formValues.idleMin)}"></div><div class="bcm-field"><label>${this.t("maxMinutes")}</label><input id="idle-max" data-form-value="idleMax" type="number" min="30" max="1440" value="${esc(this._formValues.idleMax)}"></div><div class="bcm-field"><label>${this.t("durationMinutes")}</label><input id="idle-fixed" data-form-value="idleFixed" type="number" min="5" max="1440" value="${esc(this._formValues.idleFixed)}"></div></div><div class="bcm-actions"><button class="bcm-btn" data-action="idle-auto" ${s.session.mode !== "idle" || this._busy ? "disabled" : ""}>${this.t("automaticIdle")}</button><button class="bcm-btn secondary" data-action="idle-fixed" ${s.session.mode !== "idle" || this._busy ? "disabled" : ""}>${this.t("fixedIdle")}</button></div>` : `<p class="bcm-admin">${this.t("adminOnly")}</p>`}`;
    }
    return `<div class="bcm-grid"><section class="bcm-card"><h2>${this.t("idle")}</h2>${leftContent}</section><section class="bcm-card"><h2>${this.t("baseline")}</h2><div class="bcm-metrics">${this.metric(this.t("baseline"), baselineDisplay)}${this.metric(this.t("usedCount"), String(summary.usable === false ? 0 : summary.used_count || 0))}${this.metric(this.t("reliable"), String(summary.reliable_count || 0))}${this.metric(this.t("spread"), `${fmt(summary.spread_percent,1)}%`)}</div><p><span class="bcm-badge ${qualityClass(summary.quality)}">${esc(summary.quality || "none")}</span></p></section></div><section class="bcm-card" style="margin-top:14px"><h2>${this.t("history")}</h2>${summary.baseline_is_lower_bound ? `<p class="bcm-note">${this.t("lowerBoundHint")}</p>` : ""}${this.idleTable(rows, admin)}</section>`;
  }

  selectSetupOnly() {
    const s = this._state;
    return `<div class="bcm-field"><label for="bcm-setup">${this.t("setup")}</label><select id="bcm-setup" data-select="setup" ${this.sessionActive() || this._busy ? "disabled" : ""}>${s.setups.map(item => `<option value="${esc(item.setup_id)}" ${item.setup_id === s.selected_setup_id ? "selected" : ""}>${esc(item.name)}</option>`).join("")}</select></div>`;
  }

  idleTable(rows, admin) { return this.historyTable(rows, admin, "idle"); }

  renderCalibrationSession(admin) {
    const s = this._state;
    const session = s.session;
    const setup = s.setups.find(item => item.setup_id === (session.setup_id || s.selected_setup_id));
    const battery = s.batteries.find((item) => item.battery_id === (session.battery_id || s.selected_battery_id));
    const ports = (session.ports?.length ? session.ports : selectedPorts(s)).join(" + ") || "–";
    const correction = session.idle_baseline_power_w === null || session.idle_baseline_power_w === undefined ? this.t("pendingCorrection") : this.t("valid");
    return `
      <h2>${this.t("liveCalibration")}</h2><div class="bcm-row"><span>${this.t("setup")}</span><strong>${esc(setup?.name || "–")}</strong></div>
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
      ${admin ? `<div class="bcm-actions"><button class="bcm-btn secondary" data-action="finish-calibration" ${this._busy ? "disabled" : ""}>${this.t("finishCalibration")}</button><button class="bcm-btn danger" data-action="stop" ${this._busy ? "disabled" : ""}>${this.t("stop")}</button></div><p class="bcm-muted">${this.t("manualFallback")}</p>` : ""}`;
  }

  renderCalibrationStart(admin, includeSelectors = true) {
    const s = this._state;
    const idle = s.active_idle_summary || {};
    const hasSelection = s.setups.some(item => item.setup_id === s.selected_setup_id) && s.batteries.some(item => item.battery_id === s.selected_battery_id);
    return `${includeSelectors ? this.selectors({includeTarget:false}) : `<p class="bcm-muted">${this.t("calibrationSelection")}</p>`}
      <div class="bcm-note">${this.t("calibrationHint")}</div>
      ${hasSelection ? "" : `<p class="bcm-note">${this.t("selectRequired")}</p>`}
      ${(idle.usable ?? Boolean(idle.reliable_count)) ? "" : `<p class="bcm-note">${this.t("idleRequired")}</p>`}
      ${admin ? `<div class="bcm-actions"><button class="bcm-btn" data-action="start-calibration" ${!hasSelection || this.sessionActive() || this._busy ? "disabled" : ""}>${this.t("startCalibration")}</button></div>` : `<p class="bcm-admin">${this.t("adminOnly")}</p>`}`;
  }

  renderCalibrations(admin) {
    const s = this._state;
    const summary = s.active_calibration_summary || {};
    const active = s.session.mode === "calibrating";
    const rows = s.calibrations.filter((item) => item.setup_id === s.selected_setup_id && item.battery_id === s.selected_battery_id && item.quantity === s.selected_quantity);
    const leftContent = active ? this.renderCalibrationSession(admin) : this.renderCalibrationStart(admin);
    return `<div class="bcm-grid"><section class="bcm-card"><h2>${this.t("calibrations")}</h2>${leftContent}</section><section class="bcm-card"><h2>${this.t("quality")}</h2><div class="bcm-metrics">${this.metric(this.t("calibrationValue"), `${fmt(summary.median_net_energy_wh)} Wh`)}${this.metric(this.t("calibrationDuration"), fmtDuration(summary.median_charge_duration_seconds))}${this.metric(this.t("measurements"), String(summary.count || 0))}${this.metric(this.t("pendingCorrection"), String(summary.pending_count || 0))}${this.metric(this.t("spread"), `${fmt(summary.spread_percent,1)}%`)}${this.metric(this.t("stdev"), `${fmt(summary.stdev_net_energy_wh,3)} Wh`)}${this.metric(this.t("drift"), `${fmt(summary.drift_percent,1)}%`)}${this.metric(this.t("trend"), esc(summary.trend || "not_assessable"))}</div><p><span class="bcm-badge ${qualityClass(summary.quality)}">${esc(summary.quality || "none")}</span></p>${this.linearModel()}</section></div><section class="bcm-card" style="margin-top:14px"><h2>${this.t("history")}</h2>${this.calibrationTable(rows, admin)}</section>`;
  }

  linearModel() {
    const model = this._state.linear_model || {};
    if (!model.available) return `<p class="bcm-muted">${this.t("linearModel")}: ${this.t("notAvailable")}</p>`;
    return `<div class="bcm-note"><strong>${this.t("linearModel")}</strong><br>E(n) = ${fmt(model.intercept_wh,3)} Wh + ${fmt(model.per_battery_wh,3)} Wh × n<br>R² = ${fmt(model.r_squared,3)}<br><span class="bcm-muted">Plausibilisierung; nicht als primärer Abschaltwert verwendet.</span></div>`;
  }

  calibrationTable(rows, admin) { return this.historyTable(rows, admin, "calibration"); }

  historyTable(rows, admin, kind) {
    const filter = this._historyFilters?.[kind] || "all";
    const limit = this._historyLimits?.[kind] || 25;
    const filtered = rows.filter((item) => filter === "all" || (filter === "used" ? item.used : filter === "excluded" ? !item.used : item.revision_status !== "native"));
    const setup = this._state.setups.find((item) => item.setup_id === this._state.selected_setup_id);
    const battery = this._state.batteries.find((item) => item.battery_id === this._state.selected_battery_id);
    const cell = (label, value, extra = "") => `<td data-label="${this.t(label)}" class="${extra}">${value}</td>`;
    const revision = (item) => `${this.t("setup")}: ${this.t("revision")} ${item.setup_revision}${kind === "calibration" ? `<br>${this.t("battery")}: ${this.t("revision")} ${item.battery_revision}` : ""}`;
    return `<p class="bcm-muted">${this.t("currentRevision")}: ${esc(setup?.name || this.t("setup"))} · ${this.t("revision")} ${setup?.revision ?? "–"}${kind === "calibration" ? ` / ${esc(battery?.name || this.t("battery"))} · ${this.t("revision")} ${battery?.revision ?? "–"}` : ""}</p>
      <div class="bcm-note">${this.t("historyHint")}</div>
      <div class="bcm-history-toolbar"><label>${this.t("history")} <select data-history-filter="${kind}">${[["all","allRecords"],["used","usedRecords"],["excluded","excludedRecords"],["historical","historicalRecords"]].map(([value,label]) => `<option value="${value}" ${value === filter ? "selected" : ""}>${this.t(label)}</option>`).join("")}</select></label><span>${this.t("usedCount")}: <strong>${rows.filter((item) => item.used).length}</strong> / ${rows.length}</span></div>
      <div class="bcm-table-wrap"><table class="bcm-history-table"><thead><tr>${["validity","originRevision","usage","result","recorded","actions"].map((key) => `<th>${this.t(key)}</th>`).join("")}</tr></thead><tbody>${filtered.slice(0,limit).map((item) => `<tr>
        ${cell("validity", `${this.validityBadge(item)}<div class="bcm-muted">${this.t("confidence")}: ${this.t(`confidence_${item.confidence || "unknown"}`)}</div>${kind === "idle" ? `<div class="bcm-muted">${this.t(item.reliable ? "reliable" : "unreliableLabel")}</div>` : ""}`)}
        ${cell("originRevision", `${revision(item)}<div class="bcm-muted">${this.t(`revision_${item.revision_status || "native"}`)}</div>`)}
        ${cell("usage", this.usageBadge(item), "bcm-use-cell")}
        ${cell("result", kind === "idle" ? `${item.below_detection_limit ? `&lt; ${fmt(item.upper_bound_power_w,3)}` : fmt(item.median_power_w ?? item.average_power_w,3)} W<br><span class="bcm-muted">${this.t(item.mode === "automatic" ? "auto" : "fixed")}</span>` : `${item.idle_correction_status === "pending" ? `${fmt(item.gross_energy_wh)} Wh<br><span class="bcm-muted">${this.t("gross")}</span>` : `${fmt(item.net_energy_wh)} Wh<br><span class="bcm-muted">${this.t("net")}</span>`}`)}
        ${cell("recorded", `${fmtDate(item.started_at || item.session_started_at || item.finished_at,this.language)}<br><span class="bcm-muted">${fmtDuration(item.duration_seconds ?? item.charge_duration_seconds)}</span>`)}
        ${cell("actions", this.recordActions(item,kind,admin), "bcm-record-actions")}
      </tr>`).join("")}</tbody></table></div>
      ${!filtered.length ? `<p class="bcm-muted">${this.t("measurements")}: 0</p>` : ""}
      ${filtered.length > limit ? `<button class="bcm-btn secondary" data-history-more="${kind}">${this.t("moreRecords")} (${filtered.length - limit})</button>` : ""}`;
  }

  validityBadge(item) {
    return `<span class="bcm-badge ${item.valid ? "good" : "bad"}">${this.t(item.valid ? "valid" : "invalid")}</span>`;
  }

  usageBadge(item) {
    const reason = item.usage_reason || (item.used ? "used" : "historical");
    return `<span class="bcm-badge ${reason === "used" ? "good" : reason === "invalid" ? "bad" : "warn"}">${this.t(`usage_${reason}`)}</span>`;
  }

  recordActions(item, kind, admin, inDialog = false) {
    const id = item.measurement_id || item.calibration_id;
    const disabled = this._busy || this._state.session.mode !== "idle";
    const button = (action, label, style = "secondary") => `<button class="bcm-btn ${style}" data-record-action="${action}" data-record-kind="${kind}" data-record-id="${esc(id)}" ${action !== "details" && disabled ? "disabled" : ""}>${this.t(label)}</button>`;
    return `<div class="bcm-actions">${inDialog ? "" : button("details","details")}${admin ? `${button(item.valid ? "invalidate" : "restore",item.valid ? "invalidate" : "restore")}${item.can_approve ? button("approve","approve") : ""}${item.revision_status === "approved" ? button("revoke","revoke") : ""}${inDialog && item.can_reanalyze ? button("reanalyze","reanalyze") : ""}` : ""}</div>`;
  }

  async openMeasurement(kind, recordId, decision = null) {
    const request = this._detailsRequest = (this._detailsRequest || 0) + 1;
    this._dialog = "measurement";
    this._measurementDetail = null;
    this._recordDecision = decision === "details" ? null : decision;
    this._decisionReason = "";
    this._decisionConfirmed = false;
    this._sampleIndex = 0;
    this._dialogScrollTop = 0;
    this._openDisclosures = [];
    this._error = "";
    this.render();
    try {
      const result = await this._hass.callWS({ type: `${BCM_DOMAIN}/get_measurement`, record_type: kind, record_id: recordId });
      if (request !== this._detailsRequest || this._dialog !== "measurement") return;
      this._measurementDetail = result;
    } catch (err) {
      if (request !== this._detailsRequest) return;
      this._error = err?.message || String(err);
    }
    this._requestRender();
  }

  measurementFieldLabel(key) {
    const labels = { switch_entity:"switchEntity", energy_sensor:"energySensor", power_sensor:"powerSensor", temperature_sensor:"temperatureSensor", charger_model:"chargerModel", cable_description:"cable", port_labels:"portsUsed", max_power_w:"maxPower", max_temperature_c:"maxTemperature", nominal_capacity_mah:"capacity", nominal_voltage_v:"voltage", nominal_energy_wh:"energy", form_factor:"formFactor", charging_method:"chargingMethod", discharge_method:"dischargeMethod", rest_time_minutes:"restTime", starting_condition_notes:"startingNotes" };
    return this.t(labels[key] || key);
  }

  measurementFieldValue(key, value) {
    if (value === null || value === undefined || value === "") return "–";
    if (key === "nominal_energy_wh") return esc(Number(value) * 1000);
    return esc(Array.isArray(value) ? value.join(" / ") : typeof value === "object" ? JSON.stringify(value) : value);
  }

  revisionComparison(d) {
    const pair = (original) => `${this.t("setup")}: ${this.t("revision")} ${original ? d.setup_revision : d.current_setup_revision ?? "–"}${d.record_type === "calibration" ? `<br>${this.t("battery")}: ${this.t("revision")} ${original ? d.battery_revision : d.current_battery_revision ?? "–"}` : ""}`;
    return `<div class="bcm-form-grid"><div class="bcm-note"><strong>${this.t("originRevision")}</strong><p>${pair(true)}</p></div><div class="bcm-note"><strong>${this.t("currentRevision")}</strong><p>${pair(false)}</p></div></div>`;
  }

  revisionChanges(d) {
    return `<h3>${this.t("changes")}</h3>${d.revision_differences?.length ? `<div class="bcm-table-wrap"><table class="bcm-detail-table"><thead><tr><th>${this.t("field")}</th><th>${this.t("original")}</th><th>${this.t("current")}</th></tr></thead><tbody>${d.revision_differences.map((change) => `<tr><td>${this.t(change.scope)} · ${this.measurementFieldLabel(change.field)}</td><td>${this.measurementFieldValue(change.field,change.original)}</td><td>${this.measurementFieldValue(change.field,change.current)}</td></tr>`).join("")}</tbody></table></div>` : `<p class="bcm-muted">${this.t("noChanges")}</p>`}`;
  }

  measurementDetailStale() {
    const d = this._measurementDetail;
    if (!d) return true;
    const rows = d.record_type === "calibration" ? this._state.calibrations : this._state.idle_measurements;
    const liveRow = rows.find((item) => (item.calibration_id || item.measurement_id) === (d.calibration_id || d.measurement_id));
    return Boolean(liveRow && ["valid","revision_status","current_setup_revision","current_battery_revision","analysis_revision","usage_reason"].some((key) => liveRow[key] !== d[key]));
  }

  renderMeasurementDialog(admin) {
    const d = this._measurementDetail;
    const error = this._error ? `<div class="bcm-error" role="alert">${esc(this._error)}</div>` : "";
    const title = d ? `${this.t(d.record_type === "idle" ? "idle" : "calibrations")} · ${esc((d.measurement_id || d.calibration_id).slice(0,8))}` : this.t("details");
    const header = `<div class="bcm-detail-header"><h2 id="bcm-detail-title">${title}</h2><button class="bcm-btn secondary" data-action="close-dialog">${this.t("close")}</button></div>`;
    if (!d) return `<div class="bcm-overlay"><div class="bcm-dialog" role="dialog" aria-modal="true" aria-labelledby="bcm-detail-title">${header}${error || this.t("loading")}</div></div>`;
    const calibration = d.record_type === "calibration";
    const kind = d.record_type;
    const action = this._recordDecision;
    const active = this._state.session.mode !== "idle";
    const stale = this.measurementDetailStale();
    const reasonRequired = action === "approve" || action === "revoke";
    const canConfirm = admin && !active && !this._busy && !stale && (!reasonRequired || this._decisionReason?.trim()) && (action !== "approve" || this._decisionConfirmed);
    const actionHint = action === "invalidate" ? (calibration ? "invalidateCalibrationHint" : "invalidateIdleHint") : `${action}Hint`;
    const decision = action && admin ? `<section class="bcm-decision"><h3>${this.t(action)}</h3><p>${this.t(actionHint)}</p>${action === "approve" ? `${this.revisionComparison(d)}${this.revisionChanges(d)}<label class="bcm-equivalence"><input type="checkbox" data-equivalence ${this._decisionConfirmed ? "checked" : ""}>${this.t("equivalent")}</label>` : ""}${action !== "reanalyze" ? `<div class="bcm-field"><label for="bcm-decision-reason">${this.t("decisionReason")}${reasonRequired ? " *" : ""}</label><textarea id="bcm-decision-reason" data-decision-reason>${esc(this._decisionReason || "")}</textarea></div>` : ""}<div class="bcm-actions"><button class="bcm-btn ${action === "invalidate" ? "danger" : ""}" data-action="confirm-measurement" ${canConfirm ? "" : "disabled"}>${this.t(action)}</button><button class="bcm-btn secondary" data-action="cancel-decision" ${this._busy ? "disabled" : ""}>${this.t("cancel")}</button></div></section>` : "";
    const samples = d.chart_samples || [];
    const trace = samples.length >= 2 ? `${renderSessionChart({ ...d, historical:true }, calibration ? (d.idle_correction_status === "pending" ? "gross_calibration" : "calibrating") : "idle", this.language)}<p class="bcm-muted">${this.t("traceSummary")} ${this.t("measurements")}: ${d.sample_count ?? samples.length}.</p><label class="bcm-sample-label">${this.t("point")}<input data-sample-slider type="range" min="0" max="${samples.length - 1}" value="${this._sampleIndex || 0}"></label><div data-sample-readout>${this.sampleReadout(d,this._sampleIndex || 0)}</div>` : `<div class="bcm-note">${this.t("noTrace")}</div>`;
    const metric = (key,value) => this.metric(this.t(key),value);
    const sourceLinks = calibration ? `<section><h3>${this.t("sourceMeasurements")}</h3>${d.idle_sources?.length ? d.idle_sources.map((source) => `<div class="bcm-source-row">${source.missing ? `${esc(source.measurement_id)} · ${this.t("missingSource")}` : `<button class="bcm-btn secondary" data-record-action="details" data-record-kind="idle" data-record-id="${esc(source.measurement_id)}">${fmtDate(source.started_at || source.finished_at,this.language)} · ${this.t("revision")} ${source.setup_revision}</button> ${this.validityBadge(source)}`}</div>`).join("") : `<p class="bcm-muted">${this.t("noSources")}</p>`}</section>` : `<section><h3>${this.t("dependentRecords")}: ${(d.dependent_calibration_ids || []).length}</h3>${(d.dependent_calibration_ids || []).map((id) => `<button class="bcm-btn secondary" data-record-action="details" data-record-kind="calibration" data-record-id="${esc(id)}">${this.t("calibrations")} · ${esc(id.slice(0,8))}</button>`).join(" ")}</section>`;
    const snapshots = [["setup",d.setup_snapshot], ...(calibration ? [["battery",d.battery_snapshot]] : [])].map(([scope,snapshot]) => `<h3>${this.t(scope)}</h3><table class="bcm-detail-table"><tbody>${Object.entries(snapshot || {}).filter(([key]) => !["setup_id","battery_id","created_at","updated_at","image"].includes(key)).map(([key,value]) => `<tr><th>${this.measurementFieldLabel(key)}</th><td>${this.measurementFieldValue(key,value)}</td></tr>`).join("")}</tbody></table>`).join("");
    const times = calibration ? [["recorded",d.session_started_at],["endpoint",d.charge_finished_at],["detected",d.end_detected_at]] : [["recorded",d.started_at],["detected",d.finished_at]];
    return `<div class="bcm-overlay"><div class="bcm-dialog" role="dialog" aria-modal="true" aria-labelledby="bcm-detail-title">${header}${error}
      <div class="bcm-detail-status">${this.validityBadge(d)}<span>${this.t("confidence")}: <strong>${this.t(`confidence_${d.confidence || "unknown"}`)}</strong></span>${this.usageBadge(d)}</div>
      ${stale ? `<div class="bcm-note">${this.t("staleDetail")} <button class="bcm-btn secondary" data-action="refresh-measurement">${this.t("refresh")}</button></div>` : ""}
      ${active ? `<p class="bcm-note">${this.t("activeSessionHint")}</p>` : ""}${decision}
      <section>${action === "approve" ? "" : this.revisionComparison(d)}${d.invalid_reason ? `<p>${this.t("decisionReason")}: ${esc(d.invalid_reason)}</p>` : ""}</section>
      <section><div class="bcm-metrics">${metric("gross",`${fmt(d.gross_energy_wh)} Wh`)}${calibration ? `${metric("idleEnergy", d.idle_correction_status === "pending" ? "–" : `${fmt(d.idle_energy_wh)} Wh`)}${metric("net",d.idle_correction_status === "pending" ? this.t("pendingCorrection") : `${fmt(d.net_energy_wh)} Wh`)}${metric("baseline",d.idle_correction_status === "pending" ? "–" : `${fmt(d.idle_baseline_power_w,3)} W`)}${metric("elapsed",fmtDuration(d.charge_duration_seconds))}${metric("peakPower",`${fmt(d.peak_power_w)} W`)}` : `${metric("measuredBaseline", d.below_detection_limit ? `&lt; ${fmt(d.upper_bound_power_w,3)} W` : `${fmt(d.median_power_w ?? d.average_power_w,3)} W`)}${metric("stdev",`${fmt(d.stdev_power_w,3)} W`)}${metric("elapsed",fmtDuration(d.duration_seconds))}`}</div>${calibration ? `<p>${this.t("quantity")}: ${d.quantity} · ${this.t("portsUsed")}: ${esc((d.ports || []).join(" + "))}</p><p>${this.t("method")}: ${esc(this.t(`method_${d.end_method}`))} · ${this.t("analysisRevision")} ${d.analysis_revision || 1}</p>` : `<p>${this.t("measurementMode")}: ${this.t(d.mode === "automatic" ? "auto" : "fixed")} · ${this.t(d.reliable ? "reliable" : "unreliableLabel")}</p>`}${times.map(([label,value]) => `<div class="bcm-row"><span>${this.t(label)}</span><strong>${fmtDate(value,this.language)}</strong></div>`).join("")}</section>
      ${d.idle_baseline_is_lower_bound ? `<p class="bcm-note">${this.t("lowerBoundHint")}</p>` : ""}<section><h3>${this.t("trace")}</h3>${trace}</section>${sourceLinks}
      <details data-disclosure="changes"><summary>${this.t("changes")}</summary>${this.revisionChanges(d)}</details>
      <details data-disclosure="snapshots"><summary>${this.t("snapshots")}</summary>${snapshots}</details>
      <details data-disclosure="decisions"><summary>${this.t("decisions")}</summary>${this.decisionHistory(d)}</details>
      ${calibration ? `<details data-disclosure="analyses"><summary>${this.t("priorAnalyses")} (${(d.analysis_history || []).length})</summary>${(d.analysis_history || []).map((item) => `<div class="bcm-note"><strong>${this.t("priorResult")} ${item.analysis_revision}</strong> · ${fmtDate(item.analyzed_at,this.language)}<p>${this.t("net")}: ${fmt(item.net_energy_wh)} Wh · ${this.t("baseline")}: ${fmt(item.idle_baseline_power_w,3)} W</p><p>${this.t("endpoint")}: ${fmtDate(item.charge_finished_at,this.language)}</p></div>`).join("")}</details>` : ""}
      ${!action ? this.recordActions(d,kind,admin,true) : ""}<p class="bcm-muted bcm-record-id">ID: ${esc(d.measurement_id || d.calibration_id)}</p>
    </div></div>`;
  }

  decisionHistory(d) {
    const rows = (d.validity_history || []).map((item) => ({ date:item.changed_at, label:this.t(item.valid ? "restore" : "invalidate"), reason:item.reason }));
    for (const item of d.revision_approvals || []) {
      const revisions = `${this.t("setup")} R${item.setup_revision}${item.battery_revision ? ` / ${this.t("battery")} R${item.battery_revision}` : ""}`;
      rows.push({ date:item.approved_at, label:`${this.t("approve")} · ${revisions}`, reason:item.reason });
      if (item.revoked_at) rows.push({ date:item.revoked_at, label:`${this.t("revoke")} · ${revisions}`, reason:item.revoke_reason });
    }
    return rows.length ? rows.sort((a,b) => String(b.date).localeCompare(String(a.date))).map((row) => `<div class="bcm-note"><strong>${esc(row.label)}</strong><div class="bcm-muted">${fmtDate(row.date,this.language)}</div><p>${esc(row.reason || "–")}</p></div>`).join("") : `<p class="bcm-muted">${this.t("noDecisions")}</p>`;
  }

  sampleReadout(d, index) {
    const sample = d.chart_samples?.[index];
    if (!sample) return "";
    const pending = d.record_type === "calibration" && d.idle_correction_status === "pending";
    return `<div class="bcm-note"><strong>${fmtDate(sample.timestamp,this.language)}</strong><div class="bcm-sample-values"><span>${this.t("power")}: ${fmt(sample.power_w,3)} W</span><span>${this.t("gross")}: ${fmt(sample.gross_energy_wh,4)} Wh</span>${d.record_type === "calibration" && !pending ? `<span>${this.t("net")}: ${fmt(sample.net_energy_wh,4)} Wh</span>` : ""}<span>${this.t("rawEnergy")}: ${fmt(sample.raw_energy_wh,4)} Wh</span>${sample.temperature_c !== null && sample.temperature_c !== undefined ? `<span>${this.t("temperature")}: ${fmt(sample.temperature_c,1)} °C</span>` : ""}</div></div>`;
  }

  async confirmMeasurementDecision() {
    const d = this._measurementDetail;
    const action = this._recordDecision;
    if (!d || !action || this._busy || !this._hass?.user?.is_admin) return;
    if (this._state.session.mode !== "idle") { this._error = this.t("activeSessionHint"); this.render(); return; }
    if (this.measurementDetailStale()) { this._error = this.t("staleDetail"); this.render(); return; }
    const reason = (this._decisionReason || "").trim();
    if (["approve","revoke"].includes(action) && !reason) { this._error = this.t("reasonRequired"); this.render(); return; }
    if (action === "approve" && !this._decisionConfirmed) { this._error = this.t("equivalentRequired"); this.render(); return; }
    const kind = d.record_type;
    const id = d.measurement_id || d.calibration_id;
    const revisions = { expected_setup_revision:d.current_setup_revision, ...(kind === "calibration" ? {expected_battery_revision:d.current_battery_revision} : {}) };
    const request = this._detailsRequest;
    const button = this.shadowRoot.querySelector('[data-action="confirm-measurement"]');
    if (button) button.disabled = true;
    this._renderLock += 1;
    try {
      if (action === "approve" || action === "revoke") await this.call("set_measurement_revision_approval", {record_type:kind, record_id:id, approved:action === "approve", reason, ...revisions});
      else if (action === "reanalyze") await this.call("reanalyze_calibration", {record_id:id, ...revisions});
      else if (["invalidate","restore"].includes(action)) await this.call("set_measurement_validity", {record_type:kind, record_id:id, valid:action === "restore", reason});
      if (this._dialog === "measurement" && request === this._detailsRequest) await this.openMeasurement(kind,id);
    } finally {
      this._renderLock = Math.max(0,this._renderLock - 1);
      this._requestRender(true);
    }
  }

  renderSettings(admin) {
    const s = this._state;
    return `<section class="bcm-card"><h2>${this.t("settings")}</h2><div class="bcm-note">${this.t("currentRevisionOnly")}</div>${admin ? `<div class="bcm-field"><label>${this.t("maxSession")}</label><input id="max-session" data-form-value="maxSession" type="number" min="1" max="48" step="0.5" value="${esc(this._formValues.maxSession ?? s.max_session_hours)}"></div><button class="bcm-btn" data-action="save-settings">${this.t("saveSettings")}</button>` : `<p class="bcm-admin">${this.t("adminOnly")}</p>`}</section>`;
  }

  renderDialog(admin) {
    if (this._dialog === "measurement") return this.renderMeasurementDialog(admin);
    if (!this._dialog || !admin) return "";
    const d = this._draft;
    const dialogError = this._error ? `<div class="bcm-error bcm-dialog-error"><strong>${this.t("error")}:</strong> ${esc(this._error)}</div>` : "";
    if (this._dialog === "battery") {
      return `<div class="bcm-overlay"><div class="bcm-dialog"><h2>${d.battery_id ? this.t("edit") : this.t("addBattery")}</h2>${dialogError}<div class="bcm-form-grid">${this.input("name",this.t("name"),d.name,true)}${this.input("manufacturer",this.t("manufacturer"),d.manufacturer)}${this.input("model",this.t("model"),d.model)}${this.input("nominal_capacity_mah",this.t("capacity"),d.nominal_capacity_mah ?? "",false,"number")}${this.input("nominal_voltage_v",this.t("voltage"),d.nominal_voltage_v,"", "number", "0.01")}${this.input("nominal_energy_mwh",this.t("energy"),d.nominal_energy_mwh ?? (d.nominal_energy_wh === null || d.nominal_energy_wh === undefined ? "" : Number(d.nominal_energy_wh) * 1000),false,"number","1")}${this.selectField("technology",this.t("technology"),["Li-Ion USB-C","Li-Ion","LiFePO4","NiMH","NiCd","Other"],d.technology || "Li-Ion USB-C")}${this.selectField("form_factor",this.t("formFactor"),["AAA","AA","C","D","9V","18650","21700","Proprietary","Other"],d.form_factor || "AA")}${this.selectField("charging_method",this.t("chargingMethod"),["Integrated USB-C charger","External USB charger","Dedicated charger","Other"],d.charging_method || "Integrated USB-C charger")}${this.input("discharge_method",this.t("dischargeMethod"),d.discharge_method)}${this.input("rest_time_minutes",this.t("restTime"),d.rest_time_minutes ?? "","", "number", "1")}${this.imageField("battery",d.image)}</div>${this.textarea("starting_condition_notes",this.t("startingNotes"),d.starting_condition_notes)}${this.textarea("notes",this.t("notes"),d.notes)}<div class="bcm-actions"><button class="bcm-btn" data-action="save-battery">${this.t("save")}</button><button class="bcm-btn secondary" data-action="close-dialog">${this.t("cancel")}</button></div></div></div>`;
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
    const menu = this.shadowRoot.querySelector("[data-ha-menu]");
    if (menu) {
      // Use HA's native icon control and sidebar event, without private menu properties.
      menu.label = this.t("haMenu");
      menu.path = "M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z";
      menu.addEventListener("click", () => this.dispatchEvent(new CustomEvent("hass-toggle-menu", {bubbles:true, composed:true, detail:{}})));
    }
    this.shadowRoot.querySelectorAll("[data-home-disclosure]").forEach(el => el.addEventListener("toggle", () => {
      if (el.isConnected === false) return;
      this.setHomeDisclosure(el.dataset.homeDisclosure, el.open);
    }));
    this.shadowRoot.querySelectorAll("[data-record-action]").forEach((el) => el.addEventListener("click", () => {
      const action = el.dataset.recordAction;
      const id = el.dataset.recordId;
      const d = this._measurementDetail;
      if (this._dialog === "measurement" && d && (d.measurement_id || d.calibration_id) === id && action !== "details") {
        this._recordDecision = action; this._decisionReason = ""; this._decisionConfirmed = false;
        this._dialogScrollTop = 0;
        const dialog = this.shadowRoot.querySelector(".bcm-dialog");
        if (dialog) dialog.scrollTop = 0;
        this.render();
      } else this.openMeasurement(el.dataset.recordKind,id,action);
    }));
    this.shadowRoot.querySelectorAll("[data-history-filter]").forEach((el) => el.addEventListener("change", () => { this._historyFilters[el.dataset.historyFilter] = el.value; this._historyLimits[el.dataset.historyFilter] = 25; this.render(); }));
    this.shadowRoot.querySelectorAll("[data-history-more]").forEach((el) => el.addEventListener("click", () => { const kind = el.dataset.historyMore; this._historyLimits[kind] = (this._historyLimits[kind] || 25) + 25; this.render(); }));
    const decisionReady = () => {
      const button = this.shadowRoot.querySelector('[data-action="confirm-measurement"]');
      const requiresReason = ["approve","revoke"].includes(this._recordDecision);
      if (button) button.disabled = !this._hass?.user?.is_admin || this._busy || this._state.session.mode !== "idle" || this.measurementDetailStale() || (requiresReason && !this._decisionReason?.trim()) || (this._recordDecision === "approve" && !this._decisionConfirmed);
    };
    this.shadowRoot.querySelector("[data-decision-reason]")?.addEventListener("input", (event) => { this._decisionReason = event.target.value; decisionReady(); });
    this.shadowRoot.querySelector("[data-equivalence]")?.addEventListener("change", (event) => { this._decisionConfirmed = event.target.checked; decisionReady(); });
    this.shadowRoot.querySelector("[data-sample-slider]")?.addEventListener("input", (event) => {
      this._sampleIndex = Number(event.target.value);
      const readout = this.shadowRoot.querySelector("[data-sample-readout]");
      if (readout) readout.innerHTML = this.sampleReadout(this._measurementDetail,this._sampleIndex);
    });
    this.shadowRoot.querySelectorAll("[data-tab]").forEach((el) => el.addEventListener("click", () => this.navigate(el.dataset.tab)));
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
      await this.updateSelection(payload);
    }));
    this.shadowRoot.querySelectorAll("[data-quantity]").forEach((el) => el.addEventListener("click", () => this.updateSelection({quantity:Number(el.dataset.quantity)})));
    const target = this.shadowRoot.querySelector("[data-target]");
    if (target) target.addEventListener("input", () => {
      const value = this.shadowRoot.querySelector("[data-target-value]");
      if (value) value.textContent = `${target.value}%`;
    });
    if (target) target.addEventListener("change", () => this.updateSelection({target_percent:Number(target.value)}));
    this.shadowRoot.querySelectorAll("[data-edit-battery]").forEach((el) => el.addEventListener("click", () => { const item = this._state.batteries.find((x) => x.battery_id === el.dataset.editBattery); this._draft = structuredClone(item || {}); this._dialog = "battery"; this._dialogScrollTop = 0; this.render(); }));
    this.shadowRoot.querySelectorAll("[data-edit-setup]").forEach((el) => el.addEventListener("click", () => { const item = this._state.setups.find((x) => x.setup_id === el.dataset.editSetup); this._draft = structuredClone(item || {}); this._dialog = "setup"; this._dialogScrollTop = 0; this.render(); }));
    this.shadowRoot.querySelectorAll("[data-delete-battery]").forEach((el) => el.addEventListener("click", async () => { if (confirm(this.t("confirmDelete"))) { try { await this.call("delete_battery", { battery_id: el.dataset.deleteBattery }); } catch (_err) {} } }));
    this.shadowRoot.querySelectorAll("[data-delete-setup]").forEach((el) => el.addEventListener("click", async () => { if (confirm(this.t("confirmDelete"))) { try { await this.call("delete_setup", { setup_id: el.dataset.deleteSetup }); } catch (_err) {} } }));
    this.shadowRoot.querySelectorAll("[data-action]").forEach((el) => el.addEventListener("click", () => this.handleAction(el.dataset.action)));
  }

  async updateSelection(payload) {
    if (!this._hass || this._busy || this.sessionActive()) return;
    const originTab = this._tab;
    const originDialog = this._dialog;
    const initiatingId = this.shadowRoot.activeElement?.id;
    const selectionFocusId = ["bcm-battery","bcm-setup","bcm-target"].includes(initiatingId) ? initiatingId : null;
    // Do not rely on rerendering: focused inputs intentionally defer it.
    this.shadowRoot.querySelectorAll('[data-select], [data-quantity], [data-target], [data-action="start-charge"], [data-action="start-calibration"]').forEach(el => { el.disabled = true; });
    try {
      await this.call("select", payload);
    } catch (_err) { /* call() retains the error for display. */ }
    finally {
      // A committed dropdown/range change must update readiness without waiting
      // for blur. Uncommitted text drafts still use BcmBase's deferred rendering.
      if (this._tab !== originTab || this._dialog !== originDialog) this._requestRender();
      else {
        const focused = this.shadowRoot.activeElement;
        const restoreFocus = !focused || focused.id === selectionFocusId;
        if (!restoreFocus && isEditingElement(focused)) this._requestRender();
        else {
          this._requestRender(true);
          if (restoreFocus && selectionFocusId) this.shadowRoot.getElementById(selectionFocusId)?.focus({preventScroll:true});
        }
      }
    }
  }

  async handleAction(action) {
    try {
      if (action === "confirm-measurement") { await this.confirmMeasurementDecision(); return; }
      if (action === "cancel-decision") { this._recordDecision = null; this._decisionReason = ""; this._decisionConfirmed = false; this._error = ""; this.render(); return; }
      if (action === "refresh-measurement") { const d = this._measurementDetail; await this.openMeasurement(d.record_type,d.measurement_id || d.calibration_id); return; }
      if (action === "new-battery") { this._draft = {}; this._dialog = "battery"; this._dialogScrollTop = 0; this.render(); return; }
      if (action === "new-setup") { this._draft = { port_labels:["A","B","C","D"], max_power_w:100 }; this._dialog = "setup"; this._dialogScrollTop = 0; this.render(); return; }
      if (action === "close-dialog") { this._detailsRequest += 1; this._dialog = null; this._measurementDetail = null; this._draft = {}; this._dialogScrollTop = 0; this._openDisclosures = []; this.render(); return; }
      if (action === "save-battery") { await this.saveDialog("battery", "save_battery"); return; }
      if (action === "save-setup") { await this.saveDialog("setup", "save_setup"); return; }
      if (action === "start-charge") await this.startSession("start_charge");
      if (action === "stop") await this.call("stop", { reason:"Stopped by user" });
      if (action === "start-calibration") await this.startSession("start_calibration");
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
        await this.startSession("start_idle_measurement", {
          mode: "automatic",
          auto_min_minutes: minimum,
          auto_max_minutes: maximum,
        });
      }
      if (action === "idle-fixed") await this.startSession("start_idle_measurement", {
        mode: "fixed",
        duration_minutes: this.readNumberInput("idle-fixed", 300),
      });
      if (action === "save-settings") await this.call("set_settings", {
        max_session_hours: this.readNumberInput("max-session", 12),
      });
    } catch (_err) {}
  }

  async startSession(command, payload = {}) {
    if (!this._hass || this._busy || this.sessionActive()) return;
    await this.call(command, payload);
    this.navigate("charge");
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
      if (d.nominal_energy_mwh !== undefined) {
        d.nominal_energy_wh = d.nominal_energy_mwh === "" || d.nominal_energy_mwh === null ? null : Number(d.nominal_energy_mwh) / 1000;
      }
      delete d.nominal_energy_mwh;
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
    const canStart = session.mode === "idle" && summary.median_net_energy_wh != null && s.active_idle_summary?.usable !== false && s.batteries.length && s.setups.length;
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
          ${s.active_idle_summary?.usable === false ? `<p class="bcm-muted">${this.t("idleChargeRequired")}</p>` : ""}${summary.median_net_energy_wh === null ? `<p class="bcm-muted">${this.t("noCalibration")}</p>` : `<p class="bcm-muted">${this.t("calibrationValue")}: ${fmt(summary.median_net_energy_wh)} Wh · ${esc(summary.quality)}</p>`}
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
