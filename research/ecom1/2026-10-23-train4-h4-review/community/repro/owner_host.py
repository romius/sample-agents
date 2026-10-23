import copy,json,hashlib
W=None
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def sha(x):return hashlib.sha256(x.encode()).hexdigest()
class Host:
 def __init__(self,ocr):self.ocr=ocr;self.calls=[];self.answers=[];self.writes=[];self.llms=[];self.unmatched=[];self.derivations=[]
 def task(self):return copy.deepcopy(W['task'])
 def usage(self):return {'offline_replay':True,'model_calls':0,'reported_cost_usd':'0'}
 def answer(self,message,*,outcome,refs):self.answers.append({'message':message,'outcome':outcome,'refs':refs});return {}
 def call(self,method,args):
  self.calls.append([method,copy.deepcopy(args)])
  key=canon([method,args])
  if method=='Write':
   assert set(args)=={'path','content'} and args['path']==W['export']
   self.writes.append(copy.deepcopy(args));return {'path':args['path']}
  if key in W['rpc']:
   r=copy.deepcopy(W['rpc'][key])
   if method=='Read' and args.get('path')==W['upload']:
    r['content']=self.ocr;r['sha256']=sha(self.ocr)
   return r
  if key in W['derived_rpc']:
   self.derivations.append([method,copy.deepcopy(args)]);return copy.deepcopy(W['derived_rpc'][key])
  self.unmatched.append([method,copy.deepcopy(args)]);raise RuntimeError('UNMATCHED OFFLINE RPC '+key)
 def llm(self,*args,**kwargs):
  self.llms.append({'args':copy.deepcopy(args),'kwargs':copy.deepcopy(kwargs)})
  if len(self.llms)==1:return copy.deepcopy(W['router_response'])
  # Fixed terminal stub when deterministic handling declines; never attempts task solving.
  action={'tool':'report_completion','completed_steps_laconic':[],'message':'OFFLINE FALLBACK: deterministic handler declined.','outcome':'OUTCOME_NONE_UNSUPPORTED','grounding_refs':[]}
  return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(action)}}]}
