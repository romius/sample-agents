"""Package the explicit frozen member list. Never infer, submit, or alter old seals."""
import argparse, hashlib, io, json, platform, zipfile, zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[3]
ENVIRONMENT={'python':'3.14.3','zlib_build':'1.2.12','zlib_runtime':'1.2.12'}
MANIFEST=HERE/'actual-members.json'

def sha(data):return hashlib.sha256(data).hexdigest()
def collect():
    manifest=json.loads(MANIFEST.read_text())
    files={}
    for name,pin in manifest['members'].items():
        path=WORKSPACE/name
        assert not path.is_symlink() and not name.startswith('/') and '..' not in Path(name).parts,name
        assert path.suffix not in ('.zip','.pyc') and '__pycache__' not in Path(name).parts,name
        data=path.read_bytes()
        assert sha(data)==pin['sha256'] and len(data)==pin['bytes'],('member changed',name)
        files[name]=data
    files[MANIFEST.relative_to(WORKSPACE).as_posix()]=MANIFEST.read_bytes()
    return dict(sorted(files.items()))
def packed(files):
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,raw in files.items():
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return data.getvalue()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=HERE/'actual-results-evidence.zip');args=parser.parse_args()
    env={'python':platform.python_version(),'zlib_build':zlib.ZLIB_VERSION,'zlib_runtime':zlib.ZLIB_RUNTIME_VERSION}
    assert env==ENVIRONMENT,('pinned runtime required',env)
    files=collect();raw=packed(files);assert raw==packed(files)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(raw)
    print(json.dumps({'path':str(args.output),'sha256':sha(raw),'bytes':len(raw),'files':len(files),'environment':env}))
if __name__=='__main__':main()
