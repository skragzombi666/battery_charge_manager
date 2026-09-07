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

const chartSamples = [
  {
    timestamp: "2026-09-07T08:00:00+00:00",
    gross_energy_wh: 0,
    idle_energy_wh: 0,
    net_energy_wh: 0,
    power_w: 4,
    net_power_w: 3.8,
  },
  {
    timestamp: "2026-09-07T08:30:00+00:00",
    gross_energy_wh: 2,
    idle_energy_wh: 0.1,
    net_energy_wh: 1.9,
    power_w: 3,
    net_power_w: 2.8,
  },
  {
    timestamp: "2026-09-07T09:00:00+00:00",
    gross_energy_wh: 3,
    idle_energy_wh: 0.2,
    net_energy_wh: 2.8,
    power_w: 0.25,
    net_power_w: 0.05,
  },
];

const panelState = ({ quantity = 2, mode = "idle", session = {} } = {}) => ({
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
    current_net_power_w: null,
    current_temperature_c: null,
    peak_power_w: null,
    peak_net_power_w: null,
    gross_energy_wh: 0,
    idle_energy_wh: 0,
    net_energy_wh: 0,
    elapsed_seconds: 0,
    sample_count: 0,
    ports: [],
    chart_samples: [],
    ...session,
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

test("fixed idle measurement shows live progress remaining time and chart", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  panel._state = panelState({
    mode: "idle_measuring",
    session: {
      phase: "idle_measurement",
      idle_measurement_mode: "fixed",
      requested_duration_minutes: 300,
      elapsed_seconds: 3600,
      current_power_w: 0.2,
      gross_energy_wh: 0.2,
      sample_count: 123,
      chart_samples: chartSamples,
    },
  });

  const html = panel.renderIdle(true);

  assert.match(html, /Laufende Messung/);
  assert.match(html, /Verbleibende Zeit/);
  assert.match(html, /4 h 00 min/);
  assert.match(html, /20(?:\.0)?%/);
  assert.match(html, /bcm-session-chart/);
  assert.match(html, /data-series="power"/);
  assert.match(html, /data-series="energy"/);
});

test("active calibration shows live phase ports and power-energy chart without fake percent progress", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  panel._state = panelState({
    quantity: 2,
    mode: "calibrating",
    session: {
      phase: "taper",
      elapsed_seconds: 5400,
      current_power_w: 1.2,
      peak_power_w: 7.5,
      gross_energy_wh: 8.4,
      idle_energy_wh: 0.3,
      net_energy_wh: 8.1,
      sample_count: 180,
      ports: ["A", "B"],
      chart_samples: chartSamples,
      idle_correction_status: "applied",
    },
  });

  const html = panel.renderCalibrations(true);

  assert.match(html, /Laufende Kalibration/);
  assert.match(html, /A\s*\+\s*B/);
  assert.match(html, /Abregel/);
  assert.match(html, /bcm-session-chart/);
  assert.equal(html.includes("data-target"), false);
  assert.equal(html.includes("bcm-progress"), false);
});

test("active charge shows target-energy chart and exact ports", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  panel._state = panelState({
    quantity: 2,
    mode: "charging",
    session: {
      phase: "main_charge",
      progress_percent: 50,
      target_energy_wh: 6,
      net_energy_wh: 3,
      elapsed_seconds: 1800,
      ports: ["A", "B"],
      chart_samples: chartSamples,
    },
  });

  const html = panel.renderCharge();

  assert.match(html, /Laufender Ladevorgang/);
  assert.match(html, /A\s*\+\s*B/);
  assert.match(html, /bcm-session-chart/);
  assert.match(html, /data-marker="target-energy"/);
});

test("dashboard card shows selected ports and a compact live chart during charging", () => {
  const Card = customElements.get("battery-charge-manager-card");
  const card = new Card();
  card._hass = { language: "de" };
  card._config = {};
  card._state = panelState({
    quantity: 2,
    mode: "charging",
    session: {
      phase: "main_charge",
      progress_percent: 40,
      target_energy_wh: 5,
      net_energy_wh: 2,
      ports: ["A", "B"],
      chart_samples: chartSamples,
    },
  });

  card.render();

  assert.match(card.shadowRoot.innerHTML, /A\s*\+\s*B/);
  assert.match(card.shadowRoot.innerHTML, /bcm-session-chart/);
});

test("chart degrades to energy-only when no power sensor data exists", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  const energyOnly = chartSamples.map((sample) => ({
    ...sample,
    power_w: null,
    net_power_w: null,
  }));
  panel._state = panelState({
    mode: "calibrating",
    session: {
      phase: "main_charge",
      ports: ["A", "B"],
      chart_samples: energyOnly,
    },
  });

  const html = panel.renderCalibrations(true);

  assert.equal(html.includes('data-series="power"'), false);
  assert.match(html, /data-series="energy"/);
});

test("automatic idle chart shows future minimum-duration marker before minimum is reached", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  const shortTrace = chartSamples.slice(0, 2);
  panel._state = panelState({
    mode: "idle_measuring",
    session: {
      phase: "idle_measurement",
      idle_measurement_mode: "automatic",
      auto_min_minutes: 120,
      auto_max_minutes: 480,
      elapsed_seconds: 1800,
      chart_samples: shortTrace,
    },
  });

  const html = panel.renderIdle(true);

  assert.match(html, /data-marker="minimum-duration"/);
});
