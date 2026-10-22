"""Offline archived-schema regression and explicitly synthetic counterexamples."""
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import validate_trace as v

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'2026-10-22-sku-paired-diagnostic'
RESULTS=OLD/'results'
NEW=v.DIAGNOSTIC

def load(path): return json.loads(path.read_text())
def encode(events): return ('\n'.join(json.dumps(e,separators=(',',':')) for e in events)+'\n').encode()
old_raw=(RESULTS/'trial-trace.ndjson').read_bytes()
old_events=[json.loads(line) for line in old_raw.splitlines()]
old_summary=load(RESULTS/'summary.json')
bundle=load(NEW/'fixtures.json')
retry_schema=load(HERE.parent/'2026-10-22-provider-control-review/new-failure-t045.json')['events']
retry_template=next(e for e in retry_schema if e['kind']=='llm_retry')
rejection_template=next(e for e in retry_schema if e['kind']=='llm_response' and e['data']['status']==429)
error_template=next(e for e in retry_schema if e['kind']=='llm_error')
body_template=next(e for e in old_events if e['kind']=='llm_response')['data']['response']


def seal(events, summary):
    for i,e in enumerate(events,1):e['seq']=i
    raw=encode(events);summary['trials'][0]['trace']=dict(blob=v.sha(raw),bytes=len(raw),sealed=True)
    return raw,summary


def synthetic():
    """Test data only; each response is copied from archived16, never live68."""
    trial='SYNTHETIC_TEST_ONLY';events=[];lines=[]
    def emit(kind,data):events.append(dict(seq=0,time='SYNTHETIC_TEST_ONLY',kind=kind,data=dict(trial_id=trial,**data)))
    emit('rpc_request',dict(method='StartTrial',arguments={'trialId':trial}))
    emit('rpc_response',dict(method='StartTrial',response=dict(trialId=trial,runId='SYNTHETIC_RUN_ONLY')))
    lines.append('SKU_DIAGNOSTIC_BEGIN '+json.dumps(dict(calls=68,purpose='paired next-action diagnostic, not task score')))
    for step in bundle['plan']:
        i=step['ordinal'];expected=bundle['fixtures'][step['case_index']]['arms'][step['arm']]
        lines.append('SKU_DIAGNOSTIC_REQUEST '+json.dumps(dict(ordinal=i)))
        emit('llm_request',dict(call=i,attempt=1,model=expected['model'],request=v.wire_request(expected)))
        body=copy.deepcopy(body_template);body['id']='SYNTHETIC_'+str(i)
        emit('llm_response',dict(call=i,attempt=1,model=expected['model'],status=200,response=body))
        lines.append('SKU_DIAGNOSTIC_RESULT '+json.dumps(dict(step=step,status='response',response_id=body['id'][:32],finish_reason=body['choices'][0]['finish_reason'][:16])))
    lines.append('SKU_DIAGNOSTIC_END '+json.dumps(dict(attempted=68,responses=68,errors=0)))
    emit('rpc_request',dict(method='Answer',arguments={}))
    emit('agent_finished',dict(state='answered',output='\n'.join(lines)+'\n'))
    emit('rpc_request',dict(method='EndTrial',arguments={}))
    usage=dict(cost_complete=True,unknown_cost_calls=0,pending_calls=0,reported_cost_usd=str(Decimal(str(body_template['usage']['cost']))*68),prompt_tokens=body_template['usage']['prompt_tokens']*68,completion_tokens=body_template['usage']['completion_tokens']*68)
    summary=dict(source=v.EXPECTED_SOURCE,job_id=v.EXPECTED_JOB,state='completed',trials=[dict(trial_id=trial,state='answered',usage=usage)])
    return events,summary


def finished(events):return next(e for e in events if e['kind']=='agent_finished')['data']
def metadata(events,ordinal,change):
    lines=finished(events)['output'].splitlines()
    for i,line in enumerate(lines):
        if line.startswith('SKU_DIAGNOSTIC_RESULT '):
            obj=json.loads(line.split(' ',1)[1])
            if obj['step']['ordinal']==ordinal:
                change(obj);lines[i]='SKU_DIAGNOSTIC_RESULT '+json.dumps(obj)
    finished(events)['output']='\n'.join(lines)+'\n'

def audit(events,summary):
    raw,summary=seal(events,summary)
    return v.validate(raw,summary,bundle,v.EXPECTED_SOURCE,expected_job=v.EXPECTED_JOB)


