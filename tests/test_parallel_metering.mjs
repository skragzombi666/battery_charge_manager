import assert from 'node:assert/strict';
import test from 'node:test';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
globalThis.HTMLElement = class { attachShadow() { return this.shadowRoot = { innerHTML:'', addEventListener(){}, querySelector(){return null;}, querySelectorAll(){return [];} }; } };
globalThis.customElements = { registry:new Map(), get(n){return this.registry.get(n);}, define(n,v){this.registry.set(n,v);} };
globalThis.window = {customCards:[]};
const { renderSessionChart } = await import(pathToFileURL(resolve('custom_components/battery_charge_manager/frontend/battery-charge-manager.js')));
const Panel = customElements.get('battery-charge-manager-panel');
function panel(){const p=new Panel();p._hass={language:'de',states:{},user:{is_admin:true}};p._state={session:{mode:'idle'},setups:[],batteries:[]};return p;}
test('parallel comparison labels apparent energy as diagnostic and does not promise accuracy',()=>{
 const html=panel().meteringComparison({meter_net_wh:6,power_net_wh:5.5,apparent_energy_vah:15,meter_step_wh:1,power_step_wh:.03,coverage_percent:100,power_eligible:true,reason:'usable'});
 assert.match(html,/VAh/);assert.match(html,/Plausibilität/);assert.match(html,/5[.,]500/);assert.match(html,/6[.,]000/);assert.match(html,/Genauigkeit/);
});
test('source selection exposes reason and frozen live source',()=>{
 const p=panel();const html=p.meteringDecision({source:'power',reason:'finer_repeatable_power',count:3});
 assert.match(html,/Leistungsintegration/);assert.match(html,/wiederholbar/);
 const live=p.parallelLive({energy_source:'power',metering:{meter_wh:2,power_wh:1.9,apparent_vah:4,apparent_valid:true}});
 assert.match(live,/VAh/);assert.match(live,/Leistungsintegration/);
});
test('setup has optional voltage and RMS current selectors and blank values stay null',()=>{
 const p=panel();p._dialog='setup';p._draft={};
 const html=p.renderDialog(true);
 assert.match(html,/data-draft="voltage_sensor"/);assert.match(html,/data-draft="current_sensor"/);assert.match(html,/Effektivstrom/);
 p._draft={voltage_sensor:'',current_sensor:''};const d=p.normalizeDraft('setup');
 assert.equal(d.voltage_sensor,null);assert.equal(d.current_sensor,null);
});

test('counter and W/time curves retain separate net values on the same energy scale',()=>{
 const chart_samples=[
  {timestamp:'2026-09-14T00:00:00Z',net_power_w:2,meter_energy_wh:0,power_energy_wh:0,power_integral_valid:true},
  {timestamp:'2026-09-14T02:00:00Z',chart_gap_before:false,net_power_w:0,meter_energy_wh:6,gross_energy_wh:5.8,power_energy_wh:5.8,idle_energy_wh:.2,power_integral_valid:true},
 ];
 const html=renderSessionChart({chart_samples},'calibrating','de');
 for(const series of ['power','energy','power-energy']) assert.match(html,new RegExp(`data-series="${series}"`));
 assert.match(html,/Energiezähler \(netto\) · max 5\.80 Wh/);
 assert.match(html,/Leistungsintegration · 5\.60 Wh/);
 assert.doesNotMatch(html,/stroke-dasharray/,'display thinning must not turn valid integration into uncertainty');
 const meterEnd=html.match(/class="bcm-chart-energy"[^>]*points="[^"]* ([0-9.]+),([0-9.]+)"/);
 const integratedEnd=html.match(/class="bcm-chart-power-energy"[^>]*points="[^"]* ([0-9.]+),([0-9.]+)"/);
 assert.equal(meterEnd[1], integratedEnd[1]);
 assert.ok(Number(meterEnd[2]) < Number(integratedEnd[2]),'larger counter total is higher on the shared Wh scale');
 chart_samples[1].power_estimate_wh=6.5;
 chart_samples[1].power_integral_valid=false;
 const uncertain=renderSessionChart({chart_samples},'calibrating','de');
 assert.match(uncertain,/stroke-dasharray/);
 assert.match(uncertain,/Leistungsintegration · 6\.30 Wh/);
 assert.match(uncertain,/kein bestätigter Energieverbrauch/);
});

test('settings show all modes, preserve persisted selection, and submit the new choice',async()=>{
 const p=panel();p._state.energy_mode='meter';p._state.max_session_hours=12;
 const html=p.renderSettings(true);
 for(const mode of ['auto','meter','power']) assert.match(html,new RegExp(`<option value="${mode}"`));
 assert.match(html,/<option value="meter" selected>/);
 p._formValues.energyMode='power';
 p.shadowRoot.getElementById=()=>({value:'12',min:'1',max:'48',dataset:{formValue:'maxSession'}});
 let submitted;p.call=async(command,args)=>{submitted={command,args};};
 await p.handleAction('save-settings');
 assert.deepEqual(submitted,{command:'set_settings',args:{max_session_hours:12,energy_mode:'power'}});
 assert.doesNotMatch(p.renderSettings(false),/data-action="save-settings"/);
});
