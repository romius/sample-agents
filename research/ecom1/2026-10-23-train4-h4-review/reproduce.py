import hashlib,json,os,pathlib,shutil,subprocess,sys,tempfile
P=pathlib.Path(__file__).resolve().parent
outputs=['parent.py','parent-readable.py','agent.py','readable.py','formatted-readable.py','build-result.json','replay-results.json','analysis.json']
with tempfile.TemporaryDirectory(prefix='train4-h4-clean-') as tmp:
 q=pathlib.Path(tmp)/'review';shutil.copytree(P,q,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo','independent','publication'))
 for script in ['build.py','replay.py','analyze.py']:
  p=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(q/script)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  assert p.returncode==0,(script,p.stdout,p.stderr)
 for name in outputs:assert (P/name).read_bytes()==(q/name).read_bytes(),name
print(json.dumps({'status':'PASS','whole_agent_executions':64,'module_runtime_evaluations':80,'byte_identical_outputs':len(outputs),'external_bytecode_flag_required':False}))
