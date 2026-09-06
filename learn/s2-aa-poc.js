'use strict';
const $=s=>document.querySelector(s);
let scale=1,manifest,active;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function zoom(n){scale=Math.max(.12,Math.min(2.5,n));$('#diagram').style.width=`${2100*scale}px`;$('#zoom').value=`${Math.round(scale*100)}%`;}
function fit(){zoom($('#canvas').clientWidth/2100);$('#canvas').scrollTo(0,0);}
function clear(){if(active)active.classList.remove('selected');active=null;$('#wire-info').textContent='Select a wire or a checklist row to follow its two endpoints.';}
function select(id){clear();active=[...document.querySelectorAll('[data-wire]')].find(g=>g.dataset.wire===id);active?.classList.add('selected');const w=manifest.routes.find(w=>w.id===id);$('#wire-info').textContent=`${w.id}: ${w.note}`;}
async function load(path,type){const r=await fetch(`assets/s2-aa-poc/${path}`);if(!r.ok)throw Error(`${path}: HTTP ${r.status}`);return r[type]();}
async function start(){const [svg,data]=await Promise.all([load('breadboard.svg','text'),load('wiring.json','json')]);manifest=data;$('#diagram').innerHTML=svg;$('#wires').innerHTML=data.routes.map(w=>`<tr><td><button data-select="${esc(w.id)}">${esc(w.id)}</button></td><td>${esc(w.note)}</td><td>${esc(w.net)}</td></tr>`).join('');document.querySelectorAll('[data-wire]').forEach(g=>{g.addEventListener('click',()=>select(g.dataset.wire));g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(g.dataset.wire);}});});document.querySelectorAll('[data-select]').forEach(b=>b.addEventListener('click',()=>select(b.dataset.select)));fit();}
$('#fit').onclick=fit;$('#plus').onclick=()=>zoom(scale*1.3);$('#minus').onclick=()=>zoom(scale/1.3);$('#reset').onclick=clear;
start().catch(e=>{$('#diagram').textContent='Could not load the diagram. Open this page through the local learning server.';$('#wire-info').textContent=e.message;});
