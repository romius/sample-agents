"""Copy exact archived evidence and plan bounded missing-request retrieval only."""
import hashlib,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;BASE=P.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
pins={};plan=[];census=[]
def cp(src,dst):
 target=P/dst;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);b=target.read_bytes();pins[dst]={'original_workspace_path':str(src.relative_to(BASE.parent.parent)),'bytes':len(b),'sha256':sha(b)}
for source in ['d4702','d4955']:
 root=BASE/f'2026-10-23-{source}-full100-results';res=json.loads((root/'result.json').read_text());job=res['job']['id'];seen=set()
 for n in ['result.json','SHA256SUMS.json','AUDIT-SCOPE.json','reassembly-verification.json']:cp(root/n,f'upstream/{source}/{n}')
 for f in sorted(root.glob('t*-events.ndjson')):
  task=f.name[:4];cp(f,f'upstream/{source}/{f.name}');cp(root/f'index-{task}.json',f'upstream/{source}/index-{task}.json')
  raw=f.read_bytes();events=[json.loads(x) for x in raw.splitlines()];index=[e for page in json.loads((root/f'index-{task}.json').read_text()) for e in page['items']];byseq={e['seq']:e for e in index};known={e['seq']:e for e in events}
  responses=[e for e in events if e['kind']=='llm_response'];indexed=[e for e in index if e['kind']=='llm_response'];assert {e['seq'] for e in responses}=={e['seq'] for e in indexed}
  for e in responses:
   c=e['data']['response']['choices'][0];m=c['message'];anomalous=m.get('content') is None or c.get('finish_reason')=='length'
   census.append({'source':source,'job':job,'task':task,'response_seq':e['seq'],'call':e['data']['call'],'null_content':m.get('content') is None,'finish_reason':c.get('finish_reason'),'selected':anomalous})
   if not anomalous:continue
   req=next(z for z in index if z['kind']=='llm_request' and z['data']['call']==e['data']['call'])
   following=next((z for z in index if z['kind']=='llm_request' and z['seq']>e['seq']),None)
   for z,reason in [(req,'exact anomalous-response request'),(following,'immediate next inference request: phase and feedback/context boundary')]:
    if z is None or z['seq'] in known or z['seq'] in seen:continue
    seen.add(z['seq']);plan.append({'source':source,'job':job,'task':task,'seq':z['seq'],'reason':reason,'index':z})
sources={
 'd4353-readable.py':BASE/'2026-10-23-d4702-full100-results/sources/d4353r1-readable.py',
 'd4353-agent.py':BASE/'2026-10-23-d4702-full100-results/sources/d4353r1.py',
 'd4702-readable.py':BASE/'2026-10-23-d4702-full100-results/sources/d4702r1-readable.py',
 'd4702-agent.py':BASE/'2026-10-23-d4702-full100-results/sources/d4702r1.py',
 'd4955-readable.py':BASE/'2026-10-23-d4955-full100-results/sources/2026-10-22-clarification-integration/readable.py',
 'd4955-agent.py':BASE/'2026-10-23-d4955-full100-results/sources/2026-10-22-clarification-integration/agent.py'}
for name,src in sources.items():cp(src,'sources/'+name)
for name in ['PLAN.md','source-functions.json','evidence-summary.json','SHA256SUMS.json']:cp(BASE/'2026-10-23-completion-integrity-review'/name,'prior-completion-review/'+name)
for name,obj in [('input-pins.json',pins),('harvest-plan.json',plan),('census.json',census)]: (P/name).write_text(json.dumps(obj,indent=2)+'\n')
print(json.dumps({'population':len(census),'anomalies':sum(r['selected'] for r in census),'missing_requests_to_retrieve':len(plan),'chunks':sum((e['index']['data']['trace']['bytes']+11999)//12000 for e in plan)}))
