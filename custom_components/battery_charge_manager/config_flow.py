"""Config flow for Battery Charge Manager."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_DEFAULT_TARGET,
    CONF_ENERGY_SENSOR,
    CONF_MAX_SESSION_HOURS,
    CONF_POWER_SENSOR,
    CONF_SWITCH_ENTITY,
    DEFAULT_MAX_SESSION_HOURS,
    DEFAULT_TARGET,
    DOMAIN,
    FORM_FACTORS,
    TECHNOLOGIES,
)
from .manager import BatteryChargeManager

BATTERY_ID = "battery_id"
BATTERY_NAME = "name"
BATTERY_CAPACITY = "nominal_capacity_mah"
BATTERY_TECHNOLOGY = "technology"
BATTERY_FORM_FACTOR = "form_factor"
BATTERY_IMAGE = "image"


def _hardware_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build hardware/settings schema."""
    defaults = defaults or {}

    switch_key = (
        vol.Required(CONF_SWITCH_ENTITY, default=defaults[CONF_SWITCH_ENTITY])
        if CONF_SWITCH_ENTITY in defaults
        else vol.Required(CONF_SWITCH_ENTITY)
    )
    energy_key = (
        vol.Required(CONF_ENERGY_SENSOR, default=defaults[CONF_ENERGY_SENSOR])
        if CONF_ENERGY_SENSOR in defaults
        else vol.Required(CONF_ENERGY_SENSOR)
    )
    power_key = (
        vol.Optional(CONF_POWER_SENSOR, default=defaults[CONF_POWER_SENSOR])
        if defaults.get(CONF_POWER_SENSOR)
        else vol.Optional(CONF_POWER_SENSOR)
    )

    return vol.Schema(
        {
            switch_key: selector.EntitySelector(
                selector.EntitySelectorConfig(domain="switch")
            ),
            energy_key: selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="sensor", device_class="energy"
                )
            ),
            power_key: selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="sensor", device_class="power"
                )
            ),
            vol.Required(
                CONF_DEFAULT_TARGET,
                default=defaults.get(CONF_DEFAULT_TARGET, DEFAULT_TARGET),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=20,
                    max=100,
                    step=1,
                    unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.SLIDER,
                )
            ),
            vol.Required(
                CONF_MAX_SESSION_HOURS,
                default=defaults.get(
                    CONF_MAX_SESSION_HOURS, DEFAULT_MAX_SESSION_HOURS
                ),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=24,
                    step=1,
                    unit_of_measurement="h",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }
    )


def _battery_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build battery type schema."""
    defaults = defaults or {}

    name_key = (
        vol.Required(BATTERY_NAME, default=defaults[BATTERY_NAME])
        if BATTERY_NAME in defaults
        else vol.Required(BATTERY_NAME)
    )
    image_key = (
        vol.Optional(BATTERY_IMAGE, default=defaults[BATTERY_IMAGE])
        if defaults.get(BATTERY_IMAGE)
        else vol.Optional(BATTERY_IMAGE)
    )

    return vol.Schema(
        {
            name_key: selector.TextSelector(),
            vol.Required(
                BATTERY_CAPACITY,
                default=defaults.get(BATTERY_CAPACITY, 1000),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=100000,
                    step=1,
                    unit_of_measurement="mAh",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                BATTERY_TECHNOLOGY,
                default=defaults.get(BATTERY_TECHNOLOGY, TECHNOLOGIES[0]),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=TECHNOLOGIES,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                BATTERY_FORM_FACTOR,
                default=defaults.get(BATTERY_FORM_FACTOR, "AA"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=FORM_FACTORS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            image_key: selector.MediaSelector(
                selector.MediaSelectorConfig(accept=["image/*"])
            ),
        }
    )


class BatteryChargeManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial setup."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up hardware and defaults."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Battery Charge Manager",
                data={},
                options=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_hardware_schema(),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return options flow."""
        return BatteryChargeManagerOptionsFlow(config_entry)


