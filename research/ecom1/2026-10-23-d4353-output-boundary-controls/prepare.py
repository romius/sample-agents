"""Pin exact parent/build, archived fake-host world and public native host boundary."""
import hashlib,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent;prior=B/'2026-10-23-d4353-inference-retry';pins={}
def cp(src,rel):
 out=P/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out);b=out.read_bytes();pins[rel]={'original_workspace_path':str(src.relative_to(B.parent.parent)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
for n in ['parent.py','parent-readable.py','parent-decoded.py']:cp(prior/n,n)
for folder in ['parent-build','fixture','runtime']:
 for f in sorted((prior/folder).rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts:cp(f,str(f.relative_to(prior)))
for n in ['verify_inputs.py','input-verification.json','SOURCE-PINS.json']:
 cp(prior/n,'upstream-provenance/'+n)
for n in ['README.md','source-comparison.json','decision-table.json','context-pressure.json','SHA256SUMS.json']:
 cp(B/'2026-10-23-output-budget-boundaries'/n,'audit/'+n)
(P/'INPUT-PINS.json').write_text(json.dumps(pins,indent=2)+'\n');print('Pinned',len(pins),'exact inputs; no source edits.')
