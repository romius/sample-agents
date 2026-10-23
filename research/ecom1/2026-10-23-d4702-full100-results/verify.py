"""Offline structural accounting, trace scope and exact source reproduction."""
import ast,hashlib,json,subprocess,sys,tempfile,shutil
from pathlib import Path
P=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
r=load(P/'result.json');job=r['job'];summary=r['result']
assert job['id']=='jfdd875bba6ba4773a549e8703764efa9' and job['state']=='completed'
assert summary['source']['document']=='d4702' and summary['source']['revision']==1
assert job['run_id']==summary['run_id']=='run-22rKo2UTyvRLgWXdqqZ49dSgi'
assert summary['source']['sha256']==sha((P/'sources/d4702r1.py').read_bytes())=='b5bf80e4eb3eb4f5ee86dfad2442606e33da8102a9edbac85222ecc395d507f8'
trials=summary['trials'];assert len(trials)==summary['total_trials']==summary['completed_trials']==100
assert summary['failed_trials']==summary['cancelled_trials']==0
assert all(t['state']=='answered' and t['grade']['available'] for t in trials)
assert sum(t['usage']['model_calls'] for t in trials)==summary['model_calls']==244
assert sum(t['usage']['total_tokens'] for t in trials)==summary['total_tokens']==771806
assert summary['cost_complete'] and summary['unknown_cost_calls']==summary['pending_calls']==0
assert abs(sum(t['usage']['model_cost_usd'] for t in trials)-summary['model_cost_usd'])<1e-12
assert abs(sum(t['grade']['score'] for t in trials)/100-summary['run_score'])<1e-6
instructions=load(P/'instructions-all100.json');assert len(instructions)==100
for row,t in zip(instructions,trials):
 e=json.loads(row['event']['text']);response=e['data']['response']
 assert row['task_id']==t['task_id']==response['taskId']
 assert t['trial_id']==response['trialId'] and response['runId']==summary['run_id']
 assert len(row['event']['text'].encode())==row['event']['bytes'] and not row['event']['more']
losses=[t['task_id'] for t in trials if t['grade']['score']<1]
assert len(losses)==17 and sum(t['grade']['score']==0 for t in trials)==12
all_responses=[];null_final=[];scope_report=[];read_hashes_checked=0
for task in losses:
 pages=load(P/f'index-{task}.json');index=[e for page in pages for e in page['items']]
 assert all(page['more'] for page in pages[:-1]) and not pages[-1]['more']
 assert len({e['seq'] for e in index})==len(index)
 offset=0
 for e in index:assert e['data']['trace']['offset']==offset;offset+=e['data']['trace']['bytes']
 official=next(t for t in trials if t['task_id']==task);assert offset==official['trace']['bytes']
 events=[json.loads(x) for x in (P/f'{task}-events.ndjson').read_text().splitlines()]
 for e in events:
  d=e['data']
  if e['kind']=='rpc_response' and d['method']=='Read':
   content=d['response'].get('content');expected=d['response'].get('sha256')
   if isinstance(content,str) and expected:
    assert sha(content.encode())==expected,(task,e['seq']);read_hashes_checked+=1
 seqs={e['seq'] for e in events}
 assert all(e['seq'] in seqs for e in index if e['kind'] in ['rpc_request','llm_response','llm_retry','llm_error','agent_error','agent_finished'])
 assert not any(e['kind'] in ['llm_retry','llm_error','agent_error'] for e in index)
 rs=[e for e in events if e['kind']=='llm_response'];assert len(rs)==official['usage']['model_calls']
 for e in rs:
  assert e['data']['status']==200
  assert e['data']['trial_id']==official['trial_id']
  assert e['data']['response']['provider']=='DeepInfra'
  if any(c['message'].get('content') is None for c in e['data']['response'].get('choices',[])):null_final.append({'task':task,'seq':e['seq']})
 all_responses.extend(rs)
 assert abs(sum(e['data']['response']['usage']['cost'] for e in rs)-official['usage']['model_cost_usd'])<1e-10
 scope_report.append({'task':task,'indexed_events':len(index),'retained_events':len(events),'official_scope_bytes':offset,'all_requests_and_model_responses_retained':True})
