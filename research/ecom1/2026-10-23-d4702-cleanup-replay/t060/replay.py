"""Separate eight-cell all-files witness; preserve original t03948-cell report."""
import contextlib,copy,hashlib,io,json,platform
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent;BASE=P.parent
raw=(P/'actual-trace.ndjson').read_bytes();assert len(raw)==62165 and hashlib.sha256(raw).hexdigest()=='fb120fbc6584a2a0c3a8d0a482c95991928ec6c605ededf630b61542306b21c2'
es=[json.loads(x) for x in raw.splitlines()];assert [e['seq'] for e in es]==list(range(8525,8550))
trial='vm2-M6yqkQXzn7qWmPZpfwaA8tQtq5D';assert all(e['data']['trial_id']==trial for e in es)
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
sha=lambda b:hashlib.sha256(b).hexdigest()
pending={};llms={};rpc={};actions=[];models=[];task=None;answer=None
for e in es:
 d=e['data']
 if e['kind']=='rpc_request':
  assert d['method'] not in pending;pending[d['method']]=e
  if d['method']=='Answer':answer=d['arguments']
 elif e['kind']=='rpc_response':
  q=pending.pop(d['method']);method=d['method'];args=q['data']['arguments'];response=d['response']
  if method=='StartTrial':task=response
  elif method not in ['EndTrial','Answer']:
   if method=='Read':assert sha(response['content'].encode())==response['sha256']
   k=canon([method,args]);assert k not in rpc;rpc[k]=response
   actions.append({'request_seq':q['seq'],'response_seq':e['seq'],'method':method,'args':args,'response':response})
 elif e['kind']=='llm_request':llms[d['call']]=e
 elif e['kind']=='llm_response':
  q=llms.pop(d['call']);assert d.get('status',200)==200
  models.append({'request_seq':q['seq'],'response_seq':e['seq'],'wire_request':q['data']['request'],'response':d['response']})
assert not pending and not llms and len(models)==3
root='/tmp/cleanup-6JCNXc4q';listing=rpc[canon(['List',{'path':root}])]
assert listing['path']==root.lower() and len(listing['entries'])==9
assert all(x['kind']=='NODE_KIND_FILE' and x['path']==root+'/'+x['name'] for x in listing['entries'])
expected=sorted(x['path'] for x in listing['entries']);assert not any(a['method']=='Delete' for a in actions)
w={'task':task,'root':root,'initial_listing':listing,'rpc':rpc,'actions':actions,'model_exchanges':models,'actual_answer':answer,'expected_deletes':expected,'actual_deletes':[],'trace_sha256':sha(raw)}
(P/'world.json').write_text(json.dumps(w,indent=2,ensure_ascii=False)+'\n')
(P/'oracle.json').write_text(json.dumps({'rule':'Actual instruction requests all files under explicit root; all9 List entries are files; no suffix filter. No candidate parser used.','expected_deletes':expected,'expected_message':'\n'.join(expected),'actual_deletes':[]},indent=2)+'\n')
# Reuse exact already-tested host definitions; inject only a different archived W.
host_source=(BASE/'replay.py').read_text();prefix=host_source.split('\nrows=[]',1)[0];ns={'__file__':str(BASE/'replay.py')};exec(compile(prefix,str(BASE/'replay.py'),'exec'),ns);ns['W']=w
pins=json.loads((BASE/'source-comparison.json').read_text())['source_files'];rows=[]
with m.Monty() as pool:
 for version in ['d4353r1','d4702r1']:
  for form in ['packed','readable']:
   name=version+('-readable.py' if form=='readable' else '.py');src=(BASE/'upstream'/name).read_text();assert sha(src.encode())==pins[name]['sha256']
   for engine in ['cpython','monty']:
    host=ns['Host']('actual_frozen');out=io.StringIO();native=[]
    if engine=='cpython':
     with contextlib.redirect_stdout(out):exec(compile(src,name,'exec'),{'bitgn':host})
    else:
     with pool.checkout(limits=ns['LIMITS']) as session:session.feed_run(src,inputs={'bitgn':m.ClassInstance(host,allowed_methods={'task','call','answer','llm','usage'})},print_callback=lambda *a:native.append(str(a[-1])))
    assert not host.unmatched and len(host.answers)==1
    if version=='d4353r1':
     assert host.deleted==expected and not host.state and len(host.models)==1
     assert host.answers==[{'message':'\n'.join(expected),'outcome':'OUTCOME_OK','refs':[root,'/docs/security.md']}]
     assert len(host.synthetic)==9 # No actual Delete responses in this trace.
    else:
     assert not host.deleted and len(host.state)==9 and len(host.models)==3 and host.answers==[answer]
     assert host.calls==[[a['method'],a['args']] for a in actions]
    rows.append({'version':version,'form':form,'engine':engine,'source_sha256':sha(src.encode()),'rpc_calls':host.calls,'deleted_paths':host.deleted,'remaining_paths':sorted(host.state),'answers':host.answers,'model_requests':host.models,'model_calls':len(host.models),'synthetic_mutation_responses':host.synthetic,'unmatched_calls':host.unmatched,'stdout':out.getvalue() if engine=='cpython' else ''.join(native)})
for version in ['d4353r1','d4702r1']:
 group=[r for r in rows if r['version']==version]
 for key in ['rpc_calls','deleted_paths','remaining_paths','answers','model_requests','model_calls','synthetic_mutation_responses']:
  assert all(r[key]==group[0][key] for r in group)
report={'status':'passed','executions':8,'python':platform.python_version(),'monty':'1.2.0','limits':ns['LIMITS'],'trace_sha256':sha(raw),'trace_events':len(es),'shared_host_source_sha256':sha(host_source.encode()),'zero_unmatched_calls':True,'all_four_forms_equal':True,'actual_d4702_all3_wire_requests_exact':True,'parent_shared_router_wire_request_exact':True,'parent9successful_deletes_simulated':True,'model_calls':0,'ecom_calls':0,'limits_note':'Frozen actual model replies; all parent Delete acknowledgements/state changes simulated, not actual server outcomes. No task-grade or aggregate-score causal claim.','results':rows}
(P/'replay-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
