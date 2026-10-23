"""Mechanical blinding only; never classifies semantic responses."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
events={e['seq']:e for e in map(json.loads,(P/'trial-trace.ndjson').read_text().splitlines())}
v=load(P/'validation.json');assert v['status']=='reconciled' and len(v['rows'])==20
ordered=sorted(v['rows'],key=lambda r:hashlib.sha256(('receipt-blind-v1|'+r['full_response_id']).encode()).hexdigest())
items=[];mapping=[]
for i,row in enumerate(ordered,1):
 rid=f'R{i:02d}';reqseq=row['attempts'][0]['request_events'][0];resp=events[row['response_event']]['data']
 items.append(dict(review_id=rid,request=events[reqseq]['data']['request'],status_code=resp.get('status'),raw_response=resp.get('response'),raw_error=resp.get('error')))
 mapping.append(dict(review_id=rid,ordinal=row['ordinal'],fixture=row['fixture'],arm=row['arm'],repeat=row['repeat'],request_event=reqseq,response_event=row['response_event'],transport_call_ids=row['transport_call_ids'],full_response_id=row['full_response_id']))
out={'scope':'Arm-hidden first-action review. Prompts may reveal context presence; this is partial blinding. No proposed action executed. Full raw responses are retained; only routing metadata linking arms/ordinals is withheld.','items':items}
(P/'blinded').mkdir(exist_ok=True)
(P/'blinded/items.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(P/'blinded/mapping-private.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
rubric=(P/'inputs/diagnostic-plan/PLAN.md').read_text().split('## Preregistered manual rubric\n',1)[1].split('## Accounting, logs, and missing data',1)[0]
(P/'blinded/RUBRIC.md').write_text('# Manual first review\n\nDo not open mapping-private.json or any primary/independent judgments until your own first review is frozen. Full request bodies define visible evidence; archived helper facts are not visible evidence. No action is executed.\n\n'+rubric)
for name in ['items.json','RUBRIC.md']:
 b=(P/'blinded'/name).read_bytes();print(name,len(b),hashlib.sha256(b).hexdigest())
