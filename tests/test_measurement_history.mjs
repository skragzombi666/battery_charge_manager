import assert from "node:assert/strict";
import test from "node:test";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

globalThis.HTMLElement = class {
  attachShadow() {
    return this.shadowRoot = {
      innerHTML: "", addEventListener() {}, querySelector() { return null; },
      querySelectorAll() { return []; }, activeElement: null,
    };
  }
};
globalThis.customElements = {
  registry: new Map(), get(name) { return this.registry.get(name); },
  define(name, value) { this.registry.set(name, value); },
};
globalThis.window = { customCards: [] };
await import(pathToFileURL(resolve("custom_components/battery_charge_manager/frontend/battery-charge-manager.js")));
const Panel = customElements.get("battery-charge-manager-panel");

const detail = (overrides = {}) => ({
  record_type: "calibration", calibration_id: "cal", setup_id: "setup", battery_id: "battery",
  setup_revision: 1, battery_revision: 1, current_setup_revision: 2, current_battery_revision: 3,
  revision_status: "historical", used: false, usage_reason: "historical", valid: true,
  confidence: "low", quantity: 1, ports: ["A"], can_approve: true,
  net_energy_wh: 3, gross_energy_wh: 3.2, idle_energy_wh: 0.2, idle_correction_status: "applied",
  setup_snapshot: { name: "Charger" }, battery_snapshot: { name: "AA" },
  current_setup_snapshot: { name: "Charger", revision: 2 },
  current_battery_snapshot: { name: "AA", revision: 3 },
  revision_differences: [], validity_history: [], revision_approvals: [], analysis_history: [], idle_sources: [],
  chart_samples: [
    { timestamp: "2026-09-01T10:00:00Z", power_w: 3.2, net_power_w: 3, gross_energy_wh: 0, net_energy_wh: 0 },
    { timestamp: "2026-09-01T11:00:00Z", power_w: 0.2, net_power_w: 0, gross_energy_wh: 3.2, net_energy_wh: 3 },
  ],
  ...overrides,
});

function panel(admin = true) {
  const p = new Panel();
  p._hass = { language: "de", user: { is_admin: admin } };
  p._tab = "idle";
  p._state = { setups: [{ setup_id: "setup", revision: 2, port_labels: ["A"] }], batteries: [],
    selected_setup_id: "setup", session: { mode: "idle" }, active_idle_summary: {},
    idle_measurements: [], calibrations: [], selected_quantity: 1 };
  return p;
}

test("a valid low-confidence calibration is green with separate confidence and use", () => {
  const html = panel().calibrationTable([detail({ usage_reason: "lower_confidence" })], true);
  assert.match(html, /bcm-badge good[^>]*>gültig/);
  assert.match(html, /niedrig/);
  assert.match(html, /höherem Vertrauen/);
  assert.match(html, /Revision 1/);
  assert.match(html, /Details/);
  assert.match(html, /Als ungültig markieren/);
});

test("historical details and curves can be opened by non-admin users", () => {
  const p = panel(false);
  p._dialog = "measurement";
  p._measurementDetail = detail();
  const html = p.renderDialog(false);
  assert.match(html, /data-series="power"/);
  assert.match(html, /data-series="energy"/);
  assert.match(html, /Ursprüngliche Revision/);
  assert.match(html, /Aktuelle Revision/);
  assert.doesNotMatch(html, /data-action="confirm-measurement"/);
});

test("missing historical samples display a permanent absence message", () => {
  const p = panel();
  p._dialog = "measurement";
  p._measurementDetail = detail({ chart_samples: [], legacy: true });
  const html = p.renderDialog(true);
  assert.match(html, /Keine Messkurve gespeichert/);
  assert.doesNotMatch(html, /Messkurve wird aufgebaut/);
});

test("approval sends the reviewed revision pair and reason only after equivalence confirmation", async () => {
  const p = panel();
  p._dialog = "measurement";
  p._measurementDetail = detail();
  p._recordDecision = "approve";
  p._decisionReason = "Nur Beschreibung korrigiert";
  const commands = [];
  p._hass.callWS = async (payload) => {
    commands.push(payload);
    if (payload.type.endsWith("get_state")) return p._state;
    if (payload.type.endsWith("get_measurement")) return detail({ revision_status: "approved" });
    return {};
  };
  await p.handleAction("confirm-measurement");
  assert.equal(commands.length, 0);
  p._decisionConfirmed = true;
  await p.handleAction("confirm-measurement");
  assert.deepEqual(commands[0], {
    type: "battery_charge_manager/set_measurement_revision_approval", record_type: "calibration",
    record_id: "cal", approved: true, reason: "Nur Beschreibung korrigiert",
    expected_setup_revision: 2, expected_battery_revision: 3,
  });
});

test("closing a loading detail does not reopen it when the request finishes", async () => {
  const p = panel();
  let finish;
  p._hass.callWS = () => new Promise((resolve) => { finish = resolve; });
  const request = p.openMeasurement("calibration", "cal");
  await p.handleAction("close-dialog");
  finish(detail());
  await request;
  assert.equal(p._dialog, null);
});

test("a decision is blocked after the record changes while its dialog is open", async () => {
  const p = panel();
  p._dialog = "measurement";
  p._measurementDetail = detail();
  p._state.calibrations = [detail({ current_battery_revision: 4 })];
  p._recordDecision = "approve";
  p._decisionConfirmed = true;
  p._decisionReason = "Description corrected";
  const commands = [];
  p._hass.callWS = async (command) => {
    commands.push(command);
    return command.type.endsWith("get_measurement") ? detail() : p._state;
  };
  await p.confirmMeasurementDecision();
  assert.equal(commands.length, 0);
  assert.match(p._error, /Details aktualisieren/);
});

test("an in-flight subscription is disposed when the element disconnects", async () => {
  const p = panel();
  let finish;
  let unsubscribed = 0;
  p._hass.callWS = async () => p._state;
  p._hass.connection = { subscribeMessage: () => new Promise(resolve => { finish = resolve; }) };
  const connecting = p._connect();
  await Promise.resolve();
  p.disconnectedCallback();
  finish(() => { unsubscribed += 1; });
  await connecting;
  assert.equal(unsubscribed, 1);
  assert.equal(p._unsub, null);
});

test("an unstable idle baseline visibly blocks ordinary charging", () => {
  const p = panel();
  p._state.batteries = [{ battery_id:"battery", name:"AA" }];
  p._state.active_calibration_summary = { median_net_energy_wh:3, quality:"stable" };
  p._state.active_idle_summary = { usable:false, quality:"unstable", reliable_count:2 };
  const html = p.renderCharge();
  assert.match(html, /data-action="start-charge" disabled/);
  assert.match(html, /widersprüchliche Messungen prüfen/);
});
