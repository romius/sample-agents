import lzma,hashlib,io,json,tarfile
from pathlib import Path
p=Path(__file__).resolve().parent
files=sorted(x for x in p.rglob('*') if x.is_file() and not any(y in ('publication','__pycache__') for y in x.relative_to(p).parts))
out=p/'publication';out.mkdir(exist_ok=True)
buf=io.BytesIO()
with lzma.LZMAFile(buf,mode='wb',preset=6) as gz:
 with tarfile.open(fileobj=gz,mode='w') as tar:
  for f in files:
   data=f.read_bytes();info=tarfile.TarInfo(str(f.relative_to(p)));info.size=len(data);info.mode=0o644;tar.addfile(info,io.BytesIO(data))
data=buf.getvalue();(out/'complete.tar.xz').write_bytes(data)
meta={'members':len(files),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'files':{str(x.relative_to(p)):{'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in files}}
(out/'archive.json').write_text(json.dumps(meta,indent=2)+'\n');print({k:v for k,v in meta.items() if k!='files'})
