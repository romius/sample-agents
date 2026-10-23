import contextlib,copy,hashlib,io,json,pathlib,sys
import pydantic_monty as m
sys.dont_write_bytecode=True
P=pathlib.Path(__file__).resolve().parent
A=P.parent/'2026-10-23-null-final-effort-diagnostic'
F=json.loads((A/'frozen.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda v:json.dumps(v,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
assert sha((A/'agent.py').read_bytes())=='ad1c3ebe318b7273867462b88e05ea285f81da5ad50198a703bd161f9cd774d2'
request_checks=[]
for fixture in ['A016','A074','B056','B076']:
 event=json.loads((A/'inputs'/f'{fixture}-request-event.json').read_text());q=event['data']['request']
 trigger=json.loads((A/'inputs'/f'{fixture}-trigger-event.json').read_text())
 assert trigger['data']['trial_id']==event['data']['trial_id'] and trigger['seq']+1==event['seq']
 choice=trigger['data']['response']['choices'][0];assert choice['message']['content'] is None and choice['finish_reason']=='stop'
 medium=F['requests'][fixture+'-M'];low=F['requests'][fixture+'-L']
 assert medium['args']==[q['model'],q['messages']]
 changed=copy.deepcopy(medium);changed['kwargs']['reasoning']['effort']='low';assert changed==low
 assert medium['kwargs']=={'max_completion_tokens':q['max_tokens'],'reasoning':q['reasoning'],'temperature':q['temperature']}
 assert q['messages'][-1]=={'role':'user','content':'No action executed. Fix your JSON: Return one JSON action object'}
 request_checks.append({'fixture':fixture,'trigger_seq':trigger['seq'],'request_seq':event['seq'],'messages_equal':True,'single_effort_change':True,'prior_request_bytes':len(canon(q))})
for fixture in ['A016','A074','B056','B076','V016']:
 steps=[s for s in F['steps'] if s['fixture']==fixture]
 assert len(steps)==4 and [s['arm'] for s in steps[:2]]==list(reversed([s['arm'] for s in steps[2:]]))
assert F['requests']['V016-M']==F['requests']['V016-L']==F['requests']['A016-M']
class Host:
 def __init__(self,shape,fail):self.calls=[];self.answers=[];self.shape=shape;self.fail=fail
 def llm(self,*args,**kwargs):
  self.calls.append({'args':list(copy.deepcopy(args)),'kwargs':copy.deepcopy(kwargs)})
  step=F['steps'][len(self.calls)-1];assert sha(canon(self.calls[-1]))==step['request_canonical_sha256']
  if self.fail==len(self.calls):raise RuntimeError('🙂'*20000+' do not expose error tail')
  if self.shape=='nonobject':return ['hostile','bitgn.call("Delete", {})']
  return {'id':'🙂'*20000,'choices':[{'finish_reason':'🙂'*20000,'message':{'content':'DO_NOT_EMIT_BODY'*10000,'reasoning':'DO_NOT_EMIT_REASONING'*10000}}]}
 def answer(self,*args,**kwargs):self.answers.append((args,kwargs));return {}
rows=[]
with m.Monty() as pool:
 for form in ['readable','agent']:
  source=(A/f'{form}.py').read_text()
  for engine in ['CPython','native']:
   for shape,fail in [('unicode',0),('nonobject',0),('unicode',7),('unicode',19)]:
    h=Host(shape,fail);out=[];error=None
    try:
     if engine=='native':
      with pool.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as s:s.feed_run(source,inputs={'bitgn':m.ClassInstance(h,allowed_methods={'llm','answer'})},print_callback=lambda *a:out.append(str(a[-1])))
     else:
      buf=io.StringIO()
      with contextlib.redirect_stdout(buf):
       try:exec(source,{'bitgn':h})
       finally:out=[buf.getvalue()]
    except Exception as e:error=str(e)
    stdout=''.join(out)
    assert len(h.calls)==(fail or 20) and bool(error)==bool(fail) and len(h.answers)==(0 if fail else 1)
    assert 'DO_NOT_EMIT' not in stdout and 'do not expose error tail' not in stdout
    assert len(stdout.encode())<65536
    rows.append({'form':form,'engine':engine,'shape':shape,'fail_at':fail,'calls':len(h.calls),'answers':len(h.answers),'stdout_bytes':len(stdout.encode()),'raw_body_emitted':False})
report={'status':'PASS independent mechanical checks','request_checks':request_checks,'executions':len(rows),'native_executions':sum(r['engine']=='native' for r in rows),'rows':rows,'max_stdout_bytes':max(r['stdout_bytes'] for r in rows),'paid_calls':0,'semantic_outcomes_tested':False}
(P/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['rows','request_checks']}))
