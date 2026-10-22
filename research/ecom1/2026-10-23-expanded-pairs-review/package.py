"""Deterministic evidence bundle; verify.py must pass before packaging."""
import gzip,hashlib,io,json,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
OUTPUT=Path('/tmp/ecom1-expanded-pairs-review.tar.gz')
manifest=json.loads((HERE/'SHA256SUMS.json').read_text())
for name,digest in manifest.items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,name
paths=[p for p in HERE.rglob('*') if p.is_file() and not any(x in ['__pycache__','publication'] for x in p.relative_to(HERE).parts)]
buffer=io.BytesIO()
with tarfile.open(fileobj=buffer,mode='w',format=tarfile.PAX_FORMAT) as tar:
    for path in sorted(paths,key=lambda p:str(p.relative_to(REPO))):
        data=path.read_bytes();info=tarfile.TarInfo(str(path.relative_to(REPO)))
        info.size=len(data);info.mode=0o644;info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
        tar.addfile(info,io.BytesIO(data))
data=bytearray(gzip.compress(buffer.getvalue(),mtime=0))
assert data[:4]==b'\x1f\x8b\x08\x00'
data[9]=255 # RFC1952 unknown OS; normalize Python3.12/3.14 header difference.
OUTPUT.write_bytes(data)
print(json.dumps(dict(path=str(OUTPUT),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),files=len(paths))))
