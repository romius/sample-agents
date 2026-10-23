from pathlib import Path
import hashlib, io, json, lzma, tarfile
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
H=P.parent/'2026-10-23-d4353-h4-replay'
files={p for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
files.update(P/n for n in ['README.md','package.py','verify_archive.py'])
out=P/'publication';out.mkdir(exist_ok=True)
target=out/'h4-evidence.tar.xz';manifest={}
with lzma.open(target,'wb',preset=6) as compressed:
 with tarfile.open(fileobj=compressed,mode='w|') as archive:
  for path in sorted(files):
   data=path.read_bytes();name=str(path.relative_to(ROOT))
   info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644
   archive.addfile(info,io.BytesIO(data))
   manifest[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
data=target.read_bytes()
meta={'members':len(files),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'files':manifest}
(out/'archive.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps({k:v for k,v in meta.items() if k!='files'}))
