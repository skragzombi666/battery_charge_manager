import assert from 'node:assert/strict';
import test from 'node:test';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
globalThis.HTMLElement = class {attachShadow(){return this.shadowRoot={innerHTML:'',addEventListener(){},querySelector(){return null;},querySelectorAll(){return [];}};}};
globalThis.customElements = {registry:new Map(),get(n){return this.registry.get(n);},define(n,v){this.registry.set(n,v);}};
globalThis.window = {customCards:[]};
const frontend=await import(pathToFileURL(resolve('custom_components/battery_charge_manager/frontend/battery-charge-manager.js')));
const Panel=customElements.get('battery-charge-manager-panel');
function panel(changes={}) {
 const p=new Panel();p._hass={language:'de',states:{},user:{is_admin:true}};
 p._state={setups:[{setup_id:'s',name:'Standard',power_sensor:'sensor.power',port_labels:['A']}],batteries:[{battery_id:'b',name:'Xnergy'}],selected_setup_id:'s',selected_battery_id:'b',selected_quantity:1,
  session:{mode:'calibrating',setup_id:'s',battery_id:'b',quantity:1,ports:['A'],phase:'main_charge',energy_source:'meter',source_decision:{mode:'auto'},elapsed_seconds:5940,
   gross_energy_wh:0,net_energy_wh:0,idle_baseline_power_w:0,idle_energy_wh:0,power_sensor_configured:true,
   metering:{meter_wh:0,power_wh:.2,power_estimate_wh:3.16,power_valid:false},...changes}};
 return p;
}
const tile=(html,kind)=>html.replace(/<details\b[\s\S]*?<\/details>/g, "").match(new RegExp(`<section[^>]+data-energy-kind="${kind}"[\\s\\S]*?</section>`))?.[0] || '';
test('both gross and net tiles show both sources even in fixed modes',()=>{
 for(const mode of ['auto','meter','power']) {
  const p=panel({source_decision:{mode}}),html=p.renderCalibrationSession(true);
  for(const kind of ['gross','net']) {
   const t=tile(html,kind);assert.ok(t,kind+' energy tile');
   assert.match(t,/Energiezähler/);assert.match(t,/Leistungsintegration/);
   assert.match(t,/0\.000 Wh/);assert.match(t,/3\.160 Wh/);assert.match(t,/geschätzt/);
  }
 }
});
test('a nonzero baseline is subtracted from each gross path separately',()=>{
 const p=panel({idle_baseline_power_w:.1,idle_energy_wh:.16,metering:{meter_wh:4,power_wh:3.36,power_estimate_wh:3.36,power_valid:true},metering_comparison:{power_complete:true}});
 const html=p.renderCalibrationSession(true);
 assert.match(tile(html,'gross'),/4\.000 Wh/);assert.match(tile(html,'gross'),/3\.360 Wh/);
 assert.match(tile(html,'net'),/3\.840 Wh/);assert.match(tile(html,'net'),/3\.200 Wh/);
 assert.match(tile(html,'net'),/vollständig/);assert.doesNotMatch(tile(html,'net'),/geschätzt/);
});
test('missing integration is not presented as zero energy',()=>{
 const p=panel({power_sensor_configured:false,metering:{meter_wh:0,power_wh:0,power_estimate_wh:0,power_valid:false}});
 const t=tile(p.renderCalibrationSession(true),'gross');
 assert.match(t,/data-energy-source="power"[\s\S]*?–/);
 assert.match(t,/nicht verfügbar/);
});
test('unknown idle correction does not pretend net equals gross',()=>{
 const p=panel({idle_baseline_power_w:null});const html=p.renderCalibrationSession(true);
 assert.match(tile(html,'gross'),/3\.160 Wh/);
 assert.match(tile(html,'net'),/Leerlaufkorrektur ausstehend/);
 assert.doesNotMatch(tile(html,'net'),/3\.160 Wh/);
});
test('source mode and actual selection are separate from displayed measurement paths',()=>{
 const p=panel();let html=p.parallelLive(p._state.session);
 assert.match(html,/Automatische Auswahl/);assert.match(html,/nach Abschluss/);
 assert.doesNotMatch(html,/Verwendete Energiequelle[^<]*:[\s\S]*?Energiezähler/);
 p._state.session.mode='charging';p._state.session.energy_source='power';
 html=p.parallelLive(p._state.session);
 assert.match(html,/Verwendete Energiequelle/);assert.match(html,/Leistungsintegration/);
 assert.doesNotMatch(html,/Entscheidung nach Abschluss/);
});
test('live comparison includes the same estimate as tiles and the accepted partial separately',()=>{
 const p=panel();const html=p.parallelLive(p._state.session);
 assert.match(html,/3\.160 Wh/);assert.match(html,/0\.200 Wh/);
 assert.match(html,/Teilwert/);assert.match(html,/Kein Zählerzuwachs/);
});
test('normal charging also shows both sources without changing its target',()=>{
 const p=panel({mode:'charging',energy_source:'power',target_energy_wh:4,progress_percent:5});
 const html=p.renderChargeSession();assert.match(tile(html,'gross'),/3\.160 Wh/);
 assert.match(tile(html,'net'),/0\.000 Wh/);assert.equal(p._state.session.target_energy_wh,4);
});
test('charts use professional source names and retain uncertainty',()=>{
 const chart_samples=[{timestamp:'2026-09-23T18:00:00Z',meter_energy_wh:0,power_estimate_wh:0,power_integral_valid:false},
  {timestamp:'2026-09-23T19:39:00Z',meter_energy_wh:0,power_estimate_wh:3.16,power_integral_valid:false}];
 const html=frontend.renderSessionChart({chart_samples},'calibrating','de');
 assert.match(html,/Energiezähler/);assert.match(html,/Leistungsintegration/);assert.match(html,/3\.16 Wh/);
 assert.doesNotMatch(html,/W\/Zeit|Wh-Zähler/);assert.match(html,/stroke-dasharray/);
});


test('historical tiles retain both source-matched gross values at the endpoint',()=>{
 const p=panel();
 const record={energy_source:'power',gross_energy_wh:3.4,net_energy_wh:3.2,
  idle_baseline_power_w:.1,idle_energy_wh:.2,idle_correction_status:'applied',
  metering_comparison:{meter_gross_wh:0,power_gross_wh:3.4,power_estimate_gross_wh:3.4,
   power_complete:true, meter_net_wh:0,power_net_wh:3.2}};
 assert.match(p.energyMetric('gross',record),/3\.400 Wh/);
 assert.match(p.energyMetric('gross',record),/0\.000 Wh/);
 assert.match(p.energyMetric('net',record),/3\.200 Wh/);
 assert.match(p.energyMetric('net',record),/0\.000 Wh/);
 assert.equal(record.metering_comparison.meter_gross_wh,0);
});

test('calibration without idle reference labels chart energy as gross',()=>{
 const p=panel({idle_baseline_power_w:null,chart_samples:[
  {timestamp:'2026-09-23T18:00:00Z',meter_energy_wh:0,power_estimate_wh:0},
  {timestamp:'2026-09-23T19:00:00Z',meter_energy_wh:0,power_estimate_wh:2} ]});
 assert.match(p.renderCalibrationSession(true),/Energiezähler \(brutto\)/);
 assert.doesNotMatch(p.renderCalibrationSession(true),/Energiezähler \(netto\)/);
});
