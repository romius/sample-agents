"""Exact d4353 whole-agent source controls with fake inference and fake effects."""
import copy,hashlib,json,platform
from importlib.metadata import version
assert version("pydantic-monty")=="1.2.0"
from pathlib import Path
import pydantic_monty as monty
P=Path(__file__).resolve().parent;W=json.loads((P/'fixture/world.json').read_text())
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
sha=lambda x:hashlib.sha256(x.encode()).hexdigest()
LIMITS=dict(max_feed_duration_secs=10,max_turn_duration_secs=10,max_suspensions=1000)
ARITHMETIC='Answer the arithmetic question: what is 1 + 1? Give only the number. Do not create or change any files.'
def reply(content,finish='stop'):return {'choices':[{'finish_reason':finish,'message':{'content':content}}]}
def report(message,outcome):return dict(tool='report_completion',completed_steps_laconic=[],message=message,outcome=outcome,grounding_refs=[])
CLARIFY=report('No export has been written in this scripted run; further catalogue work is needed.','OUTCOME_NONE_CLARIFICATION')
TWO=report('2','OUTCOME_OK')
RECOVERY=report('SCRIPTED recovery response; no completion claim.','OUTCOME_NONE_UNSUPPORTED')
payloads=[
 ('clarification_stop',reply(json.dumps(CLARIFY)),False),('clarification_length',reply(json.dumps(CLARIFY),'length'),False),
 ('readonly_OK_stop',reply(json.dumps(TWO)),True),('readonly_OK_length',reply(json.dumps(TWO),'length'),True),
 ('readonly_OK_fenced_stop',reply('```json\n'+json.dumps(TWO)+'\n```'),True),
 ('readonly_OK_fenced_length',reply('```json\n'+json.dumps(TWO)+'\n```','length'),True),
 ('partial_report_length',reply('{"tool":"report_completion","message":"unfinished','length'),False),
 ('partial_report_stop',reply('{"tool":"report_completion","message":"unfinished'),False),
 ('null_stop',reply(None),False),('null_length',reply(None,'length'),False),
 ('nonreport_read_stop',reply('{"tool":"read","path":"/docs/security.md"}'),False),
 ('nonreport_read_length',reply('{"tool":"read","path":"/docs/security.md"}','length'),False),
 ('report_prefix_truncated_tail_length',reply(json.dumps(TWO)+'{"tool":"report_completion","message":"Actually','length'),True),
 ]
for tool,action in [('write',dict(tool='write',path=W['export'],content='SYNTHETIC artifact bytes')),
 ('delete',dict(tool='delete',path='/tmp/boundary-canary.txt')),
 ('exec',dict(tool='exec',path='/bin/discount',args=['SYNTHETIC'],stdin=''))]:
 for finish in ['stop','length']:payloads.append((tool+'_'+finish,reply(json.dumps(action),finish),False))
cases=[{'name':stage+'_'+name,'stage':stage,'payload_name':name,'response':body,'arithmetic_overlay':overlay} for stage in ['main','forced'] for name,body,overlay in payloads]
class Host:
 def __init__(self,case):self.case=case;self.calls=[];self.requests=[];self.responses=[];self.answers=[];self.counts={};self.unmatched=[];self.effects=[];self.files={'/tmp/boundary-canary.txt':'KEEP'}
 def task(self):
  t=copy.deepcopy(W['task'])
  if self.case['arithmetic_overlay']:t['instruction']=ARITHMETIC
  return t
 def usage(self):return {'offline':True,'model_calls':0}
 def answer(self,message,*,outcome,refs):self.answers.append(dict(message=message,outcome=outcome,refs=refs));return {}
 def call(self,method,args):
  self.calls.append([method,copy.deepcopy(args)])
  if method in ['Write','Delete'] or method=='Exec' and args['path'] not in ['/bin/date','/bin/id']:
   self.effects.append([method,copy.deepcopy(args)])
   if method=='Write':self.files[args['path']]=args['content']
   elif method=='Delete':self.files.pop(args['path'],None)
   return {'stdout':'SYNTHETIC acknowledged effect'} if method=='Exec' else {}
  key=canon([method,args])
  for table in ['rpc','derived_rpc']:
   if key in W[table]:return copy.deepcopy(W[table][key])
  self.unmatched.append([method,args]);raise RuntimeError('Unmatched offline RPC '+key)
 def llm(self,*args,**kwargs):
  stage='router' if kwargs['max_completion_tokens']==1024 else 'forced' if args[1][-1]['content'].startswith('Stop working now.') else 'main'
  self.counts[stage]=self.counts.get(stage,0)+1;n=self.counts[stage]
  self.requests.append(dict(stage=stage,args=copy.deepcopy(args),kwargs=copy.deepcopy(kwargs)))
  if stage=='router':res=reply('{"docs": []}') if self.case['arithmetic_overlay'] else copy.deepcopy(W['router_response'])
  elif stage=='main' and self.case['stage']=='forced':
   # Mixed failures prove the shared consecutive-invalid counter, without a retry exception.
   assert n<=3;res=[reply(None),reply('{','length'),reply('not JSON')][n-1]
  elif stage==self.case['stage'] and n==1:res=copy.deepcopy(self.case['response'])
  else:res=reply(json.dumps(RECOVERY))
  self.responses.append(copy.deepcopy(res));return res
