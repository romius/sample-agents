"""Verify evidence completeness/accounting; does not score semantic correctness."""
import collections,hashlib,json
from decimal import Decimal
from pathlib import Path
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert json.loads(''.join(load(P/'receipts/result-json-parts.json')['parts']))==load(P/'result.json')
r=load(P/'result.json')['result'];ts={t['task_id']:t for t in r['trials']}
assert len(ts)==100 and r['completed_trials']==100 and r['failed_trials']==0
assert sum(t['grade']['score']==1 for t in ts.values())==83
assert sum(t['grade']['score']==0 for t in ts.values())==12
serialized_grade_mean=sum(Decimal(str(t['grade']['score'])) for t in ts.values())/100
aggregate_delta=Decimal(str(r['run_score']))-serialized_grade_mean
assert abs(aggregate_delta)<Decimal('0.000001')  # Report actual discrepancy, do not claim exact recomputation.
for key in ('model_calls','prompt_tokens','completion_tokens','total_tokens','unknown_cost_calls','pending_calls'):
 assert sum(t['usage'][key] for t in ts.values())==r[key],key
assert sum(Decimal(t['usage']['reported_cost_usd']) for t in ts.values())==Decimal(r['reported_cost_usd'])
assert r['cost_complete'] and all(t['usage']['cost_complete'] for t in ts.values())
ins={x['task_id']:x for x in load(P/'instructions-all100.json')};assert set(ins)==set(ts)
for t,x in ins.items():
 e=json.loads(x['event']['text']);d=e['data']['response']
 assert not x['event']['more'] and x['event']['bytes']==len(x['event']['text'].encode())
 assert d['taskId']==t and d['trialId']==ts[t]['trial_id'] and d['runId']==r['run_id']
 assert e['kind']=='rpc_response' and e['data']['method']=='StartTrial'
rows=load(P/'all100-review.json');assert {x['task_id'] for x in rows}==set(ts)
for x in rows:
 t=x['task_id'];instruction=json.loads(ins[t]['event']['text'])['data']['response']['instruction']
 assert x['instruction']==instruction and x['instruction_sha256']==sha(instruction.encode())
 assert x['official_grade']==ts[t]['grade'] and x['answer'] and x['observation'] and x['uncertainty']
 for kind in ('answer_event','agent_finished_event'):
  ref=x[kind];p=P/ref['path']
  if p.suffix=='.ndjson':b=next(b for b in p.read_bytes().splitlines(keepends=True) if json.loads(b)['seq']==ref['seq'])
  else:b=p.read_bytes()
  assert sha(b)==ref['sha256'],(t,kind)
for n,v in load(P/'success-evidence/SHA256SUMS.json').items():
 assert sha((P/'success-evidence'/n).read_bytes())==(v if isinstance(v,str) else v['sha256']),n
