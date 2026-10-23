"""Reproduce exact event extraction and explicit manual judgments, not a semantic scorer."""
import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent; U=P.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
trials={t['task_id']:t for t in json.loads((U/'result.json').read_text())['result']['trials']}
starts={r['task_id']:r for r in json.loads((U/'instructions-all100.json').read_text())}
notes=dict(line.split('\t',1) for line in (P/'manual-notes.tsv').read_text().splitlines())
assert set(notes)=={k for k,t in trials.items() if t['grade']['score']==1};assert len(notes)==83
raw={};indexes={};receipts={};tails={}
for f in sorted((P/'receipts').glob('*.json')):
 r=json.loads(f.read_text());d=r.get('receipt',r)['structuredContent'];assert d['code']==0
 if 'discard' in f.name:continue
 assert not d['data']['output_truncated']
 x=json.loads(d['output'])
 if 'task_id' not in x:continue # Extra t100 discovery index, retained as receipt.
 task=x['task_id'];trial=trials[task]['trial_id'];idx=x.get('index',x.get('supplemental_index'))
 if idx:
  for e in idx['items']:
   assert e['data']['trial_id']==trial
   key=(task,e['seq']);assert key not in indexes or indexes[key]==e
   indexes[key]=e
  if 'index' in x:assert not idx['more'];tails[task]=idx
 for e in x.get('events',x.get('supplemental_events',[])):
  assert not e['more'] and e['bytes']==e['next_offset']==len(e['text'].encode())
  v=json.loads(e['text']);assert v['seq']==e['seq'] and v['data']['trial_id']==trial
  key=(task,e['seq']);assert key not in raw or raw[key]==e['text'];raw[key]=e['text'];receipts.setdefault(key,[]).append(str(f.relative_to(P)))
assert set(tails)==set(notes)
E=P/'events';E.mkdir(exist_ok=True);out=[];pins={};read_hashes=[]
for (task,seq),text in sorted(raw.items()):
 e=json.loads(text);key=(task,seq);assert key in indexes
 assert indexes[key]['data']['trace']['bytes']==len(text.encode())
 name=f'events/{task}-{seq}.ndjson';(P/name).write_bytes(text.encode());pins[name]=sha(text.encode())
 response=e['data'].get('response',{})
 if 'content' in response:
  assert sha(response['content'].encode())==response['sha256'];read_hashes.append({'task_id':task,'seq':seq,'path':response['path'],'sha256':response['sha256']})
