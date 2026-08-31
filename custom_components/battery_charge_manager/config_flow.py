"""Config flow for Battery Charge Manager."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_DEFAULT_TARGET,
    CONF_ENERGY_SENSOR,
    CONF_MAX_SESSION_HOURS,
    CONF_POWER_SENSOR,
    CONF_SETUP_NAME,
    CONF_SWITCH_ENTITY,
    CONF_TEMPERATURE_SENSOR,
    DEFAULT_MAX_SESSION_HOURS,
    DEFAULT_SETUP_NAME,
    DEFAULT_TARGET,
    DOMAIN,
)


class BatteryChargeManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create the single integration and its first charging setup."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure the first physical charging setup."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(
                title="Battery Charge Manager",
                data={},
                options=user_input,
            )
        schema = vol.Schema(
            {
                vol.Required(CONF_SETUP_NAME, default=DEFAULT_SETUP_NAME): selector.TextSelector(),
                vol.Required(CONF_SWITCH_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="switch")
                ),
                vol.Required(CONF_ENERGY_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="energy")
                ),
                vol.Optional(CONF_POWER_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="power")
                ),
                vol.Optional(CONF_TEMPERATURE_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                ),
                vol.Required(CONF_DEFAULT_TARGET, default=DEFAULT_TARGET): selector.NumberSelector(
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
                    default=DEFAULT_MAX_SESSION_HOURS,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=48,
                        step=0.5,
                        unit_of_measurement="h",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
