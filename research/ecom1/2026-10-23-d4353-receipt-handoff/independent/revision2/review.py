"""Independent CPython/native pressure tests, not full-agent or SDK wire qualification."""
import ast,hashlib,importlib.metadata,json,sys
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent;U=P.parent.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
helper=(U/'handoff.py').read_text();parent=(U/'parent-readable.py').read_text()
obs=next(ast.get_source_segment(parent,n) for n in ast.parse(parent).body if isinstance(n,ast.FunctionDef) and n.name=='observation')
program='import json\n'+obs+'\n'+'def note_policy_read(function,result):\n  pass\n'+helper+'\n'+(P/'cases.py').read_text()
logs=[];exec(program,{'print':lambda text:logs.append(text)});expected=json.loads(logs[0]);logs=[]
limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
with m.Monty() as pool:
 with pool.checkout(limits=limits) as session:
  session.feed_run(program,print_callback=lambda stream,text:logs.append(text))
actual=json.loads(''.join(logs));assert actual==expected
readable=(U/'readable.py').read_text();tree=ast.parse(readable)
calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='receipt_pressure'];assert len(calls)==2
# Verify exact placement relative to both source callsites, not only helper math.
assert 'for index in range(0 if answered else MAX_STEPS):\n  messages, bootstrap_count, receipt_added = receipt_pressure(messages, bootstrap_count, receipt_added)\n  while len(json.dumps(messages)' in readable
assert '  messages, bootstrap_count, receipt_added = receipt_pressure(messages, bootstrap_count, receipt_added)\n  try:\n    response = bitgn.llm' in readable
r={'status':'bounded revision2 pressure checks passed; full-agent/wire qualification pending','pins':{n:sha((U/n).read_bytes()) for n in ['handoff.py','build.py','readable.py','agent.py']},'cases':actual,'CPython_native_exact_parity':True,'native_limits':limits,'python':sys.version.split()[0],'monty':importlib.metadata.version('pydantic-monty'),'two_source_callsites_verified':True,'provenance_callback_stubbed':True,'model_calls':0}
(P/'results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
