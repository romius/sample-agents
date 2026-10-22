"""Compare all actual raw wire requests, including retries, to frozen SDK inputs."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':')).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def verify_wire():
    frozen=json.loads((HERE/'frozen.json').read_text())
    indexes=json.loads((HERE/'wire-request-indexes.json').read_text())
    initial=json.loads((HERE/'upstream/initial-response-events.json').read_text())
    following=[e for p in sorted(HERE.glob('continuation-events-*.json')) for e in json.loads(p.read_text())]
    responses=[[e for e in initial if e['kind']=='llm_response'],following]
    expected_provider={'only':['deepinfra/bf16'],'quantizations':['bf16'],'allow_fallbacks':False,'require_parameters':True}
    rows=[];logical=0;retries=0
    for ji,(job,response_events) in enumerate(zip(indexes,responses)):
        label='initial' if ji==0 else 'continuation'
        assert len(job['requests'])==len(response_events)
        pending_payload=None;pending_step=None;pending_attempt=None
        for entry,response in zip(job['requests'],response_events):
            path=HERE/'wire'/(label+'-'+str(entry['seq']).zfill(4)+'.json')
            raw=path.read_bytes();assert len(raw)==entry['data']['trace']['bytes']
            event=json.loads(raw)
            assert event['seq']==entry['seq'] and event['time']==entry['time'] and event['kind']=='llm_request'
            data=event['data'];assert data['call']==response['data']['call']
            assert data['attempt']==response['data']['attempt']
            assert data['trial_id']==response['data']['trial_id']
            step=frozen['plan'][logical];case=frozen['cases'][step['case_index']]
            obs=dict(case['base'])
            if step['arm']=='treatment':obs['sku_lookup_evidence']=case['evidence']
            messages=frozen['bootstrap']+[{'role':'user','content':case['instruction']},
                {'role':'assistant','content':json.dumps(case['action'])},
                {'role':'user','content':json.dumps(case['action'])+'\n'+json.dumps(obs)}]
            expected=dict(model='openai/gpt-oss-120b',messages=messages,temperature=0,reasoning={'effort':'medium'},max_tokens=2048,seed=20261023)
            wire=data['request'];normalized=dict(wire)
            assert normalized.pop('stream') is False
            assert normalized.pop('provider')==expected_provider
            assert normalized==expected
            assert sha(canonical(normalized))==step['request_sha256']
            if pending_payload is not None:
                assert wire==pending_payload and step==pending_step
                assert data['attempt']==pending_attempt+1
                retries+=1
            else:assert data['attempt']==1
            status=response['data']['status'];assert status in [200,429]
            rows.append(dict(job=job['job'],case=step['case'],arm=step['arm'],logical_plan_index=logical,
                request_event=event['seq'],response_event=response['seq'],request_time=event['time'],response_time=response['time'],
                call=data['call'],attempt=data['attempt'],response_status=status,raw_event_file=str(path.relative_to(HERE)),
                raw_event_bytes=len(raw),raw_event_sha256=sha(raw),canonical_wire_request_sha256=sha(canonical(wire)),
                normalized_request_sha256=sha(canonical(normalized)),expected_request_sha256=step['request_sha256'],
                equal_to_frozen_after_only_provider_stream_removal=True,retry_payload_equal=(pending_payload is not None)))
            if status==429:pending_payload=wire;pending_step=step;pending_attempt=data['attempt']
            else:logical+=1;pending_payload=None;pending_step=None;pending_attempt=None
        assert pending_payload is None
        assert logical==(17 if ji==0 else 60)
    assert logical==60 and len(rows)==68 and retries==8
    result=dict(status='passed',actual_wire_events=68,successful_logical_requests=60,identical_retry_payloads=8,
        raw_event_bytes=sum(r['raw_event_bytes'] for r in rows),provider=expected_provider,stream=False,
        normalization='Only SDK-added provider and stream removed. No max_tokens alias or content normalization used; messages, seed, temperature, reasoning, model and max_tokens match exactly.',
        preservation='wire/*.json are exact trace_event UTF-8 JSON bytes, not reconstructed raw events; sizes match server trace indexes. Timestamps, attempts and response correspondence retained.',rows=rows)
    (HERE/'wire-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    result=verify_wire();print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
