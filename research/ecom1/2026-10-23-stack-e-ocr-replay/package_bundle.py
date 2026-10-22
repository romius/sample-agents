"""Deterministic workspace-relative record+candidate+replay closure."""
import gzip,hashlib,io,json,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
names=['2026-10-23-stack-e-record-review','2026-10-23-stack-e-ocr-repair','2026-10-23-stack-e-ocr-replay']
files=sorted(p for n in names for p in (P.parent/n).rglob('*') if p.is_file() and not any(x in {'__pycache__','publication'} for x in p.relative_to(P.parent/n).parts))
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.name!='BUNDLE-SHA256SUMS.json'}
mp=P/'BUNDLE-SHA256SUMS.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
if mp not in files:files.append(mp);files.sort()
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w',format=tarfile.PAX_FORMAT) as t:
 for p in files:
  data=p.read_bytes();i=tarfile.TarInfo(str(p.relative_to(ROOT)));i.size=len(data);i.mode=0o644;i.uid=i.gid=0;i.uname=i.gname='';i.mtime=0;t.addfile(i,io.BytesIO(data))
data=bytearray(gzip.compress(b.getvalue(),mtime=0));assert data[:4]==b'\x1f\x8b\x08\x00';data[9]=255
# OS metadata normalization only, with no optional header CRC; payload/CRC preserved.
out=Path('/tmp/ecom1-stack-e-ocr-complete.tar.gz');out.write_bytes(data)
print(json.dumps({'path':str(out),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'files':len(files)}))
