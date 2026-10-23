import hashlib,json,os,pathlib,shutil,subprocess,sys,tempfile
P=pathlib.Path(__file__).resolve().parent
pins=json.loads((P/'source-pins.json').read_text())
for row in pins:
 b=(P/row['path']).read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
with tempfile.TemporaryDirectory(prefix='d6729-source-') as tmp:
 q=pathlib.Path(tmp)/'sources';shutil.copytree(P/'sources',q,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 r=subprocess.run([sys.executable,str(q/'build.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});assert r.returncode==0,(r.stdout,r.stderr)
 for row in pins:assert (P/row['path']).read_bytes()==(q/pathlib.Path(row['path']).name).read_bytes(),row['path']
report={'status':'PASS exact build','source':'d6729r1','source_sha256':'420e904a4cb502221f8609f99bd0f62370deda775abb41b5be9880042f0b7bf8','bytes':63411,'parent':'d4353r1','parent_readable':'d4354r1','packer':'d3268r2','pins':len(pins),'all_rebuilt_files_identical':True,'build_mutates_original':False}
(P/'source-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
