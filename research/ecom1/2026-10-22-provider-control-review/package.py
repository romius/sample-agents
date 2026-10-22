"""Deterministic offline evidence bundle, including pinned local dependencies."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
OUTPUT=Path('/tmp/ecom1-provider-control-review.tar.gz')
manifest=json.loads((HERE/'SHA256SUMS.json').read_text())
for name,digest in manifest.items():
    assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,name
paths={p for p in HERE.rglob('*') if p.is_file() and not any(x in ['__pycache__','publication'] for x in p.relative_to(HERE).parts)}
for name,digest in json.loads((HERE/'DEPENDENCIES.json').read_text()).items():
    path=(HERE.parent/name).resolve()
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
    paths.add(path)
buffer=io.BytesIO()
with tarfile.open(fileobj=buffer,mode='w',format=tarfile.PAX_FORMAT) as tar:
    for path in sorted(paths,key=lambda p:str(p.relative_to(REPO))):
        data=path.read_bytes()
        info=tarfile.TarInfo(str(path.relative_to(REPO)))
        info.size=len(data);info.mode=0o644;info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
        tar.addfile(info,io.BytesIO(data))
data=bytearray(gzip.compress(buffer.getvalue(),mtime=0))
# Python3.12 delegates mtime=0 to zlib and exposes its OS marker;3.14 uses255.
# RFC1952 byte9=255 means unknown OS. With flags0 no header CRC is present;
# normalizing this metadata leaves the deflate payload and data CRC unchanged.
assert data[:4]==b'\x1f\x8b\x08\x00'
data[9]=255
data=bytes(data)
OUTPUT.write_bytes(data)
print(json.dumps(dict(path=str(OUTPUT),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),files=len(paths))))
