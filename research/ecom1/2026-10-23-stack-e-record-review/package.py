"""Deterministic self-contained evidence archive; excludes caches and publication."""
import gzip,hashlib,io,json,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent
for name,h in json.loads((P/'SHA256SUMS.json').read_text()).items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==h,name
files=sorted(p for p in P.rglob('*') if p.is_file() and not any(x in {'__pycache__','publication'} for x in p.relative_to(P).parts))
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w',format=tarfile.PAX_FORMAT) as t:
 for p in files:
  data=p.read_bytes();i=tarfile.TarInfo(str(Path(P.name)/p.relative_to(P)));i.size=len(data);i.mode=0o644;i.uid=i.gid=0;i.uname=i.gname='';i.mtime=0;t.addfile(i,io.BytesIO(data))
data=bytearray(gzip.compress(b.getvalue(),mtime=0));assert data[:4]==b'\x1f\x8b\x08\x00'
# Normalize only RFC1952 OS metadata; flags0 means no header CRC. Payload/CRC unchanged.
data[9]=255;out=Path('/tmp/ecom1-stack-e-record-review.tar.gz');out.write_bytes(data)
print(json.dumps({'path':str(out),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'files':len(files)}))
