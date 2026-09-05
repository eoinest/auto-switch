/* Local, static diagram viewer. No hardware API calls. */
const $=s=>document.querySelector(s);
let scale=1, layout, activeWire, drawRequest=0;
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function get(path,type='json'){
  const r=await fetch(`assets/aa-demo/${path}`);if(!r.ok)throw Error(`${path}: HTTP ${r.status}`);return r[type]();
}
function setScale(n){scale=Math.max(.08,Math.min(2.5,n));$('#diagram').style.width=`${2480*scale}px`;$('#zoom').value=`${Math.round(scale*100)}%`;}
function fit(){setScale($('#canvas').clientWidth/2480);$('#canvas').scrollTo(0,0);}
async function show(){
  const n=$('#gangs').value;
  const request=++drawRequest;
  const markup=await get(`breadboard-${n}-servo.svg`,'text');
  if(request!==drawRequest)return;
  $('#diagram').innerHTML=markup;
  for(const ext of ['svg','png'])$(`#${ext}-download`).href=`assets/aa-demo/breadboard-${n}-servo.${ext}`;
  $('#placement-download').href=`assets/aa-demo/placements-${n}-servo.csv`;
  activeWire=null;$('#wire-info').textContent='Click a wire to highlight its physical endpoints. Scroll to explore when zoomed in.';
  $('#step-list').innerHTML=layout.steps.filter(s=>n==='2'||s.id!==4).map(s=>`<li><strong>${esc(s.title)}</strong>${esc(s.text)}</li>`).join('');
  fit();
  $('#diagram').querySelectorAll('[data-wire]').forEach(g=>g.addEventListener('click',()=>{
    if(activeWire)activeWire.querySelector('path[data-from]').style.strokeWidth='4.5';
    const p=g.querySelector('path[data-from]');p.style.strokeWidth='9';activeWire=g;
    $('#wire-info').textContent=`${g.dataset.wire}: ${p.dataset.from.replace('hole:','breadboard ')} → ${p.dataset.to.replace('hole:','breadboard ')}`;
  }));
}
$('#gangs').addEventListener('change',()=>show().catch(fail));
$('#fit').addEventListener('click',fit);$('#plus').addEventListener('click',()=>setScale(scale*1.35));$('#minus').addEventListener('click',()=>setScale(scale/1.35));
$('#fullscreen').addEventListener('click',async()=>{
  try{if(document.fullscreenElement)await document.exitFullscreen();else await $('#viewer').requestFullscreen();}catch(e){$('#wire-info').textContent='Full screen unavailable; use zoom and scroll.';}
});
document.addEventListener('fullscreenchange',()=>{fit();$('#fullscreen').textContent=document.fullscreenElement?'Exit full screen':'Full screen';});
function link(url,label){return /^https:\/\//.test(url||'')?`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)}</a>`:'';}
function fail(e){$('#wire-info').textContent=`Could not load an asset: ${e.message}. Open this page through the local learning server.`;}
async function start(){
  const [p,rows]=await Promise.all([get('layout.json'),get('bom.json')]);layout=p;
  $('#bom').innerHTML='<div class="bom-wrap"><table><thead><tr><th>Part</th><th>1 / 2 servos</th><th>Buy / reuse</th><th>Purchasing notes</th></tr></thead><tbody>'+rows.map(r=>{
    const amazon=r.amazon_url,candidate=r.purchase_url===amazon?r.source_url:r.purchase_url;
    const url=candidate===amazon?'':candidate;
    return `<tr><td>${esc(r.part)}</td><td>${esc(r.quantity_one_servo)} / ${esc(r.quantity_two_servos)}<br>${esc(r.unit)}</td><td>${esc(r.buy_quantity)}<br>${link(amazon,'Amazon')}${amazon&&url?' · ':''}${link(url,amazon?'Reference / fallback':'Supplier')||(!amazon?'Reuse / see notes':'')}</td><td>${esc(r.notes)}</td></tr>`;
  }).join('')+'</tbody></table></div>';
  await show();
}
start().catch(fail);
