"""Complete exact-source cleanup replay with method-only native host; no inference."""
import contextlib,copy,hashlib,io,json,platform
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent;W=json.loads((P/'world.json').read_text())
LIMITS={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(x.encode()).hexdigest()
PROVIDER={'only':['deepinfra/bf16'],'quantizations':['bf16'],'allow_fallbacks':False,'require_parameters':True}
def wire(model,messages,kwargs):
 r=copy.deepcopy(dict(kwargs,model=model,messages=messages))
 if 'max_completion_tokens' in r:
  assert 'max_tokens' not in r;r['max_tokens']=r.pop('max_completion_tokens')
 r['stream']=False;r['provider']=copy.deepcopy(PROVIDER);return r
CASES=['actual_frozen','router_then_terminal','fresh_suffix','fresh_directory_decline','fresh_no_match_decline','partial_delete_error']
class Host:
 def __init__(self,case):
  self.case=case;self.calls=[];self.answers=[];self.models=[];self.unmatched=[];self.synthetic=[];self.deleted=[];self.failed=[]
  self.info=copy.deepcopy(W['task']);self.listing=copy.deepcopy(W['initial_listing']);root=W['root']
  if case.startswith('fresh_'):
   names=['alpha.log','bravo.log','charlie.LOG','delta.log.bak','echo.tmp','foxtrot.json']
   self.listing['entries']=[{'name':n,'path':root+'/'+n,'kind':'NODE_KIND_FILE','contentType':'text/plain'} for n in names]
   self.info['instruction']=self.info['instruction'].replace('`.tmp`','`.log`')
   if case=='fresh_directory_decline':self.listing['entries'].append({'name':'nested','path':root+'/nested','kind':'NODE_KIND_DIR'})
   if case=='fresh_no_match_decline':self.info['instruction']=self.info['instruction'].replace('`.log`','`.dat`')
  self.initial={e['path']:copy.deepcopy(e) for e in self.listing['entries']};self.state=copy.deepcopy(self.initial)
 def task(self):return copy.deepcopy(self.info)
 def usage(self):return {'offline_replay':True,'model_calls':0,'reported_cost_usd':'0'}
 def answer(self,message,*,outcome,refs):self.answers.append({'message':message,'outcome':outcome,'refs':refs});return {}
 def call(self,method,args):
  self.calls.append([method,copy.deepcopy(args)]);key=canon([method,args]);root=W['root']
  if method=='List' and args=={'path':root}:
   assert not self.deleted,'unexpected second listing after mutation'
   return copy.deepcopy(self.listing)
  if method=='Delete':
   path=args.get('path');assert set(args)=={'path'} and path in self.state and self.state[path]['kind']=='NODE_KIND_FILE',('invalid delete',args)
   if self.case=='partial_delete_error' and path==root+'/stale-export-01.tmp':
    self.failed.append(path);self.synthetic.append({'type':'injected_delete_error','path':path,'state_effect':'none'})
    raise RuntimeError('SIMULATED Delete error: operation outcome unconfirmed')
   if key in W['rpc']:
    response=copy.deepcopy(W['rpc'][key]);assert response=={}
   else:
    response={};self.synthetic.append({'type':'unobserved_delete_success','path':path,'contract':'DeleteResponse{} from pinned proto; removal is simulated, never an actual server observation'})
   self.deleted.append(path);del self.state[path];return response
  if method in ['Write','Exec'] and (method=='Write' or args.get('path') not in ['/bin/id','/bin/date']):
   self.unmatched.append([method,args]);raise RuntimeError('UNMATCHED MUTATION OR EXEC')
  if key in W['rpc']:return copy.deepcopy(W['rpc'][key])
  self.unmatched.append([method,args]);raise RuntimeError('UNMATCHED RPC '+key)
 def llm(self,model,messages,**kwargs):
  request=wire(model,messages,kwargs);i=len(self.models)
  item={'ordinal':i+1,'request_sha256':sha(canon(request)),'request':request,'wire_match':None};self.models.append(item)
  if self.case=='actual_frozen':
   expected=W['model_exchanges'][i];assert request==expected['wire_request'],('wire request mismatch',i+1)
   item['wire_match']=True;item['archived_request_seq']=expected['request_seq'];return copy.deepcopy(expected['response'])
  if i==0:
   if not self.case.startswith('fresh_'):
    assert request==W['model_exchanges'][0]['wire_request'];item['wire_match']=True
   item['stub']='actual router response, replayed for this scenario';return copy.deepcopy(W['model_exchanges'][0]['response'])
  action={'tool':'report_completion','completed_steps_laconic':[],'message':'OFFLINE TERMINAL: deterministic cleanup route declined or absent.','grounding_refs':[],'outcome':'OUTCOME_NONE_UNSUPPORTED'}
  item['stub']='explicit unsupported terminal; not a model prediction'
  return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(action)}}]}

