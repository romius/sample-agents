"""Fresh offline whole-agent controls. No real RPC/inference/cancellation claim."""
import ast,contextlib,copy,hashlib,io,json,platform
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parents[1];W=json.loads((P/'evidence/world.json').read_text())
src=(P/'evidence/replay.py').read_text();nodes=ast.parse(src).body
start=next(i for i,n in enumerate(nodes) if isinstance(n,ast.FunctionDef) and n.name=='canon')
stop=next(i for i,n in enumerate(nodes) if isinstance(n,ast.ClassDef) and n.name=='Host')
ns=dict(copy=copy,json=json,hashlib=hashlib,W=W)
exec('\n'.join(ast.get_source_segment(src,n) for n in nodes[start:stop+1]),ns)
Base=ns['Host']
CASES=[
 dict(name='healthy',position=None),
 dict(name='third_400_before',position=2,after=False,error='BitGN HTTP 400: rejected delete'),
 dict(name='third_timeout_after',position=2,after=True,error='The read operation timed out',exception='TimeoutError'),
 dict(name='third_empty_error_before',position=2,after=False,error=''),
 dict(name='third_long_unknown_after',position=2,after=True,error='X'*100000),
 dict(name='third_unicode_before',position=2,after=False,error='操作結果不明 — ошибка удаления'),
 dict(name='cancelled_and_answer_rejected',position=2,after=True,error='request cancelled',reject_answer=True),
 dict(name='third_value_error_before',position=2,after=False,error='invalid response object',exception='ValueError'),
]
class Host(Base):
 def __init__(self,c):
  super().__init__('router_then_terminal');self.c=c;self.attempts=[];self.ack=[];self.answer_attempts=[]
 def call(self,method,args):
  if method!='Delete':return super().call(method,args)
  self.attempts.append(args['path'])
  if self.c['position'] is not None and len(self.attempts)-1==self.c['position']:
   self.calls.append([method,copy.deepcopy(args)])
   if self.c['after']:self.deleted.append(args['path']);del self.state[args['path']]
   cls={'TimeoutError':TimeoutError,'ValueError':ValueError}.get(self.c.get('exception'),RuntimeError)
   raise cls(self.c['error'])
  r=super().call(method,args);self.ack.append(args['path']);return r
 def answer(self,message,*,outcome,refs):
  self.answer_attempts.append(dict(message=message,outcome=outcome,refs=refs))
  if self.c.get('reject_answer'):raise RuntimeError('SIMULATED host refuses Answer after cancellation')
  return super().answer(message,outcome=outcome,refs=refs)
rows=[]
with m.Monty() as pool:
 for form in ('readable.py','agent.py'):
  source=(P/form).read_text()
  for c in CASES:
   for engine in ('cpython','native'):
    h=Host(c);output=io.StringIO();native=[];error=None
    try:
     if engine=='cpython':
      with contextlib.redirect_stdout(output):exec(compile(source,form,'exec'),{'bitgn':h})
     else:
      with pool.checkout(limits=dict(max_feed_duration_secs=10,max_turn_duration_secs=10,max_suspensions=1000)) as sess:
       sess.feed_run(source,inputs={'bitgn':m.ClassInstance(h,allowed_methods={'task','call','answer','llm','usage'})},print_callback=lambda *a:native.append(str(a[-1])))
    except Exception as exc:error=str(exc)
    expect=W['expected_deletes'] if c['position'] is None else W['expected_deletes'][:c['position']+1]
    assert h.attempts==expect and len(h.models)==1 and not h.unmatched
    assert h.ack==(expect if c['position'] is None else expect[:-1])
    assert len(h.answer_attempts)==1
    answer=h.answer_attempts[0]
    if c['position'] is None:
     assert answer['outcome']=='OUTCOME_OK' and answer['message']=='\n'.join(expect)
    else:
     assert answer['outcome']=='OUTCOME_ERR_INTERNAL'
     assert answer['message']=='Cleanup stopped: deletion outcome unconfirmed for '+expect[-1]+'. Confirmed deleted paths:\n'+'\n'.join(expect[:-1])
    if c.get('reject_answer'):assert error and not h.answers and 'host refuses Answer' in error
    else:assert error is None and len(h.answers)==1
    removed=h.ack+([expect[-1]] if c.get('after') else [])
    assert set(h.state)==set(h.initial)-set(removed)
    assert all(h.state[k]==h.initial[k] for k in h.state)
    out=output.getvalue() if engine=='cpython' else ''.join(native)
    assert len(out.encode())<4096
    rows.append(dict(form=form,engine=engine,case=c['name'],attempts=h.attempts,acknowledged=h.ack,deleted=h.deleted,remaining=sorted(h.state),answer_attempts=h.answer_attempts,accepted_answers=h.answers,model_calls=len(h.models),stdout_bytes=len(out.encode()),termination_error=error))
for c in CASES:
 group=[r for r in rows if r['case']==c['name']]
 for k in ('attempts','acknowledged','deleted','remaining','answer_attempts','accepted_answers','model_calls'):
  assert all(r[k]==group[0][k] for r in group),(c,k)
report=dict(status='PASS',executions=len(rows),cases=len(CASES),runtime=platform.python_version(),monty='1.2.0',no_network_or_model_calls=True,scope='All host failures and cancellation rejection are simulated, not observed live SDK cancellation behavior.',results=rows)
(P/'independent/counterexample-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print('PASS',len(rows),'independent whole-agent controls')
