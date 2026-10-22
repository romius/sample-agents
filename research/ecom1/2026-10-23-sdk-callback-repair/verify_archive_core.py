"""Focused dependency-closure test; does not repeat the 216-case suites."""
import contextlib,copy,hashlib,importlib.metadata,inspect,io,json,sys
from pathlib import Path
import pydantic_monty as m
import verify
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent

def result(host):return dict(answers=host.answers,calls=host.calls,writes=host.writes,models=host.models)
def main():
 runtime=json.loads((HERE/'RUNTIME.json').read_text())
 assert importlib.metadata.version('pydantic-monty')==runtime['pydantic_monty']
 policy=Path(inspect.getsourcefile(m.ClassInstance)).read_bytes()
 assert hashlib.sha256(policy).hexdigest()==runtime['class_instance_source_sha256']
 assert policy==(HERE/'runtime_public/class_instance.py').read_bytes()
 sys.path.insert(0,str(ROOT/'2026-10-22-inventory-integration'))
 import verify_integration as suite
 probe=verify.Probe();verify.native('assert bitgn.call("Read",{})=={"ok":True}',probe);assert len(probe.calls)==1
 probe=verify.Probe()
 try:verify.native('callback=bitgn.call',probe)
 except Exception as exc:assert 'AttributeError' in str(exc) and "has no attribute 'call'" in str(exc)
 else:raise AssertionError('attribute extraction unexpectedly available')
 probe=verify.Probe();verify.native('def callback(method,args):\n return bitgn.call(method,args)\nassert callback("Read",{})=={"ok":True}',probe);assert len(probe.calls)==1
 rows=[]
 for name,(parent,_,_) in verify.PARENTS.items():
  world=suite.review.fixture('own');request=suite.review.engine['ix_request'](world['instruction']);bound=suite.review.engine['ix_bound_request'](request,world['stores'])
  expected_csv=suite.review.expected_csv(world,request,bound['branch'])
  baseline=suite.Host(copy.deepcopy(world))
  with contextlib.redirect_stdout(io.StringIO()):exec((HERE/name/'readable.py').read_text(),{'bitgn':baseline})
  assert not baseline.models and baseline.writes==[dict(path=request['path'],content=expected_csv)] and baseline.answers[0][:2]==[request['path'],'OUTCOME_OK']
  for form in ['readable.py','prepack.py','agent.py']:
   host=suite.Host(copy.deepcopy(world));source=(HERE/name/form).read_text();verify.native(source,host)
   assert result(host)==result(baseline),(name,form)
   assert not verify.attributes(verify.decode(source) if form=='agent.py' else source)
   rows.append(dict(source=name,form=form,native_proxy_parity=True,csv_oracle=True))
  for form in ['readable.py','agent.py']:
   host=suite.Host(copy.deepcopy(world))
   try:verify.native((ROOT/parent/form).read_text(),host)
   except Exception as exc:assert 'AttributeError' in str(exc) and "has no attribute 'call'" in str(exc)
   else:raise AssertionError('parent unexpectedly succeeds')
   assert not host.calls and not host.models
 report=dict(status='passed offline',candidate_native_world_runs=6,parent_failure_controls=4,small_proxy_controls=3,rows=rows,full216_suite_repeated=False,real_model_calls=0)
 (HERE/'archive-core-verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS focused closure:6 native candidate worlds,4 exact-parent failures,3 proxy controls; full216 not repeated.')
if __name__=='__main__':main()
