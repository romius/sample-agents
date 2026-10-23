"""Read-only offline evidence joins/source comparison and isolated exact rebuild."""
import ast, collections, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
result=json.loads((P/'official-result.json').read_text());trials=result['result']['trials'];bytask={t['task_id']:t for t in trials}
assert len(trials)==len(bytask)==100
assert sorted(bytask)==[f't{i:03}' for i in range(1,101)]
assert result['job']['source_blob']==result['result']['source']['sha256']==sha((P/'upstream/agent.py').read_bytes())=='588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
assert result['job']['state']=='completed' and all(t['state']=='answered' for t in trials)
assert all(t['trace']['sealed'] and t['grade']['available'] for t in trials)
assert abs(sum(t['grade']['score'] for t in trials)/100-result['result']['run_score'])<1e-7
instructions=json.loads((P/'instructions.json').read_text())
assert len(instructions)==100
for r in instructions:
 e=r['start_trial_event'];t=bytask[r['task_id']]
 assert e['data']['response']['instruction']==r['instruction']
 assert sha(r['instruction'].encode())==r['instruction_sha256']
 assert e['data']['response']['taskId']==r['task_id']
 assert e['data']['trial_id']==e['data']['response']['trialId']==r['trial_id']==t['trial_id']
 assert e['data']['response']['runId']==result['result']['run_id']
losses=[t for t in trials if t['grade']['score']<1];indexes={};event_to_task={}
for t in losses:
 task=t['task_id'];x=json.loads((P/f'losses/{task}-index.json').read_text());items=x['items']
 assert items==[e for page in x['pages'] for e in page['items']]
 assert not x['pages'][-1]['more']
 assert [e['seq'] for e in items]==sorted({e['seq'] for e in items})
 assert all(e['data']['trial_id']==t['trial_id'] for e in items)
 for i,page in enumerate(x['pages'][:-1]):assert page['next_after']==page['items'][-1]['seq'] and page['next_after']<x['pages'][i+1]['items'][0]['seq']
 indexes[task]=items
 for e in items:event_to_task[e['seq']]=(task,e)
read_checks=0
for f in (P/'events').glob('*.json'):
 raw=f.read_bytes();e=json.loads(raw);task,index=event_to_task[e['seq']]
 assert e['data']['trial_id']==bytask[task]['trial_id']
 assert e['kind']==index['kind'] and len(raw)==index['data']['trace']['bytes']
 response=e['data'].get('response',{})
 if isinstance(response,dict) and 'content' in response and 'sha256' in response:
  assert sha(response['content'].encode())==response['sha256'];read_checks+=1
for receipt_name in ['source-export-receipt.json','dependency-export-receipt.json']:
 r=json.loads((P/'receipts'/receipt_name).read_text())
 for name,d in r['data']['files'].items():
  n='build_combined.py' if name=='build' else name+'.py';raw=(P/'upstream'/n).read_bytes()
  assert len(raw)==d['size'] and sha(raw)==d['blob']
# Exact parent/build closure; run only in isolated copy.
with tempfile.TemporaryDirectory(prefix='d4353-audit-') as tmp:
 q=Path(tmp)/'upstream';shutil.copytree(P/'upstream',q)
 r=subprocess.run([sys.executable,str(q/'build_combined.py')],capture_output=True,text=True)
 assert r.returncode==0,r.stderr
 for n in ['agent.py','readable.py','decoded.py','build-receipt.json']:assert (q/n).read_bytes()==(P/'upstream'/n).read_bytes(),n
old=P/'comparison/stack-e';old_source=(old/'upstream/readable.py').read_text();new_source=(P/'upstream/readable.py').read_text()
def funcs(s):return {n.name:n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
a,b=funcs(old_source),funcs(new_source)
keys=['crosslist_parse_ocr','i2c_cleanup','route_policy_docs','i2c_llm_narrow','i2c_dispatch','dispatch','recoverable_lookup_error']
overlap={k:{'ast_equal':ast.dump(a[k],include_attributes=False)==ast.dump(b[k],include_attributes=False),'source_equal':ast.get_source_segment(old_source,a[k])==ast.get_source_segment(new_source,b[k]),'new_source_sha256':sha(ast.get_source_segment(new_source,b[k]).encode())} for k in keys}
old_instructions={}
for f in sorted(old.glob('instructions-*.json')):
 for x in json.loads(f.read_text()):old_instructions[x['task_id']]=x['event']['data']['response']['instruction']
assert len(old_instructions)==100
instruction_differences=[r['task_id'] for r in instructions if r['instruction']!=old_instructions[r['task_id']]]
old_result=json.loads((old/'result.json').read_text())
# Evaluate evidence-backed arithmetic, separate from official grader feedback.
def body(seq):return json.loads((P/f'events/{seq}.json').read_text())['data']['response']
store=json.loads(body(3355)['content']);inventory={r['sku']:r for r in store['inventory']}
same_day={sku:max(inventory[sku]['on_hand']-inventory[sku]['reserved'],0) for sku in ['PT-MOW-STI-RMA235-AK30','PT-WASH-BOS-UA135']}
assert same_day=={'PT-MOW-STI-RMA235-AK30':2,'PT-WASH-BOS-UA135':9}
products=[json.loads(body(seq)['content']) for seq in [11426,11418,11450,11404]]
subtotal=sum(p['price_cents']*q for p,q in zip(products,[1,1,2,1]));assert subtotal==101450
report={'status':'PASS','source':result['result']['source'],'official_run_score':result['result']['run_score'],'computed_mean':sum(t['grade']['score'] for t in trials)/100,'selected_trials':100,'completed_trials':100,'execution_failures':0,'fully_credited':sum(t['grade']['score']==1 for t in trials),'zero_tasks':[t['task_id'] for t in trials if t['grade']['score']==0],'partial_tasks':[t['task_id'] for t in trials if 0<t['grade']['score']<1],'all100_instruction_identity_joins':True,'complete_loss_indexes':{k:len(v) for k,v in indexes.items()},'selected_event_identity_size_joins':len(list((P/'events').glob('*.json'))),'read_content_hashes_verified':read_checks,'source_dependency_export_hashes_verified':True,'isolated_exact_rebuild':True,'comparison_with_previous_record':{'parent_source':'d3909r1','official_score_delta_points':100*(result['result']['run_score']-old_result['result']['run_score']),'instruction_differences':instruction_differences,'same_instruction_count':100-len(instruction_differences),'no_causal_attribution':True},'source_overlap':overlap,'t023_independent_inventory_check':{'store_path':body(3355)['path'],'same_day':same_day,'receipt_quantities':{'PT-MOW-STI-RMA235-AK30':4,'PT-WASH-BOS-UA135':14},'both_short':True,'note':'Correct NO truth value does not validate malformed OCR SKU lookup or missing product references.'},'t080_independent_arithmetic':{'product_sequence':[p['sku'] for p in products],'quantities':[1,1,2,1],'current_subtotal_cents':subtotal,'old_receipt_subtotal_cents':101382,'difference_cents':68,'requested_limit_cents':200,'within_requested_limit':True,'note':'Manual receipt/product calculation; official grade detail identifies missing/extraneous product references first.'},'limitations':['The official result API receipt is preserved; the full summary CAS bytes were not reconstructed.','All ten loss indexes are complete; selected full events only, not all whole trial traces.','Same instruction is not proof of identical underlying world.','Existing source overlap is static evidence, not new-parent whole-agent integration validation.']}
(P/'audit-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','official_run_score','fully_credited','zero_tasks','partial_tasks','read_content_hashes_verified','isolated_exact_rebuild','comparison_with_previous_record']},indent=2))