class BatteryChargeManagerOptionsFlow(OptionsFlow):
    """Manage hardware settings and battery library."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._selected_battery_id: str | None = None

    @property
    def manager(self) -> BatteryChargeManager:
        """Return runtime manager."""
        return self.hass.data[DOMAIN][self.config_entry.entry_id]

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show management menu."""
        menu = ["global_settings", "add_battery"]
        if self.manager.batteries:
            menu.extend(["edit_battery", "delete_battery"])
        return self.async_show_menu(step_id="init", menu_options=menu)

    async def async_step_global_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Edit hardware and defaults."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="global_settings",
            data_schema=_hardware_schema(dict(self.config_entry.options)),
        )

    async def async_step_add_battery(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add a battery type."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if any(
                battery.name.casefold()
                == str(user_input[BATTERY_NAME]).strip().casefold()
                for battery in self.manager.batteries.values()
            ):
                errors["base"] = "duplicate_name"
            else:
                await self.manager.async_add_battery(
                    name=user_input[BATTERY_NAME],
                    nominal_capacity_mah=round(user_input[BATTERY_CAPACITY]),
                    technology=user_input[BATTERY_TECHNOLOGY],
                    form_factor=user_input[BATTERY_FORM_FACTOR],
                    image=user_input.get(BATTERY_IMAGE),
                )
                return self.async_create_entry(
                    title="", data=dict(self.config_entry.options)
                )

        return self.async_show_form(
            step_id="add_battery",
            data_schema=_battery_schema(user_input),
            errors=errors,
        )

    async def async_step_edit_battery(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose a battery to edit."""
        if user_input is not None:
            self._selected_battery_id = user_input[BATTERY_ID]
            return await self.async_step_edit_battery_details()

        choices = {
            battery_id: battery.name
            for battery_id, battery in self.manager.batteries.items()
        }
        return self.async_show_form(
            step_id="edit_battery",
            data_schema=vol.Schema({vol.Required(BATTERY_ID): vol.In(choices)}),
        )

    async def async_step_edit_battery_details(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Edit battery details."""
        if not self._selected_battery_id:
            return await self.async_step_edit_battery()

        battery = self.manager.batteries[self._selected_battery_id]
        errors: dict[str, str] = {}

        if user_input is not None:
            if any(
                other.battery_id != battery.battery_id
                and other.name.casefold()
                == str(user_input[BATTERY_NAME]).strip().casefold()
                for other in self.manager.batteries.values()
            ):
                errors["base"] = "duplicate_name"
            else:
                await self.manager.async_update_battery(
                    battery.battery_id,
                    name=user_input[BATTERY_NAME],
                    nominal_capacity_mah=round(user_input[BATTERY_CAPACITY]),
                    technology=user_input[BATTERY_TECHNOLOGY],
                    form_factor=user_input[BATTERY_FORM_FACTOR],
                    image=user_input.get(BATTERY_IMAGE),
                )
                return self.async_create_entry(
                    title="", data=dict(self.config_entry.options)
                )

        defaults = {
            BATTERY_NAME: battery.name,
            BATTERY_CAPACITY: battery.nominal_capacity_mah,
            BATTERY_TECHNOLOGY: battery.technology,
            BATTERY_FORM_FACTOR: battery.form_factor,
            BATTERY_IMAGE: battery.image,
        }
        return self.async_show_form(
            step_id="edit_battery_details",
            data_schema=_battery_schema(defaults if user_input is None else user_input),
            errors=errors,
        )

    async def async_step_delete_battery(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Delete a battery type."""
        if user_input is not None:
            await self.manager.async_delete_battery(user_input[BATTERY_ID])
            return self.async_create_entry(
                title="", data=dict(self.config_entry.options)
            )

        choices = {
            battery_id: battery.name
            for battery_id, battery in self.manager.batteries.items()
        }
        return self.async_show_form(
            step_id="delete_battery",
            data_schema=vol.Schema({vol.Required(BATTERY_ID): vol.In(choices)}),
        )