assert len(all_responses)==65 and len(null_final)==9
rows=load(P/'all100-review.json');assert len(rows)==100
success_seal=load(P/'success-evidence/SHA256SUMS.json')
for path,expected in success_seal.items():assert sha((P/'success-evidence'/path).read_bytes())==expected,path
for row,t in zip(rows,trials):
 assert row['task_id']==t['task_id'] and row['official_grade']==t['grade']
 assert row['instruction_sha256']==sha(row['instruction'].encode())
 assert row['answer_evidence_level'] and row['diagnosis'] and row['uncertainty']
 assert row['answer'] and row['observation'] and row['agent_finished_stdout']
 for key,kind in [('answer_event','rpc_request'),('agent_finished_event','agent_finished')]:
  ref=row[key];raws=(P/ref['path']).read_bytes().splitlines(keepends=True)
  matches=[raw for raw in raws if json.loads(raw)['seq']==ref['seq']];assert len(matches)==1
  raw=matches[0];event=json.loads(raw);assert sha(raw)==ref['sha256'] and event['kind']==kind
  assert event['data']['trial_id']==t['trial_id']
  if key=='answer_event':assert event['data']['method']=='Answer' and event['data']['arguments']==row['answer']
  else:
   assert event['data']['output']==row['agent_finished_stdout']
   assert len(row['agent_finished_stdout'].encode())==t['output_bytes']
assert [x['task'] for x in load(P/'loss-review.json')]==losses
# Rebuild in a fresh directory using only included exact dependencies.
mapping={'parent_agent.py':'d4353r1.py','parent_readable.py':'d4353r1-readable.py',
 'record_agent.py':'d3200r2.py','record_readable.py':'d3200r2-readable.py',
 'record-to-integration-parent.patch':'d3200-to-d4353.patch','retry_donor.py':'d4445r1-retry-donor.py',
 'recovery_donor.py':'d3513r1-recovery-donor.py','lzpack.py':'lzpack.py','build.py':'d4702-build.py'}
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp)
 for name,source in mapping.items():shutil.copyfile(P/'sources'/source,d/name)
 run=subprocess.run([sys.executable,'build.py'],cwd=d,capture_output=True,text=True)
 assert run.returncode==0,run.stderr
 assert (d/'agent.py').read_bytes()==(P/'sources/d4702r1.py').read_bytes()
 assert (d/'readable.py').read_bytes()==(P/'sources/d4702r1-readable.py').read_bytes()
 reproduced=load(d/'manifest.json')
source_pins=[{'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted((P/'sources').iterdir()) if p.is_file()]
(P/'source-pins.json').write_text(json.dumps(source_pins,indent=2)+'\n')
report={'job':job['id'],'official_score':summary['run_score'],'all100_instructions_and_grades_checked':True,
 'all100_final_answers_and_stdout_checked':True,'successful_task_review_rows':83,'success_subfolder_sealed_files_verified':len(success_seal),
 'model_calls':244,'total_tokens':771806,'cost_usd':summary['model_cost_usd'],'cost_complete':True,
 'loss_responses':65,'loss_response_statuses':[200],'null_final_responses':null_final,
 'loss_response_provider':'DeepInfra','loss_response_costs_match_settled_trial_totals':True,'read_content_hashes_checked':read_hashes_checked,
 'no_transport_error_or_retry_events_in_complete_loss_indexes':True,'scope':scope_report,
 'source_rebuild_exact':True,'source_build_manifest':reproduced,
 'limits':['All100 have actual instructions, final Answer and complete stdout review; successes are not independent full action/business-fact audits.',
 'Nine loss scopes retain selected events; only eight complete trial scopes are compared to official CAS hashes.',
 'No causal score claim from task ordinal; most actual instructions differ.',
 'No model calls, new evaluations, source edits or Brain publication in this audit.']}
(P/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: all100 accounting/instructions/final Answer/stdout,83 success review seals,17 loss indexes,65 responses,9 null finals, exact source rebuild.')
