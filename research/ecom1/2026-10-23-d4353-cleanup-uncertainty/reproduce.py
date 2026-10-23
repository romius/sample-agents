import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,pin in json.loads((P/'SOURCE-PINS.json').read_text()).items():
 assert sha(P/name)==pin['sha256'] and (P/name).stat().st_size==pin['bytes'],name
names=['agent.py','readable.py','portable.py','parent-decoded.py','candidate.diff','build-result.json','test-results.json','evidence/world.json','evidence/oracle.json']
with tempfile.TemporaryDirectory(prefix='cleanup-uncertainty-clean-') as tmp:
 d=Path(tmp)/'experiment';shutil.copytree(P,d,ignore=shutil.ignore_patterns('__pycache__','publication','independent'))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 steps=[d/'parent-build/build_combined.py',d/'evidence/prepare.py',d/'build.py',d/'test.py']
 for script in steps:
  r=subprocess.run([sys.executable,str(script)],cwd=script.parent,env=env,capture_output=True,text=True)
  assert r.returncode==0,(script,r.stdout,r.stderr)
 for built,original in [('agent.py','parent.py'),('readable.py','parent-readable.py'),('decoded.py','parent-decoded.py')]:
  assert (d/'parent-build'/built).read_bytes()==(P/original).read_bytes(),built
 for name in names:assert sha(d/name)==sha(P/name),name
report={'status':'PASS','generated_files_reproduced':len(names),'whole_agent_executions':136,'exact_parent_build':True,'no_network_or_model_calls':True,'sha256':{name:sha(P/name) for name in names}}
(P/'clean-reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS clean reproduction:9 generated files;136 whole-agent executions')
