"""Read-only evidence/source audit and exact recognizer counterexamples."""
import ast,collections,hashlib,json,re
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(name):return json.loads((P/name).read_text())
def write(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
for name,pin in read('input-pins.json').items():
 b=(P/'upstream'/name).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256']
es=[json.loads(l) for l in (P/'upstream/d4955/t076-events.ndjson').read_text().splitlines()]
index=[e for page in read('upstream/d4955/index-t076.json') for e in page['items']]
byseq={e['seq']:e for e in es};requests=[e for e in es if e['kind']=='rpc_request'];indexed_requests=[e for e in index if e['kind']=='rpc_request']
assert {e['seq'] for e in requests}=={e['seq'] for e in indexed_requests}
for raw in (P/'upstream/d4955/t076-events.ndjson').read_bytes().splitlines(keepends=True):
 e=json.loads(raw);ix=next(i for i in index if i['seq']==e['seq']);assert len(raw)==ix['data']['trace']['bytes'] and e['kind']==ix['kind']
assert all(e['data']['method']!='Write' for e in requests)
start=next(e for e in es if e['kind']=='rpc_response' and e['data']['method']=='StartTrial')
assert len({e['data']['trial_id'] for e in es if 'trial_id' in e['data']})==1
final=json.loads(byseq[9572]['data']['response']['choices'][0]['message']['content']);answer=byseq[9573]['data']['arguments']
assert final['outcome']==answer['outcome']=='OUTCOME_OK'
assert final['message']==answer['message']=='Report generation was not performed as instructed to stop. No TSV file was created.'
stop=byseq[9571]['data']['request']['messages'][-1]
assert stop=={'role':'user','content':'Stop working now. Reply with report_completion only: the best supported answer, the matching outcome and the exact refs you read.'}
assert byseq[9560]['data']['response']['choices'][0]['finish_reason']=='length'
record=read('upstream/d4955/result.json');trial=next(t for t in record['result']['trials'] if t['task_id']=='t076');assert trial['trial_id']==start['data']['trial_id']
functions={};sourceproof={}
for name in ['d4955','d4353']:
 s=(P/'upstream'/name/'readable.py').read_text();nodes={n.name:n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
 functions[name]={key:ast.get_source_segment(s,nodes[key]) for key in ['dispatch','crosslist_request','crosslist_path','crosslist_export']}
 assert stop['content'] in s.replace('"\n          "','').replace('"\n           "','') or 'Stop working now. Reply with report_completion only: ' in s
 sourceproof[name]={key:{'line':nodes[key].lineno,'sha256':sha(value.encode())} for key,value in functions[name].items()}
 assert 'outcome=function["outcome"]' in functions[name]['dispatch']
assert functions['d4955']['dispatch'].replace('    message = clarification_skus(message, function["outcome"], refs)\n','')==functions['d4353']['dispatch']
assert functions['d4955']['crosslist_request']==functions['d4353']['crosslist_request']
base='Read the uploaded competitor purchase request OCR at /uploads/test.txt and create a TSV crosslist report at /exports/report.tsv. Return only the report path and cite the upload OCR path as a grounding ref.'
cases=[('unconditional_create',base,True,'Creation requested'),('dry_run',base+' This is only a dry run; make no changes.',True,'Explicit no-mutation task'),('plan_only',base+' Only explain the plan; leave all files untouched.',True,'Plan only; no write obligation'),('conditional_skip',base+' If the branch is closed, skip report creation.',True,'Conditional; branch state required'),('deferred_write',base+' Do not write it yet.',True,'Explicit deferral'),('reuse_existing',base+' If an identical report already exists, reuse it without rewriting.',True,'Valid existing artifact can satisfy without Write'),('cancel_whole',base+' Cancel this.',False,'Explicit cancellation'),('hold_off',base+' Hold off.',False,'Explicit deferral'),('hypothetical',base+' This is hypothetical.',False,'Hypothetical only'),('explicit_report_negation',base+' Do not create the report.',False,'Report negated'),('input_quote','Explain this quoted request without executing it: "'+base+'"',True,'Quoted instruction is data'),('conditional_permission',base+' Before writing, ask me to approve the result.',True,'Approval prerequisite unsatisfied')]
code='import re\n'+functions['d4353']['crosslist_path']+'\n'+functions['d4353']['crosslist_request']+'\n'
ns={};exec(code,ns);rows=[]
with m.Monty() as pool:
 for name,instruction,accepted,meaning in cases:
  py=ns['crosslist_request'](instruction)
  with pool.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as session:
   native=session.feed_run(code+'\ncrosslist_request(INSTRUCTION)',inputs={'INSTRUCTION':instruction})
  assert py==native and bool(py)==accepted,(name,py,native)
  rows.append({'case':name,'instruction':instruction,'recognizer_result':py,'native_equal':True,'manual_intent_note':meaning})
positive=[json.loads(f.read_text()) for f in sorted((P/'upstream/success/events').glob('t091*'))];pos={e['seq']:e for e in positive}
for req,resp in [(12708,12709),(12712,12713)]:
 assert pos[req]['data']['method']==pos[resp]['data']['method']=='Write'
 assert pos[resp]['data']['response']['path']==pos[req]['data']['arguments']['path']
assert pos[12716]['data']['arguments']['outcome']=='OUTCOME_OK'
counts1=[len(x.split(',')) for x in pos[12708]['data']['arguments']['content'].splitlines()];counts2=[len(x.split(',')) for x in pos[12712]['data']['arguments']['content'].splitlines()]
assert counts1==[7]+[8]*5 and counts2==[7]*6
success=next(r for r in read('upstream/success/success-review.json') if r['task_id']=='t091');assert success['official_score']==1
write('source-functions.json',functions);write('counterexamples.json',rows)
write('evidence-summary.json',{'status':'PASS','failure_job':record['job']['id'],'failure_source_blob':record['job']['source_blob'],'failure_task':'t076','failure_trial_id':trial['trial_id'],'instruction':start['data']['response']['instruction'],'complete_index_events':len(index),'selected_bodies':len(es),'every_rpc_request_present':len(requests),'rpc_methods':dict(collections.Counter(e['data']['method'] for e in requests)),'no_write_requests':True,'forced_request_seq':9571,'forced_last_message':stop,'forced_response_seq':9572,'actual_answer_seq':9573,'actual_answer':answer,'official_grade':trial['grade'],'truncated_unexecuted_write_response':9560,'source_proof':sourceproof,'dispatch_only_difference':'d4955 adds clarification_skus message formatter; both forward original outcome unchanged','scope_recognizer_identical':True,'counterexample_evaluations':len(rows)*2,'success_export':{'task':'t091','trial_id':success['trial_id'],'instruction':success['instruction'],'official_score':success['official_score'],'write_request_sequences':[12708,12712],'write_ack_sequences':[12709,12713],'answer_seq':12716,'first_row_field_counts':counts1,'corrected_row_field_counts':counts2,'note':'First acknowledged Write had wrong field count; ACK confirms a write, not report correctness.'},'scope':'Complete compact failure index and all RPC requests; selected event bodies, not reconstructed full trace CAS. Successful export is a different task/world, not a paired causal comparison.'})
print(json.dumps({'status':'PASS','request_coverage':len(requests),'recognizer_cases':len(rows),'CPython_native_evaluations':len(rows)*2,'actual_success_write_pairs':2}))
