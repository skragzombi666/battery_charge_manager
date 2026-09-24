import assert from 'node:assert/strict';
import test from 'node:test';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
globalThis.HTMLElement=class{attachShadow(){return this.shadowRoot={innerHTML:'',addEventListener(){},querySelector(){return null;},querySelectorAll(){return[];}};}};
globalThis.customElements={registry:new Map(),get(n){return this.registry.get(n);},define(n,v){this.registry.set(n,v);}};
globalThis.window={customCards:[]};
const {renderSessionChart}=await import(pathToFileURL(resolve('custom_components/battery_charge_manager/frontend/battery-charge-manager.js')));
const Panel=customElements.get('battery-charge-manager-panel');
function panel(){const p=new Panel();p._hass={language:'de',user:{is_admin:true}};p._state={entry_id:'entry',archive_available:true,session:{mode:'idle'},calibrations:[],idle_measurements:[],setups:[],batteries:[]};return p;}
function record(){return{calibration_id:'cal',record_type:'calibration',completion_status:'aborted',calibration_eligible:false,valid:false,
 setup_snapshot:{},battery_snapshot:{nominal_energy_wh:3},quantity:1,idle_baseline_power_w:.1,idle_energy_wh:1,idle_correction_status:'applied',analysis_revision:1,endpoint_editable:true,
 chart_samples:[],metering_comparison:{meter_gross_wh:0,power_gross_wh:1.35,power_estimate_gross_wh:5.75,power_net_wh:1.25,power_estimate_net_wh:4.85,meter_net_wh:0,power_complete:false},
 analysis_summary:{total:{meter_gross_wh:0,power_estimate_gross_wh:5.75},charge:null,post_charge:null,nominal:{total_wh:3,input_to_nominal_ratio:null}}};}

test('partial integration uses its own accepted-time idle correction',()=>{
 const p=panel(),r=record();delete r.metering_comparison.power_estimate_gross_wh;delete r.metering_comparison.power_estimate_net_wh;
 const html=p.energyMetric('net',r);assert.match(html,/1\.250 Wh/);assert.doesNotMatch(html,/0\.350 Wh/);
});
test('excluded attempts show status and both sources, not zero calibration result',()=>{
 const p=panel();const html=p.historyTable([record()],true,'calibration');
 assert.match(html,/Abgebrochen/);assert.match(html,/Leistungsintegration/);assert.match(html,/5\.750 Wh|4\.850 Wh/);
 assert.match(html,/Energiezähler/);
});
test('endpoint boundary editor includes reason and no implicit approval',()=>{
 const p=panel();p._measurementDetail=record();const html=p.renderMeasurementDialog(true);
 assert.match(html,/data-endpoint-time/);assert.match(html,/data-endpoint-reason/);assert.match(html,/save-endpoint/);
 assert.match(html,/keine Freigabe/);assert.match(html,/Gesamtvorgang/);assert.match(html,/Nachlauf/);assert.match(html,/Nennenergie/);
});
test('large archive download uses signed authenticated URL instead of a raw websocket Blob',async()=>{
 const p=panel();const calls=[],links=[];p._hass.callWS=async payload=>{calls.push(payload);return{path:'/api/battery_charge_manager/export/entry?authSig=test'};};p._hass.hassUrl=x=>'https://ha.example'+x;
 globalThis.document={createElement(){const l={click(){links.push(this.href);},remove(){}};return l;},body:{appendChild(){}}};
 await p.exportAllMeasurements();assert.equal(calls[0].type,'auth/sign_path');assert.equal(calls[0].path,'/api/battery_charge_manager/export/entry');assert.equal(calls.length,1);assert.match(links[0],/^https:\/\/ha.example\/api\//);
});
test('gap chart does not connect endpoints across absent raw power',()=>{
 const samples=[{timestamp:'2026-09-23T18:00:00Z',power_w:2,net_power_w:2,chart_gap_before:false},
 {timestamp:'2026-09-23T20:00:00Z',power_w:.2,net_power_w:.2,chart_gap_before:true}];
 const html=renderSessionChart({chart_samples:samples,peak_net_power_w:2.3,idle_baseline_power_w:0},'calibrating','de');
 assert.match(html,/Datenlücke/);assert.doesNotMatch(html,/<polyline[^>]*class="bcm-chart-power"/);assert.match(html,/max 2\.30 W/);
});
test('manual endpoint request has explicit optimistic revision and reason',async()=>{
 const p=panel();p._measurementDetail=record();p._endpointTime='2026-09-23T20:30:00';p._endpointReason='Externes Ladeende';
 const calls=[];p.call=async(c,args)=>calls.push([c,args]);p.openMeasurement=async()=>{};
 assert.equal(typeof p.saveEndpoint,'function');await p.saveEndpoint();
 assert.equal(calls[0][0],'set_calibration_endpoint');assert.equal(calls[0][1].expected_analysis_revision,1);assert.equal(calls[0][1].reason,'Externes Ladeende');
});
test('raw inspector loads bounded pages without losing original precision',async()=>{
 const p=panel();p._measurementDetail=record();let args;
 p._hass.callWS=async a=>{args=a;return{sample_count:100001,offset:0,next_offset:100,samples:[{timestamp:'2026-01-01T00:00:00Z',power_w:1.234567890123,provenance:{source:'state_reported'}}]};};
 assert.equal(typeof p.loadRawPage,'function');await p.loadRawPage(0);
 assert.equal(args.type,'battery_charge_manager/get_raw_samples');assert.equal(args.limit,100);
 const html=p.renderRawInspector(p._measurementDetail,true);assert.match(html,/1\.234567890123/);assert.match(html,/100001/);assert.match(html,/raw-next/);
});
test('live calibration exposes the separate energy intervals',()=>{
 const p=panel();p._state.session={...record(),mode:'calibrating',phase:'undetermined'};
 const html=p.renderCalibrationSession(true);assert.match(html,/Gesamtvorgang/);assert.match(html,/Nachlauf/);assert.match(html,/Nicht bestimmbar/);
});
test('historical chart net values follow revised baseline without altering raw input',()=>{
 const samples=[{timestamp:'2026-09-23T18:00:00Z',power_w:2,net_power_w:2,idle_energy_wh:0,meter_energy_wh:0,chart_gap_before:false},
 {timestamp:'2026-09-23T19:00:00Z',power_w:2,net_power_w:2,idle_energy_wh:0,meter_energy_wh:3,chart_gap_before:false}];
 const before=structuredClone(samples);
 const html=renderSessionChart({chart_samples:samples,switch_on_at:samples[0].timestamp,idle_baseline_power_w:1},'calibrating','de');
 assert.match(html,/max 1\.00 W/);assert.match(html,/max 2\.00 Wh/);assert.deepEqual(samples,before);
});
test('calibration summary translates trend and quality instead of exposing internal enums',()=>{
 const p=panel();p.renderCalibrationStart=()=>'';p._state.active_calibration_summary={trend:'not_assessable',quality:'none',source_decision:{source:null}};
 let html=p.renderCalibrations(true);assert.match(html,/Nicht beurteilbar/);assert.doesNotMatch(html,/not_assessable/);
 p._state.active_calibration_summary={trend:'increasing',quality:'stable',source_decision:{source:null}};
 html=p.renderCalibrations(true);assert.match(html,/Zunehmend/);assert.match(html,/Stabil/);assert.doesNotMatch(html,/>increasing</);
});
