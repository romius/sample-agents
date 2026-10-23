from pathlib import Path
import hashlib,json,os,subprocess,sys,tarfile,tempfile
P=Path(__file__).resolve().parent
meta=json.loads((P/'publication/archive.json').read_text());archive=P/'publication/h4-evidence.tar.xz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==meta['sha256']
with tempfile.TemporaryDirectory(prefix='h4-archive-check-') as td:
 root=Path(td)
 with tarfile.open(archive) as tar:
  assert sorted(tar.getnames())==sorted(meta['files'])
  tar.extractall(root,filter='data')
 def check():
  for name,pin in meta['files'].items():
   data=(root/name).read_bytes();assert len(data)==pin['bytes'] and hashlib.sha256(data).hexdigest()==pin['sha256'],name
 check();reports=[]
 for script in ['reproduce.py','independent/review.py']:
  r=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(root/'research/ecom1/2026-10-23-d4353-h4-replay'/script)],cwd=root,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
  assert r.returncode==0,(script,r.stdout,r.stderr)
  reports.append({'script':script,'stdout':r.stdout})
 check()
report={'status':'PASS','files_byte_identical':len(meta['files']),'archive_sha256':meta['sha256'],'scripts':reports,'live_model_calls':0}
(P/'publication/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='scripts'}))
