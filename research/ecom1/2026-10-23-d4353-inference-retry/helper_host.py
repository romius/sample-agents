"""Exact whole-agent helper reachability using a declared synthetic task/policy overlay."""
import copy
import json
import pydantic_monty as monty
from host import P,W,Host,execute,response,sha,canon

OVERLAY=dict(instruction="Do you have 1 'mystery model QZX777' (but not PT-UNKNOWN) in stock in Graz Center?",policy_path='/docs/catalogue-lookup.md',
 policy='Products live in `/proc/catalog`. Answer the SKU only when exactly one product matches. Cite the candidate and all mentioned SKUs. Otherwise clarify.',
 availability_policy='Same-day stock is max(on_hand - reserved, 0). Products absent from a branch inventory have zero stock. Future availability uses arrival_in_days.',
 router_response={'choices':[{'finish_reason':'stop','message':{'content':'{"docs":[]}'}}]},
 helper_success_response={'choices':[{'finish_reason':'stop','message':{'content':'{}'}}]})
class HelperHost(Host):
 def task(self):
  task=super().task();task['instruction']=OVERLAY['instruction'];return task
 def call(self,method,args):
  if method=='Read' and args.get('path')=='/docs/availability-checks.md':
   self.calls.append([method,copy.deepcopy(args)]);return {'content':OVERLAY['availability_policy']}
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
