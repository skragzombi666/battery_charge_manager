import assert from 'node:assert/strict';
import test from 'node:test';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
globalThis.HTMLElement=class{attachShadow(){return this.shadowRoot={innerHTML:'',addEventListener(){},querySelector(){return null;},querySelectorAll(){return[];}};}};
globalThis.customElements={registry:new Map(),get(n){return this.registry.get(n);},define(n,v){this.registry.set(n,v);}};
globalThis.window={customCards:[]};
const {renderSessionChart}=await import(pathToFileURL(resolve('custom_components/battery_charge_manager/frontend/battery-charge-manager.js')));
const Panel=customElements.get('battery-charge-manager-panel');
function panel(){const p=new Panel();p._hass={language:'de',user:{is_admin:true}};p._state={session:{mode:'idle'},calibrations:[],idle_measurements:[],rest_measurements:[],setups:[],batteries:[],energy_mode:'power_reported',energy_basis:'gross'};return p;}

test('pending invalid rest exposes do-not-use while explaining blocked approval',()=>{
 const p=panel(), item={measurement_id:'r',valid:false,usage_approval:'pending',usage_approval_block_reason:'invalid_measurement'};
 const html=p.recordActions(item,'rest',true,true);
 assert.match(html,/<button[^>]*data-record-action="revoke-use"[^>]*>Nicht verwenden<\/button>/);
 assert.doesNotMatch(html,/<button[^>]*data-record-action="revoke-use"[^>]*disabled/);
 assert.match(html,/<button[^>]*data-record-action="approve-use"[^>]*disabled/);
 assert.match(html,/Ungültige Messungen können nicht freigegeben werden/);
});
test('pending usable calibration offers both review decisions and revoked review has a final badge',()=>{
 const p=panel(), item={calibration_id:'c',valid:true,usage_approval:'pending',usage_approval_block_reason:null};
 const html=p.recordActions(item,'calibration',true,true);
 assert.match(html,/data-record-action="approve-use"/);assert.match(html,/data-record-action="revoke-use"/);
 assert.doesNotMatch(html,/disabled/);
 const badge=p.usageBadge({...item,usage_approval:'revoked',usage_reason:'revoked'});
 assert.match(badge,/Geprüft · nicht zur Verwendung freigegeben/);assert.doesNotMatch(badge,/ausstehend/);
 assert.doesNotMatch(p.recordActions({...item,usage_approval:'revoked'},'calibration',true,true),/data-record-action="revoke-use"/);
});
test('do-not-use submits an explicit negative decision for an invalid pending measurement',async()=>{
 const p=panel();p._measurementDetail={record_type:'rest',measurement_id:'r',valid:false,analysis_revision:1,usage_revision:2,decision_fingerprint:'trace',usage_approval:'pending'};
 p._recordDecision='revoke-use';p._decisionReason='Only a test';const calls=[];p.call=async(c,args)=>calls.push([c,args]);
 await p.confirmMeasurementDecision();assert.deepEqual(calls[0],['set_usage_approval',{record_type:'rest',record_id:'r',approved:false,reason:'Only a test',expected_analysis_revision:1,expected_fingerprint:'trace',expected_usage_revision:2}]);
});
test('rejected pilot review does not keep asking to review use in its completion banner',()=>{
 const p=panel();
 const html=p.completionBadge({completion_status:'pending_review',usage_approval:'revoked'});
 assert.match(html,/Beendet · Messdaten erhalten/);assert.doesNotMatch(html,/Verwendung prüfen/);
 assert.match(p.completionBadge({completion_status:'pending_review',usage_approval:'pending'}),/Verwendung prüfen/);
});

test('pilot source and gross or no-load-corrected basis are explicit settings',()=>{
 const html=panel().renderSettings(true);assert.match(html,/value="power_reported"/);assert.match(html,/data-form-value="energyBasis"/);assert.match(html,/value="gross"/);
});
test('full battery preparation has separate confirmation and no-load distinction',()=>{
 const p=panel();p._state.session={mode:'rest_measuring',pilot:{confirmed_at:null},chart_samples:[]};
 const html=p.renderHome(true);assert.match(html,/confirm-rest/);assert.match(html,/Nachladung/);assert.doesNotMatch(html,/data-action="start-charge"/);
});
test('held power is drawn dashed while counter remains continuous on independent axes',()=>{
 const channels={power:{gap_before:false,held:true},meter:{gap_before:false,held:false},integration:{gap_before:false,held:true}};
 const samples=[0,30].map((s,i)=>({timestamp:new Date(Date.UTC(2026,0,1,0,0,s)).toISOString(),power_w:1,net_power_w:1,meter_energy_wh:i,power_estimate_wh:i*.5,chart_channels:channels,chart_gap_before:true}));
 const html=renderSessionChart({chart_samples:samples,idle_baseline_power_w:0},'calibrating','de');
 assert.match(html,/data-axis="power"/);assert.match(html,/data-axis="energy"/);
 assert.match(html,/<polyline class="bcm-chart-power" stroke-dasharray/);assert.match(html,/<polyline class="bcm-chart-energy"/);
});
test('proposal is presented for review without claiming known charge duration',()=>{
 const p=panel();p._state.session={mode:'calibrating',energy_source:'power_reported',pilot:{energy_basis:'gross',proposal:{status:'suggested',endpoint_at:'2026-01-01T01:00:00Z'}}};
 const html=p.renderCalibrationSession(true);assert.match(html,/Restphase passend/);assert.match(html,/Beenden und prüfen/);
});
test('use approval uses its own API and optimistic analysis revision',async()=>{
 const p=panel();p._measurementDetail={record_type:'calibration',calibration_id:'r',analysis_revision:4,usage_approval:'pending'};p._recordDecision='approve-use';p._decisionReason='Kurve und USB geprüft';
 const calls=[];p.call=async(c,args)=>calls.push([c,args]);p.openMeasurement=async()=>{};
 await p.confirmMeasurementDecision();assert.equal(calls[0][0],'set_usage_approval');assert.equal(calls[0][1].expected_analysis_revision,4);assert.equal(calls[0][1].approved,true);assert.equal(calls[0][1].expected_usage_revision,0);
});
test('rest details show weighted statistics and review actions',()=>{
 const p=panel();p._measurementDetail={record_type:'rest',measurement_id:'r',statistics:{mean_power_w:.08,block_means_w:[.07,.08,.09],eligible:true,held_seconds:100},valid:true,analysis_revision:1,usage_approval:'pending',chart_samples:[]};
 const html=p.renderMeasurementDialog(true);assert.match(html,/0\.080 W/);assert.match(html,/approve-use/);assert.match(html,/Restverbrauch/);
});
