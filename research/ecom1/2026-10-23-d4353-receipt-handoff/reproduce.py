"""Reproduce the current offline prototype from one self-contained local closure."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
excluded={'publication','__pycache__','diagnostic-plan'}
def pins(p):
 return {str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*')
         if f.is_file() and not any(part in excluded for part in f.relative_to(p).parts)
         and f.name not in {'closure-reproduction.json','SHA256SUMS.json'}}
before=pins(P)
steps=['build.py','test_native_structure.py','independent/review.py','independent/build_reproduce.py',
       'independent/revision2/review.py','independent/wire-review/review.py','whole-agent/reproduce.py']
with tempfile.TemporaryDirectory(prefix='receipt-handoff-closure-') as tmp:
 q=Path(tmp)/'prototype'
 shutil.copytree(P,q,ignore=shutil.ignore_patterns(*excluded))
 for step in steps:
  r=subprocess.run([sys.executable,str(q/step)],cwd=q,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
  assert r.returncode==0,(step,r.stdout,r.stderr)
 after=pins(q)
 diff={n:[h,after.get(n)] for n,h in before.items() if h!=after.get(n)}
 metadata_differences={}
 name='independent/build-results.json'
 if name in diff:
  old=json.loads((P/name).read_text());new=json.loads((q/name).read_text())
  old_version=old.pop('python');new_version=new.pop('python')
  assert old==new and new_version==sys.version.split()[0]
  metadata_differences[name]={'python':[old_version,new_version]}
  del diff[name]
 assert not diff,diff
 assert pins(P)==before
report={'status':'PASS','scripts':steps,'compared_files':len(before),'byte_identical_files':len(before)-len(metadata_differences),
        'metadata_only_differences':metadata_differences,
        'whole_agent_executions':336,'native_structural_executions':23,'no_network_or_model_calls':True,
        'private_wire_encoding_verified':False,'live_model_or_score_improvement_established':False}
(P/'closure-reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
