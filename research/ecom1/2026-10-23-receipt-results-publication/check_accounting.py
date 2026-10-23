"""Independent accounting counterexamples; no network/model calls or semantic grading."""
from pathlib import Path
import copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parent
A=P.parent/'2026-10-23-receipt-diagnostic-results'
spec=importlib.util.spec_from_file_location('receipt_audit',A/'validate.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
raw=(A/'trial-trace.ndjson').read_bytes()
summary=json.loads((A/'summary.json').read_text())
frozen=json.loads((A/'inputs/diagnostic-runner/frozen.json').read_text())
good=mod.audit(raw,summary,frozen)
assert good['status']=='reconciled' and good['accounting']['cost_complete']
assert good['logical_calls']==good['physical_attempts']==20
events=[json.loads(line) for line in raw.splitlines()]
def run(name,mutate,expected):
 es=copy.deepcopy(events);s=copy.deepcopy(summary);mutate(es,s)
 b=b''.join((json.dumps(e,ensure_ascii=False,separators=(',',':'))+'\n').encode() for e in es)
 # Reseal only the synthetic copy, to exercise checks beyond the real CAS gate.
 s['trials'][0]['trace']['blob']=hashlib.sha256(b).hexdigest();s['trials'][0]['trace']['bytes']=len(b)
 r=mod.audit(b,s,frozen);codes=[p['code'] for p in r['problems']]
 assert r['status']=='incomplete_or_deviating' and not r['accounting']['cost_complete'] and expected in codes,(name,codes)
 return {'case':name,'expected_issue':expected,'reported_issues':codes,'cost_complete':r['accounting']['cost_complete']}
def event(es,kind):return next(e for e in es if e['kind']==kind)
cases=[]
cases.append(run('changed_temperature',lambda es,s:event(es,'llm_request')['data']['request'].__setitem__('temperature',0.5),'exact_wire_request'))
cases.append(run('changed_observed_provider',lambda es,s:event(es,'llm_response')['data']['response'].__setitem__('provider','Other'),'observed_provider'))
cases.append(run('changed_observed_model',lambda es,s:event(es,'llm_response')['data']['response'].__setitem__('model','other'),'observed_model_alias'))
cases.append(run('missing_response',lambda es,s:es.remove(event(es,'llm_response')),'attempt_request_terminal_count'))
cases.append(run('duplicate_sequence',lambda es,s:es.insert(1,copy.deepcopy(es[0])),'unordered_or_duplicate_sequence'))
cases.append(run('wrong_trial',lambda es,s:event(es,'llm_request')['data'].__setitem__('trial_id','synthetic-wrong-trial'),'event_trial_identity'))
cases.append(run('changed_cost',lambda es,s:event(es,'llm_response')['data']['response']['usage'].__setitem__('cost',0.1),'complete_accounting_mismatch'))
cases.append(run('changed_tokens',lambda es,s:event(es,'llm_response')['data']['response']['usage'].__setitem__('total_tokens',1),'complete_accounting_mismatch'))
cases.append(run('unexpected_action',lambda es,s:event(es,'rpc_request')['data'].__setitem__('method','Write'),'unexpected_ECOM_action'))
cases.append(run('wrong_source',lambda es,s:s['source'].__setitem__('revision',2),'source_identity'))
out={'status':'PASS independent accounting integrity controls','real_trace_sha256':hashlib.sha256(raw).hexdigest(),'real_trace_reconciled':True,'real_logical_calls':20,'real_physical_attempts':20,'real_cost':good['accounting'],'synthetic_resealed_counterexamples':cases,'model_calls':0,'semantic_judgments':None}
(P/'accounting-controls.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'counterexamples':len(cases),'cost':good['accounting']['observed_cost_usd']}))
