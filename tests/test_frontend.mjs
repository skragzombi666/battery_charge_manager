import assert from "node:assert/strict";
import test from "node:test";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

class FakeDialogElement {
  constructor() {
    this.scrollTop = 0;
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
    this.menu = null;
    this.dialog = null;
  }

  set innerHTML(value) {
    this._innerHTML = value;
    this.menu = String(value).includes('data-ha-menu') ? new FakeDialogElement() : null;
    this.dialog = String(value).includes('class="bcm-dialog"') ? new FakeDialogElement() : null;
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
    if (selector === "[data-ha-menu]") return this.menu;
    if (selector === ".bcm-dialog") return this.dialog;
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
  dispatchEvent(event) { this.lastEvent = event; return true; }
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
globalThis.CustomEvent = class {
  constructor(type, options) { this.type = type; Object.assign(this, options); }
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
const frontend = await import(`${pathToFileURL(source).href}?test=0.1.3`);

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
  version: "0.1.3",
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

test("home replaces peer tabs with one management entry and the HA sidebar button", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  panel._state = panelState();

  panel.render();
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /class="bcm-tabs"/);
  assert.match(panel.shadowRoot.innerHTML, /data-tab="manage"/);
  assert.ok(panel.shadowRoot.innerHTML.indexOf('<header class="bcm-header">') < panel.shadowRoot.innerHTML.indexOf('<div class="bcm-shell">'));
  const menu = panel.shadowRoot.querySelector("[data-ha-menu]");
  assert.match(menu.label, /Home Assistant/);
  assert.ok(menu.path);
  menu.listeners.get("click")();
  assert.equal(panel.lastEvent.type, "hass-toggle-menu");
  assert.equal(panel.lastEvent.bubbles, true);
  assert.equal(panel.lastEvent.composed, true);
  const scrolled = [];
  const lookup = panel.shadowRoot.querySelector.bind(panel.shadowRoot);
  panel.shadowRoot.querySelector = selector => [".bcm-header",".bcm-shell"].includes(selector)
    ? {scrollIntoView() { scrolled.push(selector); }} : lookup(selector);
  panel.navigate("manage");
  assert.deepEqual(scrolled, [".bcm-header"]);
});

function homePanel() {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { id: "user-1", is_admin: true } };
  panel._state = panelState();
  return panel;
}

test("quick charge exposes quantity and battery while setup and target are in a closed editor", () => {
  const panel = homePanel();
  const html = panel.renderCharge();
  const [frequent, rare] = html.split('<details class="bcm-charge-options"');
  assert.match(frequent, /data-quantity="2"/);
  assert.match(frequent, /data-select="battery"/);
  assert.doesNotMatch(frequent, /data-select="setup"|data-target/);
  assert.match(rare, /^ data-home-disclosure="charge-options">/);
  assert.match(rare, /Standard-Ladeanordnung/);
  assert.match(rare, /50%/);
  assert.match(rare, /data-select="setup"/);
  assert.match(rare, /data-target/);
});

test("calibration disclosure persists per browser and HA user, including explicit close", (t) => {
  const storage = new Map();
  globalThis.localStorage = { getItem: key => storage.get(key), setItem: (key, value) => storage.set(key, value) };
  t.after(() => { delete globalThis.localStorage; });
  const first = homePanel();
  assert.doesNotMatch(first.renderHome(true), /data-home-disclosure="calibration" open/);
  first.setHomeDisclosure("calibration", true);
  const reopened = homePanel();
  assert.match(reopened.renderHome(true), /data-home-disclosure="calibration" open/);
  reopened.render();
  assert.match(reopened.renderHome(true), /data-home-disclosure="calibration" open/);
  const otherUser = homePanel();
  otherUser._hass.user.id = "user-2";
  assert.doesNotMatch(otherUser.renderHome(true), /data-home-disclosure="calibration" open/);
  reopened.setHomeDisclosure("calibration", false);
  assert.doesNotMatch(homePanel().renderHome(true), /data-home-disclosure="calibration" open/);
});

test("unavailable browser storage does not prevent toggling or rendering", (t) => {
  Object.defineProperty(globalThis, "localStorage", { configurable: true, get() { throw new Error("Storage blocked"); } });
  t.after(() => { delete globalThis.localStorage; });
  const panel = homePanel();
  panel.setHomeDisclosure("calibration", true);
  assert.match(panel.renderHome(true), /data-home-disclosure="calibration" open/);
  panel.setHomeDisclosure("calibration", false);
  assert.doesNotMatch(panel.renderHome(true), /data-home-disclosure="calibration" open/);
});

test("all running modes are visible above a collapsed calibration starter on home", () => {
  for (const mode of ["charging", "calibrating", "idle_measuring"]) {
    const panel = homePanel();
    panel._state = panelState({ mode, session: { chart_samples: chartSamples } });
    const html = panel.renderHome(true);
    const active = html.split('<details class="bcm-calibration-home"')[0];
    assert.match(active, /bcm-session-chart/);
    assert.match(active, /data-action="stop"/);
    assert.doesNotMatch(html, /data-home-disclosure="calibration" open/);
    assert.doesNotMatch(html, /data-action="start-charge"/);
  }
});

