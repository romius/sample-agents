"""Native one-guest-owner comparison, classifier counterexamples and exact lookup preservation."""
import ast
import json
import hashlib
from pathlib import Path
import pydantic_monty as monty
from test_native import P,CASES,Host,execute,LIMITS,sha,canon

EXTRA=[
 dict(name='timeout_then_success',fail_stages=['main'],failures=1,error='Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out'),
 dict(name='connection_then_success',fail_stages=['main'],failures=1,error='ConnectionResetError: connection reset by peer'),
 dict(name='502_then_success',fail_stages=['main'],failures=1,error='OpenRouter HTTP 502: gateway failed'),
 dict(name='504_third_attempt_success',fail_stages=['main'],failures=2,error='HTTP 504 unavailable'),
 dict(name='sdk429_internal_recovery',fail_stages=['main'],failures=0,error='unused',sdk_attempts=3),
 dict(name='503_then400_terminal',errors=['HTTP 503 unavailable','HTTP 400 malformed request']),
 dict(name='timeout_then_unknown_terminal',errors=['TimeoutError: timed out','database connection locked']),
 dict(name='503_generation_evidence',fail_stages=['main'],error='OpenRouter HTTP 503: {"id":"gen-test","choices":[],"usage":{}}'),
 dict(name='503_malformed_json',fail_stages=['main'],error='OpenRouter HTTP 503: {broken'),
 dict(name='unknown_connection_word',fail_stages=['main'],error='database connection locked'),
 dict(name='wrapped_cancel',fail_stages=['main'],error='Inference outcome/cost unconfirmed: TimeoutError: Request cancelled'),
 dict(name='sdk429_then503_mixed_budget',fail_stages=['main'],error='HTTP 503 unavailable',sdk_attempts=5),
 dict(name='delete404_not_retried',write_first=True,first_action=dict(tool='delete',path='/tmp/offline-only'),mutation_error='BitGN HTTP 404: {"code":"not_found","message":"delete failed"}'),
 dict(name='exec500_not_retried',write_first=True,first_action=dict(tool='exec',path='/bin/offline-only',args=['mutate']),mutation_error='BitGN HTTP 503: result unconfirmed'),
 dict(name='openrouter503_cancel',fail_stages=['main'],error='OpenRouter HTTP 503: request cancelled'),
 dict(name='unconfirmed_openrouter503_cancel',fail_stages=['main'],error='Inference outcome/cost unconfirmed: OpenRouter HTTP 503: request cancelled'),
 dict(name='openrouter503_json_cancel',fail_stages=['main'],error='OpenRouter HTTP 503: {"error":{"message":"request cancelled"}}'),
 dict(name='forced503_recovers',malformed=3,fail_stages=['forced'],failures=1,error='HTTP 503 unavailable'),
 dict(name='forced_timeout_exhausts',malformed=3,fail_stages=['forced'],error='Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out'),
 dict(name='forced429_terminal',malformed=3,fail_stages=['forced'],error='OpenRouter HTTP 429: rate limited',sdk_attempts=5),
 dict(name='forced400_terminal',malformed=3,fail_stages=['forced'],error='HTTP 400 connection parameter'),
 dict(name='forced_unknown_terminal',malformed=3,fail_stages=['forced'],error='database is locked'),
]
rows=[]
with monty.Monty() as pool:
 for form in ('readable','packed'):
  source=(P/'guest-owned'/('readable.py' if form=='readable' else 'agent.py')).read_text()
  for case in CASES+EXTRA:
   row=execute(pool,source,case);row.update(form=form,source_sha256=sha(source));rows.append(row)
def row(name):return next(r for r in rows if r['form']=='readable' and r['case']==name)
for case in CASES+EXTRA:
 group=[r for r in rows if r['case']==case['name']]
 for key in ('llm_stages','guest_llm_calls','request_hashes','rpc_calls','mutations','answers'):
  assert group[0][key]==group[1][key],(case['name'],key)
 assert bool(group[0]['raised'])==bool(group[1]['raised'])
for name in ('persistent_503','uncertain_timeout'):
 assert row(name)['llm_stages']==dict(router=1,main=3)
 assert row(name)['answers'][0]['outcome']=='OUTCOME_ERR_INTERNAL'
for name in ('terminal_400_connection_word','unknown_error','sdk429_exhausted','503_generation_evidence','503_malformed_json','unknown_connection_word'):
 assert row(name)['llm_stages']==dict(router=1,main=1)
 assert row(name)['answers'][0]['outcome']=='OUTCOME_ERR_INTERNAL'
