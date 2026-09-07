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
const panelElement = "battery-charge-manager-panel-rabcdef123456";
await import(
  `${pathToFileURL(source).href}?v=0.1.5-abcdef123456&panel=${panelElement}`
);

test("frontend registers the revision-specific panel element requested by Home Assistant", () => {
  assert.ok(customElements.get(panelElement));
});
