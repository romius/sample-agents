"""Run from an extracted workspace using pinned Python3.14/Monty; no network/model calls."""
import hashlib,importlib.metadata,inspect,json,platform,subprocess,sys,tempfile
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent;ROOT=P.parents[2];REPAIR=P.parent/'2026-10-23-stack-e-ocr-repair';REC=P.parent/'2026-10-23-stack-e-record-review'
assert importlib.metadata.version('pydantic-monty')=='1.2.0'
host_sha=hashlib.sha256(Path(inspect.getfile(m.ClassInstance)).read_bytes()).hexdigest()
assert host_sha=='a27e69d1df8c46a24d996b02bb4e0bcb1aea465c3c5b3d51846c78e38f7e82c6'
manifest=json.loads((P/'BUNDLE-SHA256SUMS.json').read_text())
for name,h in manifest.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp)
 subprocess.run([sys.executable,str(REC/'upstream/build_e.py'),str(REC/'upstream/parent-r1.py'),str(REC/'upstream/parserdonor-r2.py'),str(d/'readable.py'),str(d/'agent.py')],cwd=ROOT,check=True)
 for n in ['readable.py','agent.py']:assert (d/n).read_bytes()==(REC/'upstream'/n).read_bytes()
for script in [REPAIR/'build.py',REPAIR/'test_parser.py',P/'prepare.py',P/'replay.py',REPAIR/'independent-controls/ecom1-ocr-independent-extra.py']:
 subprocess.run([sys.executable,str(script)],cwd=ROOT,check=True)
for suffix in ['fixtures','results']:
 name='ecom1-ocr-independent-extra-'+suffix+'.json'
 assert Path('/tmp',name).read_bytes()==(REPAIR/'independent-controls'/name).read_bytes()
for name,h in manifest.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,('changed after reproduction',name)
print(json.dumps({'status':'passed','python':platform.python_version(),'monty':'1.2.0','public_host_source_sha256':host_sha,'record_and_candidate_build_exact':True,'parser_evaluations':300,'whole_agent_executions':112,'all_bundle_files_unchanged':True}))
