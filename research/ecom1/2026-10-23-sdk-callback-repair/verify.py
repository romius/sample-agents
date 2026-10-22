"""Actual Monty ClassInstance boundary plus full inventory/recovery regressions."""
import ast,contextlib,copy,hashlib,io,json,os,sys,time
from pathlib import Path
import pydantic_monty as m
from build import decode,PARENTS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
ALLOWED={'task','call','answer','llm','usage'}
LIMITS=dict(max_feed_duration_secs=10,max_turn_duration_secs=10,max_suspensions=1000)

def sha(b):return hashlib.sha256(b).hexdigest()
def attributes(source):
 tree=ast.parse(source);parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)};hits=[]
 for node in ast.walk(tree):
  if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='bitgn':
   owner=parents.get(node)
   if not (isinstance(owner,ast.Call) and owner.func is node):hits.append(dict(attribute=node.attr,line=node.lineno,expression=ast.unparse(node),context=type(owner).__name__))
 return hits

class Probe:
 def __init__(self):self.calls=[]
 def task(self):return {'instruction':'fixture'}
 def call(self,method,args):self.calls.append([method,args]);return {'ok':True}

def native(source,host):
 with m.Monty() as pool:
  with pool.checkout(limits=LIMITS) as session:
   session.feed_run(source,inputs={'bitgn':m.ClassInstance(host,allowed_methods=ALLOWED)},print_callback=lambda *a:None)

