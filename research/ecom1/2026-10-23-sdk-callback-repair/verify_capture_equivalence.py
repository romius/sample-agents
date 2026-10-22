"""Posthoc compatibility evidence; never rewrites frozen requests or preregistration."""
import copy,hashlib,json,time
from pathlib import Path
import pydantic_monty as monty
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
CAPTURE=ROOT/'2026-10-22-sku-lexical-runtime-prompts'
DIAG=ROOT/'2026-10-22-sku-lexical-paired-diagnostic'
ALLOWED={'task','call','answer','llm','usage'}
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def main():
 frozen={p:sha(p.read_bytes()) for folder in [CAPTURE,DIAG] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 source=(CAPTURE/'capture.py').read_text()
 old='''session.feed_run(PROXY + source,
                external_lookup={"host_task": host.task, "host_call": host.call, "host_llm": host.llm, "host_answer": host.answer},
                print_callback=lambda *args: None)'''
 new='''session.feed_run(source,
                inputs={"bitgn":monty.ClassInstance(host,allowed_methods={"task","call","llm","answer","usage"})},
                print_callback=lambda *args: None)'''
 assert source.count(old)==1
 env={'__file__':str(CAPTURE/'capture.py'),'__name__':'method_only_capture_adapter'};exec(source.replace(old,new),env)
 fixtures=json.loads((DIAG/'inputs/semantic-fixtures.json').read_text())
 worlds=json.loads((DIAG/'inputs/worlds.json').read_text());expected_traces=json.loads((DIAG/'inputs/host-traces.json').read_text())
 bundle=json.loads((DIAG/'fixtures.json').read_text());rows=[];new_traces={};failures=[]
 with monty.Monty() as pool:
  for fixture in fixtures:
   name=fixture['case'];expected_pair=json.loads((DIAG/'inputs/requests'/(name+'.json')).read_text())
   for form in ['readable.py','agent.py']:
    # The original captured source is not reachable under method-only access.
    host=env['Host'](fixture,copy.deepcopy(worlds[name]))
    try:
     with pool.checkout(limits=env['LIMITS']) as session:
      session.feed_run((ROOT/'2026-10-22-sku-history-pressure-review'/form).read_text(),inputs={'bitgn':monty.ClassInstance(host,allowed_methods=ALLOWED)},print_callback=lambda *a:None)
    except Exception as exc:
     error=str(exc);assert 'AttributeError' in error and "has no attribute 'call'" in error,error
    else:raise AssertionError('original unexpectedly reached model boundary')
    assert not host.models and not host.calls and not host.answers
    failures.append(dict(case=name,form=form,method_only_startup_failure=True,model_calls=0,rpc_calls=0))
    for repeat in [1,2]:
     captured,elapsed=env['execute']((HERE/'d5785'/form).read_text(),fixture,worlds[name],True,pool)
     assert captured==expected_traces[name],(name,form,'whole host history mismatch')
     pair=env['make_pair'](captured['models'],fixture)
     for arm in ['C','L']:
      assert pair[arm]==expected_pair[arm]
      assert canonical(pair[arm])==canonical(expected_pair[arm])
      target=next(f for f in bundle['fixtures'] if f['case']==name)
      assert pair[arm]==target['arms'][arm]
      assert sha(canonical(pair[arm]))==target['request_sha256'][arm]
     assert captured['models'][-1]==expected_pair['captured_sdk_call']
     assert pair['removed_field_ledger']==expected_pair['removed_field_ledger']
     new_traces[name]=captured
     rows.append(dict(case=name,form=form,repeat=repeat,native_classinstance=True,seconds=elapsed,C_sha256=sha(canonical(pair['C'])),L_sha256=sha(canonical(pair['L'])),full_history_equal=True,source_sdk_call_equal=True))
 assert len(rows)==68 and len(failures)==34
 for p,h in frozen.items():assert sha(p.read_bytes())==h,str(p)
 report=dict(status='passed offline posthoc compatibility audit',new_executions=len(rows),original_startup_failures=len(failures),rows=rows,original_failures=failures,
   exact_submitted_diagnostic='d6280r1',diagnostic_sha256=sha((DIAG/'agent.py').read_bytes()),
   original_d5785_sha256=sha((ROOT/'2026-10-22-sku-history-pressure-review/agent.py').read_bytes()),successor_sha256=sha((HERE/'d5785/agent.py').read_bytes()),
   frozen_capture_sha256=sha((CAPTURE/'capture.py').read_bytes()),frozen_fixtures_sha256=sha((DIAG/'fixtures.json').read_bytes()),frozen_plan_sha256=sha((DIAG/'call-plan.json').read_bytes()),
   full_17_histories_identical=True,all_34_arm_requests_byte_identical_under_canonical_serialization=True,frozen_files_unchanged=True,
   no_model_calls=True,no_brain_writes=True,
   interpretation='Original d5785 captures used a source-defined SDK class that allowed forbidden method-value access. The original real-host path has a startup reachability gap. After the wrapper repair, method-only ClassInstance reproduces all captured histories/settings and C/L request bytes. This is posthoc runtime compatibility evidence, not a change to frozen inputs/preregistration, a production outcome, or a model-benefit claim.')
 (HERE/'capture-equivalence.json').write_text(json.dumps(report,indent=2)+'\n')
 (HERE/'capture-host-traces.json').write_text(json.dumps(new_traces,indent=2,ensure_ascii=False)+'\n')
 print('PASS:68 actual ClassInstance whole-agent captures;17pairs/34arms identical;34 original startup failures; frozen files unchanged.')
if __name__=='__main__':main()
