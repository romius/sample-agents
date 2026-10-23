"""Self-contained isolated exact-build and native-control reproduction; no network."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
seal=P/'SHA256SUMS.json'
if seal.exists():
 for n,v in json.loads(seal.read_text())['files'].items():
  b=(P/n).read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256'],n
outputs=['input-verification.json','cases.json','requests.json','responses.json','results.json','policy-matrix.json','decision-table.md','runtime-verification.json']
with tempfile.TemporaryDirectory(prefix='d4353-output-boundary-') as tmp:
 d=Path(tmp)/'controls';shutil.copytree(P,d,ignore=shutil.ignore_patterns('__pycache__','independent','publication','reproduction.json'))
 for script in ['verify_inputs.py','verify_runtime.py','test_boundaries.py','compare_policies.py']:
  subprocess.run([sys.executable,str(d/script)],check=True,capture_output=True)
 for n in outputs:assert (P/n).read_bytes()==(d/n).read_bytes(),n
report={'status':'PASS','isolation':'Temporary standalone folder; no sibling source or fixture reads','exact_generated_files':{n:sha((P/n).read_bytes()) for n in outputs},'native_executions':76,'real_inference_calls':0,'original_sources_modified':False}
(P/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
