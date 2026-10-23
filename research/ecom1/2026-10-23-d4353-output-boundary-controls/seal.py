"""Seal this author package; independent/publication material is excluded."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
files={}
for f in sorted(P.rglob('*')):
 if not f.is_file() or any(x in f.relative_to(P).parts for x in ['__pycache__','independent','publication']):continue
 if f==P/'SHA256SUMS.json' or f.suffix=='.zip':continue
 b=f.read_bytes();files[str(f.relative_to(P))]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
obj={'scope':'Exact-source offline main/forced boundary controls; no candidate source or provider call','file_count':len(files),'total_bytes':sum(v['bytes'] for v in files.values()),'files':files}
p=P/'SHA256SUMS.json';p.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps({'files':len(files),'bytes':obj['total_bytes'],'seal_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
