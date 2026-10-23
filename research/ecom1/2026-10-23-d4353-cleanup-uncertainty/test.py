"""Archived-world stateful cleanup controls; mutations/inference are offline."""
import ast,contextlib,copy,hashlib,io,json,platform
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
W=json.loads((P/'evidence/world.json').read_text())
# Reuse exact preserved host implementation without executing its test driver.
src=(P/'evidence/replay.py').read_text()
nodes=ast.parse(src).body
start=next(i for i,n in enumerate(nodes) if isinstance(n,ast.FunctionDef) and n.name=='canon')
stop=next(i for i,n in enumerate(nodes) if isinstance(n,ast.ClassDef) and n.name=='Host')
ns=dict(copy=copy,json=json,hashlib=hashlib,W=W)
exec('\n'.join(ast.get_source_segment(src,n) for n in nodes[start:stop+1]),ns)
Base=ns['Host']
cases=[dict(name=n,host_case=n) for n in ('actual_frozen','fresh_suffix','fresh_directory_decline','fresh_no_match_decline')]
cases.append(dict(name='all_files',host_case='router_then_terminal',all_files=True))
for position in (0,1,3):
 for effect in ('before','after'):
  for error in ('BitGN HTTP 404: {"code":"not_found","message":"not found"}', 'BitGN HTTP 503: result unconfirmed'):
   cases.append(dict(name=f'error_{position}_{effect}_{len(cases)}',host_case='router_then_terminal',position=position,effect=effect,error=error))

class ReviewHost(Base):
 def __init__(self,case):
  super().__init__(case['host_case']);self.control=case;self.attempted=[];self.confirmed=[];self.uncertain=[]
  if case.get('all_files'):
   self.info['instruction']='Please clean out every temporary file under '+W['root']+'. Delete all files there and nothing else. Return only the deleted paths, one per line, sorted alphabetically.'
  # Independent task selection uses exact basename suffix, not agent parsing.
  suffix='' if case.get('all_files') else '.log' if case['host_case']=='fresh_suffix' else '.tmp'
  self.expected=sorted(e['path'] for e in self.listing['entries'] if e['kind']=='NODE_KIND_FILE' and e['name'].endswith(suffix))
 def call(self,method,args):
  if method=='Delete':
   path=args['path'];self.attempted.append(path)
   if 'position' in self.control and path==self.expected[self.control['position']]:
    self.calls.append([method,copy.deepcopy(args)]);self.uncertain.append(path)
    if self.control['effect']=='after':self.deleted.append(path);del self.state[path]
    raise RuntimeError(self.control['error'])
   response=super().call(method,args);self.confirmed.append(path);return response
  return super().call(method,args)
 def llm(self,model,messages,**kwargs):
  if self.control.get('all_files') and not self.models:
   # Changed instruction: scripted router response, no exact request-match claim.
   request=ns['wire'](model,messages,kwargs);self.models.append({'request':request,'stub':'archived router response for fresh all-files instruction'})
   return copy.deepcopy(W['model_exchanges'][0]['response'])
  return super().llm(model,messages,**kwargs)

rows=[]
limits=dict(max_feed_duration_secs=10,max_turn_duration_secs=10,max_suspensions=1000)
with m.Monty() as pool:
 for version in ('parent','candidate'):
  for form in ('readable','packed'):
   file=P/('parent-readable.py' if form=='readable' else 'parent.py') if version=='parent' else P/('readable.py' if form=='readable' else 'agent.py')
   for case in cases:
    for engine in ('cpython','native'):
     host=ReviewHost(case);output=io.StringIO();native=[]
     if engine=='cpython':
      with contextlib.redirect_stdout(output):exec(compile(file.read_text(),file.name,'exec'),{'bitgn':host})
     else:
      with pool.checkout(limits=limits) as session:
       session.feed_run(file.read_text(),inputs={'bitgn':m.ClassInstance(host,allowed_methods={'task','call','answer','llm','usage'})},print_callback=lambda *a:native.append(str(a[-1])))
     assert not host.unmatched and len(host.answers)==1
     answer=host.answers[0]
     if 'position' in case:
      i=case['position'];expected=host.expected[:i+1] if version=='candidate' else host.expected
      assert host.attempted==expected
      assert host.confirmed==[x for x in expected if x not in host.uncertain]
      assert len(host.uncertain)==1 and len(host.models)==1
      assert answer['outcome']==('OUTCOME_ERR_INTERNAL' if version=='candidate' else 'OUTCOME_OK')
      if version=='candidate':
       assert 'deletion outcome unconfirmed for '+host.uncertain[0] in answer['message']
       prefix=answer['message'].split('Confirmed deleted paths:',1)[1]
       assert prefix==('\n'+'\n'.join(host.confirmed) if host.confirmed else ' none')
      else:assert answer['message']=='\n'.join(host.confirmed)
     elif case['host_case'] in ('fresh_directory_decline','fresh_no_match_decline'):
      assert not host.attempted and answer['outcome']=='OUTCOME_NONE_UNSUPPORTED'
     else:
      assert host.confirmed==host.expected and answer['outcome']=='OUTCOME_OK'
      assert answer['message']=='\n'.join(host.expected) and len(host.models)==1
     assert set(host.state)==set(host.initial)-set(host.deleted)
     assert all(host.state[k]==host.initial[k] for k in host.state)
     rows.append(dict(version=version,form=form,engine=engine,case=case['name'],rpc_calls=host.calls,models=host.models,answers=host.answers,attempted=host.attempted,confirmed=host.confirmed,uncertain=host.uncertain,deleted=host.deleted,remaining=sorted(host.state),stdout=output.getvalue() if engine=='cpython' else ''.join(native)))
for version in ('parent','candidate'):
 for case in cases:
  group=[r for r in rows if r['version']==version and r['case']==case['name']]
  for key in ('rpc_calls','models','answers','attempted','confirmed','uncertain','deleted','remaining'):
   assert all(r[key]==group[0][key] for r in group)
for case in cases:
 if 'position' not in case:
  group=[r for r in rows if r['case']==case['name']]
  for key in ('rpc_calls','models','answers','attempted','confirmed','uncertain','deleted','remaining'):
   assert all(r[key]==group[0][key] for r in group)
report={'status':'PASS','executions':len(rows),'cases':len(cases),'actual_model_calls':0,'actual_ecom_calls':0,'limits':limits,'runtime':platform.python_version(),'monty':'1.2.0','error_and_missing_delete_acks_are_simulated':True,'results':rows}
(P/'test-results.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS',len(rows),'whole-agent executions;',len(cases),'cases')
