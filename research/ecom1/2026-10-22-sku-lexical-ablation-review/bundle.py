"""Deterministic offline-review archive, including exact source dependencies."""
import hashlib,json,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
folders=[HERE,ROOT/'2026-10-22-injection-reachability-review']
paths=set()
for folder in folders:
    local=[p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['SHA256SUMS','publication.json']]
    (folder/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(folder))+'\n' for p in sorted(local)))
    paths.update(local);paths.add(folder/'SHA256SUMS')
for pin in json.loads((HERE/'DEPENDENCIES.json').read_text()).values():
    p=ROOT/pin['path'] if '/' in pin['path'] else HERE/pin['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256']
    paths.add(p)
for pin in json.loads((folders[1]/'DEPENDENCIES.json').read_text())['inputs']:
    p=ROOT/pin['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256'];paths.add(p)
output=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/ecom1-offline-qualifier-security-review.zip')
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for path in sorted(paths):
        info=zipfile.ZipInfo(str(path.relative_to(ROOT)),date_time=(1980,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
        archive.writestr(info,path.read_bytes())
print(json.dumps(dict(path=str(output),files=len(paths),bytes=output.stat().st_size,sha256=hashlib.sha256(output.read_bytes()).hexdigest())))
