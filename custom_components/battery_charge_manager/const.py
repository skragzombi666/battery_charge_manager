"""Constants for Battery Charge Manager."""

from __future__ import annotations

DOMAIN = "battery_charge_manager"
NAME = "Battery Charge Manager"
VERSION = "0.0.1"

PLATFORMS = ["sensor", "select", "number", "button"]

CONF_SWITCH_ENTITY = "switch_entity"
CONF_ENERGY_SENSOR = "energy_sensor"
CONF_POWER_SENSOR = "power_sensor"
CONF_DEFAULT_TARGET = "default_target"
CONF_MAX_SESSION_HOURS = "max_session_hours"

DEFAULT_TARGET = 50
DEFAULT_MAX_SESSION_HOURS = 8

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.storage"

SIGNAL_UPDATE = f"{DOMAIN}_update"

SESSION_IDLE = "idle"
SESSION_CHARGING = "charging"
SESSION_CALIBRATING = "calibrating"

TECHNOLOGIES = [
    "Li-Ion USB-C",
    "Li-Ion",
    "NiMH",
    "LiFePO4",
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
    "Other",
]

QUANTITIES = [str(value) for value in range(1, 9)]
