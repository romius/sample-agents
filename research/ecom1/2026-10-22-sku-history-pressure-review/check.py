"""Probe repeated-catalogue history growth with identical scripted actions."""
import contextlib,copy,io,json,sys,hashlib
from pathlib import Path
import pydantic_monty as monty
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'2026-10-22-inventory-integration'))
import verify_integration as suite
class Host(suite.Host):
 def __init__(self,world,steps):super().__init__(world);self.steps=steps;self.main_count=0;self.request_sizes=[];self.compact_sizes=[];self.request_hashes=[]
 def llm(self,*args,**kwargs):
  self.models.append(copy.deepcopy([args,kwargs]))
  request=dict(model=args[0],messages=args[1],**kwargs)
  self.request_sizes.append(len(json.dumps(request).encode()))
  self.compact_sizes.append(len(json.dumps(request,separators=(',',':')).encode()))
  self.request_hashes.append(hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest())
  if 'route a store request' in args[1][0]['content']:body={'docs':[]}
  else:
   self.main_count+=1
   if self.main_count<=self.steps:body={'tool':'catalog','query':'dewalt dcf887 xr kit case'}
   else:body={'tool':'report_completion','message':'Which battery capacity: 2.0Ah or 5.0Ah?','outcome':'OUTCOME_NONE_CLARIFICATION','grounding_refs':[]}
  return {'choices':[{'message':{'content':json.dumps(body)},'finish_reason':'stop'}]}
def execute(source,steps,native,padding=0):
 world=suite.review.fixture('record');world['instruction']='need code: dewalt dcf887 xr kit with case. answer only with sku.'
 if padding:
  world['reads']['/docs/security.md']['content']+='\n<!-- '+('x'*padding)+' -->\n'
 host=Host(world,steps)
 if native:
  with monty.Monty() as engine:
   with engine.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as session:
    session.feed_run(suite.PROXY+source,external_lookup={'host_task':host.task,'host_call':host.call,'host_llm':host.llm,'host_answer':host.answer},print_callback=lambda *a:None)
 else:
  with contextlib.redirect_stdout(io.StringIO()):exec(source,{'bitgn':host})
 assert len(host.answers)==1 and not host.writes
 main=[args[1] for args,kwargs in host.models if 'route a store request' not in args[1][0]['content']]
 prefix=main[0]
 assert all(m[:len(prefix)]==prefix for m in main),'bootstrap policy/instruction lost'
 return dict(request_hashes=host.request_hashes,request_sizes=host.request_sizes,max_request_bytes=max(host.request_sizes),over_64k=[i for i,n in enumerate(host.request_sizes) if n>65536],
   max_compact_request_bytes=max(host.compact_sizes),compact_over_64k=[i for i,n in enumerate(host.compact_sizes) if n>65536],
   message_counts=[len(m) for m in main],catalog_observation_counts=[sum('"tool": "catalog"' in x['content'] and '\n' in x['content'] for x in m) for m in main],
   answers=host.answers,rpc_calls=len(host.calls),bootstrap_preserved=True)
rows=[]
for steps,padding in [(5,0),(30,0),(30,2200)]:
 for label,path in [('parent',ROOT/'2026-10-22-inventory-integration/readable.py'),('candidate',ROOT/'2026-10-22-sku-evidence-integration/readable.py'),('repaired',HERE/'readable.py')]:
  row=execute(path.read_text(),steps,False,padding)
  assert execute(path.read_text(),steps,True,padding)==row
  if label in ['candidate','repaired']:assert execute((path.parent/'agent.py').read_text(),steps,True,padding)==row
  if label=='repaired':
   assert execute((path.parent/'prepack.py').read_text(),steps,True,padding)==row
   control=rows[-1]
   assert control['label']=='candidate'
   assert row['request_hashes'][:-1]==control['request_hashes'][:-1]
   if steps<30:assert row['request_hashes']==control['request_hashes']
   assert row['answers']==control['answers'] and row['rpc_calls']==control['rpc_calls']
   assert not row['over_64k'] and not row['compact_over_64k']
  rows.append(dict(label=label,scripted_catalogue_calls=steps,benign_policy_padding=padding,**row))
assert rows[-2]['label']=='candidate' and rows[-2]['compact_over_64k']==[31]
result=dict(status='observed and repaired',whole_agent_executions=27,cases=rows,limitations='Scripted repeated queries on archived inventory-world catalogue/policy scaffolding with derived SKU instruction; padded case adds2200 benign HTML comment characters to security policy. No live model, task-grade or final-answer benefit claim. Captures source request size before SDK provider envelope and actual history trimming. Both compact/default JSON exceed64KiB in the unrepaired counterexample; repaired cases stay below normal56k window.')
(HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
for r in rows:print(r['label'],r['scripted_catalogue_calls'],r['benign_policy_padding'],r['max_request_bytes'],r['max_compact_request_bytes'],r['over_64k'],r['catalog_observation_counts'][-5:])
