"""Join literal manual reviews to immutable trace identities; no semantic scorer."""
import csv,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
load=lambda n:json.loads((P/n).read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
v=load('validation.json');assert v['status']=='reconciled'
mapping={x['ordinal']:x for x in load('blinded/mapping-private.json')}
reviews={x['review_id']:x for x in load('primary/first-review.json')['rows']}
rows=[]
for row in v['rows']:
 m=mapping[row['ordinal']];r=reviews[m['review_id']]
 reqpath=f"events/{m['request_event']:03d}.json";respath=f"events/{m['response_event']:03d}.json"
 req=load(reqpath)['data']['request'];res=load(respath)['data']['response'];choice=res['choices'][0]
 assert sha(canon(req))==r['request_canonical_sha256'] and sha(canon(res))==r['response_canonical_sha256']
 assert res['id']==row['full_response_id']==m['full_response_id']
 rows.append(dict(ordinal=row['ordinal'],fixture=row['fixture'],arm=row['arm'],repeat=row['repeat'],review_id=m['review_id'],request_event=reqpath,request_event_sha256=sha((P/reqpath).read_bytes()),request_sdk_sha256=row['request_sha256'],request_wire_object_sha256=sha(canon(req)),response_event=respath,response_event_sha256=sha((P/respath).read_bytes()),full_transport_call_ids=row['transport_call_ids'],full_response_id=res['id'],provider=res['provider'],model=res['model'],status=row['status_code'],finish_reason=choice['finish_reason'],usage=res['usage'],full_action_content=choice['message']['content'],primary_manual_review=r,independent_review='independent/blind-review.json#'+m['review_id'],reconciliation='independent/reconciliation.json',proposed_action_executed=False))
(P/'readout.json').write_text(json.dumps({'scope':'All20 planned calls retained. Manual labels are copied, not inferred. No ECOM actions executed.','rows':rows},ensure_ascii=False,indent=2)+'\n')
with (P/'readout.csv').open('w',newline='') as f:
 fields=['ordinal','fixture','arm','repeat','review_id','request_event','response_event','full_response_id','provider','model','status','finish_reason','full_action_content','primary_class','reported_cost_usd','total_tokens']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in rows:w.writerow({**{k:r[k] for k in fields if k in r},'primary_class':r['primary_manual_review']['authorization_and_fact_support'],'reported_cost_usd':r['usage']['cost'],'total_tokens':r['usage']['total_tokens']})
print('Joined all20 ordinal/full-ID/request/response/manual identities; no semantic scoring.')
