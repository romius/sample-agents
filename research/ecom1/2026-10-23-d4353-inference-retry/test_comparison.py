"""Whole-source native faults: synthetic responses over a pinned archived world."""
import copy,json,platform
from pathlib import Path
import pydantic_monty as monty
from host import P,W,Host,execute,response,sha,canon,DONE,LIMITS
from helper_host import HelperHost,OVERLAY
VERSIONS=('parent','sdk-only','guest-owned')
TRANSIENT='HTTP 503 unavailable'
TIMEOUT='Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out'
CANCEL='OpenRouter HTTP 503: {"error":{"message":"request cancelled"}}'
ERRORS=[('503',TRANSIENT,True,False),('timeout',TIMEOUT,True,False),('400','HTTP 400 connection parameter invalid',False,False),('429','OpenRouter HTTP 429: rate limited',False,False),('unknown','database is locked',False,False),('cancel',CANCEL,False,True),('negated_cancel','OpenRouter HTTP 503: request was not cancelled; upstream unavailable',True,False)]
cases=[dict(name='healthy'),dict(name='malformed_then_valid',malformed=1),dict(name='length_then_valid',length=2),dict(name='malformed_forced',malformed=3)]
for stage in ('router','main','forced','helper'):
 for name,error,retry,cancel in ERRORS:
  c=dict(name=stage+'_'+name,stage=stage,retry=retry,cancel=cancel,error=error,fail_stages=[stage],failures=99)
  if stage=='forced':c['malformed']=3
  if stage=='helper':c.update(helper_error=error,helper_failures=99)
  if name=='429':c['sdk_attempts']=5
  cases.append(c)
 for error_name,error in [('503',TRANSIENT),('timeout',TIMEOUT)]:
  c=dict(name=stage+'_'+error_name+'_recovers',stage=stage,retry=True,cancel=False,error=error,fail_stages=[stage],failures=1,recovery=True)
  if stage=='forced':c['malformed']=3
  if stage=='helper':c.update(helper_error=error,helper_failures=1)
  cases.append(c)
cases.append(dict(name='helper_healthy',stage='helper',retry=False,cancel=False,helper_error='unused',helper_failures=0))
for name,errors in [('transient_then400',[TRANSIENT,'HTTP 400 invalid parameter']),('transient_then_unknown',[TRANSIENT,'database is locked']),('transient_then_cancel',[TRANSIENT,CANCEL]),('third_attempt_success',['HTTP 504 unavailable','HTTP 504 unavailable'])]:
 cases.append(dict(name=name,errors=errors))
cases.append(dict(name='sdk429_internal_recovery',fail_stages=['main'],failures=0,error='unused',sdk_attempts=5))
# A successful HTTP200 response with null final content is NOT a transport error.
events=[json.loads(l) for l in (P/'evidence/d4702-t016-events.ndjson').read_text().splitlines()]
nulls=[next(e for e in events if e['seq']==seq) for seq in (2642,2644,2646)]
forced=next(e for e in events if e['seq']==2648)
assert all(e['kind']=='llm_response' and e['data']['status']==200 and e['data']['response']['choices'][0]['message']['content'] is None for e in nulls)
assert all(e['data']['response']['choices'][0]['finish_reason']=='stop' for e in nulls)
cases.append(dict(name='actual_http200_null_content',null_content=3,null_responses=[e['data']['response'] for e in nulls],forced_response=forced['data']['response']))
for action in [dict(tool='write',path=W['export'],content='SCRIPTED artifact'),dict(tool='delete',path=W['export']),dict(tool='exec',path='/bin/discount',args=['SCRIPTED'],stdin='')]:
 cases.append(dict(name=action['tool']+'_side_effect_then_error',write_first=True,first_action=action,mutation_error='BitGN HTTP 503: result unconfirmed'))
cases.append(dict(name='successful_write_then_inference_error',write_first=True,after_write_error=TRANSIENT))
cases.append(dict(name='forced_answer_side_effect_then_error',malformed=3,answer_error='BitGN HTTP 503: Answer result unconfirmed'))
cases.append(dict(name='mixed_sdk429_then503',stage='main',retry=True,cancel=False,error=TRANSIENT,fail_stages=['main'],failures=99,sdk_attempts=5))
class ComparisonHost(Host):
 def llm(self,*args,**kwargs):
  stage='router' if kwargs.get('max_completion_tokens')==1024 else 'forced' if args[1][-1]['content'].startswith('Stop working now.') else 'main'
  if stage=='main' and self.case.get('null_responses'):
   n=self.counts.get('main',0)
   self.case['null_response']=self.case['null_responses'][min(n,2)]
  return super().llm(*args,**kwargs)
 def answer(self,message,*,outcome,refs):
  result=super().answer(message,outcome=outcome,refs=refs)
  if self.case.get('answer_error'):raise RuntimeError(self.case['answer_error'])
  return result
class ComparisonHelper(HelperHost):
 def llm(self,*args,**kwargs):
  # Explicit fake SDK429 accounting for helper, same declared max5 policy.
  before=self.provider_attempts
  try:return super().llm(*args,**kwargs)
  finally:
   if kwargs.get('max_completion_tokens')==200:self.provider_attempts=before+self.case.get('sdk_attempts',1)
