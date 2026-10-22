"""Observed error strings against frozen queued guard functions; not task replay."""
import copy
import json
from pathlib import Path
import pydantic_monty as monty
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
observed=json.loads((HERE/'observations.json').read_text())
source=(ROOT/'2026-10-22-inventory-integration/readable.py').read_text().split('\nIX_RESULT=')[0]
request=json.loads(observed['exec_request']['text'])['data']['arguments']
error=json.loads(observed['exec_error']['text'])['data']['error']
action=dict(tool='exec',**request)
ns={};exec(source,ns)
positive=ns['recoverable_lookup_error'](action,RuntimeError(error))
assert positive['unavailable_tool']=='/bin/grep' and 'lookup_error' in positive
# Do not transform any path-not-found or malformed status into a safe missing exec.
for message in ['BitGN HTTP 404: {"code":"not_found","message":"path not found"}', 'BitGN HTTP 404: malformed', 'BitGN HTTP 500: unavailable']:
 assert ns['recoverable_lookup_error'](action,RuntimeError(message)) is None
class Host:
 def __init__(self,error,permanent=False):self.error=error;self.calls=[];self.permanent=permanent
 def llm(self,*a,**k):
  self.calls.append(copy.deepcopy([a,k]))
  if self.permanent or len(self.calls)<3:raise RuntimeError(self.error)
  return {'response':'third attempt returned'}
rows=[]
for failure in observed['failures']:
 if failure['task_id']=='t059':continue
 # The outer traceback is harness decoration, not str(exception) inside MSR.
 message=failure['error'].split('\n')[-1].removeprefix('RuntimeError: ')
 for permanent in [False,True]:
  host=Host(message,permanent);ns['bitgn']=host
  raised=False
  try:result=ns['MSR']('openai/gpt-oss-120b',[dict(role='user',content='fixed request')],max_tokens=2048)
  except RuntimeError:raised=True
  assert raised==permanent and len(host.calls)==3 and host.calls[0]==host.calls[1]==host.calls[2]
  rows.append(dict(task=failure['task_id'],permanent=permanent,attempts=3,identical_inference_requests=True))
# Native run checks both exact observed error forms in the actual functions.
code=source+'''\nclass Fake:
 def __init__(self):self.calls=0
 def llm(self,*a,**k):
  self.calls+=1
  if self.calls<3:raise RuntimeError(timeout_message)
  return {'ok':True}
bitgn=Fake()
assert MSR('model',[])=={'ok':True} and bitgn.calls==3
assert recoverable_lookup_error(action,RuntimeError(exec_error))['unavailable_tool']=='/bin/grep'
print('PASS native')
'''
with monty.Monty() as engine:
 with engine.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as session:
  session.feed_run(code,inputs=dict(action=action,exec_error=error,timeout_message=message),print_callback=lambda *a:None)
(HERE/'verification.json').write_text(json.dumps(dict(status='passed',observed_missing_exec_action=action,guard_response=positive,inference_cases=rows,native=True,
 limitations='Concrete observed errors accepted by existing queued guards. Inference replay is simulated; no claim provider will succeed on retry, missing costs recovered, later task completes, or code caused any score difference.'),indent=2)+'\n')
print('PASS: exact community Exec404 maps to narrow recovery; four timeout strings receive bounded identical inference retries, permanent errors stop afterthree; native compatibility.')