for task,note in sorted(notes.items()):
 t=trials[task];start=starts[task];se=json.loads(start['event']['text']);instruction=se['data']['response']['instruction'];assert se['data']['trial_id']==t['trial_id']
 events=[json.loads(v) for (k,s),v in raw.items() if k==task]
 answers=[e for e in events if e['kind']=='rpc_request' and e['data'].get('method')=='Answer'];assert len(answers)==1
 a=answers[0];finished=[e for e in events if e['kind']=='agent_finished'];assert len(finished)==1;fin=finished[0]
 ack=[e for e in events if e['kind']=='rpc_response' and e['data'].get('method')=='Answer'];assert len(ack)==1 and ack[0]['data'].get('response')=={}
 assert fin['data']['task_id']==task and fin['data']['state']==t['state']=='answered'
 stdout=fin['data']['output'];assert len(stdout.encode())==fin['data']['output_bytes']==t['output_bytes'];assert fin['data']['ecom_calls']==t['ecom_calls']
 def ref(e):
  name=f"events/{task}-{e['seq']}.ndjson";return {'seq':e['seq'],'path':name,'sha256':pins[name],'receipts':receipts[(task,e['seq'])]}
 flags=[]
 invalid=[line for line in stdout.splitlines() if line.startswith('Invalid step')]
 if invalid:flags.append('recovered_invalid_action')
 if task=='t045':flags.append('proposed_placeholder_ref_removed_before_final')
 if task=='t061':flags.append('literal_unicode_escape_presentation')
 if task=='t079':flags.append('foreign_owner_reads_during_discovery')
 if task=='t091':flags.extend(['recovered_sql_connection_error','leading_space_path_only_answer'])
 if task in ['t036','t056','t076']:flags.append('preview_only_stdout_not_write_oracle')
 if task=='t100':flags.append('disjunctive_blocker_not_resolved')
 level='L2: exact instruction + final Answer request/ack + complete agent_finished stdout; sampled tail index'
 if task in ['t079','t091']:level+='; L3 targeted supporting RPC bodies'
 uncertainty='No complete action transcript or independent catalogue/policy/mutation oracle for this success; grader credit is retained, not independent semantic certification. Stdout logs attempted actions and handler summaries, not universal proof of execution.'
 if task=='t079':uncertainty+=' Targeted Reads prove foreign ownership; whether discovery access itself violates policy is not settled here. No foreign record was disclosed in the final answer or mutated in the targeted sequence.'
 if task=='t091':uncertainty+=' SQL error is exitCode1, not Exec404. Write acknowledgement is verified; all future-date inventory values are not independently recomputed.'
 out.append({'task_id':task,'trial_id':t['trial_id'],'official_score':t['grade']['score'],'official_grade':t['grade'],'instruction':instruction,'instruction_sha256':sha(instruction.encode()),'instruction_event_sha256':sha(start['event']['text'].encode()),'answer_event':ref(a),'answer_ack_event':ref(ack[0]),'agent_finished_event':ref(fin),'answer':a['data']['arguments'],'outcome':a['data']['arguments']['outcome'],'stdout':stdout,'observation':note,'diagnosis':note,'uncertainty':uncertainty,'evidence_level':level,'flags':flags,'recovered_invalid_action_lines':invalid,'official_usage':t['usage'],'agent_finished_usage':fin['data']['usage'],'full_trace_cas_descriptor':t['trace'],'full_trace_cas_independently_reassembled':False,'supplemental_event_refs':[ref(e) for e in events if e not in [a,ack[0],fin]]})
dump(P/'success-review.json',out)
dump(P/'event-manifest.json',{'events':pins,'read_content_hash_checks':read_hashes,'inputs':{n:sha((U/n).read_bytes()) for n in ['result.json','instructions-all100.json']},'judgment_source_sha256':sha((P/'manual-notes.tsv').read_bytes()),'extraction_script_sha256':sha(Path(__file__).read_bytes())})
md=['# Successful-task answer and execution-summary review','', 'All 83 official full-credit trials reviewed against exact instructions, final Answer RPC and complete agent_finished stdout. L2 = these exact events plus tail index. L3 = targeted supporting RPC bodies for t079/t091. These are manual observations, not regraded outcomes or full action-by-action certification.','', '| Task | Outcome | Evidence | Manual observation |','|---|---|---|---|']
for r in out:md.append('| '+r['task_id']+' | '+r['outcome'].replace('OUTCOME_','')+' | '+('L3' if r['task_id'] in ['t079','t091'] else 'L2')+' | '+r['observation'].replace('|','\\|')+' |')
(P/'success-review.md').write_text('\n'.join(md)+'\n')
verification={'status':'passed','successful_tasks':len(out),'unique_exact_events':len(raw),'answer_requests':83,'answer_acknowledgements':83,'complete_agent_finished_outputs':83,'all_event_lengths_and_index_lengths_match':True,'all_trial_ids_instruction_ids_and_official_output_lengths_match':True,'read_content_hashes_verified':len(read_hashes),'raw_complete_trial_cas_reassembly':False,'invalid_action_tasks':{r['task_id']:len(r['recovered_invalid_action_lines']) for r in out if r['recovered_invalid_action_lines']},'all_agent_finished_usage_zero_model_calls':all(r['agent_finished_usage']['model_calls']==0 for r in out),'official_total_model_calls_successes':sum(r['official_usage']['model_calls'] for r in out),'model_calls_during_audit':0,'brain_mutations':0,'manual_judgments_not_automatic_semantic_scorer':True}
dump(P/'verification.json',verification);print(json.dumps(verification,indent=2))
