import assert from "node:assert/strict";
import test from "node:test";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

class ShadowRootStub {
  constructor() {
    this.activeElement = null;
  }
  addEventListener() {}
  querySelector() { return null; }
  querySelectorAll() { return []; }
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
  get(name) { return this.registry.get(name); },
  define(name, value) { this.registry.set(name, value); },
};

globalThis.Event = class {
  constructor(type) { this.type = type; }
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
await import(`${pathToFileURL(source).href}?test=battery-energy-mwh`);

const panelClass = () => customElements.get(
  [...customElements.registry.keys()].find((name) => name.startsWith("battery-charge-manager-panel")),
);

test("battery form converts nominal energy from mWh and leaves mAh optional", () => {
  const Panel = panelClass();
  const panel = new Panel();
  panel._draft = {
    name: "3600",
    nominal_capacity_mah: null,
    nominal_voltage_v: 1.5,
    nominal_energy_wh: null,
    nominal_energy_mwh: 3600,
    technology: "Li-Ion USB-C",
    form_factor: "AA",
  };

  const normalized = panel.normalizeDraft("battery");

  assert.equal(normalized.nominal_capacity_mah, null);
  assert.equal(normalized.nominal_energy_wh, 3.6);
  assert.equal("nominal_energy_mwh" in normalized, false);
});

test("battery edit dialog labels energy as mWh and does not require mAh", () => {
  const Panel = panelClass();
  const panel = new Panel();
  panel._hass = { language: "de" };
  panel._dialog = "battery";
  panel._draft = {
    name: "3600",
    nominal_capacity_mah: null,
    nominal_voltage_v: 1.5,
    nominal_energy_wh: 3.6,
    technology: "Li-Ion USB-C",
    form_factor: "AA",
  };

  const html = panel.renderDialog(true);
  const capacityTag = html.match(/<input data-draft="nominal_capacity_mah"[^>]*>/)?.[0] || "";

  assert.match(html, /Nennenergie \(mWh\)/);
  assert.match(html, /data-draft="nominal_energy_mwh"[^>]*value="3600"/);
  assert.doesNotMatch(capacityTag, /required/);
});
