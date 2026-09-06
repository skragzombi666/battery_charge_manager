import assert from "node:assert/strict";
import test from "node:test";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

class ShadowRootStub {
  constructor() {
    this.activeElement = null;
    this.innerHTML = "";
    this.listeners = new Map();
  }

  addEventListener(type, callback) {
    this.listeners.set(type, callback);
  }

  emit(type) {
    this.listeners.get(type)?.({ type });
  }
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
const frontend = await import(`${pathToFileURL(source).href}?test=0.1.1`);

test("numeric values below the minimum clamp to the minimum", () => {
  assert.equal(frontend.clampNumberValue("1", 5, 1440, 300), 5);
  assert.equal(frontend.clampNumberValue("15", 5, 1440, 300), 15);
  assert.equal(frontend.clampNumberValue("", 5, 1440, 300), 300);
});

test("Home Assistant updates do not replace a focused form control", async () => {
  class ProbeElement extends frontend.BcmBase {
    constructor() {
      super();
      this.renderCount = 0;
    }

    render() {
      this.renderCount += 1;
    }
  }

  const probe = new ProbeElement();
  probe.shadowRoot.activeElement = {
    matches(selector) {
      return selector === "input, select, textarea";
    },
  };

  probe.hass = {};
  assert.equal(probe.renderCount, 0);

  probe.shadowRoot.activeElement = null;
  probe.shadowRoot.emit("focusout");
  await new Promise((resolvePromise) => queueMicrotask(resolvePromise));

  assert.equal(probe.renderCount, 1);
});
