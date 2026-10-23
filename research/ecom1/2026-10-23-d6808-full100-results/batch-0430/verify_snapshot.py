"""Recover one fixed official result output, not a new status query."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
rs=[json.loads((P/f'receipts/result-part{i}.json').read_text()) for i in range(3)]
r=[x['response'] for x in rs]
assert rs[0]['request']['seq']==3
assert rs[1]['request']['source']=='print(brain.output(3, offset=24000))'
assert rs[2]['request']['source']=='print(brain.output(3, offset=44000))'
assert all(x['code']==0 for x in r)
assert r[0]['data']['displayed_bytes']==24000 and r[0]['data']['output_truncated']
assert all(not x['data']['output_truncated'] for x in r[1:])
# First output includes a server truncation notice outside displayed bytes.
# Each print(brain.output(...)) appends exactly one LF to the returned slice.
b=r[0]['output'].encode()[:24000]+r[1]['output'][:-1].encode()+r[2]['output'][:-1].encode()
assert len(b)==r[0]['data']['output_bytes']==63075
d=json.loads(b)
assert d==json.loads((P/'result.json').read_text())
assert d['job']['id']=='jb4798f05fa4941f88eacf20a40f42800'
assert d['job']['state']=='running' and d['result']['completed_trials']==66
assert sum(t.get('trace',{}).get('sealed',False) for t in d['result']['trials'])==66
assert d['result']['trials'][-1]['task_id']=='t067'
print(json.dumps({'result_output_bytes':len(b),'result_output_sha256':hashlib.sha256(b).hexdigest(),'exact_snapshot_projection':True,'completed_sealed':66,'failed':0,'running_task':'t067','grades_pending':True}))
