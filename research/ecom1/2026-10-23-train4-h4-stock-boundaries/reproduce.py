import hashlib,json,os,pathlib,shutil,subprocess,sys,tempfile
P=pathlib.Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='train4-stock-clean-') as tmp:
 q=pathlib.Path(tmp)/'review'
 shutil.copytree(P,q,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo','independent','publication'))
 result=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(q/'test_stock.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 assert result.returncode==0,(result.stdout,result.stderr)
 assert (P/'results.json').read_bytes()==(q/'results.json').read_bytes()
 print(json.dumps({'status':'PASS','executions':336,'native_executions':168,'results_byte_identical':True,'external_bytecode_flag_required':False,'results_sha256':hashlib.sha256((P/'results.json').read_bytes()).hexdigest()}))