assert not [x for x in rows if ' Candidates: ' in x['answer']['message']]
reads=[];modelrows=[];scopes=[]
for f in sorted(P.glob('index-t*.json')):
 t=f.stem.removeprefix('index-');pages=load(f);assert not pages[-1]['more'] and all(p['more'] for p in pages[:-1])
 idx=[e for p in pages for e in p['items']];seq=[e['seq'] for e in idx];assert seq==sorted(set(seq))
 off=0
 for e in idx:assert e['data']['trace']['offset']==off;off+=e['data']['trace']['bytes']
 assert off==ts[t]['trace']['bytes'] and ts[t]['trace']['sealed']
 assert idx[0]['data']['method']=='StartTrial' and idx[-1]['data']['method']=='EndTrial' and idx[-1]['kind']=='rpc_response'
 raw=(P/(t+'-events.ndjson')).read_bytes();es=[json.loads(x) for x in raw.splitlines()];by={e['seq']:e for e in es}
 assert len(by)==len(es)
 for selected in load(P/'additional-harvest-plan.json')[t]:assert selected['seq'] in by,(t,selected['seq'])
 for b in raw.splitlines(keepends=True):
  e=json.loads(b);ix=next(z for z in idx if z['seq']==e['seq']);assert len(b)==ix['data']['trace']['bytes'] and e['kind']==ix['kind']
  assert e['data'].get('trial_id',ts[t]['trial_id'])==ts[t]['trial_id']
 for e in idx:
  if e['kind'] in ('rpc_request','llm_response','llm_error','llm_retry','agent_error','agent_finished'):assert e['seq'] in by,(t,e['seq'])
 if len(es)==len(idx):assert sha(raw)==ts[t]['trace']['blob']
 errors=[e for e in idx if e['kind'] in ('llm_error','llm_retry','agent_error')]
 models=[e for e in es if e['kind']=='llm_response'];assert len(models)==ts[t]['usage']['model_calls']
 assert len({e['data']['call'] for e in models})==len(models)
 for e in models:
  d=e['data'];resp=d['response'];assert d['status']==200 and resp['provider']=='DeepInfra' and d['model']=='openai/gpt-oss-120b'
  c=resp['choices'][0];modelrows.append(dict(task=t,seq=e['seq'],call=d['call'],status=d['status'],provider=resp['provider'],finish_reason=c['finish_reason'],null_content=c['message']['content'] is None,cost=str(resp['usage']['cost']),tokens=resp['usage']['total_tokens']))
 assert abs(sum(Decimal(str(e['data']['response']['usage']['cost'])) for e in models)-Decimal(ts[t]['usage']['reported_cost_usd']))<Decimal('0.000000000001')
 for key in ('prompt_tokens','completion_tokens','total_tokens'):assert sum(e['data']['response']['usage'][key] for e in models)==ts[t]['usage'][key]
 for e in es:
  if e['kind']=='rpc_response' and e['data']['method']=='Read':
   d=e['data']['response'];assert sha(d['content'].encode())==d['sha256']
   request=by[e['seq']-1];assert request['data']['method']=='Read' and request['data']['arguments']['path']==d['path']
   reads.append(dict(task=t,seq=e['seq'],path=d['path'],sha256=d['sha256'],bytes=len(d['content'].encode()),envelope_keys=sorted(d),truncation_fields={k:v for k,v in d.items() if 'trunc' in k.lower()}))
 for e in es:
  if e['kind']=='llm_request':
   d=e['data'];req=d['request'];assert req['model']=='openai/gpt-oss-120b' and req['provider']['only']==['deepinfra/bf16'] and req['provider']['allow_fallbacks'] is False
   assert any(z['data']['call']==d['call'] for z in models)
 scopes.append(dict(task=t,indexed_events=len(idx),retained_events=len(es),full_cas_verified=len(idx)==len(es),error_retry_events=len(errors)))
report=dict(status='PASS',all100_actual_instructions_answers_stdout=True,official_score=r['run_score'],serialized_grade_mean=str(serialized_grade_mean),reported_aggregate_minus_serialized_mean=str(aggregate_delta),aggregate_tolerance='0.000001; exact numerical cause not inferred',official_calls=r['model_calls'],official_cost=r['reported_cost_usd'],official_cost_complete=r['cost_complete'],official_tokens=r['total_tokens'],loss_model_responses=len(modelrows),loss_null_content=sum(x['null_content'] for x in modelrows),loss_finish_reasons=dict(collections.Counter(x['finish_reason'] for x in modelrows)),loss_errors_or_retry_events=sum(x['error_retry_events'] for x in scopes),loss_reads_verified=len(reads),scopes=scopes,limit='Structural/accounting verification, not an automated semantic score; all100 provider transcripts are not captured.')
(P/'read-content-verification.json').write_text(json.dumps(reads,indent=2)+'\n')
(P/'loss-model-accounting.json').write_text(json.dumps(modelrows,indent=2)+'\n')
(P/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
