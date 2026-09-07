import assert from "node:assert/strict";
import test from "node:test";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

class ShadowRootStub {
  constructor() {
    this.activeElement = null;
  }
  addEventListener() {}
}

globalThis.HTMLElement = class {
  attachShadow() {
    const root = new ShadowRootStub();
    this.shadowRoot = root;
    return root;
  }
};

globalThis.customElements = {
  registry: new Map(),
  get(name) {
    return this.registry.get(name);
  },
  define(name, value) {
    this.registry.set(name, value);
  },
};

globalThis.Event = class {
  constructor(type) {
    this.type = type;
  }
};

globalThis.window = {
  customCards: [],
  history: { pushState() {} },
  dispatchEvent() {},
  location: { assign() {} },
};

const source = resolve(
  "custom_components/battery_charge_manager/frontend/battery-charge-manager.js",
);
await import(`${pathToFileURL(source).href}?test=dialog-error-visibility`);

test("setup dialog displays save errors inside the modal", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true }, states: {} };
  panel._dialog = "setup";
  panel._draft = {
    name: "Standard-Ladeanordnung",
    port_labels: ["A", "B", "C", "D"],
    max_power_w: 100,
  };
  panel._error = "Value must be greater than zero";

  const html = panel.renderDialog(true);

  assert.match(html, /bcm-dialog-error/);
  assert.match(html, /Value must be greater than zero/);
});