for name in ('recoverable_503_on_second_guest_request','timeout_then_success','connection_then_success','502_then_success'):
 assert row(name)['llm_stages']==dict(router=1,main=2)
 assert row(name)['answers'][0]['outcome']=='OUTCOME_NONE_UNSUPPORTED'
assert row('504_third_attempt_success')['llm_stages']==dict(router=1,main=3)
assert row('sdk429_internal_recovery')['llm_stages']==dict(router=1,main=1)
assert row('sdk429_then503_mixed_budget')['llm_stages']==dict(router=1,main=3)
assert row('sdk429_then503_mixed_budget')['simulated_provider_attempts']==16 # router1 + three hypothetical5-attempt SDK calls
for name in ('503_then400_terminal','timeout_then_unknown_terminal'):
 assert row(name)['llm_stages']==dict(router=1,main=2)
for name in ('main_cancel','main_cancel_connection','main_cancel503','wrapped_cancel','openrouter503_cancel','unconfirmed_openrouter503_cancel','openrouter503_json_cancel'):
 assert row(name)['llm_stages']==dict(router=1,main=1)
 assert row(name)['raised'] and not row(name)['answers']
assert row('router_cancel')['llm_stages']==dict(router=1) and row('router_cancel')['raised']
assert row('forced_cancel')['llm_stages']==dict(router=1,main=3,forced=1) and row('forced_cancel')['raised']
assert row('forced503_recovers')['llm_stages']==dict(router=1,main=3,forced=2)
assert row('forced503_recovers')['answers'][0]['outcome']=='OUTCOME_NONE_UNSUPPORTED'
assert row('forced_timeout_exhausts')['llm_stages']==dict(router=1,main=3,forced=3)
for name in ('forced429_terminal','forced400_terminal','forced_unknown_terminal'):
 assert row(name)['llm_stages']==dict(router=1,main=3,forced=1)
assert row('router_negated_cancel_false_positive')['llm_stages']==dict(router=3,main=1)
assert not row('router_negated_cancel_false_positive')['raised']
for name in ('write_then_main_error','write_mutation_error_no_retry'):
 assert len(row(name)['mutations'])==1
assert row('write_mutation_error_no_retry')['raised']
assert row('write_then_main_error')['llm_stages']==dict(router=1,main=4)
for name in ('delete404_not_retried','exec500_not_retried'):
 assert len(row(name)['mutations'])==1 and row(name)['raised']
# Same prompt/model/settings for each repeated main inference after first error;
# only previously executed actions can change a later logical request.
for name in ('persistent_503','uncertain_timeout','timeout_then_success','connection_then_success','503_then400_terminal'):
 calls=[x for x in row(name)['request_details'] if x['stage']=='main']
 assert all(x==calls[0] for x in calls)

src=(P/'guest-owned/readable.py').read_text();parent=(P/'parent-readable.py').read_text()
def defs(source,names):
 return '\n'.join(ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names)
control_source='import json\nimport re\n'+defs(src,{'inference_cancelled','inference_retryable','inference_call'})
class ClassifierHost:
 def __init__(self):self.results=[]
 def record(self,result):self.results.append(result)
classifiers=[
 ('HTTP 400 connection timeout unavailable',False,False),('OpenRouter HTTP 429: rejected',False,False),
 ('HTTP 401 unauthorized',False,False),('HTTP 500 internal error',False,False),('HTTP 503 unavailable',False,True),
 ('HTTP 503 request cancelled',True,False),('Cancelled: connection closed',True,False),
 ('HTTP 503 request was not cancelled; unavailable',False,True),('HTTP 400 invalid cancellation_policy',False,False),
 ('TimeoutError: request was not cancelled',False,True),('Inference outcome/cost unconfirmed: TimeoutError: Request cancelled',True,False),
 ('OpenRouter HTTP 503: {"choices":[]}',False,False),('OpenRouter HTTP 503: {"usage":{}}',False,False),
 ('OpenRouter HTTP 503: {"id":""}',False,False),('OpenRouter HTTP 503: {broken',False,False),
 ('OpenRouter HTTP 503: {"error":{"message":"upstream unavailable"}}',False,True),
 ('temporary connection timeout unavailable',False,False),('request canceled',True,False),('Cancellation requested',True,False),
 ('Sandbox job cancelled',True,False),('ConnectionError: unknown connection failure',False,True),
 ('OpenRouter HTTP 503: request cancelled',True,False),
 ('Inference outcome/cost unconfirmed: OpenRouter HTTP 503: request cancelled',True,False),
 ('OpenRouter HTTP 503: {"error":{"message":"request cancelled"}}',True,False),
 ('OpenRouter HTTP 503: {"error":{"message":"request was not cancelled; upstream unavailable"}}',False,True),
 ('OpenRouter HTTP 503: [broken',False,False),
 ('OpenRouter HTTP 503: [{"id":"gen-synthetic","choices":[],"usage":{}}]',False,False),
 ('OpenRouter HTTP 503: []',False,False),
]
host=ClassifierHost()
with monty.Monty() as pool:
 with pool.checkout(limits=LIMITS) as session:
  session.feed_run(control_source+'\nfor error in errors:\n bitgn.record([inference_cancelled(RuntimeError(error)),inference_retryable(RuntimeError(error))])',
    inputs={'bitgn':monty.ClassInstance(host,allowed_methods={'record'}),'errors':[x[0] for x in classifiers]})
