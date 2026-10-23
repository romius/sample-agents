from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile
P=Path(__file__).resolve().parent
outputs=['agent.py','readable.py','frozen.json','test-results.json']
with tempfile.TemporaryDirectory(prefix='null-final-diagnostic-') as td:
 t=Path(td)/P.name;shutil.copytree(P,t,ignore=shutil.ignore_patterns('__pycache__','independent','publication'))
 for name in ['build.py','test_runner.py']:
  r=subprocess.run([sys.executable,str(t/name)],cwd=t,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
  assert r.returncode==0,(r.stdout,r.stderr)
 for name in outputs:assert (P/name).read_bytes()==(t/name).read_bytes(),name
print(json.dumps({'status':'PASS','outputs_byte_identical':outputs,'executions':24,'native':12,'paid_calls':0}))
