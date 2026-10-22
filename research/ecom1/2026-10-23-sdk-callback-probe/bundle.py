"""Reproducible probe evidence archive; no live calls."""
import hashlib,json,platform,zipfile,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=Path('/tmp/ecom1-sdk-callback-probe.zip')
files=sorted(p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not any(s in p.name for s in ('publication','submission','archive-manifest')))
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for p in files:
        info=zipfile.ZipInfo(str(p.relative_to(HERE)),date_time=(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
        archive.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
manifest={'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'python':platform.python_version(),'zlib':zlib.ZLIB_RUNTIME_VERSION,'files':{str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(HERE/'archive-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k!='files'}))
