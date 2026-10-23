"""Self-contained offline reproduction; never call inference or ECOM services."""
import hashlib,importlib.metadata,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
assert importlib.metadata.version('pydantic-monty')=='1.2.0'
manifest=json.loads((P/'SHA256SUMS.json').read_text())
for n,h in manifest.items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
for n in ['prepare.py','replay.py','t060/replay.py']:subprocess.run([sys.executable,str(P/n)],cwd=P,check=True)
for n,h in manifest.items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,('changed',n)
print('PASS exact CAS/source pins,48 original +8 separate executions, all preserved files unchanged.')
