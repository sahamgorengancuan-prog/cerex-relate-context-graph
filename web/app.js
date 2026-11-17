'use strict';
(()=>{
const api='/judge/relate-api';
const el=id=>document.getElementById(id);
let response=null, selected=null, inFlight=false;
const esc=s=>String(s||'');
function setStatus(x,ok){el('status').textContent=x;el('db-health').textContent=ok?'RELATE ONLINE':'SERVICE ERROR';el('db-health').className=ok?'state good':'state bad';}
async function load(){
 if(inFlight)return;
 inFlight=true; el('rerun').disabled=true; el('receipt').disabled=true;
 setStatus('Running six allowlisted Cypher queries in actual Relate…',true);
 try{
  const r=await fetch(api+'/graph',{credentials:'omit',cache:'no-store',headers:{Accept:'application/json'}});
  if(!r.ok)throw Error('Relate API returned HTTP '+r.status);
  const data=await r.json();
  if(data.status!=='READ_ONLY_PREFLIGHT_NOT_EXECUTION'||!Array.isArray(data.tasks)||data.tasks.length>50)throw Error('Unexpected graph response.');
  response=data;
  el('task-count').textContent=data.counts.tasks;
  el('permit-count').textContent=data.counts.permitted;
  el('deny-count').textContent=data.counts.denied;
  el('query-count').textContent=data.verified_query_count;
  el('hash').textContent=data.graph_sha256;
  const list=el('graph');list.replaceChildren();
  data.tasks.forEach(task=>{
   const btn=document.createElement('button');btn.type='button';btn.className='task';btn.dataset.task=task.id;btn.setAttribute('role','listitem');
   const id=document.createElement('span');id.className='id';id.textContent=task.id;
   const title=document.createElement('span');title.className='name';title.textContent=task.title;
   const sub=document.createElement('span');sub.className='sub';sub.textContent=task.deps.length?'↳ depends: '+task.deps.join(', '):'↳ root task';
   title.append(sub);
   const flag=document.createElement('span');flag.className='flag '+(task.status==='PERMITTED'?'ok':'blocked');flag.textContent=task.status==='PERMITTED'?'✓ PERMIT':'× DENY';
   btn.append(id,title,flag);btn.addEventListener('click',()=>select(task.id));
   list.append(btn);
  });
  el('receipt').disabled=false;
  setStatus('Real Relate engine queried successfully. Read-only graph and SHA-256 verified.',true);
  await select(selected&&data.tasks.find(t=>t.id===selected)?selected:data.tasks[0].id);
 }catch(e){el('graph').textContent='Relate service unavailable. Local source may still be cloned and run.';setStatus('Could not verify: '+(e.message||'Unknown error'),false)}
 finally{inFlight=false;el('rerun').disabled=false}
}
async function select(taskId){
 if(!response)return;
 selected=taskId;
 document.querySelectorAll('.task').forEach(b=>b.classList.toggle('selected',b.dataset.task===taskId));
 try{
  const r=await fetch(api+'/task/'+encodeURIComponent(taskId),{credentials:'omit',cache:'no-store'});
  if(!r.ok)throw Error('Task detail HTTP '+r.status);
  const d=await r.json();
  if(!d||d.id!==taskId)return;
  el('task-state').textContent=d.status;
  el('task-state').className='state '+(d.status==='PERMITTED'?'good':'bad');
  el('node-title').textContent=d.title;
  el('node-subtitle').textContent=d.status==='PERMITTED'?'Graph checks allow this task to proceed in the SYNTHETIC plan only.':'Graph checks refuse this task in the SYNTHETIC plan. No OS action is attempted.';
  el('d-id').textContent=d.id;
  el('d-tool').textContent=d.requested_tool;
  el('d-deps').textContent=d.deps.length?d.deps.join(', '):'(none)';
  const reasons=el('reasons');reasons.replaceChildren();d.reasons.forEach(text=>{const li=document.createElement('li');li.textContent=text;reasons.append(li)});
 }catch(e){setStatus('Could not read task detail: '+e.message,false)}
}
function download(name,payload){
 const b=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'}),u=URL.createObjectURL(b),a=document.createElement('a');
 a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),30000);
}
el('rerun').addEventListener('click',load);
el('receipt').addEventListener('click',()=>response&&download('cerex-relate-real-graph-proof.json',response));
el('copyhash').addEventListener('click',()=>{
 const s=response?.graph_sha256||'';
 if(!s)return;
 if(navigator.clipboard?.writeText){navigator.clipboard.writeText(s).then(()=>el('copyhash').textContent='Copied').catch(()=>el('copyhash').textContent='Select text')}else el('copyhash').textContent='Select text';
});
load();
})();