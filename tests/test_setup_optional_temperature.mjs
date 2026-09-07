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
await import(`${pathToFileURL(source).href}?test=optional-temperature-limit`);

test("blank optional setup temperature limit remains null", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._draft = {
    name: "Standard-Ladeanordnung",
    power_sensor: "sensor.plug_power",
    temperature_sensor: null,
    max_power_w: 100,
    max_temperature_c: null,
    port_labels: ["A", "B", "C", "D"],
  };

  const normalized = panel.normalizeDraft("setup");

  assert.equal(normalized.temperature_sensor, null);
  assert.equal(normalized.max_temperature_c, null);
});
