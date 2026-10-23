"""Whole-source offline handoff mechanisms; fixed replies, never model outcomes."""
import copy,hashlib,json,contextlib,io
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
LIMITS=dict(max_feed_duration_secs=10,max_turn_duration_secs=10,max_suspensions=1000)
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
sha=lambda x:hashlib.sha256(x.encode()).hexdigest()
def response(action):return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(action)}}]}
WORLDS={t:json.loads((P/'upstream'/t/'world.json').read_text()) for t in ['t023','t063']}
CONTEXT={t:json.loads((P/'upstream'/t/'context.json').read_text()) for t in WORLDS}
CASES=[{'name':'archived','reply':'archived'},{'name':'fixed_ok','reply':'ok'},{'name':'fixed_denial','reply':'denial'},{'name':'fixed_clarification','reply':'clarification'}]
class Host:
 def __init__(self,task,case):
  self.task_id=task;self.case=case;self.w=copy.deepcopy(WORLDS[task]);self.ctx=CONTEXT[task];self.calls=[];self.answers=[];self.requests=[];self.unmatched=[];self.derivations=[];self.overlays=[]
 def task(self):return {'instruction':self.case.get('instruction',self.ctx['instruction'])}
 def usage(self):return {'offline':True}
 def answer(self,message,*,outcome,refs):self.answers.append(dict(message=message,outcome=outcome,refs=refs));return {}
 def call(self,method,args):
  self.calls.append([method,copy.deepcopy(args)])
  if method=='Read' and args.get('path') in self.w['files'] and all(k=='path' or v in (0,False) for k,v in args.items()):
   return copy.deepcopy(self.w['files'][args['path']])
  matches=[r for r in self.w['rpc'] if canon([r['method'],r['arguments']])==canon([method,args])]
  if matches:
   assert all(r['response']==matches[0]['response'] for r in matches);return copy.deepcopy(matches[0]['response'])
  if method=='Tree' and args.get('root','').startswith('/proc/') and args.get('level') in [0,3]:
   complete=next(r for r in self.w['trees'] if r['arguments']=={'root':'/proc','level':0})
   node=complete['response']['root']
   for part in args['root'].split('/')[2:]:
    children=[c for c in node.get('children',[]) if c['name']==part]
    if len(children)!=1:break
    node=children[0]
   else:
    def depth(n):return max([depth(c)+1 for c in n.get('children',[])]+[0])
    assert args['level']==0 or depth(node)<=args['level']
    result={'root':copy.deepcopy(node)};self.derivations.append({'request':[method,copy.deepcopy(args)],'source_response_seq':complete['response_seq'],'maximum_depth':depth(node),'response_sha256':sha(canon(result))});return result
  self.unmatched.append([method,copy.deepcopy(args)]);raise RuntimeError('UNMATCHED '+canon([method,args]))
 def llm(self,*args,**kwargs):
  self.requests.append({'args':copy.deepcopy(args),'kwargs':copy.deepcopy(kwargs)})
  archived=[e['data']['response'] for e in self.ctx['llm_events'] if e['kind']=='llm_response']
  if len(self.requests)==1:return copy.deepcopy(archived[0])
  assert len(self.requests)==2,'unexpected extra model request'
  reply=self.case['reply']
  if reply=='archived':return copy.deepcopy(archived[1])
  action={'tool':'report_completion','completed_steps_laconic':[],'message':{'ok':'TRUE(1)','denial':'SCRIPTED denial','clarification':'SCRIPTED please clarify the receipt'}[reply], 'outcome':{'ok':'OUTCOME_OK','denial':'OUTCOME_DENIED_SECURITY','clarification':'OUTCOME_NONE_CLARIFICATION'}[reply],'grounding_refs':['/docs/security.md','/docs/checkout.md']}
  return response(action)
def run(source,task,case,engine):
 host=Host(task,case);output=io.StringIO();out=[];error=None
 try:
  if engine=='CPython':
   with contextlib.redirect_stdout(output):exec(compile(source,'agent.py','exec'),{'bitgn':host})
  else:
   with m.Monty() as pool:
    with pool.checkout(limits=LIMITS) as session:session.feed_run(source,inputs={'bitgn':m.ClassInstance(host,allowed_methods={'call','task','answer','usage','llm'})},print_callback=lambda *a:out.append(str(a[-1])))
 except Exception as e:error=str(e)
 assert not host.unmatched,(task,case,host.unmatched)
 assert not error,(task,case,error)
 assert len(host.answers)==1
 assert all(method not in ['Write','Delete'] for method,args in host.calls)
 return {'task':task,'case':case['name'],'engine':engine,'calls':host.calls,'answers':host.answers,'requests':host.requests,'derivations':host.derivations,'overlays':host.overlays,'stdout':output.getvalue() if engine=='CPython' else ''.join(out)}
def main():
 rows=[]
 for arm in ['parent','combined','context_only','provenance_only']:
  for form in ['readable','packed']:
   filename={'parent':('parent-readable.py','parent.py'),'combined':('readable.py','agent.py'),'context_only':('context_only-readable.py','context_only.py'),'provenance_only':('provenance_only-readable.py','provenance_only.py')}[arm][form=='packed']
   source=(P/'upstream'/filename).read_text()
   for task in WORLDS:
    for case in CASES:
     for engine in ['CPython','native']:
      r=run(source,task,case,engine);r.update(arm=arm,form=form,source_sha256=sha(source));rows.append(r)
 for arm in ['parent','combined','context_only','provenance_only']:
  for task in WORLDS:
   for case in CASES:
    group=[r for r in rows if (r['arm'],r['task'],r['case'])==(arm,task,case['name'])]
    for key in ['calls','answers','requests','derivations']:assert all(r[key]==group[0][key] for r in group),(arm,task,case,key)
 report={'status':'PASS','executions':len(rows),'cases':len(CASES),'worlds':2,'limits':LIMITS,'results':rows}
 (P/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in report.items() if k!='results'})
if __name__=='__main__':main()