def run(pool,source,case):
 h=Host(case);out=[];error=None
 try:
  with pool.checkout(limits=LIMITS) as session:
   session.feed_run(source,inputs={'bitgn':monty.ClassInstance(h,allowed_methods={'task','call','answer','llm','usage'})},print_callback=lambda *a:out.append(str(a[-1])))
 except Exception as exc:error=str(exc)
 assert not h.unmatched and error is None,(case['name'],h.unmatched,error)
 return dict(case=case['name'],counts=h.counts,requests=h.requests,scripted_responses=h.responses,rpc_calls=h.calls,answers=h.answers,synthetic_effects=h.effects,synthetic_file_state=h.files,output=''.join(out),error=error)
rows=[]
with monty.Monty() as pool:
 for form,path in [('readable','parent-readable.py'),('packed','parent.py')]:
  source=(P/path).read_text()
  for c in cases:
   r=run(pool,source,c);r.update(form=form,source_sha256=sha(source));rows.append(r)
for c in cases:
 a,b=[r for r in rows if r['case']==c['name']]
 for key in ['counts','requests','scripted_responses','rpc_calls','answers','synthetic_effects','synthetic_file_state','output','error']:assert a[key]==b[key],(c['name'],key)
 assert len(a['answers'])==1
 main=c['stage']=='main';name=c['payload_name'];finish=c['response']['choices'][0]['finish_reason'];content=c['response']['choices'][0]['message']['content']
 complete_report=name.startswith(('clarification_','readonly_OK_','report_prefix_'))
 accepted_report=complete_report and (not main or finish!='length')
 if accepted_report:assert a['answers'][0]['message']==('2' if c['arithmetic_overlay'] else CLARIFY['message'])
 elif main:assert a['answers'][0]['message']==RECOVERY['message']
 else:assert a['answers'][0]['outcome']=='OUTCOME_ERR_INTERNAL' and '30-step limit' in a['answers'][0]['message']
 assert a['counts']==({'router':1,'main':1 if accepted_report else 2} if main else {'router':1,'main':3,'forced':1})
 ismutation=name.startswith(('write_','delete_','exec_'));expected_effect=main and ismutation and finish=='stop'
 assert len(a['synthetic_effects'])==int(expected_effect),(c['name'],a['synthetic_effects'])
 if not expected_effect:assert a['synthetic_file_state']=={'/tmp/boundary-canary.txt':'KEEP'}
 if not main:
  assert a['requests'][-1]['stage']=='forced';assert a['requests'][-1]['kwargs']==a['requests'][1]['kwargs']
# Cross-case controls: only a main stop Read executes the injected lookup.
lookup=['Read',{'path':'/docs/security.md'}]
bycase={r['case']:r for r in rows if r['form']=='readable'}
base=bycase['main_clarification_stop']['rpc_calls'].count(lookup)
for stage in ['main','forced']:
 for finish in ['stop','length']:
  row=bycase[stage+'_nonreport_read_'+finish]
  assert row['rpc_calls'].count(lookup)==base+int(stage=='main' and finish=='stop')
for r in rows:
 for q in r['requests']:
  if q['stage']!='router':
   assert q['kwargs']=={'max_completion_tokens':2048,'reasoning':{'effort':'medium'},'temperature':0}
# Public native proxy boundary control: no lazy method extraction is enabled.
with monty.Monty() as pool:
 h=Host(cases[0]);failed=False
 try:
  with pool.checkout(limits=LIMITS) as session:session.feed_run('callback = bitgn.call',inputs={'bitgn':monty.ClassInstance(h,allowed_methods={'call'})})
 except Exception as exc:failed='AttributeError' in str(exc)
 assert failed
requests={r['form']+'/'+r['case']:r.pop('requests') for r in rows}
responses={r['form']+'/'+r['case']:r.pop('scripted_responses') for r in rows}
for name,obj in [('cases.json',cases),('requests.json',requests),('responses.json',responses),('results.json',{'status':'PASS exact-source native whole-agent controls','python':platform.python_version(),'monty':'1.2.0','executions':len(rows),'scenarios':len(cases),'limits':LIMITS,'method_only_proxy_negative_control':True,'real_model_calls':0,'all_effects_in_memory':True,'results':rows})]: (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(rows),'whole-agent executions; readable/packed parity, exact stage/call/effect assertions; no real inference.')
