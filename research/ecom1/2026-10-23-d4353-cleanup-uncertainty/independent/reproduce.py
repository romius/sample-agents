import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=json.loads((P/'SHA256SUMS.json').read_text())
for n,v in seal.items():assert sha(P/n)==v['sha256'] and (P/n).stat().st_size==v['bytes'],n
pins=json.loads((P/'SOURCE-PINS.json').read_text())
for n,v in pins.items():assert sha(P/n)==v['sha256'] and (P/n).stat().st_size==v['bytes'],n
with tempfile.TemporaryDirectory(prefix='independent-cleanup-') as tmp:
 d=Path(tmp)/'package';shutil.copytree(P,d,ignore=shutil.ignore_patterns('independent','__pycache__','publication'))
 r=subprocess.run([sys.executable,str(d/'reproduce.py')],cwd=d,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),text=True,capture_output=True)
 assert r.returncode==0,(r.stdout,r.stderr)
 assert (d/'clean-reproduction.json').read_bytes()==(P/'clean-reproduction.json').read_bytes()
for n,v in seal.items():assert sha(P/n)==v['sha256'],n
report=dict(status='PASS',sealed_files=len(seal),dependency_pins=len(pins),whole_agent_executions=136,clean_report_byte_identical=True,original_seal_unchanged=True,stdout=r.stdout,seal_sha256=sha(P/'SHA256SUMS.json'))
(P/'independent/reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
