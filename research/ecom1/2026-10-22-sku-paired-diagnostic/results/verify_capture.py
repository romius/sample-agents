"""Verify sealed trace, exact planned prompts/order, all raw outputs and settled cost."""
import hashlib,json,decimal
from pathlib import Path
HERE=Path(__file__).resolve().parent
frozen=json.loads((HERE.parent/'fixtures.json').read_text())
summary=json.loads((HERE/'summary.json').read_text())
assert summary['state']=='completed'
assert summary['source']==dict(document='d5622',revision=1,sha256=hashlib.sha256((HERE.parent/'agent.py').read_bytes()).hexdigest(),sdk_version='0.3.7')
raw=(HERE/'trial-trace.ndjson').read_bytes()
assert hashlib.sha256(raw).hexdigest()==summary['trials'][0]['trace']['blob']
events=[json.loads(line) for line in raw.decode().splitlines()]
requests=[e for e in events if e['kind']=='llm_request'];responses=[e for e in events if e['kind']=='llm_response']
assert len(requests)==len(responses)==len(frozen['plan'])==16
finished=next(e for e in events if e['kind']=='agent_finished')
output=finished['data']['output']
(HERE/'agent-output.txt').write_text(output)
records=[json.loads(line.split(' ',1)[1]) for line in output.splitlines() if line.startswith('SKU_DIAGNOSTIC_RESULT ')]
request_markers=[json.loads(line.split(' ',1)[1]) for line in output.splitlines() if line.startswith('SKU_DIAGNOSTIC_REQUEST ')]
assert len(records)==16 and request_markers==frozen['plan']
rows=[];cost=decimal.Decimal(0)
for i,(step,event,response,record) in enumerate(zip(frozen['plan'],requests,responses,records),1):
 assert record['step']==step and event['data']['call']==response['data']['call']==i
 assert event['data']['attempt']==response['data']['attempt']==1
 actual=dict(event['data']['request']);provider=actual.pop('provider');assert actual.pop('stream') is False
 assert provider==dict(only=['deepinfra/bf16'],quantizations=['bf16'],allow_fallbacks=False,require_parameters=True)
 expected=frozen['fixtures'][step['case_index']]['arms'][step['arm']]
 assert actual==expected
 sha=hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert sha==step['request_sha256']
 assert response['data']['status']==200 and record['response']==response['data']['response']
 body=record['response'];choice=body['choices'][0]
 assert len(body['choices'])==1 and choice['finish_reason']=='stop'
 action=json.loads(choice['message']['content'])
 assert action['tool']=='report_completion' and isinstance(action['message'],str)
 assert isinstance(action['grounding_refs'],list) and all(isinstance(ref,str) for ref in action['grounding_refs'])
 assert action['outcome'] in ['OUTCOME_OK','OUTCOME_NONE_CLARIFICATION']
 cost+=decimal.Decimal(str(body['usage']['cost']))
 rows.append(dict(call=i,**step,request_verified=True,attempts=1,status=200,finish_reason=choice['finish_reason'],response_sha256=hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(),usage=body['usage'],action_text=choice['message']['content']))
assert cost==decimal.Decimal(summary['reported_cost_usd'])
assert sum(row['usage']['prompt_tokens'] for row in rows)==summary['prompt_tokens']
assert sum(row['usage']['completion_tokens'] for row in rows)==summary['completion_tokens']
assert summary['cost_complete'] and summary['unknown_cost_calls']==0 and summary['pending_calls']==0
methods=[e['data']['method'] for e in events if e['kind']=='rpc_request']
assert methods==['StartTrial','Answer','EndTrial']
(HERE/'records.json').write_text(json.dumps(records,indent=2)+'\n')
(HERE/'verified-calls.json').write_text(json.dumps(rows,indent=2)+'\n')
(HERE/'capture-verification.json').write_text(json.dumps(dict(status='passed',sealed_trace_sha256=hashlib.sha256(raw).hexdigest(),trace_bytes=len(raw),calls=16,provider_attempts=16,requests_match_frozen=True,all_responses_preserved=True,reported_cost_usd=str(cost),cost_complete=True,world_rpc_methods=methods,carrier_grade_ignored=True),indent=2)+'\n')
for row in rows:print(row['call'],row['case'],row['repeat'],row['arm'],row['finish_reason'],row['action_text'])