rows=[]
with monty.Monty() as pool:
 for version in VERSIONS:
  for form in ('readable','packed'):
   path=P/('parent-readable.py' if form=='readable' else 'parent.py') if version=='parent' else P/version/('readable.py' if form=='readable' else 'agent.py')
   source=path.read_text()
   for case in cases:
    row=execute(pool,source,copy.deepcopy(case),ComparisonHelper if case.get('stage')=='helper' else ComparisonHost)
    row.update(version=version,form=form,source_sha256=sha(source));rows.append(row)
def get(v,name):return next(r for r in rows if r['version']==v and r['form']=='readable' and r['case']==name)
for version in VERSIONS:
 for c in cases:
  group=[r for r in rows if r['version']==version and r['case']==c['name']]
  for key in ('llm_stages','guest_llm_calls','simulated_provider_attempts','request_hashes','rpc_calls','mutations','answers'):
   assert group[0][key]==group[1][key],(version,c['name'],key)
  assert bool(group[0]['raised'])==bool(group[1]['raised'])
  r=group[0]
  stage=c.get('stage')
  if stage:
   expected=2 if c.get('recovery') else 3
   if version!='guest-owned' or not c['retry']:expected=1
   assert r['llm_stages'][stage]==expected,(version,c['name'],r['llm_stages'],expected)
   calls=[x for x in r['request_details'] if x['stage']==stage]
   assert all(x==calls[0] for x in calls),(version,c['name'],'changed retry request')
   expected_raise=c['cancel'] and version!='parent' or version=='parent' and stage!='helper'
   assert bool(r['raised'])==bool(expected_raise),(version,c['name'],r['raised'])
   if expected_raise:assert not r['answers']
   else:
    assert len(r['answers'])==1
    failed_main=stage=='main' and not (version=='guest-owned' and c.get('recovery'))
    failed_forced=stage=='forced' and not (version=='guest-owned' and c.get('recovery'))
    expected_outcome='OUTCOME_ERR_INTERNAL' if failed_main or failed_forced else 'OUTCOME_NONE_UNSUPPORTED'
    assert r['answers'][0]['outcome']==expected_outcome,(version,c['name'],r['answers'])
   if stage=='main':assert 'forced' not in r['llm_stages']
  if '_side_effect_then_error' in c['name']:
   assert r['raised'],(version,c['name'])
   if c['name'].startswith('forced_answer'):assert len(r['answers'])==1 and not r['mutations']
   else:assert len(r['mutations'])==1 and not r['answers']
  if c['name']=='successful_write_then_inference_error':
   assert len(r['mutations'])==1
   assert r['llm_stages']['main']==(4 if version=='guest-owned' else 2)
   assert bool(r['raised'])==(version=='parent')
  if c['name'].startswith('transient_then') or c['name']=='third_attempt_success':
   expected=3 if c['name']=='third_attempt_success' else 2
   assert r['llm_stages']['main']==(expected if version=='guest-owned' else 1)
   cancel=c['name']=='transient_then_cancel' and version=='guest-owned'
   assert bool(r['raised'])==(version=='parent' or cancel)
   if version!='parent' and not cancel:
    assert r['answers'][0]['outcome']==('OUTCOME_NONE_UNSUPPORTED' if version=='guest-owned' and c['name']=='third_attempt_success' else 'OUTCOME_ERR_INTERNAL')
   calls=[x for x in r['request_details'] if x['stage']=='main']
   assert all(x==calls[0] for x in calls)
  if c['name']=='sdk429_internal_recovery':
   assert r['llm_stages']=={'router':1,'main':1} and r['simulated_provider_attempts']==6
   assert not r['raised'] and r['answers'][0]['outcome']=='OUTCOME_NONE_UNSUPPORTED'
  if c['name']=='actual_http200_null_content':
   assert r['llm_stages']=={'router':1,'main':3,'forced':1}
   assert r['answers'][0]['outcome']=='OUTCOME_ERR_INTERNAL'
   assert not r['raised'] and not r['mutations']
   main=[x for x in r['request_details'] if x['stage']=='main']
   assert len({canon(x) for x in main})==3 # correction requests, NOT identical retry
for name in ('healthy','helper_healthy','malformed_then_valid','length_then_valid','malformed_forced','actual_http200_null_content','sdk429_internal_recovery'):
 for version in VERSIONS[1:]:
  for key in ('llm_stages','request_hashes','rpc_calls','mutations','answers'):
   assert get(version,name)[key]==get('parent',name)[key],(version,name,key)
for version in VERSIONS:
 r=get(version,'mixed_sdk429_then503')
 # One router + main (1SDK call or3), each main simulates5 HTTP attempts.
 assert r['simulated_provider_attempts']==1+(15 if version=='guest-owned' else 5)
(P/'helper-overlay.json').write_text(json.dumps(OVERLAY,indent=2)+'\n')
(P/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
requests={r['version']+'/'+r['form']+'/'+r['case']:r.pop('request_details') for r in rows}
(P/'requests.json').write_text(json.dumps(requests,indent=2)+'\n')
report={'status':'PASS','python':platform.python_version(),'monty':'1.2.0','whole_agent_executions':len(rows),'scenarios':len(cases),'limits':LIMITS,'no_paid_calls':True,'physical_attempt_counts_are_declared_simulation':True,'results':rows}
(P/'test-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='results'}))
