"""Exact-source same-world native replay; archived model bodies + scripted continuation."""
import copy,json,hashlib
from pathlib import Path
import pydantic_monty as monty
P=Path(__file__).resolve().parent;W=json.loads((P/'world.json').read_text())
LIMITS=dict(max_feed_duration_secs=10,max_turn_duration_secs=10,max_suspensions=1000)
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'));sha=lambda x:hashlib.sha256(x.encode()).hexdigest()
def response(action):return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(action)}}]}
def err(message,code='not_found'):return 'BitGN HTTP 404: '+json.dumps({'code':code,'message':message})
CASES=[dict(name='actual_boundary',error=W['original_error'],recover=True),dict(name='raw_http_equivalent',error=W['original_error'][len('RuntimeError: '):],recover=True),dict(name='fresh_missing_executable',error=err('runtime tool not found: /bin/new-tool'),action={'tool':'exec','path':'/bin/new-tool','args':[]},recover=True),
 dict(name='generic404',error=err('not found')),dict(name='invoice404',error=err('invoice not found: INV-7'),action={'tool':'exec','path':'/bin/invoice','args':['INV-7']}),dict(name='payment404',error=err('payment not found: pay-9'),action={'tool':'exec','path':'/bin/payments','args':['pay-9']}),
 dict(name='malformed_json',error='BitGN HTTP 404: {broken'),dict(name='array_json',error='BitGN HTTP 404: []'),dict(name='prefix_collision',error=err('runtime tool not foundry inventory missing')),dict(name='nonstring_message',error=err(['runtime tool not found: not found'])),dict(name='wrong_code',error=err('runtime tool not found: not found','permission_denied')),
 dict(name='non404500',error='BitGN HTTP 500: runtime tool not found: not found'),dict(name='non404400',error='BitGN HTTP 400: invalid arguments',inherited_recovery=True),dict(name='non404403',error='BitGN HTTP 403: denied',inherited_recovery=True),
 dict(name='existing_sql_exit1',result={'exitCode':1,'stderr':'SQL syntax error'},action={'tool':'exec','path':'/bin/sql','args':['bad query']},inherited_recovery=True),dict(name='healthy_exec',result={'stdout':'SCRIPTED success'},inherited_recovery=True),
 dict(name='delete404',error=err('not found'),action={'tool':'delete','path':'/tmp/scripted-target'},inherited_recovery=True),dict(name='delete_malformed404',error='BitGN HTTP 404: {broken',action={'tool':'delete','path':'/tmp/scripted-target'},inherited_recovery=True),dict(name='delete500',error='BitGN HTTP 500: failed',action={'tool':'delete','path':'/tmp/scripted-target'})]
CONTINUATION=[{'tool':'tree','root':'/','level':2},{'tool':'report_completion','message':'Scripted recovery stopped without updating the basket.','outcome':'OUTCOME_ERR_INTERNAL','grounding_refs':['/docs/checkout.md']}]
class Host:
 def __init__(self,case):self.case=case;self.calls=[];self.llms=[];self.answers=[];self.unmatched=[];self.target_calls=[];self.help_calls=[];self.effect_records=[]
 def task(self):return copy.deepcopy(W['task'])
 def usage(self):return {'offline':True}
 def answer(self,message,*,outcome,refs):self.answers.append(dict(message=message,outcome=outcome,refs=refs));return {}
 def call(self,method,args):
  self.calls.append([method,copy.deepcopy(args)])
  action=self.case.get('action',{'tool':'exec',**W['original_exec']});target_method=action['tool'].capitalize();target_path=action['path']
  if method==target_method and args.get('path')==target_path:
   if method=='Exec' and args.get('args')==['--help']:
    self.help_calls.append([method,copy.deepcopy(args)]);raise RuntimeError('SCRIPTED help unavailable')
   self.target_calls.append([method,copy.deepcopy(args)])
   if self.case.get('side_effect'):self.effect_records.append([method,copy.deepcopy(args)])
   if 'error' in self.case:raise RuntimeError(self.case['error'])
   return copy.deepcopy(self.case['result'])
  key=canon([method,args])
  for name in ('rpc','derived_rpc'):
   if key in W[name]:return copy.deepcopy(W[name][key])
  if method=='Read' and args.get('path') in W['files']:
   # d4353 can attach explicit false/zero line options. Return exact same whole
   # archived file only for default-equivalent options, never partial invention.
   assert all(k=='path' or v in (False,0) for k,v in args.items());return copy.deepcopy(W['files'][args['path']])
  self.unmatched.append([method,args]);raise RuntimeError('UNMATCHED '+key)
 def llm(self,*args,**kwargs):
  self.llms.append({'args':copy.deepcopy(args),'kwargs':copy.deepcopy(kwargs)})
  n=len(self.llms)
  if n==1:return copy.deepcopy(W['router_response'])
  if n<=4:
   if n==4 and self.case.get('action'):return response(self.case['action'])
   return copy.deepcopy(W['model_responses'][n-2])
  assert n<=6,n
  return response(CONTINUATION[n-5])
