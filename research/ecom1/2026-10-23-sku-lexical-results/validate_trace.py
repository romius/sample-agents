"""Offline evidence reconciliation, never semantic scoring or inference.

Input event schema is the archived SDK 0.3.7 trial NDJSON. Unknown schemas fail
closed. A supplied summary must describe exactly one trial, never an aggregate.
"""
import argparse
import copy
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIAGNOSTIC = HERE.parent / '2026-10-22-sku-lexical-paired-diagnostic'
PROVIDER = dict(only=['deepinfra/bf16'], quantizations=['bf16'], allow_fallbacks=False, require_parameters=True)
EXPECTED_SOURCE = dict(document='d6280', revision=1, sha256='dc5e1951f404dca549fe97a6fd38de36419ece9ecd0c3aa07d4f6369998bda3e', sdk_version='0.3.7')
EXPECTED_JOB = 'j8359aedb3a54484e876f62f0bba9221a'
PINS = {'fixtures.json': 'c2dd7b4f5917d6118351becaa7d9aeee7cd2c7d510cb1c5eb5076bb202b57571', 'call-plan.json': '89550772dc28c05a1f73d06d5c09d325e7c78de5fb7e89fd5d2c7c1490ff97a5'}


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
def read_json(path): return json.loads(path.read_text())


def wire_request(request):
    """Only SDK 0.3.7 completion-token alias; no fuzzy prompt normalization."""
    value = copy.deepcopy(request)
    if 'max_completion_tokens' in value:
        assert 'max_tokens' not in value
        value['max_tokens'] = value.pop('max_completion_tokens')
    value['provider'] = copy.deepcopy(PROVIDER)
    value['stream'] = False
    return value


