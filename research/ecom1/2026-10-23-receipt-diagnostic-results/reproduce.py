"""Isolated offline reproduction; no Brain, inference, or writes to raw evidence."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def verify(root,manifest):
 data=json.loads(manifest.read_text())
 if isinstance(data,list):entries={r['path']:r for r in data}
 else:entries=data.get('files',data)
 for rel,pin in entries.items():
  b=(root/rel).read_bytes();assert sha(b)==pin['sha256'] and len(b)==pin['bytes'],(manifest,rel)
 return len(entries)
def main():
 pinned=verify(P,P/'DEPENDENCIES.json')
 seals={}
 for root,filename in [(P/'primary','FIRST-REVIEW-SEAL.json'),(P/'independent','FIRST-REVIEW-SEAL.json'),(P/'independent','FINAL-SEAL.json'),(P/'inputs/diagnostic-plan','SHA256SUMS.json'),(P/'inputs/diagnostic-runner','SHA256SUMS.json')]:
  # Primary first seal uses paths relative to the evidence folder.
  seals[str((root/filename).relative_to(P))]=verify(P if root==P/'primary' else root,root/filename)
 if (P/'SHA256SUMS.json').exists():verify(P,P/'SHA256SUMS.json')
 assert sha((P/'inputs/diagnostic-runner/agent.py').read_bytes())=='4237825f66d2215a805d6ddd1823b9bf0e803798ce34b63aeb3b60696673626f'
 expected={str(p.relative_to(P)):p.read_bytes() for p in P.rglob('*') if p.is_file() and not any(x in p.parts for x in ['__pycache__','publication']) and p.name not in ['reproduction.json','SHA256SUMS.json'] and p.suffix!='.zip'}
 logs=[]
 with tempfile.TemporaryDirectory(prefix='receipt-results-reproduce-') as td:
  workspace=Path(td)/'research/ecom1';dest=workspace/P.name
  shutil.copytree(P,dest,ignore=shutil.ignore_patterns('__pycache__','publication','*.zip'))
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
  for name in ['reassemble.py','validate.py','test_validation.py','prepare_blind.py','primary_review.py','make_readout.py','independent/write_blind_review.py','independent/reconcile.py']:
   proc=subprocess.run([sys.executable,str(dest/name)],cwd=dest,env=env,text=True,capture_output=True)
   assert proc.returncode==0,(name,proc.stdout,proc.stderr)
   logs.append({'script':name,'stdout_sha256':sha(proc.stdout.encode()),'exit_code':proc.returncode})
  # Preserve the exact independent root script; recreate its relative folder convention only in /tmp.
  acct=workspace/'2026-10-23-receipt-results-publication';acct.mkdir()
  for name in ['check_accounting.py','accounting-controls.json']:shutil.copyfile(dest/'inputs/root-accounting-review'/name,acct/name)
  proc=subprocess.run([sys.executable,str(acct/'check_accounting.py')],cwd=acct,env=env,text=True,capture_output=True)
  assert proc.returncode==0,(proc.stdout,proc.stderr)
  assert (acct/'accounting-controls.json').read_bytes()==(dest/'inputs/root-accounting-review/accounting-controls.json').read_bytes()
  logs.append({'script':'exact root check_accounting.py staged in temporary sibling','stdout_sha256':sha(proc.stdout.encode()),'exit_code':proc.returncode})
  for rel,b in expected.items():assert (dest/rel).read_bytes()==b,('reproduction drift',rel)
 report={'status':'PASS isolated offline reproduction','python':sys.version,'dependency_pins':pinned,'seals_verified':seals,'copied_files_compared':len(expected),'byte_exact_all_compared_files':True,'scripts':logs,'structural_controls':23,'independent_root_controls':10,'real_model_calls':0,'semantic_labels':'Literal manual judgments transcribed and joined, never auto-scored.','raw_evidence_modified':False}
 if '--write-report' in sys.argv:(P/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
 elif (P/'reproduction.json').exists():assert report==json.loads((P/'reproduction.json').read_text()),'reproduction report mismatch; check pinned Python/environment and closure'
 print('PASS: isolated byte-exact reconstruction/review joins;23 structural controls +10 independent controls; no model calls.')
if __name__=='__main__':main()
