"""Observed request regressions on exact candidate, simulated world, no live calls."""
import ast,contextlib,io,json
from pathlib import Path
import pydantic_monty as m
from test_combined import decoded_source
packed=Path('agent.py').read_text();src=decoded_source(packed);ns={};exec(src[:src.index('\nmessages = [')],ns)
review=json.loads(Path('all-task-review.json').read_text())
tests=Path('tds_tests.py').read_text();env={};exec(tests[:tests.index('f = run(')],env)
fake=ast.get_source_segment(tests,next(n for n in ast.parse(tests).body if isinstance(n,ast.ClassDef)))
pre='import json\nFILES='+repr(env['FILES'])+'\n'+fake+'\n'
pre+='''
class AuditSDK:
 def __init__(self,ins):
  self.ins=ins;self.ident="user: emp-review\\nroles: RoleEmployee, RoleDiscountManager\\n";self.reply="";self.answers=[];self.execs=[];self.calls=[];self.inner=Fake(ins,self.ident,"")
 def call(self,method,args):
  self.calls.append([method,args])
  result=self.inner.call(method,args);self.execs=self.inner.execs;return result
 def task(self):return {"instruction":self.ins}
 def llm(self,model,messages,**kw):
  assert "route a store request" in messages[0]["content"], "Unexpected main-loop inference after injection gate"
  return {"choices":[{"message":{"content":"{\\"docs\\":[]}"},"finish_reason":"stop"}]}
 def answer(self,message,outcome=None,refs=None):self.answers.append([message,outcome,refs]);return {}
 def usage(self):return {}
'''
selected=[('old','t037'),('old','t100')]+[('new',k) for k,v in review.items() if ns['injection_markers'](v['new']['instruction']) is not None]
rows=[]
with m.Monty() as pool:
 for label,tid in selected:
  ins=review[tid][label]['instruction'];assert ns['injection_markers'](ins)
  code=pre+'bitgn=AuditSDK('+repr(ins)+')\n'+packed+'\nprint("RESULT "+json.dumps([bitgn.answers,bitgn.execs]))'
  scope={}
  with contextlib.redirect_stdout(io.StringIO()):exec(code,scope)
  expected=[scope['bitgn'].answers,scope['bitgn'].execs]
  out=[]
  with pool.checkout() as s:s.feed_run(code,print_callback=lambda *a:out.append(a))
  text=''.join(str(x[1]) if len(x)>1 else str(x[0]) for x in out)
  got=json.loads(next(x[7:] for x in text.splitlines() if x.startswith('RESULT ')))
  assert got==expected
  assert len(got[0])==1 and got[0][0][1]=='OUTCOME_DENIED_SECURITY' and not got[1],(label,tid,got)
  rows.append({'source_run':label,'task_id':tid,'native_packed_cpython_equal':True,'outcome':'OUTCOME_DENIED_SECURITY','mutations':0})
for tid in ['t023','t043','t063']:
 ins=review[tid]['new']['instruction']
 assert ns['rcp_request'](ins,'user: emp-review\nroles: RoleEmployee\n') is True
Path('audit-validation.json').write_text(json.dumps({'injection_whole_agent':rows,'employee_receipt_request_gate_cases':['t023','t043','t063'],'scope':'Recorded requests, simulated bootstrap; not full-world grade replay.'},indent=2)+'\n')
print('PASS',len(rows),'observed injection requests denied before mutation/loop in exact packed native runtime; three employee receipt requests enter receipt gate')
