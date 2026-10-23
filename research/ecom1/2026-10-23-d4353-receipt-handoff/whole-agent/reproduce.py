import pathlib,tempfile,shutil,subprocess,sys,json,hashlib,os
P=pathlib.Path(__file__).resolve().parent
outputs=['source-pins.json','results.json','gate-results.json','gate-cases.json','analysis.json']+[str(p.relative_to(P)) for p in (P/'upstream').glob('*_only*.py')]
with tempfile.TemporaryDirectory(prefix='receipt-handoff-whole-') as tmp:
 q=pathlib.Path(tmp)/'test';shutil.copytree(P,q,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'))
 child_env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for script in ['prepare.py','replay.py','gates.py','analyze.py']:
  subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(q/script)],check=True,stdout=subprocess.DEVNULL,env=child_env)
 for name in outputs:assert (P/name).read_bytes()==(q/name).read_bytes(),name
print(json.dumps({'status':'PASS','whole_agent_executions':336,'byte_identical_outputs':len(outputs)}))
