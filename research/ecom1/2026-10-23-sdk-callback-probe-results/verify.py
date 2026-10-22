"""Verify the complete sealed SDK probe trace, not its carrier grade."""
import hashlib
import json
from pathlib import Path
P=Path(__file__).resolve().parent
raw=(P/'trace.jsonl').read_bytes()
assert len(raw)==3244
assert hashlib.sha256(raw).hexdigest()=='e102a5f3ef60e690915f8f4059f4abfff090f9ed3c4c6074ff5ebcf5f923068f'
events=[json.loads(line) for line in raw.splitlines()]
index=json.loads((P/'trace-index.json').read_text())
assert [e['seq'] for e in events]==list(range(4,15))==[e['seq'] for e in index['items']]
assert not index['more']
offset=0
for line,event,entry in zip(raw.splitlines(keepends=True),events,index['items']):
    trace=entry['data']['trace'];assert trace['offset']==offset and trace['bytes']==len(line)
    assert event['kind']==entry['kind'];offset+=len(line)
r=json.loads((P/'result.json').read_text())
assert r['job']['state']=='completed' and r['job']['source_blob']=='223cb4dc6ad9b6226f5dd2ce1aaf39001af7c840e902cc65be021866d86ef1a3'
assert r['result']['model_calls']==0 and r['result']['cost_complete'] and r['result']['unknown_cost_calls']==0
assert r['result']['reported_cost_usd']=='0'
calls=[e['data'] for e in events if e['kind']=='rpc_request']
assert [e['method'] for e in calls]==['StartTrial','Exec','Exec','Answer','EndTrial']
assert all(e['arguments']=={'path':'/bin/id'} for e in calls if e['method']=='Exec')
responses=[e['data']['response'] for e in events if e['kind']=='rpc_response' and e['data']['method']=='Exec']
assert len(responses)==2 and responses[0]==responses[1]
assert responses[0]['stdout'].startswith('user: ') and '\nroles: customer\n' in responses[0]['stdout']
assert not any(e['kind'].startswith('llm_') or e['kind']=='rpc_error' for e in events)
finished=next(e['data'] for e in events if e['kind']=='agent_finished')
output=finished['output'];assert output.startswith('SDK_CALLBACK_PROBE ')
observed=json.loads(output[output.index('{'):output.rindex('}')+1])
assert observed['method_value_access']=='raised'
assert observed['method_value_error']=="'BitGN' object has no attribute 'call'"
assert observed['direct_call']=='returned identity stdout'
assert observed['named_callback']=='returned identical identity stdout'
report={'status':'verified','sdk_version':r['job']['sdk_version'],'events':len(events),'sealed_trace_bytes':len(raw),'trace_sha256':hashlib.sha256(raw).hexdigest(),'model_calls':0,'reported_cost_usd':'0','cost_complete':True,'direct_and_wrapper_exec_responses_identical':True,'method_value_access_rejected':True,'limit':'One SDK boundary probe, not a whole-agent result or benchmark improvement; responses omit exitCode, so no exit-code claim.'}
(P/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
