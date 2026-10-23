"""One exact shared dispatch-world control, reconstructed from both live traces."""
import json,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent;C=P/'comparison'
def load(p):return json.loads(p.read_text())
index=[e for p in load(C/'d4353-t024-index.json')['pages'] for e in p['items']]
parts={}
for f in sorted(C.glob('t024-receipt-*.json')):
 r=load(f);response=r['response'];assert response['code']==0 and not response['data']['output_truncated']
 requests=re.findall(r"trace_event\('j6d6d4adb60f241a4a1d111a9719b59dc',(\d+),offset=(\d+),limit=(\d+)\)",r['request']['source'])
 chunks=json.loads(response['output']);assert len(chunks)==len(requests)
 for (seq,off,lim),chunk in zip(requests,chunks):
  seq,off,lim=map(int,(seq,off,lim));raw=chunk['text'].encode()
  assert chunk['seq']==seq and len(raw)<=lim and off+len(raw)==chunk['next_offset']
  parts.setdefault(seq,[]).append((off,raw))
raw=b''
for e in index:
 row=b''
 for off,b in sorted(parts[e['seq']]):assert off==len(row);row+=b
 assert len(row)==e['data']['trace']['bytes'] and len(raw)==e['data']['trace']['offset']
 assert json.loads(row)['seq']==e['seq'];raw+=row
trial=next(t for t in load(C/'d4353-official-result.json')['result']['trials'] if t['task_id']=='t024')
assert len(raw)==trial['trace']['bytes'] and hashlib.sha256(raw).hexdigest()==trial['trace']['blob']
(C/'d4353-t024-events.ndjson').write_bytes(raw)
old=[json.loads(x) for x in raw.splitlines()];new=[json.loads(x) for x in (P/'t024-events.ndjson').read_text().splitlines()]
def reads(events):
 return {e['data']['response']['path']:e['data']['response']['content'] for e in events if e['kind']=='rpc_response' and e['data']['method']=='Read'}
a,b=reads(old),reads(new)
paths=[p for p in a if p.startswith('/ops/dispatch/') or p=='/docs/dispatch.md']
assert len(paths)==4 and all(a[p]==b[p] for p in paths)
def answer(es):return next(e['data']['arguments'] for e in es if e['kind']=='rpc_request' and e['data']['method']=='Answer')
same_answer=answer(old)==answer(new)
def instruction(es):return next(e['data']['response']['instruction'] for e in es if e['kind']=='rpc_response' and e['data']['method']=='StartTrial')
assert instruction(old)==instruction(new)
def actions(es):return [(e['data']['method'],e['data']['arguments']) for e in es if e['kind']=='rpc_request' and e['data']['method'] not in ['StartTrial','EndTrial']]
assert actions(old)==actions(new)
def observations(es):return [(e['data']['method'],e['data']['response']) for e in es if e['kind']=='rpc_response' and e['data']['method'] not in ['StartTrial','EndTrial']]
assert observations(old)==observations(new)
assert a==b
def model_requests(es):return [e['data']['request'] for e in es if e['kind']=='llm_request']
assert model_requests(old)==model_requests(new)
result={'scope':'One dispatch control with identical actual instruction, every observed RPC request/response and model request; not an assertion about unobserved files or an aggregate causal estimate. Transport trial/run IDs and timestamps are excluded from comparison.','record_trial_trace':trial['trace'],
 'same_ordinal':'t024','same_instruction':True,'exact_equal_dispatch_inputs':{p:hashlib.sha256(a[p].encode()).hexdigest() for p in paths},
 'all_six_read_content_hashes':{p:hashlib.sha256(a[p].encode()).hexdigest() for p in a},
 'instruction_sha256':hashlib.sha256(instruction(old).encode()).hexdigest(),
 'all_observed_rpc_actions_exact_equal':True,'rpc_actions_compared':len(actions(old)),
 'all_observed_rpc_responses_exact_equal':True,'rpc_responses_compared':len(observations(old)),
 'rpc_comparison_excludes':['StartTrial/EndTrial request/response identity wrappers; actual instruction compared separately'],
 'includes':['Tree root listing','AGENTS/security/dispatch policy Read contents','wave description/packages/lanes Read contents','Exec date and identity stdout','Answer parameters and acknowledgement'],
 'model_request_parameters_and_messages_exact_equal':True,'model_requests_compared':len(model_requests(old)),
 'exact_answer_equal':same_answer,'record_score':trial['grade']['score'],'own_score':next(t for t in load(P/'result.json')['result']['trials'] if t['task_id']=='t024')['grade']['score']}
(C/'t024-shared-world-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
