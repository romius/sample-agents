"""Verify exact paired inputs, bounded calls, native packing and error recording."""
import copy
import contextlib
import hashlib
import io
import json
from pathlib import Path
import pydantic_monty as monty
HERE=Path(__file__).resolve().parent
bundle=json.loads((HERE/'fixtures.json').read_text())
canonical=lambda obj:json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
for fixture in bundle['fixtures']:
 p=fixture['arms']['parent'];t=copy.deepcopy(fixture['arms']['treatment'])
 header,body=t['messages'][9]['content'].split('\n',1)
 observation=json.loads(body);evidence=observation.pop('sku_lookup_evidence')
 assert evidence['request_description'] and evidence['pool_complete'] is False
 t['messages'][9]['content']=header+'\n'+json.dumps(observation)
 assert t==p
 for arm,request in fixture['arms'].items():
  assert hashlib.sha256(canonical(request)).hexdigest()==fixture['request_sha256'][arm]
 assert [s['arm'] for s in bundle['plan'] if s['case']==fixture['case']].count('parent')==2
class Host:
 def __init__(self,fail):self.calls=[];self.answers=[];self.fail=fail
 def llm(self,model,messages,**kwargs):
  request=dict(model=model,messages=copy.deepcopy(messages),**kwargs)
  step=bundle['plan'][len(self.calls)]
  assert request==bundle['fixtures'][step['case_index']]['arms'][step['arm']]
  self.calls.append(request)
  if self.fail and len(self.calls)==3:raise RuntimeError('simulated provider timeout')
  return {'choices':[{'message':{'content':'{"tool":"read","path":"/proc/catalog/example.json"}'},'finish_reason':'stop'}],'usage':{'cost':0.001}}
 def usage(self):return {'calls':len(self.calls),'cost':0.016}
 def answer(self,*args,**kwargs):self.answers.append([args,kwargs])
proxy='''class Proxy:
 def llm(self,*a,**k):return host_llm(*a,**k)
 def usage(self):return host_usage()
 def answer(self,*a,**k):return host_answer(*a,**k)
bitgn=Proxy()
'''
rows=[]
for form in ['readable.py','agent.py']:
 for native in [False,True]:
  for fail in [False,True]:
   host=Host(fail);out=[];source=(HERE/form).read_text()
   if native:
    with monty.Monty() as engine:
     with engine.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as session:
      session.feed_run(proxy+source,external_lookup={'host_llm':host.llm,'host_usage':host.usage,'host_answer':host.answer},print_callback=lambda *a:out.append(str(a[1]) if len(a)>1 else str(a[0])))
    output=''.join(out)
   else:
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream):exec(source,dict(bitgn=host))
    output=stream.getvalue()
   results=[json.loads(line.split(' ',1)[1]) for line in output.splitlines() if line.startswith('SKU_DIAGNOSTIC_RESULT ')]
   assert len(host.calls)==16 and len(host.answers)==1 and len(results)==16
   assert sum('error' in r for r in results)==int(fail)
   assert host.answers[0][1]==dict(outcome='OUTCOME_NONE_UNSUPPORTED',refs=[])
   rows.append(dict(form=form,native=native,simulated_provider_error=fail,logical_calls=16,raw_result_records=16))
(HERE/'verification.json').write_text(json.dumps(dict(status='passed',executions=rows,notes='Only host_llm/usage/answer exposed. Exact ordered paired requests verified; no ECOM RPCs or real model calls. Native limits10sec/1000 suspensions.'),indent=2)+'\n')
print('PASS:8 diagnostic runner executions; exact ordered16 calls, both forms/runtimes, provider-error preservation, single final answer, no ECOM RPCs.')
