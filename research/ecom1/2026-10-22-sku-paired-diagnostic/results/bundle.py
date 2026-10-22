"""Build a deterministic evidence archive; no network or inference required."""
import hashlib,json,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
output=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/ecom1-sku-diagnostic-results.zip')
dependencies=json.loads((HERE/'DEPENDENCIES.json').read_text())
paths={p for p in HERE.rglob('*') if p.is_file() and p.name not in ['publication.json','SHA256SUMS'] and '__pycache__' not in p.parts}
paths.update((HERE/d['path']).resolve() for d in dependencies['dependency_files'])
for dependency in dependencies['dependency_files']:
    data=(HERE/dependency['path']).read_bytes()
    assert len(data)==dependency['bytes'] and hashlib.sha256(data).hexdigest()==dependency['sha256']
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
(HERE/'SHA256SUMS').write_text(''.join(h+'  '+p+'\n' for p,h in manifest.items()))
paths.add(HERE/'SHA256SUMS')
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for p in sorted(paths):
        info=zipfile.ZipInfo(str(p.relative_to(ROOT)),date_time=(1980,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
        archive.writestr(info,p.read_bytes())
print(json.dumps(dict(path=str(output),files=len(paths),bytes=output.stat().st_size,sha256=hashlib.sha256(output.read_bytes()).hexdigest())))
