"""Audit each complete sealed trial; no inference, evaluation or business grading."""
import ast,collections,hashlib,importlib.metadata,json,os,re,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
official=json.loads((P/'official-result.json').read_text());job=official['job'];result=official['result']
assert job['id']=='j2f9717b672c04c9a94f1df3219579692' and job['document']=='d5204' and job['revision']==1
assert job['run_id']==result['run_id']=='run-22rLKF8bmYV6huGenJqrnWgj8'
assert job['state']==result['state']=='completed'
assert result['completed_trials']==result['failed_trials']==result['selected_trials']==result['total_trials']==100
assert result['run_score']==0 and result['run_score_available'] and result['run_state']=='RUN_STATE_EVALUATED'
for k in ('model_calls','model_cost_usd','unknown_cost_calls','pending_calls','prompt_tokens','completion_tokens','total_tokens','cancelled_trials','skipped_trials','unselected_trials'):assert result[k]==0,k
assert result['reported_cost_usd']=='0' and result['cost_complete']
up=P/'closure/2026-10-22-inventory-integration';packed=(up/'agent.py').read_bytes();prepack=(up/'prepack.py').read_text();readable=(up/'readable.py').read_text()
assert sha(packed)==job['source_blob']==result['source']['sha256']=='0cb742d544039b1d9dc4a862021ee1bfe3967c2ced8082756525e075b6c1ca67'
assert importlib.metadata.version('python-minifier')=='3.4.0'
for item in json.loads((up/'dependencies.json').read_text())['exact_files']:
 b=(P/'closure'/item['path']).read_bytes();assert len(b)==item['bytes'] and sha(b)==item['sha256']
