"""Deterministic complete current-record audit and narrow OCR candidate archive."""
import gzip,hashlib,io,json,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
folders=[P.parent/'2026-10-23-d4353-record-review',P]
files=sorted(f for folder in folders for f in folder.rglob('*') if f.is_file() and not any(x in {'__pycache__','publication'} for x in f.relative_to(folder).parts) and f.name!='BUNDLE-SHA256SUMS.json')
manifest={str(f.relative_to(ROOT)):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files}
seal=P/'BUNDLE-SHA256SUMS.json';seal.write_text(json.dumps(manifest,indent=2)+'\n')
files.append(seal);files.sort()
raw=io.BytesIO()
with tarfile.open(fileobj=raw,mode='w',format=tarfile.PAX_FORMAT) as archive:
 for f in files:
  data=f.read_bytes();entry=tarfile.TarInfo(str(f.relative_to(ROOT)));entry.size=len(data);entry.mode=0o644;entry.uid=entry.gid=entry.mtime=0;entry.uname=entry.gname='';archive.addfile(entry,io.BytesIO(data))
data=bytearray(gzip.compress(raw.getvalue(),mtime=0));assert data[:4]==b'\x1f\x8b\x08\x00';data[9]=255
out=P/'publication';out.mkdir(exist_ok=True)
(out/'complete.tar.gz').write_bytes(data)
receipt={'files':len(files),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'candidate':'420e904a4cb502221f8609f99bd0f62370deda775abb41b5be9880042f0b7bf8','parent':'d4353r1','archive':'complete.tar.gz'}
(out/'archive.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
