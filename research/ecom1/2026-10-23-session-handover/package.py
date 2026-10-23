from pathlib import Path
import hashlib,io,json,lzma,tarfile
P=Path(__file__).resolve().parent;R=P.parent
names=['2026-10-23-d6729-full100-results','2026-10-23-d6808-full100-results','2026-10-23-null-final-effort-diagnostic','2026-10-23-null-effort-review','2026-10-23-null-effort-adjudication','2026-10-23-d4353-output-boundary-controls','2026-10-23-output-controls-publication']
members={}
for name in names:
 for f in sorted((R/name).rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts and f.name!='evidence.tar.xz':members[str(f.relative_to(R))]=f.read_bytes()
for name in ['SESSION-HANDOVER.md','OVERNIGHT-STATUS.md','2026-10-23-stack-e-integration-plan/PLAN.md','2026-10-23-output-boundaries-publication/brain-receipt.json','2026-10-23-output-boundaries-publication/finding.md']:
 members[name]=(R/name).read_bytes()
for f in sorted(P.iterdir()):
 if f.is_file() and f.name not in ['evidence.tar.xz','archive-manifest.json','brain-receipt.json','GIT.txt']:members[str(f.relative_to(R))]=f.read_bytes()
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w',format=tarfile.PAX_FORMAT) as t:
 for n,data in sorted(members.items()):
  info=tarfile.TarInfo(n);info.size=len(data);info.mode=0o644;info.mtime=0;t.addfile(info,io.BytesIO(data))
raw=lzma.compress(b.getvalue(),preset=9);(P/'evidence.tar.xz').write_bytes(raw)
r={'members':len(members),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'files':{n:hashlib.sha256(v).hexdigest() for n,v in members.items()}}
(P/'archive-manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='files'}))
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as t:
 assert all(hashlib.sha256(t.extractfile(n).read()).hexdigest()==h for n,h in r['files'].items())
print('All archived members verified against source bytes')
