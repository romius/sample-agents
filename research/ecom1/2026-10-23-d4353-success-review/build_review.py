"""Exact extraction/joins plus explicit manual observations; not a semantic scorer."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;U=P/'upstream';sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
for dep in json.loads((P/'input-provenance.json').read_text()):assert sha((P/dep['local']).read_bytes())==dep['sha256']
trials={t['task_id']:t for t in json.loads((U/'official-result.json').read_text())['result']['trials']}
starts={r['task_id']:r for r in json.loads((U/'instructions.json').read_text())}
notes=dict(line.split('\t',1) for line in (P/'manual-notes.tsv').read_text().splitlines());assert len(notes)==90 and set(notes)=={k for k,t in trials.items() if t['grade']['score']==1}
raw={};indexes={};origins={};tails={}
def add(task,e,origin):
 assert not e['more'] and e['bytes']==e['next_offset']==len(e['text'].encode())
 v=json.loads(e['text']);assert v['seq']==e['seq'] and v['data']['trial_id']==trials[task]['trial_id']
 key=(task,e['seq']);assert key not in raw or raw[key]==e['text'];raw[key]=e['text'];origins.setdefault(key,[]).append(origin)
for f in sorted((U/'receipts').glob('start-*.json')):
 for r in json.loads(f.read_text()):
  task=r['task_id']
  if task not in notes:continue
  e=r['receipt'];indexes[(task,e['seq'])]=r['index'];add(task,e,str(f.relative_to(P)))
for f in sorted((P/'receipts').glob('*.json')):
 if 'start' in f.name:continue
 r=json.loads(f.read_text());d=r['receipt']['structuredContent'];assert d['code']==0
 if 'discard' in f.name:continue
 assert not d['data']['output_truncated'];x=json.loads(d['output']);task=x['task_id'];idx=x.get('index',x.get('supplemental_index'))
 if idx:
  for e in idx['items']:
   assert e['data']['trial_id']==trials[task]['trial_id'];key=(task,e['seq']);assert key not in indexes or indexes[key]==e;indexes[key]=e
  if 'index' in x:assert not idx['more'];tails[task]=idx
 for e in x.get('events',x.get('supplemental_events',[])):add(task,e,str(f.relative_to(P)))
assert set(tails)==set(notes)
(P/'events').mkdir(exist_ok=True);pins={};read_hashes=[]
for (task,seq),text in sorted(raw.items()):
 e=json.loads(text);assert indexes[(task,seq)]['data']['trace']['bytes']==len(text.encode());name=f'events/{task}-{seq}.ndjson';(P/name).write_bytes(text.encode());pins[name]=sha(text.encode())
 response=e['data'].get('response',{})
 if 'content' in response:assert sha(response['content'].encode())==response['sha256'];read_hashes.append({'task_id':task,'seq':seq,'path':response['path'],'sha256':response['sha256']})
out=[]
for task,note in sorted(notes.items()):
 t=trials[task];start=starts[task];instruction=start['instruction'];assert sha(instruction.encode())==start['instruction_sha256']
 events=[json.loads(v) for (k,s),v in raw.items() if k==task]
 se=[e for e in events if e['kind']=='rpc_response' and e['data'].get('method')=='StartTrial'];assert len(se)==1 and se[0]==start['start_trial_event']
 def one(kind,method=None):
  found=[e for e in events if e['kind']==kind and (method is None or e['data'].get('method')==method)];assert len(found)==1;return found[0]
 a=one('rpc_request','Answer');ack=one('rpc_response','Answer');fin=one('agent_finished');assert ack['data']['response']=={}
 assert fin['data']['task_id']==task and fin['data']['state']==t['state']=='answered';stdout=fin['data']['output']
 assert len(stdout.encode())==fin['data']['output_bytes']==t['output_bytes'] and fin['data']['ecom_calls']==t['ecom_calls']
 def ref(e):
  name=f"events/{task}-{e['seq']}.ndjson";return {'seq':e['seq'],'path':name,'sha256':pins[name],'receipts':origins[(task,e['seq'])]}
 invalid=[l for l in stdout.splitlines() if l.startswith('Invalid step')];flags=[]
 if invalid:flags.append('recovered_invalid_action')
 if task in ['t006','t022','t042','t051','t094']:flags.append('explicit_embedded_override_rejected')
 if task in ['t016','t036','t056','t076']:flags.append('preview_only_stdout_not_write_oracle')
 if task in ['t039','t060']:flags.append('actual_successful_cleanup_rpc_witness')
 if task=='t091':flags.extend(['recovered_list_404','malformed_csv_successfully_written_then_corrected'])
 if task=='t100':flags.append('disjunctive_blocker_not_resolved')
 level='L2: exact StartTrial instruction + final Answer request/ack + complete agent_finished stdout; sampled tail index'
 if task in ['t039','t060','t091']:level+='; L3 targeted supporting RPC bodies'
 uncertainty='Official grade retained; no complete action-body/CAS certification or independent business-data oracle. Stdout can contain intended steps and summaries, not universal execution proof. Unfetched catalogue, identity, inventory and policy details are not independently certified.'
 if task in ['t039','t060']:uncertainty+=' Targeted List/Delete acknowledgements verify selected operations; no post-delete readback was observed or invented. Existing partial-Delete error concern remains untested by these successful real operations.'
 if task=='t091':uncertainty+=' Both CSV writes are confirmed; first malformed intermediate file was actually acknowledged, then corrected. Final future inventory values are not independently recomputed.'
 if task=='t079':uncertainty+=' d4702 comparison differs in task bytes, product, identity and path layout; absence of foreign Read steps here is not a causal code comparison.'
 out.append({'task_id':task,'trial_id':t['trial_id'],'official_score':t['grade']['score'],'official_grade':t['grade'],'instruction':instruction,'instruction_sha256':sha(instruction.encode()),'instruction_event':ref(se[0]),'answer_event':ref(a),'answer_ack_event':ref(ack),'agent_finished_event':ref(fin),'answer':a['data']['arguments'],'outcome':a['data']['arguments']['outcome'],'stdout':stdout,'observation':note,'diagnosis':note,'uncertainty':uncertainty,'evidence_level':level,'flags':flags,'recovered_invalid_action_lines':invalid,'official_usage':t['usage'],'agent_finished_usage':fin['data']['usage'],'full_trace_cas_descriptor':t['trace'],'full_trace_cas_independently_reassembled':False,'supplemental_event_refs':[ref(e) for e in events if e not in [se[0],a,ack,fin]]})
dump(P/'success-review.json',out)
dump(P/'event-manifest.json',{'events':pins,'read_content_hash_checks':read_hashes,'inputs':{n:sha((U/n).read_bytes()) for n in ['official-result.json','instructions.json']},'judgment_source_sha256':sha((P/'manual-notes.tsv').read_bytes()),'extraction_script_sha256':sha(Path(__file__).read_bytes())})
md=['# Current-record successful-task final-log review','', 'All 90 official full-credit trials reviewed against exact instructions, final Answer RPC and complete agent_finished stdout. L2 = these exact events plus tail index. L3 = targeted supporting RPC bodies for t039/t060/t091. Explicit manual observations, not regraded outcomes or full action-by-action certification.','', '| Task | Outcome | Evidence | Manual observation |','|---|---|---|---|']
for r in out:md.append('| '+r['task_id']+' | '+r['outcome'].replace('OUTCOME_','')+' | '+('L3' if r['task_id'] in ['t039','t060','t091'] else 'L2')+' | '+r['observation'].replace('|','\\|')+' |')
(P/'success-review.md').write_text('\n'.join(md)+'\n')
v={'status':'passed','successful_tasks':len(out),'unique_exact_events':len(raw),'start_trial_events':90,'answer_requests':90,'answer_acknowledgements':90,'complete_agent_finished_outputs':90,'all_event_lengths_and_index_lengths_match':True,'all_trial_instruction_ids_and_official_output_lengths_match':True,'read_content_hashes_verified':len(read_hashes),'raw_complete_trial_cas_reassembly':False,'invalid_action_tasks':{r['task_id']:len(r['recovered_invalid_action_lines']) for r in out if r['recovered_invalid_action_lines']},'all_agent_finished_usage_zero_model_calls':all(r['agent_finished_usage']['model_calls']==0 for r in out),'official_total_model_calls_successes':sum(r['official_usage']['model_calls'] for r in out),'model_calls_during_audit':0,'brain_mutations':0,'manual_judgments_not_automatic_semantic_scorer':True}
dump(P/'verification.json',v);print(json.dumps(v,indent=2))
