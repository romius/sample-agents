"""Clean self-contained offline reproduction, original directory read-only."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def members():return {str(p.relative_to(P)):sha(p.read_bytes()) for p in sorted(P.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and 'publication' not in p.parts and not (p.parent==P and p.name in ['SHA256SUMS.json','clean-reproduction.json'])}
before=members()
with tempfile.TemporaryDirectory(prefix='ecom1-x10-h4-') as tmp:
 dest=Path(tmp)/'composition';dest.mkdir()
 for name in before:
  target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/name,target)
 outputs=[]
 for script in ['build.py','replay.py','analyze.py','resolver_controls.py']:
  run=subprocess.run([sys.executable,str(dest/script)],cwd=tmp,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},text=True,capture_output=True)
  assert run.returncode==0,(script,run.stdout[-1000:],run.stderr)
  outputs.append({'script':script,'status':'passed'})
 for name,wanted in before.items():assert sha((dest/name).read_bytes())==wanted,name
assert members()==before
r={'status':'PASS clean offline deterministic reproduction','files_compared':len(before),'scripts':outputs,'model_calls':0,'original_files_unchanged':True}
(P/'clean-reproduction.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
