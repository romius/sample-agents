"""Reconstruct t039 from complete archived CAS; no synthetic facts in baseline world."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
RAW=P/'actual-trace.ndjson'
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
raw=RAW.read_bytes();assert len(raw)==145117 and sha(raw)=='081fd389a34a7e447ce02f7f75f1db80933d447702f389027c036b1b44755994'
es=[json.loads(l) for l in raw.splitlines()];assert [e['seq'] for e in es]==list(range(5480,5521))
trial='vm2-M6yqkQXzn7qWmPZpfwaA8tQtq4r';assert all(e['data']['trial_id']==trial for e in es)
requests={};llms={};rpc={};actions=[];models=[];task=None;answer=None
for e in es:
 d=e['data']
 if e['kind']=='rpc_request':
  assert d['method'] not in requests;requests[d['method']]=e
  if d['method']=='Answer':answer=d['arguments']
 elif e['kind']=='rpc_response':
  q=requests.pop(d['method']);method=d['method'];args=q['data']['arguments'];response=d['response']
  if method=='StartTrial':task=response
  elif method not in ['EndTrial','Answer']:
   if method=='Read':assert sha(response['content'].encode())==response['sha256']
   k=canon([method,args]);assert k not in rpc
   rpc[k]=response;actions.append({'request_seq':q['seq'],'response_seq':e['seq'],'method':method,'args':args,'response':response})
 elif e['kind']=='llm_request':
  key=(d['call'],d.get('attempt',1));assert key not in llms;llms[key]=e
 elif e['kind']=='llm_response':
  key=(d['call'],d.get('attempt',1));q=llms.pop(key);assert d.get('status',200)==200
  models.append({'request_seq':q['seq'],'response_seq':e['seq'],'wire_request':q['data']['request'],'response':d['response']})
assert not requests and not llms and len(models)==7 and answer is not None
root='/tmp/scoped-cleanup-H54TXHks';listing=rpc[canon(['List',{'path':root}])]
assert listing['path']==root.lower() # Actual response canonicalizes this field; preserve exact entry paths below.
entries=listing['entries'];assert len({e['path'] for e in entries})==len(entries)
assert all(e['path']==root+'/'+e['name'] for e in entries)
expected=sorted(e['path'] for e in entries if e['kind']=='NODE_KIND_FILE' and e['name'].endswith('.tmp'))
actual_deletes=[x['args']['path'] for x in actions if x['method']=='Delete']
assert len(expected)==4 and len(actual_deletes)==3 and set(expected)-set(actual_deletes)=={root+'/stale-export-01.tmp'}
save('world.json',{'task':task,'root':root,'initial_listing':listing,'rpc':rpc,'actions':actions,'model_exchanges':models,'actual_answer':answer,'expected_deletes':expected,'actual_deletes':actual_deletes,'trace_sha256':sha(raw),'scope':'All baseline RPCs/models from complete actual CAS. Counterfactual fourth Delete response must be simulated explicitly; no live model or task-grade claim.'})
save('oracle.json',{'method':'Independent literal basename suffix rule from actual task and List entries; no candidate parser used','instruction':task['instruction'],'selected_paths':expected,'unselected_paths':sorted(e['path'] for e in entries if e['path'] not in expected),'expected_message':'\n'.join(expected),'actual_deletes':actual_deletes,'missing_actual_delete':root+'/stale-export-01.tmp','note':'Live grader confirms missing deletion. This oracle checks local simulated final state; it is not a fresh grade.'})
print(json.dumps({'status':'verified complete CAS','events':len(es),'models':len(models),'listed_entries':len(entries),'expected_deletes':len(expected),'actual_deletes':len(actual_deletes)}))
