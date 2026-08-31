"""Constants for Battery Charge Manager."""

from __future__ import annotations

DOMAIN = "battery_charge_manager"
NAME = "Battery Charge Manager"
VERSION = "0.1.0"
ALGORITHM_VERSION = "0.1.0"

PLATFORMS = ["sensor", "select", "number", "button"]

CONF_SETUP_NAME = "setup_name"
CONF_SWITCH_ENTITY = "switch_entity"
CONF_ENERGY_SENSOR = "energy_sensor"
CONF_POWER_SENSOR = "power_sensor"
CONF_TEMPERATURE_SENSOR = "temperature_sensor"
CONF_DEFAULT_TARGET = "default_target"
CONF_MAX_SESSION_HOURS = "max_session_hours"

DEFAULT_SETUP_NAME = "Standard-Ladeanordnung"
DEFAULT_TARGET = 50
DEFAULT_MAX_SESSION_HOURS = 12
DEFAULT_MAX_POWER_W = 100.0
DEFAULT_HEARTBEAT_SECONDS = 30
DEFAULT_IDLE_AUTO_MIN_MINUTES = 30
DEFAULT_IDLE_AUTO_MAX_HOURS = 8
DEFAULT_IDLE_WARMUP_MINUTES = 5
DEFAULT_IDLE_RESOLUTION_MULTIPLIER = 10
DEFAULT_IDLE_RELIABLE_UPPER_BOUND_W = 0.10
DEFAULT_IDLE_FIXED_MINUTES = 300
DEFAULT_CHARGE_START_TIMEOUT_MINUTES = 15
DEFAULT_END_WINDOW_MINUTES = 10
DEFAULT_END_CONFIRM_MINUTES = 20
DEFAULT_MIN_CHARGE_MINUTES = 10
DEFAULT_CALIBRATION_MAX_FACTOR = 1.5
DEFAULT_CALIBRATION_ABSOLUTE_MAX_WH = 100.0
DEFAULT_CALIBRATION_DRIFT_WARN_PERCENT = 10.0

STORAGE_VERSION = 1
DATA_SCHEMA_VERSION = 2
STORAGE_KEY = f"{DOMAIN}.storage"

SIGNAL_UPDATE = f"{DOMAIN}_update"

SESSION_IDLE = "idle"
SESSION_CHARGING = "charging"
SESSION_CALIBRATING = "calibrating"
SESSION_IDLE_MEASURING = "idle_measuring"
SESSION_OBSERVING = "observing"
ACTIVE_SESSION_MODES = {
    SESSION_CHARGING,
    SESSION_CALIBRATING,
    SESSION_IDLE_MEASURING,
    SESSION_OBSERVING,
}

PHASE_IDLE = "idle"
PHASE_PREPARING = "preparing"
PHASE_WAITING_FOR_LOAD = "waiting_for_load"
PHASE_MAIN_CHARGE = "main_charge"
PHASE_TAPER = "taper"
PHASE_CONFIRMING_END = "confirming_end"
PHASE_TARGET_REACHED = "target_reached"
PHASE_FINISHED = "finished"
PHASE_ERROR = "error"
PHASE_IDLE_MEASUREMENT = "idle_measurement"

IDLE_MODE_FIXED = "fixed"
IDLE_MODE_AUTOMATIC = "automatic"

CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"
CONFIDENCE_UNKNOWN = "unknown"

QUALITY_NONE = "none"
QUALITY_PROVISIONAL = "provisional"
QUALITY_LIMITED = "limited"
QUALITY_STABLE = "stable"
QUALITY_UNSTABLE = "unstable"
QUALITY_OUTDATED = "outdated"

TECHNOLOGIES = [
    "Li-Ion USB-C",
    "Li-Ion",
    "LiFePO4",
    "NiMH",
    "NiCd",
    "Other",
]

CHARGING_METHODS = [
    "Integrated USB-C charger",
    "External USB charger",
    "Dedicated charger",
    "Other",
]

FORM_FACTORS = [
    "AAA",
    "AA",
    "C",
    "D",
    "9V",
    "18650",
    "21700",
    "Proprietary",
    "Other",
]

QUANTITIES = [str(value) for value in range(1, 9)]
PORT_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H"]

PANEL_URL_PATH = "battery-charge-manager"
PANEL_ELEMENT_NAME = "battery-charge-manager-panel"
CARD_ELEMENT_NAME = "battery-charge-manager-card"
FRONTEND_MODULE_URL = f"/api/{DOMAIN}/frontend/battery-charge-manager.js"