def validate(raw, summary, bundle, expected_source, *, legacy=False, expected_job=None):
    problems = []
    def issue(code, detail=None, ordinal=None):
        problems.append(dict(code=code, ordinal=ordinal, detail=detail))
    events = []
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            event = json.loads(line)
            if not isinstance(event, dict) or not isinstance(event.get('data'), dict) or not isinstance(event.get('seq'), int) or not isinstance(event.get('kind'),str):
                raise ValueError('event envelope')
            events.append(event)
        except (ValueError, TypeError) as exc:
            issue('malformed_trace_line', dict(line=number, error=str(exc)))
    seqs = [e['seq'] for e in events]
    if seqs != sorted(set(seqs)): issue('duplicate_or_unordered_sequence')
    if summary.get('source') != expected_source: issue('source_identity_mismatch')
    if summary.get('state') not in ('completed','failed','cancelled','canceled'): issue('job_not_terminal')
    if expected_job and summary.get('job_id') != expected_job: issue('job_identity_missing_or_mismatch')
    trials = summary.get('trials', [])
    if len(trials) != 1:
        issue('single_trial_summary_required')
    trial = trials[0] if trials else {}
    trial_id = trial.get('trial_id')
    sealed = trial.get('trace', {})
    if sealed.get('blob') != sha(raw): issue('trace_hash_mismatch')
    if sealed.get('bytes') != len(raw): issue('trace_size_mismatch')
    if sealed.get('sealed') is not True: issue('trace_unsealed')
    if not trial_id: issue('trial_identity_missing')
    if trial.get('state') not in ('answered','failed','error','cancelled','canceled'): issue('trial_not_terminal')
    for event in events:
        if event['data'].get('trial_id') != trial_id:
            issue('event_trial_mismatch', event['seq'])
    finished = [e for e in events if e['kind'] == 'agent_finished']
    if len(finished) != 1: issue('missing_or_duplicate_agent_finished')
    output = finished[0]['data'].get('output', '') if finished else ''
    if not isinstance(output, str): output = ''; issue('invalid_stdout')
    markers = {'BEGIN': [], 'REQUEST': [], 'RESULT': [], 'END': []}
    order = []
    for line in output.splitlines():
        if not line.startswith('SKU_DIAGNOSTIC_'): continue
        try:
            prefix, text = line.split(' ', 1)
            kind = prefix.removeprefix('SKU_DIAGNOSTIC_')
            value = json.loads(text)
            if kind not in markers or not isinstance(value, dict): raise ValueError('marker shape')
            markers[kind].append(value); order.append((kind, value))
        except (ValueError, TypeError) as exc: issue('malformed_stdout_marker', str(exc))
    plan = bundle['plan']; n = len(plan)
    if len(markers['BEGIN']) != 1 or markers['BEGIN'][0].get('calls') != n: issue('begin_marker_mismatch')
    if not legacy and len(output.encode()) > 65536: issue('stdout_limit_exceeded')
    requested = markers['REQUEST']; records = markers['RESULT']
    expected_requests = plan[:len(requested)] if legacy else [{'ordinal': p['ordinal']} for p in plan[:len(requested)]]
    if requested != expected_requests: issue('request_marker_order_or_count_mismatch')
    if len(requested) > n or len(records) > n: issue('too_many_logical_calls')
    records_by_ord = {}
    for i, record in enumerate(records):
        if i >= n or record.get('step') != plan[i]: issue('result_step_mismatch', ordinal=i+1)
        ordinal = i+1 if legacy else record.get('step', {}).get('ordinal')
        if ordinal in records_by_ord: issue('duplicate_result_ordinal', ordinal=ordinal)
        records_by_ord[ordinal] = record
        if not legacy:
            for key, cap in [('response_id',32), ('finish_reason',16), ('error_preview',32)]:
                value = record.get(key)
                if value is not None and (not isinstance(value,str) or len(value)>cap): issue('metadata_cap_or_type_mismatch', key, ordinal)
            if 'response' in record or 'error' in record: issue('unbounded_stdout_payload', ordinal=ordinal)
            allowed={'step','status','response_id','finish_reason'}
            if record.get('status') in ('error','cancelled'): allowed.add('error_preview')
            if set(record)!=allowed: issue('unexpected_metadata_fields',ordinal=ordinal)
    # The runner is sequential: REQUEST must precede its RESULT, then the next
    # REQUEST. A final in-flight request may have no result after host cancellation.
    expected_order = [('BEGIN', markers['BEGIN'][0])] if markers['BEGIN'] else []
    for i, marker in enumerate(requested):
        expected_order.append(('REQUEST', marker))
        if i < len(records): expected_order.append(('RESULT', records[i]))
    expected_order.extend(('END', marker) for marker in markers['END'])
    if order != expected_order or len(records) > len(requested): issue('stdout_event_order_mismatch')
    groups = {}
    inference = [e for e in events if e['kind'].startswith('llm_')]
    for event in inference:
        data = event['data']; call = data.get('call')
        if event['kind'] not in ('llm_request','llm_response','llm_error','llm_retry'):
            issue('unsupported_inference_event', event['kind'])
        if not isinstance(call, int) or isinstance(call, bool): issue('missing_call_identity', event['seq']); continue
        groups.setdefault(call, []).append(event)
    # Full call identities, not truncated response IDs, identify logical calls.
    # Order is a candidate mapping only: every request is checked against its
    # planned ordinal. Missing entire calls invalidate reconciliation globally.
    if len(groups) != len(requested): issue('logical_call_marker_count_mismatch', [len(groups),len(requested)])
    calls = list(groups)
    for left,right in zip(calls,calls[1:]):
        if max(e['seq'] for e in groups[left]) >= min(e['seq'] for e in groups[right]): issue('logical_calls_interleaved')
    if len(calls) > n: issue('extra_inference_calls')
    rows = []; attempt_count = 0; known_cost = Decimal(0); unknown_cost = []
    tokens = dict(prompt_tokens=0, completion_tokens=0); tokens_complete = True
    cancel_ordinals = [r.get('step',{}).get('ordinal') for r in records if r.get('status')=='cancelled']
    terminal_cancel = (summary.get('state') in ('cancelled','canceled') or trial.get('state') in ('cancelled','canceled'))
    valid_cancel_marker = bool(len(cancel_ordinals)==1 and requested and cancel_ordinals[0]==len(requested) and records and records[-1].get('step')==plan[len(requested)-1]) if len(requested)<=n else False
    cancelled = valid_cancel_marker or terminal_cancel
    infer_unattempted = (cancelled and len(finished)==1 and len(markers['BEGIN'])==1
                         and markers['BEGIN'][0].get('calls')==n and requested==expected_requests
                         and order==expected_order and len(groups)<=len(requested)
                         and sealed.get('blob')==sha(raw) and sealed.get('bytes')==len(raw)
                         and sealed.get('sealed') is True
                         and not any(p['code'] in ('malformed_stdout_marker','malformed_trace_line','result_step_mismatch') for p in problems))
    if cancel_ordinals and (len(cancel_ordinals)!=1 or cancel_ordinals[0]!=len(requested)): issue('calls_after_cancellation')
    for index, step in enumerate(plan):
        ordinal = step.get('ordinal', index+1); call = calls[index] if index < len(calls) else None
        record = records_by_ord.get(ordinal); own = groups.get(call, [])
        row = dict(step=step, logical_call=call, state='missing_evidence', request_verified=False, attempts=[], raw_final_event=None, stdout_metadata=record, semantic_review='pending_manual_review')
        rows.append(row)
        if not own:
            if index >= len(requested) and infer_unattempted: row['state']='unattempted_after_cancellation'
            elif index >= len(requested): row['state']='missing_or_unattempted_unknown'; issue('unattempted_without_cancellation', ordinal=ordinal)
            else: issue('attempted_call_events_missing', ordinal=ordinal)
            continue
        expected = bundle['fixtures'][step['case_index']]['arms'][step['arm']]
        if sha(canonical(expected)) != step['request_sha256']: issue('frozen_plan_hash_mismatch', ordinal=ordinal)
        attempts = {}
        for event in own:
            data=event['data']; attempt=data.get('attempt')
            if not isinstance(attempt,int) or isinstance(attempt,bool): issue('missing_attempt_identity',event['seq'],ordinal); continue
            attempts.setdefault(attempt,[]).append(event)
            if data.get('model')!=expected['model']: issue('event_model_mismatch',event['seq'],ordinal)
        if list(attempts)!=list(range(1,len(attempts)+1)) or len(attempts)>5: issue('attempt_sequence_mismatch',ordinal=ordinal)
        all_requests = True; final = None
        for attempt, ae in attempts.items():
            reqs=[e for e in ae if e['kind']=='llm_request']; replies=[e for e in ae if e['kind'] in ('llm_response','llm_error')]; retries=[e for e in ae if e['kind']=='llm_retry']
            attempt_count += len(reqs)
            if len(reqs)!=1: issue('request_event_missing_or_duplicate',attempt,ordinal); all_requests=False
            if len(replies)!=1: issue('terminal_attempt_event_missing_or_duplicate',attempt,ordinal)
            request_ok = len(reqs)==1 and reqs[0]['data'].get('request')==wire_request(expected)
            if not request_ok: issue('wire_request_mismatch',attempt,ordinal); all_requests=False
            response = replies[0] if len(replies)==1 else None
            if reqs and response and reqs[0]['seq']>=response['seq']: issue('response_before_request',attempt,ordinal)
            row['attempts'].append(dict(attempt=attempt, request_event_seq=[e['seq'] for e in reqs], terminal_event_seq=[e['seq'] for e in replies], retry_event_seq=[e['seq'] for e in retries], request_verified=request_ok, events_sha256=[sha(canonical(e)) for e in ae]))
            if response:
                data=response['data']; body=data.get('response')
                if response['kind']=='llm_response' and 'response' not in data: issue('full_response_body_missing',attempt,ordinal)
                usage=body.get('usage') if isinstance(body,dict) else None
                try:
                    price=Decimal(str(usage['cost']))
                    if not price.is_finite() or price<0: raise ValueError('cost')
                    known_cost+=price
                except (KeyError,TypeError,ValueError,InvalidOperation): unknown_cost.append(dict(call=call,attempt=attempt,event_seq=response['seq']))
                for key in tokens:
                    value=usage.get(key) if isinstance(usage,dict) else None
                    if isinstance(value,int) and not isinstance(value,bool) and value>=0: tokens[key]+=value
                    else: tokens_complete=False
            else: unknown_cost.append(dict(call=call,attempt=attempt,event_seq=None)); tokens_complete=False
            if attempt<len(attempts):
                eligible = bool(response and response['kind']=='llm_response' and response['data'].get('status')==429)
                body=response['data'].get('response') if response else None
                eligible = eligible and isinstance(body,dict) and not any(body.get(k) for k in ('id','choices','usage'))
                valid_retry = len(retries)==1 and retries[0]['data'].get('reason')=='http_429' and retries[0]['data'].get('next_attempt')==attempt+1
                if not eligible or not valid_retry: issue('unsupported_or_missing_retry',attempt,ordinal)
                if retries and response and retries[0]['seq']<=response['seq']: issue('retry_before_response',attempt,ordinal)
                if retries:
                    delay=retries[0]['data'].get('delay_seconds')
                    if not isinstance(delay,(int,float)) or not 0<=delay<=60: issue('retry_delay_invalid',attempt,ordinal)
                    next_reqs=[e for e in attempts.get(attempt+1,[]) if e['kind']=='llm_request']
                    if next_reqs and next_reqs[0]['seq']<=retries[0]['seq']: issue('next_attempt_before_retry',attempt,ordinal)
            else:
                if retries: issue('retry_without_followup_attempt',attempt,ordinal)
                final=response
        waits=[e['data'].get('delay_seconds',0) for e in own if e['kind']=='llm_retry']
        if all(isinstance(x,(int,float)) for x in waits) and sum(waits)>60: issue('retry_wait_budget_exceeded',ordinal=ordinal)
        row['request_verified']=all_requests and bool(attempts)
        if final:
            row['raw_final_event']=final
            row['raw_final_event_sha256']=sha(canonical(final))
            success=final['kind']=='llm_response' and final['data'].get('status')==200
            row['state']='response' if success else 'provider_error'
            body=final['data'].get('response')
            choices=body.get('choices') if isinstance(body,dict) else None
            choice=choices[0] if isinstance(choices,list) and choices and isinstance(choices[0],dict) else {}
            row['finish_reason']=choice.get('finish_reason')
            row['length_truncated']=choice.get('finish_reason')=='length'
            row['raw_content']=choice.get('message',{}).get('content') if isinstance(choice.get('message'),dict) else None
            if record is None: issue('result_metadata_missing',ordinal=ordinal)
            elif legacy:
                if record.get('response')!=body: issue('legacy_raw_response_mismatch',ordinal=ordinal)
            elif record.get('status')=='response':
                if not success: issue('response_metadata_vs_error_event',ordinal=ordinal)
                rid=body.get('id') if isinstance(body,dict) else None; finish=choice.get('finish_reason')
                if record.get('response_id')!=(rid[:32] if isinstance(rid,str) else None) or record.get('finish_reason')!=(finish[:16] if isinstance(finish,str) else None): issue('response_metadata_mismatch',ordinal=ordinal)
            elif record.get('status') in ('error','cancelled'):
                row['state']=record['status']
                if success: issue('error_metadata_with_success_event',ordinal=ordinal)
                if final['kind']=='llm_error' and not isinstance(final['data'].get('error'),str): issue('full_error_context_missing',ordinal=ordinal)
                # The SDK wraps provider errors before Python catches them. Preserve
                # both exact strings; never manufacture full errors from previews.
            else: issue('unknown_result_status',ordinal=ordinal)
        elif record: issue('raw_final_event_missing',ordinal=ordinal)
    if not cancelled:
        if len(markers['END'])!=1: issue('end_marker_missing_or_duplicate')
        elif not legacy:
            expected_end=dict(attempted=n,responses=sum(r.get('status')=='response' for r in records),errors=sum(r.get('status')=='error' for r in records))
            if markers['END'][0]!=expected_end: issue('end_count_mismatch')
        if len(requested)!=n or len(records)!=n: issue('incomplete_planned_execution')
    elif markers['END']: issue('end_marker_after_cancellation')
    starts=[e for e in events if e['kind']=='rpc_response' and e['data'].get('method')=='StartTrial']
    run_id=starts[0]['data'].get('response',{}).get('runId') if len(starts)==1 else None
    if not run_id: issue('run_identity_missing')
    if len(starts)==1 and starts[0]['data'].get('response',{}).get('trialId')!=trial_id: issue('start_response_trial_mismatch')
    methods=[e['data'].get('method') for e in events if e['kind']=='rpc_request']
    if any(m not in ('StartTrial','Answer','EndTrial') for m in methods): issue('unexpected_ecom_action')
    if not cancelled and methods!=['StartTrial','Answer','EndTrial']: issue('carrier_lifecycle_mismatch')
    if cancelled and 'Answer' in methods: issue('carrier_answer_after_cancel')
    accounting=trial.get('usage',{})
    cost_declared=accounting.get('cost_complete') is True and accounting.get('unknown_cost_calls')==0 and accounting.get('pending_calls')==0
    try: cost_matches=Decimal(str(accounting['reported_cost_usd']))==known_cost
    except (KeyError,InvalidOperation): cost_matches=False
    token_matches=tokens_complete and all(accounting.get(k)==v for k,v in tokens.items())
    aggregate_matches=all(summary.get(k,accounting.get(k))==accounting.get(k) for k in ('reported_cost_usd','cost_complete','unknown_cost_calls','pending_calls','prompt_tokens','completion_tokens'))
    costs_complete=cost_declared and cost_matches and not unknown_cost and token_matches and aggregate_matches
    # A 429 without usage has no observed per-attempt cost. Do not silently price
    # it at zero even if the job-level summary declares accounting settled.
    return dict(status='reconciled' if not problems else 'incomplete_or_deviating', semantic_score=None,
                planned_calls=n, observed_logical_calls=len(groups), provider_attempts=attempt_count,
                retry_events=sum(e['kind']=='llm_retry' for e in inference), cancelled=cancelled,
                source=summary.get('source'), job_id=summary.get('job_id'), trial_id=trial_id,
                run_id=run_id, trace_sha256=sha(raw), trace_bytes=len(raw), stdout_bytes=len(output.encode()),
                problems=problems, rows=rows, carrier_grade_ignored=True,
                billing=dict(summary_declares_complete=cost_declared, full_attempt_cost_evidence=not unknown_cost,
                             observed_cost_usd=str(known_cost), unknown_attempt_costs=unknown_cost,
                             summary_cost_matches_observed=cost_matches, single_trial_and_job_accounting_agree=aggregate_matches, tokens=tokens, tokens_match=token_matches,
                             cost_complete=costs_complete),
                limitations=['No semantic pass/fail scorer. Malformed and length-truncated content remains raw manual-review evidence.',
                             'Call-to-ordinal mapping uses sequential full call identities plus exact requests and stdout order; any gap invalidates reconciliation.',
                             'No live trace retention or future output is established by synthetic tests.',
                             'SDK error wrapper text is not reconstructed from an error preview.',
                             'Zero price is never inferred for missing per-attempt usage, including 429 rejection.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace',type=Path,required=True)
    parser.add_argument('--summary',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    for file,digest in PINS.items():
        assert sha((DIAGNOSTIC/file).read_bytes())==digest, file
    bundle=read_json(DIAGNOSTIC/'fixtures.json')
    assert len(bundle['plan'])==68 and bundle['plan']==read_json(DIAGNOSTIC/'call-plan.json')
    report=validate(args.trace.read_bytes(),read_json(args.summary),bundle,EXPECTED_SOURCE,expected_job=EXPECTED_JOB)
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:report[k] for k in ('status','planned_calls','observed_logical_calls','provider_attempts','retry_events','cancelled')}))
    print('Full evidence and deviations written; semantic review remains manual.')


if __name__=='__main__': main()
