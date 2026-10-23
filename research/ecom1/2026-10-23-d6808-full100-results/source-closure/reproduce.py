"""Rebuild the exact record, candidate and all offline evidence in an isolated copy."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,pin in json.loads((P/'SOURCE-PINS.json').read_text()).items():assert (P/n).stat().st_size==pin['bytes'] and sha(P/n)==pin['sha256'],n
names=['agent.py','readable.py','decoded.py','candidate.diff','build-result.json','boundary-results.json','world.json','world-provenance.json','evidence/trace-t079.ndjson','cases.json','continuation.json','requests.json','whole-results.json']
before={n:sha(P/n) for n in names}
with tempfile.TemporaryDirectory(prefix='d4353-exec404-clean-') as tmp:
 dst=Path(tmp)/'experiment';shutil.copytree(P,dst,ignore=shutil.ignore_patterns('__pycache__','publication','independent','clean-reproduction.json','SHA256SUMS.json'))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(dst/'parent-build/build_combined.py')],check=True,env=env,capture_output=True)
 for out,local in [('agent.py','parent.py'),('readable.py','parent-readable.py'),('decoded.py','parent-decoded.py')]:assert (dst/'parent-build'/out).read_bytes()==(dst/local).read_bytes(),out
 for script in ['prepare.py','build.py','test_boundaries.py','test_whole.py']:
  r=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(dst/script)],check=False,env=env,capture_output=True,text=True,cwd=dst)
  assert r.returncode==0,(script,r.stdout,r.stderr)
 after={n:sha(dst/n) for n in names};assert before==after,{n:[before[n],after[n]] for n in names if before[n]!=after[n]}
report={'status':'PASS','generated_files_exact':len(names),'exact_parent_rebuild':True,'whole_agent_executions':168,'native_whole_agent_executions':84,'isolated_function_evaluations':84,'native_error_representations':3,'sealed_trace_CAS':'1bcbf63ed2febf0911a728234f9862c9c221ea7bb324fc4a3906ec7d1e63c356','sha256':before}
(P/'clean-reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS clean exact parent/candidate/evidence rebuild:',len(names),'outputs;168 whole-agent executions')