rows=[]
with m.Monty() as pool:
 for version in ['d4353r1','d4702r1']:
  for form in ['packed','readable']:
   filename=version+('-readable.py' if form=='readable' else '.py');source=(P/'upstream'/filename).read_text()
   for case in CASES:
    for engine in ['cpython','monty']:
     host=Host(case);stdout=io.StringIO();native=[]
     if engine=='cpython':
      with contextlib.redirect_stdout(stdout):exec(compile(source,filename,'exec'),{'bitgn':host})
     else:
      with pool.checkout(limits=LIMITS) as session:session.feed_run(source,inputs={'bitgn':m.ClassInstance(host,allowed_methods={'task','call','answer','llm','usage'})},print_callback=lambda *a:native.append(str(a[-1])))
     assert not host.unmatched and len(host.answers)==1,(version,form,case,engine,host.unmatched,host.answers)
     answer=host.answers[0];parent=version=='d4353r1'
     if case=='actual_frozen' and not parent:
      assert host.deleted==W['actual_deletes'] and answer==W['actual_answer'] and len(host.models)==7
      assert host.calls==[[x['method'],x['args']] for x in W['actions']]
      assert host.state.get(W['root']+'/stale-export-01.tmp') is not None
     elif parent and case in ['actual_frozen','router_then_terminal','fresh_suffix','partial_delete_error']:
      expected=[W['root']+'/alpha.log',W['root']+'/bravo.log'] if case=='fresh_suffix' else W['expected_deletes']
      if case=='partial_delete_error':expected=[x for x in expected if x!=W['root']+'/stale-export-01.tmp'];assert len(host.failed)==1
      assert host.deleted==expected and answer=={'message':'\n'.join(expected),'outcome':'OUTCOME_OK','refs':[W['root'],'/docs/security.md']},(version,case,answer)
      assert len(host.models)==1
     else:
      assert not host.deleted and answer['outcome']=='OUTCOME_NONE_UNSUPPORTED' and answer['message'].startswith('OFFLINE TERMINAL')
      assert len(host.models)==2
     assert set(host.state)==set(host.initial)-set(host.deleted)
     assert all(host.state[k]==host.initial[k] for k in host.state)
     rows.append({'version':version,'source_sha256':sha(source),'form':form,'engine':engine,'case':case,'instruction':host.info['instruction'],'rpc_calls':host.calls,'deleted_paths':host.deleted,'remaining_paths':sorted(host.state),'answers':host.answers,'model_calls':len(host.models),'model_requests':host.models,'unmatched_calls':host.unmatched,'synthetic_mutation_responses':host.synthetic,'injected_errors':host.failed,'stdout':stdout.getvalue() if engine=='cpython' else ''.join(native)})
for version in ['d4353r1','d4702r1']:
 for case in CASES:
  group=[r for r in rows if r['version']==version and r['case']==case];assert len(group)==4
  for k in ['rpc_calls','deleted_paths','remaining_paths','answers','model_calls','model_requests','synthetic_mutation_responses','injected_errors']:
   assert all(r[k]==group[0][k] for r in group),(version,case,k)
report={'status':'passed','python':platform.python_version(),'monty':'1.2.0','limits':LIMITS,'executions':len(rows),'cases':CASES,'exact_trace_sha256':W['trace_sha256'],'native_host':'public method-only ClassInstance','actual_wire_replay':'d4702 all7requests match after SDK completion-token alias/providerwrapper; d4353 onlysharedrouterrequest executed and matched','all_four_forms_equal':True,'zero_unmatched_calls':True,'actual_model_calls':0,'actual_ecom_calls':0,'scope':'Archived-world mechanism evidence; fourth Delete success is simulated. Fresh fixtures and failure injection declared. No real provider recovery or live grade claim.','results':rows}
(P/'replay-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
