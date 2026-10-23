"""Deterministically archive the immutable author evidence plus root review."""
from pathlib import Path
import hashlib,io,json,lzma,tarfile
P=Path(__file__).resolve().parent
A=P.parent/'2026-10-23-train4-h4-review'
members={f'review/{p.relative_to(A)}':p.read_bytes() for p in sorted(A.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
members['publication/ROOT-REVIEW.md']=(P/'ROOT-REVIEW.md').read_bytes()
members['publication/package.py']=Path(__file__).read_bytes()
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w',format=tarfile.PAX_FORMAT) as t:
 for name,data in sorted(members.items()):
  info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0
  t.addfile(info,io.BytesIO(data))
raw=lzma.compress(b.getvalue(),preset=9)
(P/'evidence.tar.xz').write_bytes(raw)
r={'members':len(members),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'files':{n:hashlib.sha256(v).hexdigest() for n,v in members.items()}}
(P/'archive-manifest.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='files'}))