test("live charge identifies the running session rather than a changed selection", () => {
  const panel = homePanel();
  panel._state = panelState({ mode: "charging", session: {
    setup_id: "running-setup", battery_id: "running-battery", quantity: 3, target_percent: 80,
  } });
  panel._state.setups.push({ setup_id: "running-setup", name: "Running charger" });
  panel._state.batteries.push({ battery_id: "running-battery", name: "Running battery" });
  const html = panel.renderHome(true);
  assert.match(html, /Running charger/);
  assert.match(html, /Running battery/);
  assert.match(html, /<strong>3<\/strong>/);
  assert.match(html, /<strong>80%<\/strong>/);
});

test("management children have a parent path and a running-operation link", () => {
  const panel = homePanel();
  panel._tab = "manage";
  panel.render();
  for (const tab of ["batteries", "setups", "idle", "calibrations", "settings"]) {
    assert.match(panel.shadowRoot.innerHTML, new RegExp(`data-tab="${tab}"`));
  }
  panel._tab = "batteries";
  panel._state.session.mode = "calibrating";
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /data-tab="charge"/);
  assert.match(panel.shadowRoot.innerHTML, /data-tab="manage"/);
  assert.match(panel.shadowRoot.innerHTML, /data-active-link/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /data-tab="settings"/);
});

test("successful measurement start returns home; failure stays on the form", async () => {
  const panel = homePanel();
  panel._tab = "idle";
  const commands = [];
  panel._hass.callWS = async command => {
    commands.push(command);
    return command.type.endsWith("get_state") ? panel._state : {};
  };
  await panel.handleAction("idle-fixed");
  assert.equal(commands[0].type, "battery_charge_manager/start_idle_measurement");
  assert.equal(commands[0].duration_minutes, 300);
  assert.equal(panel._tab, "charge");
  panel._tab = "calibrations";
  panel._hass.callWS = async () => { throw new Error("Switch unavailable"); };
  await panel.handleAction("start-calibration");
  assert.equal(panel._tab, "calibrations");
  assert.match(panel._error, /Switch unavailable/);
});

test("busy selections cannot be changed and read-only users have no calibration start", () => {
  const panel = homePanel();
  panel._busy = true;
  const html = panel.renderCharge();
  assert.match(html, /data-select="battery" disabled/);
  assert.match(html, /data-quantity="2"[^>]*disabled/);
  panel.setHomeDisclosure("calibration", true);
  assert.doesNotMatch(panel.renderHome(false), /data-action="start-calibration"/);
});

test("committed battery selection refreshes readiness even while its dropdown stays focused", async () => {
  const panel = homePanel();
  panel._state.batteries.push({ battery_id: "battery-2", name: "AAA" });
  panel.shadowRoot.activeElement = { id:"bcm-battery", matches: selector => selector === "input, select, textarea" };
  const commands = [];
  panel._hass.callWS = async command => {
    commands.push(command);
    if (command.type.endsWith("get_state")) return {
      ...panel._state, selected_battery_id:"battery-2",
      active_calibration_summary:{median_net_energy_wh:7.5,quality:"good"},
    };
    return {};
  };
  await panel.updateSelection({battery_id:"battery-2"});
  assert.deepEqual(commands[0], {type:"battery_charge_manager/select",battery_id:"battery-2"});
  assert.match(panel.shadowRoot.innerHTML, /7.50 Wh/);
  assert.match(panel.shadowRoot.innerHTML, /value="battery-2" selected/);
});

test("selection and disclosure event bindings update their shared state", async () => {
  const panel = homePanel();
  const control = data => ({dataset:data, listeners:new Map(), addEventListener(type,fn) { this.listeners.set(type,fn); }});
  const battery = Object.assign(control({select:"battery"}), {value:"battery-2"});
  const quantity = control({quantity:"3"});
  const disclosure = Object.assign(control({homeDisclosure:"calibration"}), {open:true});
  panel.shadowRoot.querySelectorAll = selector => ({"[data-select]":[battery],"[data-quantity]":[quantity],"[data-home-disclosure]":[disclosure]}[selector] || []);
  const calls = [];
  panel._hass.callWS = async command => { calls.push(command); return command.type.endsWith("get_state") ? panel._state : {}; };
  panel.bindEvents();
  await battery.listeners.get("change")();
  await quantity.listeners.get("click")();
  disclosure.listeners.get("toggle")();
  assert.deepEqual(calls.filter(c => c.type.endsWith("/select")), [
    {type:"battery_charge_manager/select",battery_id:"battery-2"},
    {type:"battery_charge_manager/select",quantity:3},
  ]);
  assert.match(panel.renderHome(true), /data-home-disclosure="calibration" open/);
});

