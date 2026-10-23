"""Native error representation and isolated recovery/observation counterexamples."""
import ast,copy,json,hashlib
from pathlib import Path
import pydantic_monty as monty
P=Path(__file__).resolve().parent
LIMITS=dict(max_feed_duration_secs=10,max_turn_duration_secs=10,max_suspensions=1000)
audit=json.loads((P/'evidence/audit-old2-chunk076.json').read_text());row=next(r for r in audit['rows'] if r['task_id']=='t079')
error=next(e for e in row['events'] if e['seq']==10609);saved=error['data']['error'];assert saved.startswith('RuntimeError: ')
raw=saved[len('RuntimeError: '):]
terminal=next(e for e in row['events'] if e['seq']==10610)['data']['error'].splitlines()[-1]
assert terminal=='RuntimeError: '+saved
class BoundaryHost:
 def __init__(self,arg):self.arg=arg;self.captured=[]
 def fail(self):raise RuntimeError(self.arg)
 def record(self,x):self.captured.append(x)
representation=[]
with monty.Monty() as pool:
 for name,arg in [('raw_http',raw),('archived_rpc_error',saved),('incorrect_extra_prefix','RuntimeError: '+saved)]:
  h=BoundaryHost(arg)
  with pool.checkout(limits=LIMITS) as s:s.feed_run('try:\n bitgn.fail()\nexcept RuntimeError as exc:\n bitgn.record(str(exc))',inputs={'bitgn':monty.ClassInstance(h,allowed_methods={'fail','record'})})
  assert h.captured==[arg]
  raised=None
  try:
   with pool.checkout(limits=LIMITS) as s:s.feed_run('bitgn.fail()',inputs={'bitgn':monty.ClassInstance(h,allowed_methods={'fail'})})
  except Exception as exc:raised=str(exc)
  assert raised and raised.splitlines()[-1]=='RuntimeError: '+arg
  representation.append({'name':name,'python_host_exception_argument':arg,'native_guest_str':h.captured[0],'uncaught_final_line':raised.splitlines()[-1],'matches_archived_final_line':raised.splitlines()[-1]==terminal})
assert [x['matches_archived_final_line'] for x in representation]==[False,True,False]
def error_body(message,code='not_found'):return 'BitGN HTTP 404: '+json.dumps({'code':code,'message':message})
cases=[('actual_raw','exec',raw,True),('actual_saved','exec',saved,True),('fresh_missing_binary','exec',error_body('runtime tool not found: /bin/unavailable'),True),
 ('generic404','exec',error_body('not found'),False),('invoice404','exec',error_body('invoice not found: INV-7'),False),('payment404','exec',error_body('payment not found: pay-9'),False),
 ('prefix_collision','exec',error_body('runtime tool not foundry inventory missing'),False),('missing_colon','exec',error_body('runtime tool not found'),False),('wrong_code','exec',error_body('runtime tool not found: not found','invoice_missing'),False),
 ('wrong_message_type','exec',error_body(['runtime tool not found: not found']),False),('malformed_json','exec','BitGN HTTP 404: {broken',False),('array_json','exec','BitGN HTTP 404: []',False),('null_json','exec','BitGN HTTP 404: null',False),('wrong_status','exec',raw.replace('404','500',1),False),('extra_wrapper','exec','RuntimeError: '+saved,False),
 ('read404','read',error_body('file not found'),None),('delete404','delete',error_body('not found'),None),('delete_malformed404','delete','BitGN HTTP 404: {broken',None),('non404400','exec','BitGN HTTP 400: invalid arguments',None),('non404429','exec','BitGN HTTP 429: retry later',None),('non404403','exec','BitGN HTTP 403: denied',None)]
class Host:
 def __init__(self):self.results=[];self.calls=[]
 def record(self,x):self.results.append(x)
 def call(self,method,args):self.calls.append([method,copy.deepcopy(args)]);return {'stdout':'SCRIPTED help'}
def extracts(src):
 tree=ast.parse(src);names={'recoverable_lookup_error','observation','tool_help'}
 code='import json\n'+'\n'.join(ast.get_source_segment(src,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names)
 code+='\n'+next(ast.get_source_segment(src,n) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REPORTING_BINS' for t in n.targets))+'\nHELP_SHOWN=[]\n'
 return code
outputs={}
for version in ('parent','candidate'):
 src=(P/('parent-readable.py' if version=='parent' else 'readable.py')).read_text();code=extracts(src)
 for engine in ('CPython','native'):
  h=Host();script=code+'\nfor name,tool,message,expected in cases:\n f={"tool":tool,"path":"/bin/ls" if tool=="exec" else "/tmp/example"}\n r=recoverable_lookup_error(f,RuntimeError(message))\n bitgn.record([name,r,observation(f,r) if r is not None else None])\n'
  if engine=='CPython':exec(script,{'bitgn':h,'cases':cases})
  else:
   with monty.Monty() as pool:
    with pool.checkout(limits=LIMITS) as s:s.feed_run(script,inputs={'bitgn':monty.ClassInstance(h,allowed_methods={'record','call'}),'cases':cases})
  outputs[version+'/'+engine]={'results':h.results,'help_calls':h.calls}
for version in ('parent','candidate'):assert outputs[version+'/CPython']==outputs[version+'/native']
old=outputs['parent/native']['results'];new=outputs['candidate/native']['results']
for c,a,b in zip(cases,old,new):
 if c[3] is True:
  assert a[1] is None and b[1]['unavailable_tool']=='/bin/ls'
 elif c[3] is False:assert a[1] is None and b[1] is None
 else:assert a==b,(c,a,b)
# Existing exitCode1 SQL is returned as a process result and never enters recovery.
sql=[]
for version in ('parent','candidate'):
 h=Host();code=extracts((P/('parent-readable.py' if version=='parent' else 'readable.py')).read_text())
 script=code+'\nbitgn.record(observation({"tool":"exec","path":"/bin/sql","args":["bad query"]},{"exitCode":1,"stderr":"syntax error"}))'
 with monty.Monty() as pool:
  with pool.checkout(limits=LIMITS) as s:s.feed_run(script,inputs={'bitgn':monty.ClassInstance(h,allowed_methods={'call','record'})})
 assert not h.calls;sql.append(h.results)
assert sql[0]==sql[1]
report={'status':'PASS','scope':'Isolated exact function/native host boundary controls; whole-agent replay separate','representation':representation,'cases':cases,'results':outputs,'sql_exitCode1_observation_equal':True,'classifier_evaluations':len(cases)*4}
(P/'boundary-results.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(cases)*4,'isolated evaluations +3 native error representations +SQL observation parity')
