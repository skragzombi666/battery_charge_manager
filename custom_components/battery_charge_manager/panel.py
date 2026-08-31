"""Register and serve the bundled Battery Charge Manager frontend."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from aiohttp import web

from homeassistant.components.frontend import (
    add_extra_js_url,
    async_register_built_in_panel,
    async_remove_panel,
)
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers.http import KEY_HASS

from .const import (
    CARD_ELEMENT_NAME,
    DOMAIN,
    FRONTEND_MODULE_URL,
    PANEL_ELEMENT_NAME,
    PANEL_URL_PATH,
)

_FRONTEND_PATH = Path(__file__).parent / "frontend" / "battery-charge-manager.js"
_PANEL_STATE_KEY = f"{DOMAIN}_frontend"
_NO_STORE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}


def _integration_version() -> str:
    """Read version without importing packaging metadata."""
    with Path(__file__).with_name("manifest.json").open(encoding="utf-8") as file:
        return str(json.load(file)["version"])


def _frontend_revision() -> str:
    """Return cache-busting frontend content revision."""
    return hashlib.sha256(_FRONTEND_PATH.read_bytes()).hexdigest()[:12]


class BatteryChargeManagerFrontendView(HomeAssistantView):
    """Serve the panel and dashboard card ES module."""

    url = FRONTEND_MODULE_URL
    name = f"api:{DOMAIN}:frontend"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        """Return frontend module source."""
        source = await request.app[KEY_HASS].async_add_executor_job(
            _FRONTEND_PATH.read_text, "utf-8"
        )
        return web.Response(
            text=source,
            content_type="application/javascript",
            headers=_NO_STORE_HEADERS,
        )


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Register module endpoint, global card module, and optional sidebar panel."""
    state = hass.data.setdefault(_PANEL_STATE_KEY, {})
    if not state.get("view_registered"):
        hass.http.register_view(BatteryChargeManagerFrontendView())
        state["view_registered"] = True
    version = _integration_version()
    revision = _frontend_revision()
    module_url = f"{FRONTEND_MODULE_URL}?v={version}-{revision}"
    if not state.get("card_registered"):
        add_extra_js_url(hass, module_url)
        state["card_registered"] = True
    async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="Battery Charge Manager",
        sidebar_icon="mdi:battery-charging-medium",
        frontend_url_path=PANEL_URL_PATH,
        config={
            "version": version,
            "card_element": CARD_ELEMENT_NAME,
            "_panel_custom": {
                "name": PANEL_ELEMENT_NAME,
                "module_url": module_url,
                "embed_iframe": False,
                "trust_external": False,
            },
        },
        require_admin=False,
        update=True,
    )
    state["panel_registered"] = True


def async_unregister_frontend(hass: HomeAssistant) -> None:
    """Remove the sidebar panel on unload."""
    state = hass.data.setdefault(_PANEL_STATE_KEY, {})
    if state.get("panel_registered"):
        async_remove_panel(hass, PANEL_URL_PATH)
        state["panel_registered"] = False
