"""Rebuild/test a clean self-contained copy; no original evidence is changed."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    exclude={'SHA256SUMS.json','clean-reproduction.json'}
    files=[f for f in sorted(P.rglob('*')) if f.is_file() and not (f.parent==P and f.name in exclude) and '__pycache__' not in f.parts]
    expected={str(f.relative_to(P)):sha(f.read_bytes()) for f in files}
    with tempfile.TemporaryDirectory(prefix='receipt-diagnostic-runner-') as td:
        dest=Path(td)/'package'
        for src in files:
            out=dest/src.relative_to(P);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)
        scripts=[]
        for name in ['build.py','test_runner.py']:
            r=subprocess.run([sys.executable,str(dest/name)],cwd=td,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
            assert r.returncode==0,(name,r.stdout,r.stderr)
            scripts.append({'script':name,'stdout':r.stdout})
        for rel,digest in expected.items():assert sha((dest/rel).read_bytes())==digest,rel
        tamper=[]
        for rel,kind in [('inputs/plan/requests/A023-P.json','request content drift'),('inputs/plan/call-plan.json','plan order drift')]:
            path=dest/rel;original=path.read_bytes();data=json.loads(original)
            if kind=='request content drift':data['args'][1][-1]['content']+=' changed'
            else:data['calls'][0],data['calls'][1]=data['calls'][1],data['calls'][0]
            path.write_text(json.dumps(data))
            r=subprocess.run([sys.executable,str(dest/'build.py')],cwd=td,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
            assert r.returncode!=0 and 'AssertionError' in r.stderr,(kind,r.returncode)
            path.write_bytes(original)
            tamper.append({'case':kind,'build_rejected_before_packing':True})
        for rel,digest in expected.items():assert sha((dest/rel).read_bytes())==digest,rel
    report={'status':'PASS isolated offline reproduction','files_compared':len(files),'scripts':scripts,'tamper_controls':tamper,'real_model_calls':0}
    (P/'clean-reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
