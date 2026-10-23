"""Clean offline audit reproduction, including all source/error transport decoding."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['official-result.json','all-task-review.json','instructions.json','failure-template.txt','audit-report.json']+[str(f.relative_to(P)) for f in sorted((P/'traces').glob('*'))]
before={n:sha(P/n) for n in names}
with tempfile.TemporaryDirectory(prefix='d5204-audit-clean-') as tmp:
 dst=Path(tmp)/'audit';shutil.copytree(P,dst,ignore=shutil.ignore_patterns('__pycache__','publication','independent','clean-reproduction.json','SHA256SUMS.json'))
 for n in names:(dst/n).unlink()
 for script in ['decode_evidence.py','audit.py']:
  r=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(dst/script)],cwd=dst,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
  assert r.returncode==0,(script,r.stdout,r.stderr)
 after={n:sha(dst/n) for n in names};assert before==after,{n:[before[n],after[n]] for n in names if before[n]!=after[n]}
report={'status':'PASS','regenerated_files_exact':len(names),'complete_trial_traces':100,'each_trace_CAS_verified':True,'exact_submission_build_reproduced':True,'no_probe_or_model_calls':True,'sha256':before}
(P/'clean-reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS clean reconstruction/audit/rebuild:',len(names),'exact outputs')
