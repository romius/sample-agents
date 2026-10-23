"""Independent bounded syntax controls; no network, paid calls or candidate changes."""
import ast, hashlib, json
from pathlib import Path
import pydantic_monty as monty
P=Path(__file__).resolve().parent.parent
source=(P/'guest-owned/readable.py').read_text()
names={'inference_cancelled','inference_retryable'}
code='import json\nimport re\n'+'\n'.join(ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names)
errors=[
 'OpenRouter HTTP 503: [broken',
 'OpenRouter HTTP 503: [{"id":"gen-synthetic","choices":[],"usage":{}}]',
 'OpenRouter HTTP 503: {"error":{"message":"request was not cancelled; upstream unavailable"}}',
 'Inference outcome/cost unconfirmed: OpenRouter HTTP 503: {"error":{"message":"Request cancelled"}}',
 'OpenRouter HTTP 503: {"error":{"message":"request cancelledness is invalid"}}',
 'HTTP 503: {"choices":null}',
 'HTTP 503: {"error":{"message":null}}',
 'HTTP 429: {"error":{"message":"request cancelled"}}',
 'HTTP 400: {"error":{"message":"invalid cancellation_policy"}}',
 'TimeoutError: request was not cancelled',
]
receipts=[]
for path in sorted((P.parent/'2026-10-22-provider-control-review').glob('new-failure-*.json')):
 d=json.loads(path.read_text())
 for e in d['events']:
  if e['kind']=='llm_error':
   raw=e['data']['error'];errors.extend([raw,'Inference outcome/cost unconfirmed: '+raw]);receipts.append({'source':str(path.relative_to(P.parent)), 'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'event_seq':e['seq'],'error':raw})
class Host:
 def __init__(self):self.values=[]
 def record(self,x):self.values.append(x)
host=Host()
with monty.Monty() as pool:
 with pool.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as session:
  session.feed_run(code+'\nfor error in errors:\n bitgn.record([inference_cancelled(RuntimeError(error)), inference_retryable(RuntimeError(error))])',inputs={'errors':errors,'bitgn':monty.ClassInstance(host,allowed_methods={'record'})})
cp={};exec(code,cp)
expected=[[cp['inference_cancelled'](RuntimeError(e)),cp['inference_retryable'](RuntimeError(e))] for e in errors]
assert host.values==expected
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'cpython_native_parity':True,'synthetic_control_count':10,'actual_timeout_receipts':receipts,'observations':[{'error':e,'cancelled':r[0],'retryable':r[1]} for e,r in zip(errors,host.values)],'scope':'Fresh syntax controls only; no claim these synthetic envelopes occurred at provider boundary.'}
(P/'independent/classifier-observations.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
