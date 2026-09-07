import assert from "node:assert/strict";
import test from "node:test";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

class FakeTabsElement {
  constructor() {
    this.scrollLeft = 0;
    this.listeners = new Map();
  }

  addEventListener(type, callback) {
    this.listeners.set(type, callback);
  }
}

class ShadowRootStub {
  constructor() {
    this.activeElement = null;
    this._innerHTML = "";
    this.listeners = new Map();
    this.tabs = null;
  }

  set innerHTML(value) {
    this._innerHTML = value;
    this.tabs = String(value).includes('class="bcm-tabs"') ? new FakeTabsElement() : null;
  }

  get innerHTML() {
    return this._innerHTML;
  }

  addEventListener(type, callback) {
    this.listeners.set(type, callback);
  }

  emit(type) {
    this.listeners.get(type)?.({ type });
  }

  querySelector(selector) {
    if (selector === ".bcm-tabs") return this.tabs;
    return null;
  }

  querySelectorAll() {
    return [];
  }

  getElementById() {
    return null;
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

globalThis.confirm = () => true;

const source = resolve(
  "custom_components/battery_charge_manager/frontend/battery-charge-manager.js",
);
const frontend = await import(`${pathToFileURL(source).href}?test=0.1.2`);

const panelState = ({ quantity = 2, mode = "idle" } = {}) => ({
  version: "0.1.2",
  setups: [
    {
      setup_id: "setup-1",
      name: "Standard-Ladeanordnung",
      port_labels: ["A", "B", "C", "D"],
      idle_summary: {},
    },
  ],
  batteries: [{ battery_id: "battery-1", name: "3600" }],
  selected_setup_id: "setup-1",
  selected_battery_id: "battery-1",
  selected_quantity: quantity,
  target_percent: 50,
  session: {
    mode,
    phase: "idle",
    progress_percent: 0,
    current_power_w: null,
    current_temperature_c: null,
    gross_energy_wh: 0,
    idle_energy_wh: 0,
    net_energy_wh: 0,
    elapsed_seconds: 0,
    ports: [],
  },
  active_calibration_summary: {
    median_net_energy_wh: null,
    pending_count: 0,
    quality: "none",
  },
  active_idle_summary: { reliable_count: 1 },
  idle_measurements: [],
  calibrations: [],
  linear_model: { available: false },
  max_session_hours: 12,
});

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

test("calibration page omits relative charge target and shows exact selected ports", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  panel._state = panelState({ quantity: 2 });

  const html = panel.renderCalibrations(true);

  assert.equal(html.includes("data-target"), false);
  assert.match(html, /2 Akkus/);
  assert.match(html, /A\s*\+\s*B/);
});

test("charge page keeps relative charge target and shows exact selected ports", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  panel._state = panelState({ quantity: 1 });

  const html = panel.renderCharge();

  assert.equal(html.includes("data-target"), true);
  assert.match(html, /1 Akku/);
  assert.match(html, /Anschluss A/);
});

test("panel rerender preserves horizontal navigation scroll position", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  panel._state = panelState();

  panel.render();
  panel.shadowRoot.querySelector(".bcm-tabs").scrollLeft = 180;
  panel.render();

  assert.equal(panel.shadowRoot.querySelector(".bcm-tabs").scrollLeft, 180);
});
