"""Structural trace/accounting audit only; manual semantics remain separate."""
import copy,hashlib,json
from decimal import Decimal,InvalidOperation
from pathlib import Path
P=Path(__file__).resolve().parent
JOB='j9c4eb06afb6e42e690ff96d0b75c47bd'
SOURCE={'document':'d6954','revision':1,'sha256':'4237825f66d2215a805d6ddd1823b9bf0e803798ce34b63aeb3b60696673626f','sdk_version':'0.3.7'}
PROVIDER={'only':['deepinfra/bf16'],'quantizations':['bf16'],'allow_fallbacks':False,'require_parameters':True}
KINDS={'rpc_request','rpc_response','llm_request','llm_response','llm_error','llm_retry','agent_error','agent_finished'}
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
def wire(q):
 out={'model':q['args'][0],'messages':q['args'][1],**copy.deepcopy(q['kwargs'])}
 out['max_tokens']=out.pop('max_completion_tokens');out['provider']=copy.deepcopy(PROVIDER);out['stream']=False
 return out
def audit(raw,summary,frozen):
 problems=[]
 def require(condition,code,detail=None):
  if not condition:problems.append({'code':code,'detail':detail})
 events=[]
 for number,line in enumerate(raw.splitlines(),1):
  try:
   e=json.loads(line);assert isinstance(e,dict) and isinstance(e.get('data'),dict) and isinstance(e.get('seq'),int)
   events.append(e)
  except Exception:require(False,'malformed_event',number)
 require(all(e.get('kind') in KINDS for e in events),'unreviewed_event_kind')
 require([e['seq'] for e in events]==sorted({e['seq'] for e in events}),'unordered_or_duplicate_sequence')
 require(summary.get('job_id')==JOB,'job_identity')
 require(summary.get('source')==SOURCE,'source_identity')
 require(summary.get('state') in ['completed','failed','cancelled'],'job_not_terminal')
 trials=summary.get('trials',[]);require(len(trials)==1,'single_carrier_trial_required');trial=trials[0] if trials else {}
 tid=trial.get('trial_id');trace=trial.get('trace',{})
 complete=trace.get('sealed') is True and trace.get('blob')==sha(raw) and trace.get('bytes')==len(raw)
 require(complete,'incomplete_or_mismatching_trace_CAS')
 require(bool(tid) and all(e['data'].get('trial_id')==tid for e in events),'event_trial_identity')
 finished=[e for e in events if e['kind']=='agent_finished'];require(len(finished)==1,'agent_finished_count')
 finish=finished[0]['data'] if len(finished)==1 else {}
 require(finish.get('state')==trial.get('state'),'finished_state_mismatch')
 output=finish.get('output','');require(isinstance(output,str),'stdout_type');output=output if isinstance(output,str) else ''
 require(finish.get('output_bytes')==len(output.encode()),'stdout_byte_accounting')
 require(len(output.encode())<=65536,'stdout_budget')
 logs=[]
 for line in output.splitlines():
  try:
   prefix,value=line.split(' ',1);value=json.loads(value)
   assert prefix in ['RECEIPT_BEGIN','RECEIPT_REQUEST','RECEIPT_RESULT','RECEIPT_STOP','RECEIPT_END'] and isinstance(value,dict)
   logs.append((prefix.removeprefix('RECEIPT_'),value))
  except Exception:require(False,'malformed_stdout_record',line[:100])
 markers={kind:[v for k,v in logs if k==kind] for kind in ['BEGIN','REQUEST','RESULT','STOP','END']}
 plan=frozen['steps'];n=len(plan);require(n==20,'frozen_count')
 require(markers['BEGIN']==[{'calls':n,'plan_sha256':frozen['plan_sha256']}],'begin_marker')
 requests=markers['REQUEST'];results=markers['RESULT'];count=len(requests)
 require(count<=n and requests==plan[:count],'request_marker_order')
 require(len(results)<=count and [r.get('ordinal') for r in results]==list(range(1,len(results)+1)),'result_ordinal_order')
 for r in results:
  status=r.get('status');allowed={'ordinal','status','error_preview'} if status=='error' else {'ordinal','status','response_id_preview','finish_reason_preview'}
  require(status in ['returned','error'] and set(r)==allowed,'result_shape',r.get('ordinal'))
  for key,cap in [('error_preview',32),('response_id_preview',32),('finish_reason_preview',16)]:
   v=r.get(key);require(v is None or isinstance(v,str) and len(v)<=cap,'metadata_cap',[r.get('ordinal'),key])
 expected_logs=[('BEGIN',markers['BEGIN'][0])] if markers['BEGIN'] else []
 for i,r in enumerate(requests):
  expected_logs.append(('REQUEST',r))
  if i<len(results):expected_logs.append(('RESULT',results[i]))
 expected_logs += [('STOP',v) for v in markers['STOP']]+[('END',v) for v in markers['END']]
 require(logs==expected_logs,'stdout_order')
 stop=bool(markers['STOP']);terminal_cancel=summary.get('state')=='cancelled' or trial.get('state')=='cancelled'
 if stop:
  require(count>=1 and markers['STOP']==[{'attempted':count,'responses':count-1,'errors':1,'next_planned_ordinal':count+1}],'stop_counts')
  require(len(results)==count and results[-1].get('status')=='error' and all(r.get('status')=='returned' for r in results[:-1]),'stop_result')
  require(not markers['END'] and trial.get('state') in ['failed','error','cancelled'],'stop_terminal_state')
 elif not terminal_cancel:
  require(markers['END']==[{'attempted':20,'returned':20,'errors':0}],'end_marker')
  require(count==n and len(results)==n and all(r.get('status')=='returned' for r in results),'full_execution')
 else:require(not markers['END'],'cancelled_with_END')
 rpc_req=[e for e in events if e['kind']=='rpc_request'];rpc_resp=[e for e in events if e['kind']=='rpc_response']
 require(all(e['data'].get('method') in ['StartTrial','Answer','EndTrial'] for e in rpc_req+rpc_resp),'unexpected_ECOM_action')
 starts=[e for e in rpc_resp if e['data'].get('method')=='StartTrial'];start_req=[e for e in rpc_req if e['data'].get('method')=='StartTrial']
 require(len(starts)==len(start_req)==1,'StartTrial_count')
 if len(starts)==len(start_req)==1:
  sr=starts[0]['data']['response'];require(sr.get('trialId')==tid and sr.get('runId')==summary.get('run_id'),'StartTrial_identity')
  require(start_req[0]['data'].get('arguments',{}).get('trialId')==tid and start_req[0]['seq']<starts[0]['seq'],'StartTrial_request_identity_order')
 ends=[e for e in rpc_resp if e['data'].get('method')=='EndTrial'];end_req=[e for e in rpc_req if e['data'].get('method')=='EndTrial']
 require(len(ends)==len(end_req)==1,'EndTrial_count')
 if len(ends)==len(end_req)==1:require(end_req[0]['data'].get('arguments',{}).get('trialId')==tid and end_req[0]['seq']<ends[0]['seq'],'EndTrial_identity_order')
 answers=[e for e in rpc_req if e['data'].get('method')=='Answer'];acks=[e for e in rpc_resp if e['data'].get('method')=='Answer']
 if stop or terminal_cancel:require(not answers and not acks,'Answer_after_stop')
 elif trial.get('state')=='answered':
  require(len(answers)==len(acks)==1,'carrier_Answer_ack')
  if len(answers)==len(acks)==1:
   a=answers[0]['data']['arguments'];require(a.get('outcome')=='OUTCOME_NONE_UNSUPPORTED' and not a.get('refs') and 'Carrier task was not attempted' in a.get('message',''),'carrier_Answer_content')
   require(len(finished)==len(end_req)==1 and answers[0]['seq']<acks[0]['seq']<finished[0]['seq']<end_req[0]['seq'],'carrier_lifecycle_order')
 errors=[e for e in events if e['kind']=='agent_error']
 require(all(isinstance(e['data'].get('error'),str) for e in errors),'full_agent_error_missing')
 if trial.get('state')=='answered':require(not errors,'answered_with_agent_error')
 infer=[e for e in events if e['kind'].startswith('llm_')];bycall={}
 for e in infer:
  call=e['data'].get('call');require(isinstance(call,int) and not isinstance(call,bool),'transport_ID',e['seq']);bycall.setdefault(call,[]).append(e)
 groups=[]
 for call,es in bycall.items():
  attempts={e['data'].get('attempt') for e in es};require(len(attempts)==1,'transport_call_attempt_reuse',call)
  attempt=next(iter(attempts)) if len(attempts)==1 else None
  if attempt==1:groups.append([])
  elif not groups:require(False,'orphan_retry_attempt',call);groups.append([])
  groups[-1].append((call,attempt,es))
 require(len(groups)<=n and len(groups)==count,'logical_request_marker_count')
 known=Decimal(0);unknown=[];tokens={'prompt_tokens':0,'completion_tokens':0,'total_tokens':0};tokens_complete=True
 rows=[];physical=0;prior_end=-1
 for i,step in enumerate(plan):
  row={'ordinal':i+1,'fixture':step['fixture'],'arm':step['arm'],'repeat':step['repeat'],'request_sha256':step['request_canonical_sha256'],'state':'missing_or_unknown','transport_call_ids':[],'attempts':[],'full_response_id':None,'response_event':None,'raw_response':None,'raw_error':None,'semantic_review':'pending_manual'};rows.append(row)
  if i>=len(groups):continue
  group=groups[i];expected=frozen['requests'][step['fixture']+'-'+step['arm']]
  require(sha(canon(expected))==step['request_canonical_sha256'],'frozen_request_hash',i+1)
  require([a for c,a,e in group]==list(range(1,len(group)+1)) and len(group)<=5,'attempt_sequence',i+1)
  seqs=[e['seq'] for c,a,es in group for e in es];require(min(seqs)>prior_end,'interleaved_logical_calls',i+1);prior_end=max(seqs)
  final=None;wait=0
  for j,(call,attempt,es) in enumerate(group):
   row['transport_call_ids'].append(call)
   req=[e for e in es if e['kind']=='llm_request'];terminal=[e for e in es if e['kind'] in ['llm_response','llm_error']];retry=[e for e in es if e['kind']=='llm_retry'];physical+=len(req)
   require(len(req)==len(terminal)==1,'attempt_request_terminal_count',[i+1,attempt])
   require(all(e['data'].get('model')==expected['args'][0] for e in es),'event_model',[i+1,attempt])
   good=len(req)==1 and req[0]['data'].get('request')==wire(expected);require(good,'exact_wire_request',[i+1,attempt])
   term=terminal[0] if len(terminal)==1 else None
   if req and term:require(req[0]['seq']<term['seq'],'request_response_order',i+1)
   row['attempts'].append({'attempt':attempt,'transport_call_id':call,'request_events':[e['seq'] for e in req],'terminal_events':[e['seq'] for e in terminal],'retry_events':[e['seq'] for e in retry],'exact_request':good})
   if term:
    d=term['data'];body=d.get('response');usage=body.get('usage') if isinstance(body,dict) else None
    if term['kind']=='llm_response':require('response' in d,'full_response_missing',term['seq'])
    else:require(isinstance(d.get('error'),str),'full_error_missing',term['seq'])
    if isinstance(body,dict) and d.get('status')==200:
     require(body.get('provider')=='DeepInfra','observed_provider',term['seq']);require(body.get('model')==expected['args'][0],'observed_model_alias',term['seq'])
    try:
     cost=Decimal(str(usage['cost']));assert cost.is_finite() and cost>=0;known+=cost
    except (TypeError,KeyError,InvalidOperation,AssertionError):unknown.append({'transport_call_id':call,'event_seq':term['seq']})
    for k in tokens:
     value=usage.get(k) if isinstance(usage,dict) else None
     if isinstance(value,int) and not isinstance(value,bool) and value>=0:tokens[k]+=value
     else:tokens_complete=False
   else:unknown.append({'transport_call_id':call,'event_seq':None});tokens_complete=False
   if j<len(group)-1:
    body=term['data'].get('response') if term else None
    eligible=term is not None and term['kind']=='llm_response' and term['data'].get('status')==429 and isinstance(body,dict) and not any(body.get(k) for k in ['id','choices','usage'])
    require(eligible,'retry_not_eligible',[i+1,attempt])
    require(len(retry)==1 and retry[0]['data'].get('reason')=='http_429' and retry[0]['data'].get('next_attempt')==attempt+1,'retry_marker',[i+1,attempt])
    if len(retry)==1:
     delay=retry[0]['data'].get('delay_seconds');require(isinstance(delay,(int,float)) and 0<=delay<=60,'retry_delay',retry[0]['seq'])
     if isinstance(delay,(int,float)):wait+=delay
     require(term is not None and term['seq']<retry[0]['seq']<min(e['seq'] for e in group[j+1][2]),'retry_order',[i+1,attempt])
   else:require(not retry,'retry_missing_next_attempt',[i+1,attempt]);final=term
  require(wait<=60,'retry_wait_budget',i+1)
  if final:
   d=final['data'];body=d.get('response');row['response_event']=final['seq'];row['raw_response']=body;row['raw_error']=d.get('error');row['status_code']=d.get('status');row['state']='returned' if final['kind']=='llm_response' and d.get('status')==200 else 'inference_error'
   if isinstance(body,dict):row['full_response_id']=body.get('id')
   record=results[i] if i<len(results) else None;require(record is not None,'result_marker_missing',i+1)
   if record and record.get('status')=='returned':
    require(row['state']=='returned','returned_marker_on_error',i+1)
    choices=body.get('choices') if isinstance(body,dict) else None;choice=choices[0] if isinstance(choices,list) and choices and isinstance(choices[0],dict) else {};rid=row['full_response_id'];fr=choice.get('finish_reason')
    require(record.get('response_id_preview')==(rid[:32] if isinstance(rid,str) else None) and record.get('finish_reason_preview')==(fr[:16] if isinstance(fr,str) else None),'bounded_metadata_matches_raw',i+1)
   elif record:require(row['state']=='inference_error','error_marker_on_returned',i+1)
 usage=trial.get('usage',{});declared=usage.get('cost_complete') is True and usage.get('unknown_cost_calls')==0 and usage.get('pending_calls')==0
 require(usage.get('model_calls')==physical,'durable_model_call_count')
 for k in ['model_calls','reported_cost_usd','unknown_cost_calls','pending_calls','cost_complete','prompt_tokens','completion_tokens','total_tokens']:require(summary.get(k)==usage.get(k),'job_trial_usage_agreement',k)
 try:price_match=Decimal(str(usage.get('reported_cost_usd')))==known
 except InvalidOperation:price_match=False
 token_match=tokens_complete and all(usage.get(k)==v for k,v in tokens.items())
 if declared and not unknown:require(price_match and token_match,'complete_accounting_mismatch')
 # Never infer absent calls from absent data alone, or with broken identity/CAS.
 if not problems and complete and (stop or terminal_cancel):
  for r in rows[count:]:r['state']='unattempted_after_verified_stop' if stop else 'unattempted_after_terminal_cancellation'
 return {'status':'reconciled' if not problems else 'incomplete_or_deviating','problems':problems,'planned_calls':n,'logical_calls':len(groups),'physical_attempts':physical,'retry_events':sum(e['kind']=='llm_retry' for e in events),'rows':rows,
  'job_id':summary.get('job_id'),'run_id':summary.get('run_id'),'trial_id':tid,'source':summary.get('source'),'trial_trace_sha256':sha(raw),'trial_trace_bytes':len(raw),'stdout_bytes':len(output.encode()),'stop':stop,'terminal_cancellation':terminal_cancel,
  'accounting':{'reported_cost_usd':usage.get('reported_cost_usd'),'observed_cost_usd':str(known),'summary_declares_complete':declared,'unknown_attempt_costs':unknown,'observed_tokens':tokens,'tokens_match':token_match,'cost_match':price_match,'cost_complete':not problems and declared and not unknown and token_match and price_match},'carrier_grade_ignored':True,'semantic_score':None}
def main():
 raw=(P/'trial-trace.ndjson').read_bytes();summary=json.loads((P/'summary.json').read_text());frozen=json.loads((P/'inputs/diagnostic-runner/frozen.json').read_text())
 result=audit(raw,summary,frozen);(P/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['rows']}))
if __name__=='__main__':main()