test("busy starts stay on the current page and empty profiles cannot start calibration", async () => {
  const panel = homePanel();
  panel._busy = true;
  panel._tab = "idle";
  panel._hass.callWS = async () => { assert.fail("must not send a command while busy"); };
  await panel.handleAction("idle-fixed");
  assert.equal(panel._tab, "idle");
  panel._state.batteries = [];
  assert.match(panel.renderCalibrationStart(true), /data-action="start-calibration" disabled/);
});

test("a late selection error preserves a newly opened edit form and its focus", async () => {
  const panel = homePanel();
  let rejectSelection;
  panel._hass.callWS = () => new Promise((resolve, reject) => { rejectSelection = reject; });
  const selection = panel.updateSelection({battery_id:"battery-2"});
  panel._tab = "batteries";
  panel._dialog = "battery";
  panel._draft = {name:"Uncommitted name"};
  panel.shadowRoot.activeElement = {matches: selector => selector === "input, select, textarea"};
  panel.shadowRoot.innerHTML = "editing form";
  rejectSelection(new Error("Selection rejected"));
  await selection;
  assert.equal(panel.shadowRoot.innerHTML, "editing form");
  assert.equal(panel._draft.name, "Uncommitted name");
  assert.match(panel._error, /Selection rejected/);
  assert.equal(panel._renderPending, true);
});

test("pending selection immediately disables existing operational controls even with deferred rendering", async () => {
  const panel = homePanel();
  const battery = {id:"bcm-battery",disabled:false,matches:selector => selector === "input, select, textarea"};
  const quantity = {disabled:false};
  const start = {disabled:false};
  let batteryDisabled = false;
  let restoredFocus = null;
  Object.defineProperty(battery, "disabled", {
    get() { return batteryDisabled; },
    set(value) { batteryDisabled = value; if (value) panel.shadowRoot.activeElement = null; },
  });
  panel.shadowRoot.getElementById = id => ({focus() { restoredFocus = id; }});
  panel.shadowRoot.activeElement = battery;
  panel.shadowRoot.querySelectorAll = selector => selector.includes('[data-action="start-charge"]') ? [battery,quantity,start] : [];
  let finishSelection;
  let commands = 0;
  panel._hass.callWS = command => {
    if (command.type.endsWith("get_state")) return Promise.resolve(panel._state);
    commands += 1;
    return new Promise(resolve => { finishSelection = resolve; });
  };
  const selection = panel.updateSelection({battery_id:"battery-2"});
  assert.equal(panel._busy, true);
  assert.equal(battery.disabled, true);
  assert.equal(quantity.disabled, true);
  assert.equal(start.disabled, true);
  await panel.updateSelection({battery_id:"battery-3"});
  assert.equal(commands, 1);
  finishSelection({});
  await selection;
  assert.equal(panel._busy, false);
  assert.equal(restoredFocus, "bcm-battery");
  assert.match(panel.shadowRoot.innerHTML, /data-select="battery" >|data-select="battery"\s*>/);
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

test("new battery form leaves technical numeric fields empty and clarifies output voltage", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  panel._state = panelState();
  panel._dialog = "battery";
  panel._draft = {};

  const html = panel.renderDialog(true);

  assert.match(html, /Nennspannung \(Ausgangsspannung\) \(V\)/);
  assert.match(html, /data-draft="nominal_capacity_mah"[^>]*value=""/);
  assert.match(html, /data-draft="rest_time_minutes"[^>]*value=""/);
  assert.match(html, /data-image-upload="battery"/);
});

test("charging setup form supports image upload", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true }, states: {} };
  panel._state = panelState();
  panel._dialog = "setup";
  panel._draft = {};

  const html = panel.renderDialog(true);

  assert.match(html, /data-image-upload="setup"/);
  assert.match(html, /data-draft="image"/);
});

test("save flow suppresses intermediate dialog rerender and closes once", async () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true } };
  panel._state = panelState();
  panel._dialog = "battery";
  panel._draft = { name: "Test", nominal_capacity_mah: "1700" };
  const renderedDialogStates = [];
  panel.render = () => renderedDialogStates.push(panel._dialog);
  panel.call = async () => {
    panel._requestRender();
    return {};
  };

  await panel.handleAction("save-battery");

  assert.deepEqual(renderedDialogStates, [null]);
});

test("dialog rerender preserves vertical scroll position", () => {
  const Panel = customElements.get("battery-charge-manager-panel");
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: true }, states: {} };
  panel._state = panelState();
  panel._dialog = "battery";
  panel._draft = { name: "Test", nominal_capacity_mah: 1700 };

  panel.render();
  panel.shadowRoot.querySelector(".bcm-dialog").scrollTop = 420;
  panel.render();

  assert.equal(panel.shadowRoot.querySelector(".bcm-dialog").scrollTop, 420);
});