prior=json.loads((P/'prior-probe/verification.json').read_text());b=(P/'prior-probe/trace.jsonl').read_bytes();assert len(b)==prior['sealed_trace_bytes'] and sha(b)==prior['trace_sha256']
values=[];exec(packed.decode(),{'exec':values.append});assert values==[prepack]
# Prove failure location evaluates method as a value, not a method invocation.
call=next(n for n in ast.walk(ast.parse(prepack)) if isinstance(n,ast.Call) and n.lineno==2094 and isinstance(n.func,ast.Name) and n.func.id=='Db')
assert isinstance(call.args[1],ast.Attribute) and isinstance(call.args[1].value,ast.Name) and call.args[1].value.id=='bitgn' and call.args[1].attr=='call'
assert prepack.splitlines()[2093]=="AE=Db(bitgn.task()['instruction'],bitgn.call)"
readable_call=next(n for n in ast.walk(ast.parse(readable)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='ix_run' and n.args and isinstance(n.args[-1],ast.Attribute))
assert readable_call.lineno==3914 and ast.get_source_segment(readable,readable_call)=='ix_run(bitgn.task()["instruction"],bitgn.call)'
expected_tasks=[f't{i:03d}' for i in range(1,101)];trials={t['task_id']:t for t in result['trials']};assert sorted(trials)==expected_tasks
trace_meta={t['task_id']:t for t in result['traces'] if t['task_id'] is not None};assert sorted(trace_meta)==expected_tasks
rows=[];error_hashes=collections.Counter();terminal_errors=collections.Counter();events_total=0;trace_bytes=0;instructions=[]
for task in expected_tasks:
 t=trials[task];path=P/'traces'/f'{task}.ndjson';blob=path.read_bytes();index=json.loads((P/'traces'/f'{task}-index.json').read_text())
 assert sha(blob)==t['trace']['blob']==trace_meta[task]['blob'] and len(blob)==t['trace']['bytes']==trace_meta[task]['bytes']
 assert t['trace']['sealed'] and trace_meta[task]['sealed'] and not index['more']
 events=[json.loads(l) for l in blob.splitlines()];assert len(events)==len(index['items'])==6
 expected=['rpc_request','rpc_response','agent_error','agent_finished','rpc_request','rpc_response']
 assert [e['kind'] for e in events]==expected,(task,[e['kind'] for e in events])
 cursor=0
 for raw,e,idx in zip(blob.splitlines(keepends=True),events,index['items']):
  assert e['seq']==idx['seq'] and e['kind']==idx['kind'] and e['time']==idx['time']
  assert e['data']['trial_id']==idx['data']['trial_id']==t['trial_id']
  assert idx['data']['trace']['offset']==cursor and idx['data']['trace']['bytes']==len(raw);cursor+=len(raw)
 assert cursor==len(blob)
 startq,start,error,finish,endq,end=events
 assert startq['data']['method']==start['data']['method']=='StartTrial'
 assert startq['data']['arguments']=={'trialId':t['trial_id']}
 st=start['data']['response'];assert st['taskId']==task and st['trialId']==t['trial_id'] and st['runId']==result['run_id'] and st['benchmarkId']==result['benchmark']
 instruction=st['instruction'];assert isinstance(instruction,str) and instruction
 err=error['data']['error'];tail=err.splitlines()[-1]
 assert tail=="AttributeError: 'BitGN' object has no attribute 'call'",(task,tail)
 assert '  File "<string>", line 2094, in <module>\n'+tail in err
 assert '  File "<python-input-0>", line 11, in <module>\n    '+packed.decode().splitlines()[10]+'\n' in err
 assert len(re.findall(r'File "',err))==2 # no ix_run frame entered
 f=finish['data'];assert f['task_id']==task and f['state']==t['state']=='failed'
 assert f['output']=='' and f['output_bytes']==t['output_bytes']==0 and f['ecom_calls']==t['ecom_calls']==0
 assert f['error']==t['error'] and err.startswith(f['error']) # summary/finished error is truncated, full event is authoritative
 assert len(f['error'])==2000
 for usage in (f['usage'],t['usage']):
  for k in ('model_calls','model_cost_usd','unknown_cost_calls','pending_calls','prompt_tokens','completion_tokens','total_tokens'):assert usage[k]==0
  assert usage['reported_cost_usd']=='0' and usage['cost_complete']
 assert t['grade']['available'] and t['grade']['score']==0 and t['grade']['detail']=="['no answer provided']"
 assert f['grade']=={'available':False,'score':None} # grade arrives after submission
 assert endq['data']['method']==end['data']['method']=='EndTrial'
 assert endq['data']['arguments']=={'trialId':t['trial_id']}
 assert end['data']['response']=={'trialId':t['trial_id'],'state':'TRIAL_STATE_DONE'}
 eh=sha(err.encode());error_hashes[eh]+=1;terminal_errors[tail]+=1;events_total+=len(events);trace_bytes+=len(blob)
 row={'task_id':task,'trial_id':t['trial_id'],'instruction':instruction,'instruction_sha256':sha(instruction.encode()),'state':t['state'],'grade':t['grade'],'trace_sha256':sha(blob),'trace_bytes':len(blob),'seqs':{name:e['seq'] for name,e in zip(['start_request','start_response','agent_error','agent_finished','end_request','end_response'],events)},'full_error_sha256':eh,'full_error_bytes':len(err.encode()),'terminal_error':tail,'failure_location':{'packed_line':11,'decoded_line':2094,'readable_line':3914,'expression':"AE=Db(bitgn.task()['instruction'],bitgn.call)",'ix_run_invoked':False},'stdout':f['output'],'stdout_bytes':0,'ecom_calls':0,'usage':t['usage'],'end_trial':end['data']['response']}
 rows.append(row);instructions.append({'task_id':task,'trial_id':t['trial_id'],'instruction':instruction,'sha256':row['instruction_sha256']})
assert len(error_hashes)==1 and next(iter(error_hashes.values()))==100
(P/'failure-template.txt').write_text(next(json.loads(l)['data']['error'] for l in (P/'traces/t001.ndjson').read_text().splitlines() if json.loads(l)['kind']=='agent_error'))
for name,data in [('all-task-review.json',rows),('instructions.json',instructions)]: (P/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
# Rebuild immutable submission in a temporary dependency closure; no source edits.
with tempfile.TemporaryDirectory(prefix='d5204-exact-build-') as tmp:
 dst=Path(tmp)/'closure';shutil.copytree(P/'closure',dst)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');script=dst/'2026-10-22-inventory-integration/build.py'
 proc=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(script)],env=env,capture_output=True,text=True)
 assert proc.returncode==0,(proc.stdout,proc.stderr)
 for n in ['agent.py','readable.py','prepack.py','manifest.json']:assert (script.parent/n).read_bytes()==(up/n).read_bytes(),n
summary={'status':'PASS','job':job['id'],'source':'d5204r1','source_bytes':len(packed),'source_sha256':sha(packed),'exact_build_reproduced':True,'run_id':result['run_id'],'finished_at':result['finished_at'],'official_score':0,'completed_trials':100,'failed_trials':100,'every_full_trace_CAS_verified':True,'complete_trial_traces':100,'trace_bytes':trace_bytes,'events_checked':events_total,'each_event_shape':expected,'instructions_preserved':100,'full_error_hash_counts':dict(error_hashes),'terminal_error_counts':dict(terminal_errors),'failures_before_ix_run_body':100,'ecom_actions':0,'model_calls':0,'reported_cost_usd':'0','cost_complete':True,'stdout_bytes':0,'successful_EndTrial_responses':100,'summary_errors_truncated_to_chars':2000,'business_correctness_evaluated':False,'no_new_probe_or_model_calls':True}
(P/'audit-report.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