def main():
    for relative,digest in load(HERE/'DEPENDENCIES.json').items():
        assert v.sha((HERE.parent/relative).read_bytes())==digest,relative
    evidence=load(HERE/'normalization-evidence.json')
    assert evidence['sdk']=='0.3.7' and evidence['source_parameter']=='max_completion_tokens'
    assert 'max_completion_tokens=1024' in (HERE.parent/evidence['source']).read_text()
    assert v.sha((HERE.parent/evidence['source']).read_bytes())==evidence['source_sha256']
    tests=[]
    def record(name,report,expected_code=None):
        codes=[p['code'] for p in report['problems']]
        if expected_code: assert expected_code in codes,(name,codes)
        else: assert not codes,(name,codes)
        assert len(report['rows'])==report['planned_calls'] and report['semantic_score'] is None
        tests.append(dict(name=name,passed=True,scope='offline test; not real68 results',status=report['status'],problem_codes=sorted(set(codes)),cost_complete=report['billing']['cost_complete']))
    # Original verifier executed untouched against copied immutable files.
    with tempfile.TemporaryDirectory(prefix='sku-original-verifier-') as temporary:
        root=Path(temporary);results=root/'results';results.mkdir()
        for name in ('agent.py','fixtures.json'):shutil.copyfile(OLD/name,root/name)
        for name in ('verify_capture.py','trial-trace.ndjson','summary.json'):shutil.copyfile(RESULTS/name,results/name)
        run=subprocess.run([sys.executable,str(results/'verify_capture.py')],capture_output=True,text=True,timeout=30)
        assert run.returncode==0,run.stderr
        original=load(results/'capture-verification.json');assert original['calls']==16 and original['cost_complete']
    report=v.validate(old_raw,old_summary,load(OLD/'fixtures.json'),old_summary['source'],legacy=True)
    record('actual_archived16_schema_and_cost',report);assert report['billing']['cost_complete']
    events,summary=synthetic();report=audit(events,summary);record('synthetic68_complete_metadata_only',report);assert report['billing']['cost_complete']
    mutations={
        'wrong_prompt': ('wire_request_mismatch',lambda es,s:next(e for e in es if e['kind']=='llm_request')['data']['request']['messages'][0].update(content='changed')),
        'wrong_completion_limit':('wire_request_mismatch',lambda es,s:next(e for e in es if e['kind']=='llm_request')['data']['request'].update(max_tokens=2047)),
        'provider_fallback':('wire_request_mismatch',lambda es,s:next(e for e in es if e['kind']=='llm_request')['data']['request']['provider'].update(allow_fallbacks=True)),
        'wrong_source':('source_identity_mismatch',lambda es,s:s.update(source={})),
        'wrong_job':('job_identity_missing_or_mismatch',lambda es,s:s.update(job_id='another-job')),
        'wrong_trial':('event_trial_mismatch',lambda es,s:es[2]['data'].update(trial_id='other')),
        'missing_response':('terminal_attempt_event_missing_or_duplicate',lambda es,s:es.remove(next(e for e in es if e['kind']=='llm_response' and e['data']['call']==3))),
        'missing_request':('request_event_missing_or_duplicate',lambda es,s:es.remove(next(e for e in es if e['kind']=='llm_request' and e['data']['call']==3))),
        'wrong_metadata_id':('response_metadata_mismatch',lambda es,s:metadata(es,3,lambda m:m.update(response_id='incorrect'))),
        'missing_all_stdout':('begin_marker_mismatch',lambda es,s:finished(es).update(output='')),
        'stdout_truncated_json':('malformed_stdout_marker',lambda es,s:finished(es).update(output=finished(es)['output'][:-25])),
        'unexpected_world_action':('unexpected_ecom_action',lambda es,s:es.append(dict(seq=0,kind='rpc_request',data=dict(trial_id='SYNTHETIC_TEST_ONLY',method='Write')))),
        'not_terminal':('job_not_terminal',lambda es,s:s.update(state='running')),
    }
    for name,(code,mutate) in mutations.items():
        events,summary=synthetic();mutate(events,summary);record(name,audit(events,summary),code)
    events,summary=synthetic();events[:]=[e for e in events if e['data'].get('call')!=3]
    record('entire_call_missing_not_shifted_into_success',audit(events,summary),'logical_call_marker_count_mismatch')
    events,summary=synthetic();raw,summary=seal(events,summary);summary['trials'][0]['trace']['blob']='0'*64
    record('immutable_trace_hash_mismatch',v.validate(raw,summary,bundle,v.EXPECTED_SOURCE,expected_job=v.EXPECTED_JOB),'trace_hash_mismatch')
    # A length stop or malformed model content is preserved, not a validator pass
    # on semantics. Full raw output remains available for manual review.
    events,summary=synthetic();reply=next(e for e in events if e['kind']=='llm_response');reply['data']['response']['choices'][0].update(finish_reason='length');reply['data']['response']['choices'][0]['message']['content']='{broken'
    metadata(events,1,lambda m:m.update(finish_reason='length'));report=audit(events,summary);record('length_and_malformed_content_preserved',report);assert report['rows'][0]['length_truncated'] and report['rows'][0]['raw_content']=='{broken'
    # A host 429 adds an attempt, never an experimental repeat. Use actual
    # archived retry/error event envelopes and preserve unpriced rejection.
    events,summary=synthetic();pos=next(i for i,e in enumerate(events) if e['kind']=='llm_response' and e['data']['call']==1)
    final=events[pos];final['data']['attempt']=2
    reject=copy.deepcopy(rejection_template);retry=copy.deepcopy(retry_template);req=copy.deepcopy(events[pos-1]);req['data']['attempt']=2
    for e in (reject,retry):e['data'].update(call=1,trial_id='SYNTHETIC_TEST_ONLY')
    events[pos:pos]=[reject,retry,req];report=audit(events,summary);record('observed429_schema_separate_attempt',report);assert report['provider_attempts']==69 and report['observed_logical_calls']==68 and not report['billing']['cost_complete']
    events2=copy.deepcopy(events);events2.remove(next(e for e in events2 if e['kind']=='llm_retry'));record('retry_event_missing',audit(events2,copy.deepcopy(summary)),'unsupported_or_missing_retry')
    events2=copy.deepcopy(events);next(e for e in events2 if e['kind']=='llm_response' and e['data']['status']==429)['data']['response']['id']='generation-evidence';record('retry_with_generation_evidence_rejected',audit(events2,copy.deepcopy(summary)),'unsupported_or_missing_retry')
    events,summary=synthetic();pos=next(i for i,e in enumerate(events) if e['kind']=='llm_response');err=copy.deepcopy(error_template);err['data'].update(call=1,trial_id='SYNTHETIC_TEST_ONLY');events[pos]=err
    metadata(events,1,lambda m:m.update(status='error',response_id=None,finish_reason=None,error_preview='Inference outcome/cost unconfirmed'[:32]))
    finished(events)['output']=finished(events)['output'].replace('"responses": 68, "errors": 0','"responses": 67, "errors": 1')
    report=audit(events,summary);record('observed_timeout_schema_raw_error_linked',report);assert report['rows'][0]['raw_final_event']['data']['error']==error_template['data']['error'] and not report['billing']['cost_complete']
    events,summary=synthetic();summary['state']='cancelled';summary['trials'][0]['state']='cancelled'
    events[:]=[e for e in events if e['data'].get('call',0)<=3 and not (e['kind']=='rpc_request' and e['data'].get('method')=='Answer')]
    pos=next(i for i,e in enumerate(events) if e['kind']=='llm_response' and e['data']['call']==3)
    err=copy.deepcopy(error_template);err['data'].update(call=3,trial_id='SYNTHETIC_TEST_ONLY',error='Cancelled by user');events[pos]=err
    metadata(events,3,lambda m:m.update(status='cancelled',response_id=None,finish_reason=None,error_preview='Cancelled by user'))
    lines=finished(events)['output'].splitlines();finished(events)['output']='\n'.join(lines[:7])+'\n'
    report=audit(events,summary);record('cancellation_keeps_all68_cells',report);assert sum(r['state']=='unattempted_after_cancellation' for r in report['rows'])==65
    # Host cancellation before terminal inference event is incomplete, not guessed.
    events.remove(err);record('cancelled_inflight_missing_terminal_event',audit(events,summary),'terminal_attempt_event_missing_or_duplicate')
    events,summary=synthetic();summary['trials'][0]['usage']['reported_cost_usd']='999';report=audit(events,summary);record('settled_cost_mismatch_flagged_separately',report);assert not report['billing']['cost_complete']
    events,summary=synthetic();del next(e for e in events if e['kind']=='llm_response')['data']['response']['usage']['cost'];report=audit(events,summary);record('missing_cost_not_zero_imputed',report);assert not report['billing']['cost_complete']
    events,summary=synthetic();raw,summary=seal(events,summary)
    truncated=raw[:len(raw)//2];report=v.validate(truncated,summary,bundle,v.EXPECTED_SOURCE,expected_job=v.EXPECTED_JOB)
    record('truncated_paginated_trace_not_complete',report,'trace_hash_mismatch')
    assert len(report['rows'])==68 and all(r['state']!='unattempted_after_cancellation' for r in report['rows'])
    events,summary=synthetic();i=next(i for i,e in enumerate(events) if e['kind']=='llm_response');events[i],events[i+1]=events[i+1],events[i]
    record('interleaved_logical_calls',audit(events,summary),'logical_calls_interleaved')
    events,summary=synthetic();req=next(e for e in events if e['kind']=='llm_request');events.insert(3,copy.deepcopy(req))
    record('duplicate_request_event',audit(events,summary),'request_event_missing_or_duplicate')
    events,summary=synthetic();summary['state']='cancelled';summary['trials'][0]['state']='cancelled';finished(events)['output']=''
    report=audit(events,summary);record('cancel_status_without_stdout_not_unattempted',report,'begin_marker_mismatch')
    assert all(r['state']!='unattempted_after_cancellation' for r in report['rows'])
    report=dict(status='offline tests passed',real68_results_available=False,real_model_calls=0,tests=tests,total_tests=len(tests),original_verifier_reused_unchanged=True,no_semantic_scorer=True)
    (HERE/'test-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS {len(tests)} offline trace checks; original archived16 verifier reproduced; no real68 outputs or model calls.')

if __name__=='__main__':main()
