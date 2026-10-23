"""Exact whole-agent helper reachability using a declared synthetic task/policy overlay."""
import copy
import json
import pydantic_monty as monty
from test_native import P,W,Host,execute,response,sha,canon

OVERLAY=dict(instruction='SKU only for mystery model QZX777.',policy_path='/docs/catalogue-lookup.md',
 policy='Products live in `/proc/catalog`. Answer the SKU only when exactly one product matches. Cite the candidate and all mentioned SKUs. Otherwise clarify.',
 router_response={'choices':[{'finish_reason':'stop','message':{'content':'{"docs":[]}'}}]},
 helper_success_response={'choices':[{'finish_reason':'stop','message':{'content':'{}'}}]})
class HelperHost(Host):
 def task(self):
  task=super().task();task['instruction']=OVERLAY['instruction'];return task
 def call(self,method,args):
  if method=='Read' and args.get('path')==OVERLAY['policy_path']:
   self.calls.append([method,copy.deepcopy(args)]);return {'content':OVERLAY['policy']}
  if method=='Read' and args.get('path') in W['files']:
   self.calls.append([method,copy.deepcopy(args)]);return copy.deepcopy(W['files'][args['path']])
  return super().call(method,args)
 def llm(self,*args,**kwargs):
  if kwargs.get('max_completion_tokens')==200:
   stage='helper';self.counts[stage]=self.counts.get(stage,0)+1
   self.llms.append(dict(stage=stage,args=copy.deepcopy(args),kwargs=copy.deepcopy(kwargs)));self.provider_attempts+=1
   if self.counts[stage]<=self.case['helper_failures']:raise RuntimeError(self.case['helper_error'])
   return copy.deepcopy(OVERLAY['helper_success_response'])
  if kwargs.get('max_completion_tokens')==1024:
   # Preserve logging through the original fake host, but use explicit no-route
   # response for this synthetic helper task rather than the archived OCR route.
   super().llm(*args,**kwargs);return copy.deepcopy(OVERLAY['router_response'])
  return super().llm(*args,**kwargs)
cases=[dict(name='helper_cancel',helper_error='OpenRouter HTTP 503: request cancelled',helper_failures=99),
       dict(name='helper400_fallback',helper_error='HTTP 400 invalid cancellation_policy',helper_failures=99),
       dict(name='helper503_recovers',helper_error='HTTP 503 unavailable',helper_failures=1),
       dict(name='helper_timeout_exhausts',helper_error='Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out',helper_failures=99)]
rows=[]
with monty.Monty() as pool:
 for version in ('parent','sdk-only','guest-owned'):
  for form in ('readable','packed'):
   path=P/('parent-readable.py' if form=='readable' else 'parent.py') if version=='parent' else (P/'guest-owned' if version=='guest-owned' else P)/('readable.py' if form=='readable' else 'agent.py')
   source=path.read_text()
   for case in cases:
    row=execute(pool,source,case,HelperHost);row.update(version=version,form=form,source_sha256=sha(source));rows.append(row)
for row in rows:
 expected=2 if row['case']=='helper503_recovers' else 3
 if row['version']!='guest-owned' or row['case'] in ('helper_cancel','helper400_fallback'):expected=1
 assert row['llm_stages']['helper']==expected,(row['version'],row['case'],row['llm_stages'])
 cancel=row['case']=='helper_cancel' and row['version']!='parent'
 assert bool(row['raised'])==cancel
 assert ('main' not in row['llm_stages'])==cancel
 assert not row['mutations']
 calls=[c for c in row['request_details'] if c['stage']=='helper']
 assert all(c==calls[0] for c in calls)
for version in ('parent','sdk-only','guest-owned'):
 for case in cases:
  group=[r for r in rows if r['version']==version and r['case']==case['name']]
  for key in ('llm_stages','request_hashes','rpc_calls','mutations','answers'):
   assert group[0][key]==group[1][key]
(P/'helper-whole-fixture.json').write_text(json.dumps(OVERLAY,indent=2)+'\n')
(P/'helper-whole-results.json').write_text(json.dumps(dict(status='passed',whole_agent_executions=len(rows),
 scope='Exact whole source; synthetic task/catalogue-policy/router/helper overlay; archived catalogue files and Tree; no replaced agent functions',
 real_model_calls=0,results=rows),indent=2)+'\n')
print('PASS24 exact whole-agent helper executions; no replaced source functions.')