assert host.results==[[c,r] for e,c,r in classifiers]
# This timeout suffix is actual archived evidence, not an invented transient.
actual_timeouts=[]
for task in ('t003','t045','t056','t059'):
 relative='2026-10-22-provider-control-review/new-failure-'+task+'.json'
 actual=json.loads((P.parent/relative).read_text())
 timeout_event=next(e for e in actual['events'] if e['kind']=='llm_error')
 agent_error=next(e for e in actual['events'] if e['kind']=='agent_error')
 assert timeout_event['data']['error']=='TimeoutError: The read operation timed out'
 assert 'RuntimeError: Inference outcome/cost unconfirmed: '+timeout_event['data']['error'] in agent_error['data']['error']
 assert next(c for c in EXTRA if c['name']=='timeout_then_success')['error']=='Inference outcome/cost unconfirmed: '+timeout_event['data']['error']
 actual_timeouts.append(dict(source=relative,seq=timeout_event['seq'],call=timeout_event['data']['call'],error=timeout_event['data']['error'],wrapper_verified_in_agent_error=True))
helpers=[]
names={'inference_cancelled','inference_retryable','inference_call','i2c_llm_narrow','i2c_dispatch','i2c_flat'}
code='import json\nimport re\n'+defs(src,names)
outer=next(n for n in ast.parse(src).body if isinstance(n,ast.If) and any(isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='i2c_dispatch' for c in ast.walk(n)))
code+='\nINSTRUCTION="SKU only mystery model"\ndef helper_probe(ins):\n return i2c_llm_narrow(ins,[])\nI2C_MODULES=[["helper",helper_probe]]\nanswered=False\n'+ast.get_source_segment(src,outer)
for error,count,raises in [('HTTP 503 unavailable',3,False),('HTTP 400 invalid connection parameter',1,False),('Cancelled: connection closed',1,True),('Inference outcome/cost unconfirmed: TimeoutError: Request cancelled',1,True)]:
 h=Host(dict(name='isolated-helper',fail_stages=['main'],error=error));failure=None
 with monty.Monty() as pool:
  try:
   with pool.checkout(limits=LIMITS) as session:
    session.feed_run(code,inputs={'bitgn':monty.ClassInstance(h,allowed_methods={'llm','answer'})},print_callback=lambda *a:None)
  except Exception as exc:failure=str(exc)
 assert len(h.llms)==count and bool(failure)==raises and not h.answers
 helpers.append(dict(error=error,guest_calls=len(h.llms),raised=failure))
# Lookup recovery is exactly unchanged, including the known broad parent Exec404
# issue. Do not silently combine that separate repair with inference work.
assert defs(src,{'recoverable_lookup_error','dispatch'})==defs(parent,{'recoverable_lookup_error','dispatch'})
requests={r['form']+'/'+r['case']:r.pop('request_details') for r in rows}
(P/'guest-owned/fake-requests.json').write_text(json.dumps(requests,indent=2)+'\n')
out=dict(status='passed',whole_agent_executions=len(rows),scenarios=len(CASES+EXTRA),
    isolated_nested_helper_controls=helpers,
    actual_timeout_events=actual_timeouts,
    native_classifier_cases=[dict(error=e,cancelled=c,retryable=r) for e,c,r in classifiers],
    controls='Public method-only native Monty; fake inference only; SDK429 behavior declared simulation',
    real_model_calls=0,mutation_retry=False,lookup_recovery_identical=True,results=rows)
(P/'guest-owned/test-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('status','whole_agent_executions','scenarios','real_model_calls','mutation_retry')}))
