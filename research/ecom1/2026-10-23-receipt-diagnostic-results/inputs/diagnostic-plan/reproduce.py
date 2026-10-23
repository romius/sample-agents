"""Clean-copy offline preparation; does not edit upstream evidence or dispatch."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    deps=json.loads((P/'dependency-pins.json').read_text())
    excluded={'SHA256SUMS.json','clean-reproduction.json'}
    own=[f for f in P.rglob('*') if f.is_file() and f.name not in excluded and '__pycache__' not in f.parts]
    with tempfile.TemporaryDirectory(prefix='receipt-first-action-plan-') as td:
        temp=Path(td)
        for name,pin in deps.items():
            src=ROOT/name;assert sha(src.read_bytes())==pin['sha256']
            dst=temp/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        for src in own:
            dst=temp/src.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        copied=temp/P.relative_to(ROOT);reports=[]
        for script in ['prepare.py','verify.py']:
            result=subprocess.run([sys.executable,str(copied/script)],cwd=temp,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
            assert result.returncode==0,(script,result.stdout,result.stderr)
            reports.append({'script':script,'stdout':result.stdout})
        for src in own:assert src.read_bytes()==(temp/src.relative_to(ROOT)).read_bytes(),str(src)
    report={'status':'PASS','scripts':reports,'own_files_compared':len(own),'dependency_files':len(deps),'model_calls_made':0}
    (P/'clean-reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