def main():
 started=time.monotonic();report=dict(status='offline validation in progress',proxy='pydantic_monty.ClassInstance(host, allowed_methods=task/call/answer/llm/usage); eager_attrs=None; lazy_attrs=None',native_limits=LIMITS,audit=[],boundary=[],whole_agent=[],regressions=[])
 pins=json.loads((HERE/'DEPENDENCIES.json').read_text())
 for rel,h in pins.items():assert sha((ROOT/rel).read_bytes())==h,rel
 sources=[('d4702','2026-10-22-record-integration'),('d4955','2026-10-22-clarification-integration'),('d5204','2026-10-22-inventory-integration'),('d5785','2026-10-22-sku-history-pressure-review'),('d6280','2026-10-22-sku-lexical-paired-diagnostic')]
 for name,folder in sources:
  for form in ['readable.py','agent.py']:
   source=(ROOT/folder/form).read_text();decoded=decode(source) if form=='agent.py' else source
   hits=attributes(decoded);expected=1 if name in ['d5204','d5785'] else 0
   assert len(hits)==expected,(name,form,hits)
   if hits:assert hits[0]['attribute']=='call'
   report['audit'].append(dict(source=name,form=form,sha256=sha(source.encode()),decoded_sha256=sha(decoded.encode()),noncallee_bitgn_attributes=hits))
 for name in PARENTS:
  for form in ['readable.py','prepack.py','agent.py']:
   source=(HERE/name/form).read_text();decoded=decode(source) if form=='agent.py' else source
   assert not attributes(decoded)
   report['audit'].append(dict(source=name+'-successor',form=form,sha256=sha(source.encode()),noncallee_bitgn_attributes=[]))
 # Method dispatch is authorized; loading the same method as an attribute is not.
 probe=Probe();native('assert bitgn.call("Read", {"path":"/x"}) == {"ok":True}',probe);assert len(probe.calls)==1
 report['boundary'].append(dict(case='direct_method_call',passed=True,calls=probe.calls))
 for source in ['rpc=bitgn.call','def take(rpc):return None\ntake(bitgn.call)']:
  probe=Probe()
  try:native(source,probe)
  except Exception as exc:
   message=str(exc);assert 'AttributeError' in message and "has no attribute 'call'" in message,message
  else:raise AssertionError('noncallee attribute unexpectedly available')
  assert not probe.calls;report['boundary'].append(dict(case=source,passed=True,error=message))
 probe=Probe();native('def ix_rpc(method,args):\n return bitgn.call(method,args)\ndef invoke(rpc):\n return rpc("Read",{"path":"/x"})\nassert invoke(ix_rpc)=={"ok":True}',probe);assert len(probe.calls)==1
 report['boundary'].append(dict(case='named_wrapper_callback',passed=True,calls=probe.calls))
 sys.path.insert(0,str(ROOT/'2026-10-22-inventory-integration'))
 import verify_integration as suite
 old_execute=suite.execute
 def faithful_execute(source,world,fault='',native=False):
  if not native:return old_execute(source,world,fault,False)
  host=suite.Host(world,fault)
  with m.Monty() as pool:
   with pool.checkout(limits=LIMITS) as session:
    session.feed_run(source,inputs={'bitgn':m.ClassInstance(host,allowed_methods=ALLOWED)},print_callback=lambda *a:None)
  return dict(answers=host.answers,calls=host.calls,writes=host.writes,models=host.models)
 # Exact parent forms fail at the early inventory entry even on benign requests.
 for name,(folder,_,_) in PARENTS.items():
  for world_name in ['own','record','benign']:
   world=suite.review.fixture('own' if world_name=='benign' else world_name)
   if world_name=='benign':world['instruction']='Please explain inventory CSV exports.'
   for form in ['readable.py','agent.py']:
    host=suite.Host(world)
    try:native((ROOT/folder/form).read_text(),host)
    except Exception as exc:
     error=str(exc);assert 'AttributeError' in error and "has no attribute 'call'" in error,error
    else:raise AssertionError('parent unexpectedly accepted by actual proxy')
    assert not host.models and not host.writes and not host.answers and not host.calls
    report['whole_agent'].append(dict(source=name,form=form,world=world_name,expected_failure=True,error=error,model_calls=0,writes=0,rpc_calls=0))
 # Reuse full216 cases with only the native SDK exposure replaced. Recovery's
 # host Harness stays outside Monty, passed through the same real ClassInstance.
 original=(ROOT/'2026-10-22-inventory-integration/verify_integration.py').read_text()
 marker="env=dict(ast=ast,contextlib=contextlib,io=io,json=json,Path=Path,m=m);exec(part,env)"
 assert original.count(marker)==1
 adapted=original.replace(marker,marker+";env['run']=faithful_recovery(env)")
 def faithful_recovery(env):
  original_run=env['run']
  def run(src,mode='main',err='',count=0,native=False):
   if not native:return original_run(src,mode,err,count,False)
   hostns={};exec(env['pre'],hostns);host=hostns['Harness'](mode,err,count);out=[]
   code='failure=None\ntry:\n exec('+repr(src)+')\nexcept RuntimeError as e:failure=str(e)\nprint("PROXY_FAILURE "+json.dumps(failure))'
   with m.Monty() as pool:
    with pool.checkout(limits=LIMITS) as session:
     session.feed_run('import json\n'+code,inputs={'bitgn':m.ClassInstance(host,allowed_methods=ALLOWED)},print_callback=lambda *a:out.append(str(a[1]) if len(a)>1 else str(a[0])))
   failure=json.loads(next(x[len('PROXY_FAILURE '):] for x in ''.join(out).splitlines() if x.startswith('PROXY_FAILURE ')))
   return [host.answers,host.calls,host.requests,host.successes,failure]
  return run
 env={'__file__':str(ROOT/'2026-10-22-inventory-integration/verify_integration.py'),'__name__':'adapted_inventory_verifier','faithful_recovery':faithful_recovery}
 exec(adapted,env)
 for name in PARENTS:
  env['HERE']=HERE/name;env['SOURCES']={f:(HERE/name/f).read_text() for f in ['readable.py','prepack.py','agent.py']};env['execute']=faithful_execute
  with contextlib.redirect_stdout(io.StringIO()):env['main']()
  result=json.loads((HERE/name/'integration-results.json').read_text())
  count=sum(len(result[k]) for k in ['success','faults','benign','recovery'])*6
  assert count==216,count
  report['regressions'].append(dict(source=name+'-successor',executions=count,native_classinstance_executions=count//2,success_worlds=len(result['success']),faults=len(result['faults']),benign=len(result['benign']),recovery=len(result['recovery']),advisory_replays=len(result['replays']),source_forms=['readable.py','prepack.py','agent.py'],passed=True))
 for rel,h in pins.items():assert sha((ROOT/rel).read_bytes())==h,rel
 report.update(status='passed offline; actual hosted SDK check still separate',seconds=time.monotonic()-started,real_model_calls=0,source_parents_unchanged=True)
 (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS actual ClassInstance boundary; exact parent failures; both successors each216 regressions /108native; unchanged inputs.')
if __name__=='__main__':main()
