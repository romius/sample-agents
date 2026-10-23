import contextlib,copy,hashlib,io,json,pathlib,sys
import pydantic_monty as m
P=pathlib.Path(__file__).resolve().parent
F=json.loads((P/'frozen.json').read_text())
canon=lambda v:json.dumps(v,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
hostile={'id':'r'*1000,'choices':[{'finish_reason':'stop','message':{'content':'{"tool":"delete","path":"/proc/carts/anything"}'}}]}
class Host:
 def __init__(self,shape,fail):self.calls=[];self.answers=[];self.shape=shape;self.fail=fail
 def llm(self,*args,**kwargs):
  q={'args':list(copy.deepcopy(args)),'kwargs':copy.deepcopy(kwargs)};self.calls.append(q)
  step=F['steps'][len(self.calls)-1]
  assert hashlib.sha256(canon(q)).hexdigest()==step['request_canonical_sha256']
  if len(self.calls)==self.fail:raise RuntimeError('sentinel terminal inference exception')
  return copy.deepcopy({'hostile':hostile,'null':{'choices':[{'finish_reason':'stop','message':{'content':None}}]},'malformed':{'choices':'not a choice list'}}[self.shape])
 def answer(self,*args,**kwargs):self.answers.append([args,kwargs]);return {}
 def call(self,*args,**kwargs):raise AssertionError('ECOM action forbidden')
rows=[]
with m.Monty() as pool:
 for form in ['readable','agent']:
  source=(P/(form+'.py')).read_text()
  for engine in ['CPython','native']:
   for shape,fail in [('hostile',0),('null',0),('malformed',0),('hostile',1),('hostile',10),('hostile',20)]:
    h=Host(shape,fail);out=[];error=None
    try:
     if engine=='native':
      with pool.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as s:s.feed_run(source,inputs={'bitgn':m.ClassInstance(h,allowed_methods={'llm','answer','call'})},print_callback=lambda *a:out.append(str(a[-1])))
     else:
      stream=io.StringIO()
      with contextlib.redirect_stdout(stream):exec(source,{'bitgn':h})
      out=[stream.getvalue()]
    except Exception as e:error=str(e)
    assert len(h.calls)==(fail or 20)
    if fail:assert error and 'sentinel terminal inference exception' in error and not h.answers
    else:
     assert error is None and len(h.answers)==1
     assert h.answers[0][1]=={'outcome':'OUTCOME_NONE_UNSUPPORTED','refs':[]}
     assert 'Carrier task was not attempted' in h.answers[0][0][0]
    rows.append({'form':form,'engine':engine,'shape':shape,'fail_at':fail,'inference_calls':len(h.calls),'carrier_answers':len(h.answers),'expected_exception':bool(fail),'source_sha256':hashlib.sha256(source.encode()).hexdigest()})
assert len(rows)==24
for n in ['A016','A074','B056','B076','V016']:
 steps=[s for s in F['steps'] if s['fixture']==n]
 assert [s['arm'] for s in steps[:2]]==list(reversed([s['arm'] for s in steps[2:]]))
assert F['requests']['V016-M']==F['requests']['V016-L']==F['requests']['A016-M']
(P/'test-results.json').write_text(json.dumps({'status':'PASS','executions':24,'native_executions':12,'real_model_calls':0,'ECOM_actions':0,'cases':rows},indent=2)+'\n')
print('PASS24 whole-run checks,12 native, exact requests and terminal exception bounds')