def run(source,case,engine):
 h=Host(case);output=[];error=None
 try:
  if engine=='CPython':exec(source,{'bitgn':h,'print':lambda *a:output.append(' '.join(map(str,a))+'\n')})
  else:
   with monty.Monty() as pool:
    with pool.checkout(limits=LIMITS) as s:s.feed_run(source,inputs={'bitgn':monty.ClassInstance(h,allowed_methods={'task','call','llm','answer','usage'})},print_callback=lambda *a:output.append(str(a[-1])))
 except Exception as exc:error=str(exc)
 assert not h.unmatched,(case['name'],h.unmatched)
 return {'case':case['name'],'engine':engine,'calls':h.calls,'llm_requests':h.llms,'llm_calls':len(h.llms),'answers':h.answers,'target_calls':h.target_calls,'help_calls':h.help_calls,'side_effects':h.effect_records,'error':error,'output':''.join(output)}
# Business404 after a scripted side effect must still propagate without replay.
for name in ['invoice404','payment404']:
 c=copy.deepcopy(next(c for c in CASES if c['name']==name));c['name']+='_after_effect';c['side_effect']=True;CASES.append(c)
rows=[]
for version in ('parent','candidate'):
 for form in ('readable','packed'):
  path=P/('parent-readable.py' if form=='readable' else 'parent.py') if version=='parent' else P/('readable.py' if form=='readable' else 'agent.py')
  source=path.read_text()
  for engine in ('CPython','native'):
   for case in CASES:
    r=run(source,case,engine);r.update(version=version,form=form,source_sha256=sha(source));rows.append(r)
for case in CASES:
 for version in ('parent','candidate'):
  group=[r for r in rows if r['case']==case['name'] and r['version']==version]
  for key in ('calls','llm_requests','llm_calls','answers','target_calls','help_calls','side_effects'):
   assert all(x[key]==group[0][key] for x in group),(case['name'],version,key)
  recover=case.get('inherited_recovery') or case.get('recover') and version=='candidate'
  for r in group:
   assert bool(r['error'])==(not bool(recover)),(case['name'],version,r['error'])
   assert len(r['target_calls'])==1
   assert len(r['answers'])==int(bool(recover)) and r['llm_calls']==(6 if recover else 4)
   if case.get('recover') and version=='candidate':
    assert not r['help_calls'] and 'unavailable_tool' in r['llm_requests'][4]['args'][1][-1]['content']
   if case.get('side_effect'):assert len(r['side_effects'])==1
  if not case.get('recover'):
   p=next(r for r in rows if r['version']=='parent' and r['form']=='readable' and r['engine']=='native' and r['case']==case['name'])
   q=next(r for r in rows if r['version']=='candidate' and r['form']=='readable' and r['engine']=='native' and r['case']==case['name'])
   for key in ('calls','llm_requests','answers','target_calls','help_calls','side_effects'):assert p[key]==q[key],(case['name'],key)
# Actual witness input requests before first failed Exec are identical across
# parent/candidate; archived inference bodies are reused, not regenerated.
a=next(r for r in rows if r['case']=='actual_boundary' and r['version']=='parent' and r['form']=='readable' and r['engine']=='native')
b=next(r for r in rows if r['case']=='actual_boundary' and r['version']=='candidate' and r['form']=='readable' and r['engine']=='native')
assert a['llm_requests']==b['llm_requests'][:4]
assert a['error'].splitlines()[-1]==W['original_agent_error'].splitlines()[-1]
(P/'cases.json').write_text(json.dumps(CASES,indent=2)+'\n');(P/'continuation.json').write_text(json.dumps(CONTINUATION,indent=2)+'\n')
requests={r['version']+'/'+r['form']+'/'+r['engine']+'/'+r['case']:r.pop('llm_requests') for r in rows}
(P/'requests.json').write_text(json.dumps(requests,indent=2)+'\n')
report={'status':'PASS','whole_agent_executions':len(rows),'native_executions':len(rows)//2,'scenarios':len(CASES),'limits':LIMITS,'parent_actual_error_final_line_equal':True,'no_actual_task_completion_claim':True,'results':rows}
(P/'whole-results.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='results'})
