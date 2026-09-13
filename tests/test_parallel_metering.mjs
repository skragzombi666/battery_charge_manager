import assert from 'node:assert/strict';
import test from 'node:test';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
globalThis.HTMLElement = class { attachShadow() { return this.shadowRoot = { innerHTML:'', addEventListener(){}, querySelector(){return null;}, querySelectorAll(){return [];} }; } };
globalThis.customElements = { registry:new Map(), get(n){return this.registry.get(n);}, define(n,v){this.registry.set(n,v);} };
globalThis.window = {customCards:[]};
await import(pathToFileURL(resolve('custom_components/battery_charge_manager/frontend/battery-charge-manager.js')));
const Panel = customElements.get('battery-charge-manager-panel');
function panel(){const p=new Panel();p._hass={language:'de',states:{},user:{is_admin:true}};p._state={session:{mode:'idle'},setups:[],batteries:[]};return p;}
test('parallel comparison labels apparent energy as diagnostic and does not promise accuracy',()=>{
 const html=panel().meteringComparison({meter_net_wh:6,power_net_wh:5.5,apparent_energy_vah:15,meter_step_wh:1,power_step_wh:.03,coverage_percent:100,power_eligible:true,reason:'usable'});
 assert.match(html,/VAh/);assert.match(html,/Plausibilität/);assert.match(html,/5[.,]500/);assert.match(html,/6[.,]000/);assert.match(html,/Genauigkeit/);
});
test('source selection exposes reason and frozen live source',()=>{
 const p=panel();const html=p.meteringDecision({source:'power',reason:'finer_repeatable_power',count:3});
 assert.match(html,/Wirkleistung/);assert.match(html,/wiederholbar/);
 const live=p.parallelLive({energy_source:'power',metering:{meter_wh:2,power_wh:1.9,apparent_vah:4,apparent_valid:true}});
 assert.match(live,/VAh/);assert.match(live,/Wirkleistung/);
});
test('setup has optional voltage and RMS current selectors and blank values stay null',()=>{
 const p=panel();p._dialog='setup';p._draft={};
 const html=p.renderDialog(true);
 assert.match(html,/data-draft="voltage_sensor"/);assert.match(html,/data-draft="current_sensor"/);assert.match(html,/Effektivstrom/);
 p._draft={voltage_sensor:'',current_sensor:''};const d=p.normalizeDraft('setup');
 assert.equal(d.voltage_sensor,null);assert.equal(d.current_sensor,null);
});
