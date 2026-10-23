"""Rebuild reports and source in an isolated copy; preserve original evidence."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def files(p):return {str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts and 'publication' not in f.parts and f.name not in ('clean-reproduction.json','SHA256SUMS.json')}
before=files(P)
steps=['source_verify.py','reassemble.py','prepare_extra.py','build_loss_review.py','build_evidence_notes.py','build_review.py','verify.py','check_crosslist_ocr.py','success-evidence/reproduce.py']
with tempfile.TemporaryDirectory(prefix='d4955-audit-reproduction-') as tmp:
 q=Path(tmp)/'audit';shutil.copytree(P,q,ignore=shutil.ignore_patterns('__pycache__','publication'))
 for step in steps:
  r=subprocess.run([sys.executable,str(q/step)],cwd=q,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
  assert r.returncode==0,(step,r.stdout,r.stderr)
 after=files(q)
 differences=[n for n,h in before.items() if after.get(n)!=h]
 assert not differences,differences
 assert files(P)==before
report={'status':'PASS','python':sys.version,'scripts':steps,'preserved_files_compared':len(before),'all_compared_files_byte_identical':True,'no_live_or_model_calls':True,'original_evidence_unchanged':True,'scope':'Reproduces structural/accounting/source/parser reports and success subpackage. Manual judgments are preserved inputs, not automatically re-scored.'}
(P/'clean-reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
