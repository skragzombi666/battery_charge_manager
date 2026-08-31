"""WebSocket API used by the bundled panel and dashboard card."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, IDLE_MODE_AUTOMATIC
from .manager import BatteryChargeManager


def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register frontend commands."""
    for command in (
        ws_get_state,
        ws_subscribe,
        ws_save_setup,
        ws_delete_setup,
        ws_save_battery,
        ws_delete_battery,
        ws_select,
        ws_set_settings,
        ws_start_charge,
        ws_start_calibration,
        ws_finish_calibration,
        ws_start_idle_measurement,
        ws_stop,
        ws_set_measurement_validity,
    ):
        websocket_api.async_register_command(hass, command)


def _manager(hass: HomeAssistant) -> BatteryChargeManager:
    """Return the single configured manager."""
    managers = hass.data.get(DOMAIN, {})
    if not managers:
        raise HomeAssistantError("Battery Charge Manager is not configured")
    return next(iter(managers.values()))


def _send_error(
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
    err: Exception,
) -> None:
    """Return a frontend-safe operation error."""
    connection.send_error(
        msg["id"],
        websocket_api.ERR_HOME_ASSISTANT_ERROR,
        str(err),
    )


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get_state"})
@callback
def ws_get_state(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return complete panel state."""
    try:
        result = _manager(hass).frontend_state()
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"], result)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/subscribe"})
@callback
def ws_subscribe(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Subscribe to manager updates."""
    try:
        manager = _manager(hass)
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return

    @callback
    def forward_update() -> None:
        connection.send_message(
            websocket_api.event_message(msg["id"], manager.frontend_state())
        )

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, manager.signal, forward_update
    )
    connection.send_result(msg["id"], manager.frontend_state())


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save_setup",
        vol.Required("data"): dict,
    }
)
@websocket_api.async_response
async def ws_save_setup(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Create or update a charging setup."""
    try:
        setup = await _manager(hass).async_add_or_update_setup(msg["data"])
    except (HomeAssistantError, ValueError, TypeError) as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"], setup.as_dict())


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/delete_setup",
        vol.Required("setup_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_setup(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Delete a charging setup."""
    try:
        await _manager(hass).async_delete_setup(msg["setup_id"])
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"])


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save_battery",
        vol.Required("data"): dict,
    }
)
@websocket_api.async_response
async def ws_save_battery(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Create or update a battery type."""
    try:
        battery = await _manager(hass).async_add_or_update_battery(msg["data"])
    except (HomeAssistantError, ValueError, TypeError) as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"], battery.as_dict())


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/delete_battery",
        vol.Required("battery_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_battery(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Delete a battery type."""
    try:
        await _manager(hass).async_delete_battery(msg["battery_id"])
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/select",
        vol.Optional("setup_id"): str,
        vol.Optional("battery_id"): str,
        vol.Optional("quantity"): vol.Coerce(int),
        vol.Optional("target_percent"): vol.Coerce(int),
    }
)
@websocket_api.async_response
async def ws_select(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update operational selections."""
    manager = _manager(hass)
    try:
        if "setup_id" in msg:
            await manager.async_select_setup(msg["setup_id"])
        if "battery_id" in msg:
            await manager.async_select_battery(msg["battery_id"])
        if "quantity" in msg:
            await manager.async_select_quantity(msg["quantity"])
        if "target_percent" in msg:
            await manager.async_set_target_percent(msg["target_percent"])
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"], manager.frontend_state())


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/set_settings",
        vol.Required("max_session_hours"): vol.Coerce(float),
    }
)
@websocket_api.async_response
async def ws_set_settings(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update global safety settings."""
    manager = _manager(hass)
    try:
        await manager.async_set_max_session_hours(msg["max_session_hours"])
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"], manager.frontend_state())


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/start_charge"})
@websocket_api.async_response
async def ws_start_charge(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Start normal charging."""
    try:
        await _manager(hass).async_start_charge()
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"])


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/start_calibration"}
)
@websocket_api.async_response
async def ws_start_calibration(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Start automatic calibration."""
    try:
        await _manager(hass).async_start_calibration()
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"])


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/finish_calibration"}
)
@websocket_api.async_response
async def ws_finish_calibration(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Manually finish calibration as a low-confidence fallback."""
    try:
        value = await _manager(hass).async_finish_calibration()
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"], {"net_energy_wh": value})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/start_idle_measurement",
        vol.Optional("mode", default=IDLE_MODE_AUTOMATIC): vol.In(
            [IDLE_MODE_AUTOMATIC, "fixed"]
        ),
        vol.Optional("duration_minutes"): vol.Coerce(float),
        vol.Optional("auto_min_minutes", default=30): vol.Coerce(float),
        vol.Optional("auto_max_minutes", default=480): vol.Coerce(float),
    }
)
@websocket_api.async_response
async def ws_start_idle_measurement(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Start fixed-duration or automatic reliability-driven idle measurement."""
    try:
        await _manager(hass).async_start_idle_measurement(
            mode=msg["mode"],
            duration_minutes=msg.get("duration_minutes"),
            auto_min_minutes=msg["auto_min_minutes"],
            auto_max_minutes=msg["auto_max_minutes"],
        )
    except (HomeAssistantError, ValueError, TypeError) as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/stop",
        vol.Optional("reason", default="Stopped by user"): str,
    }
)
@websocket_api.async_response
async def ws_stop(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Abort active operation."""
    await _manager(hass).async_stop(msg["reason"])
    connection.send_result(msg["id"])


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/set_measurement_validity",
        vol.Required("record_type"): vol.In(["idle", "calibration"]),
        vol.Required("record_id"): str,
        vol.Required("valid"): bool,
        vol.Optional("reason", default=""): str,
    }
)
@websocket_api.async_response
async def ws_set_measurement_validity(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Invalidate or restore a retained measurement record."""
    try:
        await _manager(hass).async_set_measurement_validity(
            msg["record_type"],
            msg["record_id"],
            msg["valid"],
            msg["reason"],
        )
    except HomeAssistantError as err:
        _send_error(connection, msg, err)
        return
    connection.send_result(msg["id"])
