"""Offline structural controls derived from the real complete trace.
Synthetic errors/retries do not assert that this diagnostic experienced them.
No response semantics are scored.
"""
import copy,json
from decimal import Decimal
from pathlib import Path
import validate as v
P=Path(__file__).resolve().parent
RAW=(P/'trial-trace.ndjson').read_bytes();EVENTS=[json.loads(x) for x in RAW.splitlines()]
SUMMARY=json.loads((P/'summary.json').read_text());FROZEN=json.loads((P/'inputs/diagnostic-runner/frozen.json').read_text())
def encoded(es):return b''.join((json.dumps(e,ensure_ascii=False,separators=(',',':'))+'\n').encode() for e in es)
def run(es,s,reseal=True):
 raw=encoded(es)
 if reseal:s['trials'][0]['trace'].update(blob=v.sha(raw),bytes=len(raw),sealed=True)
 return v.audit(raw,s,FROZEN)
def cases():
 result=v.audit(RAW,SUMMARY,FROZEN);assert result['status']=='reconciled' and result['accounting']['cost_complete'];yield {'case':'real_complete_trace','status':'reconciled','logical':20,'physical':20}
 edits=[
 ('unknown_event',lambda es,s:es[0].update(kind='unreviewed_event'),'unreviewed_event_kind'),
 ('wrong_StartTrial_argument',lambda es,s:es[0]['data']['arguments'].update(trialId='wrong'),'StartTrial_request_identity_order'),
 ('wrong_finished_state',lambda es,s:next(e for e in es if e['kind']=='agent_finished')['data'].update(state='failed'),'finished_state_mismatch'),
 ('wrong_model_call_count',lambda es,s:s['trials'][0]['usage'].update(model_calls=99),'durable_model_call_count'),
 ('missing_agent_finished',lambda es,s:es.__setitem__(slice(None),[e for e in es if e['kind']!='agent_finished']),'agent_finished_count'),
 ('missing_EndTrial_request',lambda es,s:es.__setitem__(slice(None),[e for e in es if not(e['kind']=='rpc_request' and e['data'].get('method')=='EndTrial')]),'EndTrial_count'),
 ('missing_response',lambda es,s:es.__setitem__(slice(None),[e for e in es if e['seq']!=7]),'attempt_request_terminal_count'),
 ('missing_raw_response',lambda es,s:next(e for e in es if e['seq']==7)['data'].pop('response'),'full_response_missing'),
 ('wrong_requested_route',lambda es,s:next(e for e in es if e['seq']==6)['data']['request']['provider'].update(only=['another/provider']),'exact_wire_request'),
 ('wrong_observed_provider',lambda es,s:next(e for e in es if e['seq']==7)['data']['response'].update(provider='Other'),'observed_provider'),
 ('wrong_source',lambda es,s:s['source'].update(revision=2),'source_identity'),
 ('wrong_stdout_byte_count',lambda es,s:next(e for e in es if e['kind']=='agent_finished')['data'].update(output_bytes=0),'stdout_byte_accounting'),
 ]
 for name,edit,want in edits:
  es,s=copy.deepcopy(EVENTS),copy.deepcopy(SUMMARY);edit(es,s);r=run(es,s);codes=[p['code'] for p in r['problems']];assert want in codes and not r['accounting']['cost_complete'];yield dict(case=name,expected=want,issues=codes)
 truncated=v.audit(RAW[:10000],SUMMARY,FROZEN);assert truncated['status']!='reconciled' and not truncated['accounting']['cost_complete'];assert not any(r['state'].startswith('unattempted') for r in truncated['rows']);yield dict(case='truncated_raw_trace',issues=[p['code'] for p in truncated['problems']],unattempted_claims=0)
 # Remove suffix and its markers without any stop/cancellation: absence remains unknown.
 es=copy.deepcopy(EVENTS);s=copy.deepcopy(SUMMARY)
 es=[e for e in es if not e['kind'].startswith('llm_') or e['data']['call']<=3]
 f=next(e for e in es if e['kind']=='agent_finished')['data'];f['output']='\n'.join(f['output'].splitlines()[:7])+'\n';f['output_bytes']=len(f['output'].encode())
 r=run(es,s);assert len([q for q in r['rows'] if q['state']=='missing_or_unknown'])==17 and not r['accounting']['cost_complete'];yield dict(case='missing_suffix_without_stop',unknown=17,unattempted=0)
 # A genuine-style SDK429 chain uses different transport IDs, never same-call grouping.
 es=copy.deepcopy(EVENTS);s=copy.deepcopy(SUMMARY);firstreq=copy.deepcopy(es[2]);firstresp=copy.deepcopy(es[3]);tid=s['trials'][0]['trial_id']
 for e in es:
  if e['seq']>=7:e['seq']+=3
  if e['kind'].startswith('llm_') and e['data']['call']>=2:e['data']['call']+=1
 es[3]['data'].update(call=2,attempt=2)
 retryresp=copy.deepcopy(firstresp);retryresp['data'].update(status=429,response={'error':{'message':'rate limited'}})
 retry={'seq':8,'time':firstresp['time'],'kind':'llm_retry','data':{'trial_id':tid,'call':1,'attempt':1,'model':firstreq['data']['model'],'reason':'http_429','next_attempt':2,'delay_seconds':1}}
 nextreq=copy.deepcopy(firstreq);nextreq['seq']=9;nextreq['data'].update(call=2,attempt=2)
 es=es[:3]+[retryresp,retry,nextreq]+es[3:]
 for u in [s,s['trials'][0]['usage']]:u.update(model_calls=21,unknown_cost_calls=1,cost_complete=False)
 r=run(es,s);assert r['status']=='reconciled' and r['logical_calls']==20 and r['physical_attempts']==21 and r['rows'][0]['transport_call_ids']==[1,2] and not r['accounting']['cost_complete'];yield dict(case='distinct_transport_429_retry',logical=20,physical=21,unknown_attempt_costs=r['accounting']['unknown_attempt_costs'])
 for name,edit,want in [
  ('missing_retry_link',lambda z:z.__setitem__(slice(None),[e for e in z if e['kind']!='llm_retry']),'retry_marker'),
  ('wrong_retry_next_attempt',lambda z:next(e for e in z if e['kind']=='llm_retry')['data'].update(next_attempt=4),'retry_marker'),
  ('retry_request_drift',lambda z:next(e for e in z if e['seq']==9)['data']['request'].update(temperature=0.7),'exact_wire_request'),
  ('same_prompt_new_call_not_retry',lambda z:next(e for e in z if e['seq']==9)['data'].update(attempt=1),'transport_call_attempt_reuse')]:
  z=copy.deepcopy(es);edit(z);r=run(z,copy.deepcopy(s));codes=[p['code'] for p in r['problems']];assert want in codes and r['status']!='reconciled';yield dict(case=name,issues=codes)
 # Explicit stop/rethrow synthetic fixture: 3 returns, then one terminal inference error.
 es=copy.deepcopy(EVENTS[:10]);s=copy.deepcopy(SUMMARY);es[-1]['kind']='llm_error';es[-1]['data'].pop('response');es[-1]['data'].pop('status');es[-1]['data']['error']='Synthetic terminal ValueError'
 f=copy.deepcopy(next(e for e in EVENTS if e['kind']=='agent_finished'));f['seq']=15;f['data']['state']='failed'
 lines=f['data']['output'].splitlines()[:8]+['RECEIPT_RESULT '+json.dumps({'ordinal':4,'status':'error','error_preview':'Synthetic terminal ValueError'}),'RECEIPT_STOP '+json.dumps({'attempted':4,'responses':3,'errors':1,'next_planned_ordinal':5})]
 f['data']['output']='\n'.join(lines)+'\n';f['data']['output_bytes']=len(f['data']['output'].encode())
 es += [{'seq':14,'time':f['time'],'kind':'agent_error','data':{'trial_id':tid,'error':'Synthetic terminal ValueError'}},f]
 for e in EVENTS[-2:]:
  e=copy.deepcopy(e);e['seq']-=33;es.append(e)
 s['trials'][0]['state']='failed';usage=[e['data']['response']['usage'] for e in es if e['kind']=='llm_response']
 for u in [s,s['trials'][0]['usage']]:
  u.update(model_calls=4,reported_cost_usd=str(sum((Decimal(str(x['cost'])) for x in usage),Decimal(0))),unknown_cost_calls=1,cost_complete=False)
  for k in ['prompt_tokens','completion_tokens','total_tokens']:u[k]=sum(x[k] for x in usage)
 r=run(es,s);assert r['status']=='reconciled',r['problems'];assert len([q for q in r['rows'] if q['state']=='unattempted_after_verified_stop'])==16 and not r['accounting']['cost_complete'];yield dict(case='explicit_stop_after_fourth_error',logical=4,unattempted=16,cost_complete=False)
 for name,edit in [('stop_wrong_source',lambda s:s['source'].update(revision=99)),('stop_wrong_trial',lambda s:s['trials'][0].update(trial_id='wrong'))]:
  z=copy.deepcopy(s);edit(z);r=run(copy.deepcopy(es),z);assert r['status']!='reconciled' and all(not q['state'].startswith('unattempted') for q in r['rows']);yield dict(case=name,unattempted=0,issues=[p['code'] for p in r['problems']])
out={'scope':'Structural controls only; all modified traces explicitly synthetic and resealed locally, no model calls.','cases':list(cases())}
(P/'validation-tests.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(out['cases']),'structural controls; no semantic scorer.')
