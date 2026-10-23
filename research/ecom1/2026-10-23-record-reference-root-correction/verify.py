"""Verify archived per-world path resolution; do not infer grader acceptance."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;UP=HERE/'upstream'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
pin=load(HERE/'provenance.json')
for name,p in pin['upstream'].items():
 raw=(UP/name).read_bytes();assert len(raw)==p['bytes'] and sha(raw)==p['sha256'],name
seal=load(UP/'SHA256SUMS.json')
for name in ['events-t091.jsonl','responses-t091.jsonl','index-t091.json','result.json']:
 value=seal[name];expected=value if isinstance(value,str) else value['sha256']
 assert sha((UP/name).read_bytes())==expected,name
index=load(UP/'index-t091.json');indexed={r[0]:r for r in index};assert len(indexed)==267
raws={};events={}
for name in ['events-t091.jsonl','responses-t091.jsonl']:
 for raw in (UP/name).read_bytes().splitlines(keepends=True):
  e=json.loads(raw);s=e['seq'];assert s not in events and raw.endswith(b'\n')
  assert (e['kind'],e['data'].get('method'),len(raw))==tuple(indexed[s][1:]),s
  assert e['data']['trial_id']==pin['trial'],s
  raws[s]=raw;events[s]=e
all_requests={s for s,k,m,n in index if k=='rpc_request'}
assert all_requests=={s for s,e in events.items() if e['kind']=='rpc_request'}
answer=events[12182];assert answer['data']['method']=='Answer'
args=answer['data']['arguments'];refs=args['refs'];assert len(refs)==len(set(refs))==9
out='/exports/inventory-family-eqMvAeV3.csv';assert refs[0]==args['message']==out and args['outcome']=='OUTCOME_OK'
reads={e['data']['arguments']['path']:s for s,e in events.items() if e['kind']=='rpc_request' and e['data']['method']=='Read'}
assert out not in reads
proof=[];selected={11924,11925,12180,12181,12182,12183}
for ref in refs[1:]:
 s=next(s for s,e in sorted(events.items()) if e['kind']=='rpc_request' and e['data']['method']=='Read' and e['data']['arguments']['path']==ref and s+1 in events)
 response=events[s+1];r=response['data']['response']
 assert response['kind']=='rpc_response' and response['data']['method']=='Read'
 assert r['path']==ref and sha(r['content'].encode())==r['sha256']
 selected.update([s,s+1]);proof.append({'path':ref,'request_seq':s,'response_seq':s+1,'content_sha256':r['sha256'],'request_event_sha256':sha(raws[s]),'response_event_sha256':sha(raws[s+1]),'read_succeeded':True})
expected={11956:('/proc/stores/store-linz-hafen.json','4b5ab949347aa12ff38c33d3744b8dac86bec548f7c4a9f82b4f059869ba903b'),12038:('/proc/products/cat-garden-outdoor/kind-pressure-washers/PT-WASH-KAR-K4-CAR.json','56e3441b326c93f3c958f785db0db03ac30a18dee95d98fa65343ee0619a69e9')}
for s,(path,h) in expected.items():
 assert events[s]['data']['arguments']['path']==path
 response=events[s+1]['data']['response'];assert response['sha256']==h
 value=json.loads(response['content']);assert isinstance(value,dict) and value
agents=events[11925]['data']['response'];assert sha(agents['content'].encode())==agents['sha256']
assert '`/proc/products`' in agents['content'] and '`/proc/stores`' in agents['content']
write=events[12180];ack=events[12181];assert write['data']['method']=='Write' and write['data']['arguments']['path']==out and ack['data']['response']['path']==out
result=load(UP/'result.json');assert result['job']['id']==pin['job'] and result['job']['source_blob']==pin['source_sha256']
trial=next(t for t in result['result']['trials'] if t['trial_id']==pin['trial']);assert trial['task_id']=='t091' and trial['grade']['score']==0
assert trial['grade']['detail']=="['answer contains too many invalid references']"
(HERE/'selected-evidence.jsonl').write_bytes(b''.join(raws[s] for s in sorted(selected)))
report={'status':'passed','job':pin['job'],'trial':pin['trial'],'task':'t091','source_document':pin['source_document'],'full_trace_receipt':trial['trace'],'full_trace_cas_reconstructed_here':False,'indexed_events':267,'all_indexed_rpc_requests_preserved':len(all_requests),'answer_seq':12182,'answer_refs':refs,'successfully_read_source_refs':proof,'source_refs_count':8,'output_ref_was_written':True,'output_ref_was_read':False,'world_agents_policy_seq':11925,'policy_names_actual_roots':True,'grade':trial['grade'],'conclusion':'This world successfully resolves the cited /proc/products and /proc/stores paths. A static root-name blacklist misclassifies these concrete records as nonexistent.','not_established':['why the grader rejected this answer','whether each successfully Read source reference is grader-accepted','whether an output readback would change the grade','whether these roots exist in other worlds','whether /proc/returns exists in this world'],'model_calls':0,'ecom_calls':0}
(HERE/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('PASS: both roots resolve, all8 source refs have successful hash-verified Reads;9ref Answer preserved. Grader cause remains unresolved.')
