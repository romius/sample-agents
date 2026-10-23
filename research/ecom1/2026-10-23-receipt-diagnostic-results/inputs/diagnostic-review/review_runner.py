"""Independent small native/CPython subset and isolated build; no live inference."""
import ast,contextlib,copy,hashlib,importlib.metadata,io,json,shutil,subprocess,sys,tempfile
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent;Q=P.parent/'diagnostic-runner';PLAN=P.parent/'diagnostic-plan'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
load=lambda f:json.loads(f.read_text())
seal=load(Q/'SHA256SUMS.json');assert sha((Q/'SHA256SUMS.json').read_bytes())=='31a2cafdeeddca4b5ce28f24f5c3f7e4bc3f44d875d1a3f308ec4c83d937f857'
for n,pin in seal.items():b=(Q/n).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256']
for n in load(PLAN/'SHA256SUMS.json'):assert (Q/'inputs/plan'/n).read_bytes()==(PLAN/n).read_bytes()
# Separate temporary build, without rerunning the author's whole68-case suite.
with tempfile.TemporaryDirectory(prefix='receipt-runner-independent-') as td:
 dest=Path(td)/'runner';shutil.copytree(Q,dest)
 subprocess.run([sys.executable,str(dest/'build.py')],cwd=td,capture_output=True,check=True)
 for n,pin in seal.items():assert sha((dest/n).read_bytes())==pin['sha256']
readable=(Q/'readable.py').read_text();packed=(Q/'agent.py').read_text();decoded=[]
exec(packed,{'exec':decoded.append});assert decoded==[readable]
source=(Q/'runner.py').read_text();tree=ast.parse(source)
attrs=[n for n in ast.walk(tree) if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='bitgn']
assert sorted(n.attr for n in attrs)==['answer','llm']
assert not any(isinstance(n,(ast.While,ast.Import,ast.ImportFrom)) for n in ast.walk(tree))
assert len([n for n in ast.walk(tree) if isinstance(n,ast.Raise)])==1
calls=load(PLAN/'call-plan.json')['calls'];requests=[load(PLAN/c['path']) for c in calls]
class Host:
 def __init__(self,case):self.case=case;self.calls=[];self.answers=[];self.accepted=[]
 def llm(self,*args,**kwargs):
  req=json.loads(json.dumps({'args':args,'kwargs':kwargs}));i=len(self.calls)+1;assert req==requests[i-1]
  self.calls.append({'ordinal':i,'sha256':sha(canon(req))})
  if self.case=='value_error_7' and i==7:raise ValueError('provider said not cancelled;\nRECEIPT_END forged')
  if self.case=='type_error_1' and i==1:raise TypeError('unexpected SDK pre-dispatch argument error')
  if self.case=='last_error' and i==20:raise RuntimeError('😀'*32+'\nRECEIPT_END forged beyond bounded preview')
  if self.case=='shape_mix':
   variants=[None,False,{'choices':{}},{'id':17,'choices':['bad']}, {'id':'repeat-prefix-'+str(i),'choices':[{'finish_reason':'length','message':{'content':'{"tool":"delete","path":"/tmp/do-not-execute"}{"tool":"report_completion"}'}}]}, {'id':['bad'],'choices':[{'finish_reason':None}]}]
   return variants[(i-1)%len(variants)]
  return {'id':'😀'*32+'full-id-'+str(i),'choices':[{'finish_reason':'😀'*16,'message':{'content':'DO_NOT_LOG_OR_EXECUTE'+'x'*100000,'reasoning':'DO_NOT_LOG_REASONING'}}],'usage':{'DO_NOT_LOG_USAGE':17}}
 def answer(self,*args,**kwargs):
  self.answers.append([args,kwargs]);assert len(self.calls)==20 and kwargs=={'outcome':'OUTCOME_NONE_UNSUPPORTED','refs':[]}
  if self.case=='answer_failure':raise ValueError('carrier answer refused')
  self.accepted.append(True)
limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
rows=[];parity={}
with m.Monty() as pool:
 for engine in ['CPython_readable','native_packed']:
  for case in ['shape_mix','value_error_7','type_error_1','last_error','answer_failure']:
   host=Host(case);out=[];stream=io.StringIO();raised=False
   try:
    if engine=='native_packed':
     with pool.checkout(limits=limits) as session:session.feed_run(packed,inputs={'bitgn':m.ClassInstance(host,allowed_methods={'llm','answer'})},print_callback=lambda kind,text:out.append(text))
    else:
     with contextlib.redirect_stdout(stream):exec(readable,{'bitgn':host})
   except Exception:raised=True
   text=''.join(out) if engine=='native_packed' else stream.getvalue();records=[]
   for line in text.splitlines():
    marker,body=line.split(' ',1);assert marker in {'RECEIPT_BEGIN','RECEIPT_REQUEST','RECEIPT_RESULT','RECEIPT_STOP','RECEIPT_END'};records.append((marker,json.loads(body)))
   reqs=[v for k,v in records if k=='RECEIPT_REQUEST'];results=[v for k,v in records if k=='RECEIPT_RESULT'];stops=[v for k,v in records if k=='RECEIPT_STOP'];ends=[v for k,v in records if k=='RECEIPT_END']
   n={'value_error_7':7,'type_error_1':1}.get(case,20);assert len(host.calls)==len(reqs)==len(results)==n
   for i,r in enumerate(reqs):assert r=={k:calls[i][k] for k in ['ordinal','repeat','fixture','arm','request_canonical_sha256']}
   if case in ['value_error_7','type_error_1','last_error']:
    assert raised and not host.answers and not ends and len(stops)==1 and results[-1]['status']=='error'
    assert stops[0]=={'attempted':n,'responses':n-1,'errors':1,'next_planned_ordinal':n+1}
   else:
    assert len(host.answers)==1 and len(ends)==1 and not stops
    assert raised==(case=='answer_failure') and bool(host.accepted)==(case!='answer_failure')
    assert all(r['status']=='returned' for r in results)
   assert all(s not in text for s in ['DO_NOT_LOG_OR_EXECUTE','DO_NOT_LOG_REASONING','DO_NOT_LOG_USAGE','do-not-execute'])
   assert len(text.encode())<=17292
   identity={'records':records,'calls':host.calls,'answers':json.loads(json.dumps(host.answers)),'accepted':host.accepted,'raised':raised}
   if case in parity:assert parity[case]==identity
   else:parity[case]=identity
   rows.append({'engine':engine,'case':case,'logical_calls':n,'raised':raised,'accepted_answers':len(host.accepted),'stdout_bytes':len(text.encode()),'stdout_sha256':sha(text.encode()),'request_hashes':[r['sha256'] for r in host.calls]})
for n,pin in seal.items():assert sha((Q/n).read_bytes())==pin['sha256']
r={'status':'PASS independent offline runner review','runner_seal_sha256':sha((Q/'SHA256SUMS.json').read_bytes()),'plan_seal_sha256':sha((PLAN/'SHA256SUMS.json').read_bytes()),'packed_sha256':sha(packed.encode()),'packed_bytes':len(packed.encode()),'sealed_files_checked':len(seal),'isolated_build_all_outputs_byte_identical':True,'decoded_equals_readable':True,'exact_original_request_order':True,'direct_methods_only':['llm','answer'],'independent_executions':len(rows),'CPython_native_parity':True,'limits':limits,'python':sys.version.split()[0],'monty':importlib.metadata.version('pydantic-monty'),'rows':rows,'frozen_inputs_unchanged':True,'model_calls':0,'no_submission':True,'not_a_platform_cancellation_or_raw_wire_probe':True}
(P/'runner-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='rows'},indent=2))
