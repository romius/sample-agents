"""Isolated classifier parity plus pinned actual timeout suffix checks."""
import ast,json,re
import pydantic_monty as monty
from host import P,LIMITS,sha
src=(P/'guest-owned/readable.py').read_text()
code='import re\nimport json\n'+'\n'.join(ast.get_source_segment(src,n) for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name in ('inference_cancelled','inference_retryable'))
classifiers=[
 ('HTTP 400 connection timeout unavailable',False,False),('OpenRouter HTTP 429: rejected',False,False),
 ('HTTP 401 unauthorized',False,False),('HTTP 500 internal error',False,False),('HTTP 503 unavailable',False,True),
 ('HTTP 503 request cancelled',True,False),('Cancelled: connection closed',True,False),
 ('HTTP 503 request was not cancelled; unavailable',False,True),('HTTP 400 invalid cancellation_policy',False,False),
 ('TimeoutError: request was not cancelled',False,True),('Inference outcome/cost unconfirmed: TimeoutError: Request cancelled',True,False),
 ('OpenRouter HTTP 503: {"choices":[]}',False,False),('OpenRouter HTTP 503: {"usage":{}}',False,False),
 ('OpenRouter HTTP 503: {"id":""}',False,False),('OpenRouter HTTP 503: {broken',False,False),
 ('OpenRouter HTTP 503: {"error":{"message":"upstream unavailable"}}',False,True),
 ('temporary connection timeout unavailable',False,False),('request canceled',True,False),('Cancellation requested',True,False),
 ('Sandbox job cancelled',True,False),('ConnectionError: unknown connection failure',False,True),
 ('OpenRouter HTTP 503: request cancelled',True,False),
 ('Inference outcome/cost unconfirmed: OpenRouter HTTP 503: request cancelled',True,False),
 ('OpenRouter HTTP 503: {"error":{"message":"request cancelled"}}',True,False),
 ('OpenRouter HTTP 503: {"error":{"message":"request was not cancelled; upstream unavailable"}}',False,True),
 ('OpenRouter HTTP 503: [broken',False,False),
 ('OpenRouter HTTP 503: [{"id":"gen-synthetic","choices":[],"usage":{}}]',False,False),
 ('OpenRouter HTTP 503: []',False,False),
]
class Recorder:
 def __init__(self):self.results=[]
 def record(self,x):self.results.append(x)
script=code+'\nfor error in errors:\n bitgn.record([inference_cancelled(RuntimeError(error)),inference_retryable(RuntimeError(error))])'
outputs={}
for engine in ('CPython','native'):
 host=Recorder()
 if engine=='CPython':exec(script,{'bitgn':host,'errors':[x[0] for x in classifiers]})
 else:
  with monty.Monty() as pool:
   with pool.checkout(limits=LIMITS) as session:
    session.feed_run(script,inputs={'bitgn':monty.ClassInstance(host,allowed_methods={'record'}),'errors':[x[0] for x in classifiers]})
 assert host.results==[[c,r] for e,c,r in classifiers]
 outputs[engine]=host.results
receipts=[]
for task in ('t003','t045','t056','t059'):
 p=P/'evidence'/('new-failure-'+task+'.json');receipt=json.loads(p.read_text())
 event=next(e for e in receipt['events'] if e['kind']=='llm_error')
 err=next(e for e in receipt['events'] if e['kind']=='agent_error')
 assert event['data']['error']=='TimeoutError: The read operation timed out'
 assert 'RuntimeError: Inference outcome/cost unconfirmed: '+event['data']['error'] in err['data']['error']
 receipts.append({'file':p.name,'sha256':sha(p.read_text()),'seq':event['seq'],'error':event['data']['error'],'wrapper_verified':True})
(P/'classifier-results.json').write_text(json.dumps({'status':'PASS','cases':classifiers,'results':outputs,'actual_timeout_receipts':receipts},indent=2)+'\n')
print('PASS',len(classifiers)*2,'classifier evaluations and4 actual timeout receipts')
