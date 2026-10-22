"""Rebuild exact immutable record in a temporary directory, then run local audit."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)
    subprocess.run([sys.executable,str(P/'upstream/build_e.py'),str(P/'upstream/parent-r1.py'),str(P/'upstream/parserdonor-r2.py'),str(d/'readable.py'),str(d/'agent.py')],check=True)
    for name in ['readable.py','agent.py']:assert (d/name).read_bytes()==(P/'upstream'/name).read_bytes()
subprocess.run([sys.executable,str(P/'audit.py')],check=True)
print(json.dumps({'exact_build':'passed','packed_bytes':62475,'packed_sha256':'56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c'}))
