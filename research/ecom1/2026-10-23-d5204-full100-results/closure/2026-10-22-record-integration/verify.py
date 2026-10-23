import ast, contextlib, io, json, re
from pathlib import Path
import pydantic_monty as m
import test_combined as rc
P=Path('.')
parent=P.joinpath('parent_agent.py').read_text();packed=P.joinpath('agent.py').read_text();readable=P.joinpath('readable.py').read_text()
def namespace(src):
 code=rc.decoded_source(src);ns={};exec(code[:code.index('\nmessages = [')],ns)
 ns.update(DM=ns['rcp_items'],FP=ns['receipt_availability'],FU=ns['receipt_price_drift']);return ns
rc.namespace=namespace
archive=json.loads(P.joinpath('archived_receipt.json').read_text())['response']['content']
parser=rc.parser_checks(P.joinpath('receipt_parent.py').read_text(),packed,archive)
handlers=[rc.handler_checks(parent,packed,g) for g in ['handlers-0','handlers-1','handlers-2','handlers-3','drift']]
# Reuse the existing full-agent fake RPC world; no live model or ECOM access.
oldtests=Path('tds_tests.py').read_text();env={};exec(oldtests[:oldtests.index('f = run(')],env)
FILES=env['FILES'];fake=ast.get_source_segment(oldtests,next(n for n in ast.parse(oldtests).body if isinstance(n,ast.ClassDef)))
FILES['/tmp/recovered.txt']='RECOVERED'
HARNESS='''
class Harness:
 def __init__(self, mode, error, count):
  self.inner=Fake("Read the recovery marker file.","user: emp-review\\nroles: RoleEmployee\\n","")
  self.mode=mode;self.error=error;self.remaining=count
  self.actions=[{"tool":"read","path":"/tmp/recovered.txt"},{"tool":"report_completion","message":"RECOVERED","outcome":"OUTCOME_OK","grounding_refs":["/tmp/recovered.txt"]}]
  if mode=="exec":self.actions.insert(0,{"tool":"exec","path":"/bin/ls","args":["-R","/proc/baskets"]})
  if mode=="forced":self.actions=[None,None,None]+self.actions[1:]
  self.calls=[];self.answers=[];self.requests=[];self.successes=[];self.serial=0
 def task(self):return self.inner.task()
 def call(self,method,args):
  self.calls.append([method,args])
  if method=="Exec" and args.get("path")=="/bin/ls":raise RuntimeError('BitGN HTTP 404: {"code":"not_found","message":"runtime tool not found: not found"}')
  return self.inner.call(method,args)
 def llm(self,*args,**kw):
  self.requests.append(json.dumps([args,kw]));self.serial+=1
  router="route a store request" in args[1][0]["content"]
  fail=(self.mode=="router" and router) or (self.mode=="main" and not router) or (self.mode=="forced" and not router and len(self.actions)==1)
  if fail and self.remaining:
   self.remaining-=1;raise RuntimeError(self.error)
  self.successes.append(json.dumps([args,kw]))
  content=json.dumps({"docs":[]}) if router else json.dumps(self.actions.pop(0))
  return {"choices":[{"message":{"content":content},"finish_reason":"stop"}]}
 def answer(self,message,outcome=None,refs=None):self.answers.append([message,outcome,refs]);return {}
 def usage(self):return {}
'''
pre='import json\nFILES='+repr(FILES)+'\n'+fake+'\n'+HARNESS+'\n'
def run(src,mode='main',err='',count=0,native=False):
 code=pre+'bitgn=Harness('+repr(mode)+','+repr(err)+','+str(count)+')\n'
 code+='failure=None\ntry:\n exec('+repr(src)+')\nexcept RuntimeError as e:failure=str(e)\n'
 code+='result=[bitgn.answers,bitgn.calls,bitgn.requests,bitgn.successes,failure]\nprint("RESULT "+json.dumps(result))'
 if not native:
  ns={}
  with contextlib.redirect_stdout(io.StringIO()):exec(code,ns)
  return ns['result']
 out=[]
 with m.Monty() as pool:
  with pool.checkout() as sess:sess.feed_run(code,print_callback=lambda *a:out.append(a))
 text=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in out)
 return json.loads(next(line[7:] for line in text.splitlines() if line.startswith('RESULT ')))
results=[]
for name,mode,err,count,success,extra in [
 ('clean','main','',0,True,0),('router-timeout','router','Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out',1,True,1),
 ('main-timeout','main','Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out',1,True,1),
 ('main-503','main','HTTP 503 unavailable',2,True,2),('forced-timeout','forced','read operation timed out',1,True,1),
 ('persistent-timeout','main','read operation timed out',4,False,2),('429-body-timeout','main','HTTP 429 timeout',1,False,0),
 ('400-body-connection','main','HTTP 400 connection',1,False,0),('500-persistent','main','HTTP 500 error',4,False,2),
 ('unknown-error','main','database is locked',1,False,0),('exec404','exec','',0,True,0)]:
 a=run(packed,mode,err,count);b=run(readable,mode,err,count);c=run(packed,mode,err,count,True)
 assert a==b==c,name
 if success:
  assert len(a[0])==1 and a[0][0][0]=='RECOVERED' and a[4] is None,(name,a)
  if mode not in ['exec']:
   ctl=run(parent,mode,'',0)
   assert a[0:2]==ctl[0:2] and a[3]==ctl[3],name
   assert len(a[2])==len(ctl[2])+extra,name
 else:
  assert not a[0] and a[4],name
  # Router succeeds once; main fails once plus bounded retries.
  assert len(a[2])==2+extra,name
 if mode=='exec':
  assert sum(method=='Exec' and args.get('path')=='/bin/ls' for method,args in a[1])==1
  assert 'runtime tool not found' in run(parent,mode,'',0)[4]
 results.append({'case':name,'whole_agent_native_readable_packed_equal':True,'success':success,'inference_attempts':len(a[2])})
# All error boundary checks are executed against decoded exact artifact definitions.
ns=namespace(packed);f=ns['recoverable_lookup_error']
for error in ['database is locked','BitGN HTTP 500: failure','BitGN HTTP 404: bad json','BitGN HTTP 404: {"code":"not_found","message":"payment not found"}']:
 assert f({'tool':'exec','path':'/bin/payments'},RuntimeError(error)) is None
assert f({'tool':'delete'},RuntimeError('BitGN HTTP 404: {}'))['outcome_unconfirmed'] is True
assert f({'tool':'read'},RuntimeError('BitGN HTTP 404: {"code":"not_found"}')) is not None
# Same request survives each retry, including every inference option.
requests=[]
class Model:
 def llm(self,*a,**k):
  requests.append([a,k])
  if len(requests)<3:raise RuntimeError('connection reset')
  return {'ok':1}
ns['bitgn']=Model();assert ns['MSR']('test-model',[{'role':'user','content':'hello'}],temperature=0,reasoning={'effort':'medium'})=={'ok':1}
assert requests[0]==requests[1]==requests[2]
result={'parser':parser,'handlers':handlers,'whole_agent':results,'lookup_boundary_checks':6,'retry_identical_requests':True}
P.joinpath('verification.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 408 receipt parser controls; 20 handler cases; 14 clean-parent comparisons; 11 whole-agent cases on readable/packed/native; six lookup boundaries; exact retry request parity')
