"""Self-contained clean-copy build/replay/analysis, no model or Brain calls."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 files=[p for p in sorted(P.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and 'independent' not in p.relative_to(P).parts and not(p.parent==P and p.name in ['SHA256SUMS.json','clean-reproduction.json'])]
 hashes={str(p.relative_to(P)):sha(p.read_bytes()) for p in files}
 with tempfile.TemporaryDirectory(prefix='d4353-h4-replay-') as td:
  dest=Path(td)/'package'
  for src in files:
   out=dest/src.relative_to(P);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)
  results=[]
  for script in ['build.py','replay.py','analyze.py']:
   r=subprocess.run([sys.executable,str(dest/script)],cwd=td,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
   assert r.returncode==0,(script,r.stdout,r.stderr)
   results.append({'script':script,'stdout':r.stdout})
  for path,digest in hashes.items():assert sha((dest/path).read_bytes())==digest,path
 report={'status':'PASS exact clean-copy reproduction','files_compared':len(files),'scripts':results,'live_calls':0}
 (P/'clean-reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'files_compared':len(files),'status':report['status']}))
if __name__=='__main__':main()
