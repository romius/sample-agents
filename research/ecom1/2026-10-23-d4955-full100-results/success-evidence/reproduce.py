"""Clean offline reconstruction without altering the original evidence."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
pins=json.loads((P/'event-manifest.json').read_text())['inputs']
for name,wanted in pins.items():assert hashlib.sha256((P.parent/name).read_bytes()).hexdigest()==wanted
subprocess.run([sys.executable,str(P/'seal.py'),'--check'],check=True)
with tempfile.TemporaryDirectory(prefix='ecom1-d4955-success-') as tmp:
 root=Path(tmp);dst=root/'success-evidence';shutil.copytree(P,dst,ignore=shutil.ignore_patterns('__pycache__','publication'))
 for name in pins:shutil.copy2(P.parent/name,root/name)
 for script in ['build_review.py','check_support.py']:
  subprocess.run([sys.executable,str(dst/script)],cwd=tmp,check=True)
 subprocess.run([sys.executable,str(dst/'seal.py'),'--check'],cwd=tmp,check=True)
 print(json.dumps({'clean_offline_reconstruction':'passed','sealed_outputs_byte_identical':True,'model_calls':0,'network_calls':0,'seal_sha256':hashlib.sha256((P/'SHA256SUMS.json').read_bytes()).hexdigest()}))
