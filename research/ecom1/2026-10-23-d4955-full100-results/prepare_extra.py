"""Deterministic evidence selection; no model/evaluation calls."""
from pathlib import Path
import json,re
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
trials={t['task_id']:t for t in load(P/'result.json')['result']['trials']}
ins={r['task_id']:json.loads(r['event']['text'])['data']['response']['instruction'] for r in load(P/'instructions-all100.json')}
full={'t004','t014','t024','t044','t064','t060','t063','t065'}
family={'t002':'GEX125','t022':'TEAC270','t041':'M18FID3','t047':'/PowerTools Academy/','t079':'DHS680'}
plan={}
for f in sorted(P.glob('index-t*.json')):
 t=f.stem.removeprefix('index-');idx=[e for p in load(f) for e in p['items']];by={e['seq']:e for e in idx}
 es=[json.loads(s) for s in (P/(t+'-events.ndjson')).read_text().splitlines()];have={e['seq'] for e in es if e['kind']=='rpc_request' or e['kind']=='llm_response' or e['kind'] not in ('rpc_response','llm_request') or (e['kind']=='rpc_response' and e['data']['method']!='Read')};select={}
 def add(e,reason):
  if e['seq'] not in have:select.setdefault(e['seq'],{'seq':e['seq'],'bytes':e['data']['trace']['bytes'],'kind':e['kind'],'reasons':[]})['reasons'].append(reason)
 if t in full:
  for e in idx:add(e,'Complete CAS scope for small dispatch/cleanup/availability/count trial')
 else:
  support=ins[t]+' '+trials[t]['grade']['detail']+' '+json.dumps([e['data'] for e in es if e['kind'] in ('llm_response','agent_finished')])
  skus=set(re.findall(r'PT-[A-Z0-9]+(?:-[A-Z0-9]+)+',support))
  for e in es:
   if e['kind']=='rpc_request' and e['data']['method']=='Read':
    path=e['data']['arguments']['path']
    noncatalog = not path.startswith('/proc/catalog/')
    if '/proc/locations/' in path or '/proc/stores/' in path:
     noncatalog = path.rsplit('/',1)[-1].removesuffix('.json') in support
    if noncatalog or any(s in path for s in skus) or (t in family and family[t] in path):
     response=by[e['seq']+1];assert response['kind']=='rpc_response' and response['data']['method']=='Read'
     add(response,'Actual successful Read: policy/upload/noncatalog data, referenced store ID, or SKU/family referenced by instruction/model/grade; unrelated bulk store/catalogue responses omitted')
  req=[e for e in idx if e['kind']=='llm_request']
  for e in (req[:2]+req[-1:]):add(e,'Exact router, first main-model, and final-model request (other middle requests intentionally not claimed captured)')
 plan[t]=list(select.values())
(P/'additional-harvest-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({t:{'events':len(a),'bytes':sum(e['bytes'] for e in a)} for t,a in plan.items()},indent=2))
