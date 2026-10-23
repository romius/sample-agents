"""Deterministic workspace-relative retry comparison bundle; bounded isolated checks."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import runpy
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
WORKSPACE=HERE.parents[2]
OUTPUTS={'retry-comparison.zip','archive-manifest.json','BUNDLE.json'}
ENVIRONMENT=dict(python='3.14.3',monty='1.2.0',zlib_build='1.2.12',zlib_runtime='1.2.12')
def sha(data):return hashlib.sha256(data).hexdigest()
def load(path):return json.loads(path.read_text())
def excluded(path):
    return '__pycache__' in path.parts or path.suffix in ('.pyc','.zip') or path.name in OUTPUTS or any('publication' in part.lower() for part in path.parts)
def collect():
    files,pins={},{}
    def add(path,digest=None):
        assert not path.is_symlink(),path
        path=path.resolve();name=path.relative_to(WORKSPACE).as_posix()
        assert not name.startswith('/') and '..' not in Path(name).parts and not excluded(path)
        data=path.read_bytes()
        if digest is not None:
            assert sha(data)==digest,('dependency mismatch',name)
            pins[name]=digest
        files[name]=data
    assert (HERE/'independent/independent-review.md').is_file(),'final independent review required'
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and not excluded(path):add(path)
    for line in (HERE/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split(maxsplit=1)
        assert sha((HERE/name).read_bytes())==digest,('original seal mismatch',name)
    dependencies=load(HERE/'DEPENDENCIES.json')
    assert len(dependencies)==14
    for name,digest in dependencies.items():add(ROOT/name,digest)
    return dict(sorted(files.items())),dict(sorted(pins.items()))
def write_zip(path,files):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in files.items():
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
            archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'retry-comparison.zip')
    args=parser.parse_args();output=args.output.resolve();assert output.suffix=='.zip'
    environment=dict(python=platform.python_version(),monty=importlib.metadata.version('pydantic-monty'),zlib_build=zlib.ZLIB_VERSION,zlib_runtime=zlib.ZLIB_RUNTIME_VERSION)
    assert environment==ENVIRONMENT,('pinned runtime required',environment)
    files,pins=collect();hashes={n:sha(b) for n,b in files.items()}
    with tempfile.TemporaryDirectory(prefix='retry-comparison-bundle-') as directory:
        directory=Path(directory);a=directory/'a.zip';b=directory/'b.zip'
        write_zip(a,files);write_zip(b,files);assert a.read_bytes()==b.read_bytes()
        extracted=directory/'workspace'
        with zipfile.ZipFile(a) as archive:
            assert archive.namelist()==list(files)
            assert all(not n.startswith('/') and '..' not in Path(n).parts for n in archive.namelist())
            archive.extractall(extracted)
        assert all(sha((extracted/n).read_bytes())==d for n,d in hashes.items())
        local=extracted/HERE.relative_to(WORKSPACE);steps=[]
        for script in ['build.py','test_helper_whole.py','independent/check-classifier.py']:
            run=subprocess.run([sys.executable,str(local/script)],cwd=extracted,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),text=True,capture_output=True,timeout=120)
            assert run.returncode==0,(script,run.stdout[-3000:],run.stderr[-3000:])
            steps.append(dict(script=script,returncode=run.returncode))
        # Source and report reproduction must be exact; do not restore over
        # drift to make the reconstructed archive appear deterministic.
        assert all(sha((extracted/n).read_bytes())==d for n,d in hashes.items())
        namespace=runpy.run_path(str(local/'build_archive.py'))
        rebuilt,rebuilt_pins=namespace['collect']();assert rebuilt==files and rebuilt_pins==pins
        c=directory/'c.zip';namespace['write_zip'](c,rebuilt);assert c.read_bytes()==a.read_bytes()
        assert all(sha((WORKSPACE/n).read_bytes())==d for n,d in hashes.items())
        output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(a.read_bytes())
    manifest=dict(format='workspace-relative ZIP_DEFLATED level9, sorted, timestamp1980-01-01,0644',environment=environment,
        members={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()},dependency_pins=pins)
    metadata=dict(status='passed isolated deterministic archive reproduction',files=len(files),archive_bytes=output.stat().st_size,archive_sha256=sha(output.read_bytes()),
        uncompressed_bytes=sum(map(len,files.values())),environment=environment,dependency_pins=14,
        sources={label:load(HERE/path)['files']['agent.py'] for label,path in [('SDK-only','manifest.json'),('bounded_guest','guest-owned/manifest.json')]},
        original_seal_sha256=sha((HERE/'SHA256SUMS').read_bytes()),independent_review_sha256=sha((HERE/'independent/independent-review.md').read_bytes()),
        source_build_byte_identical=True,helper24_reproduced=True,independent_classifier18_reproduced=True,
        full194_suite_repeated_for_packaging=False,all_archived_reports_unchanged=True,extracted_builder_identical=True,deterministic_double_write=True,
        no_paid_calls=True,no_Brain_writes=True,no_live_agent_edit=True,OCR_integration=False,steps=steps,
        scope='Mechanism comparison only; independent review is not a score claim or automatic candidate preference',
        preserved_forced_branch_wording='Parent can report30-step limit after3malformed main replies and forced inference failure')
    (HERE/'archive-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (HERE/'BUNDLE.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({k:metadata[k] for k in ('status','files','archive_bytes','archive_sha256')},indent=2))
if __name__=='__main__':main()
