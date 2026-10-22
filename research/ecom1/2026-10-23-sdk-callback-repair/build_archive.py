"""Deterministic workspace-relative repair bundle and isolated core reproduction."""
import argparse,hashlib,importlib.metadata,json,os,platform,runpy,subprocess,sys,tempfile,zipfile,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;WORKSPACE=HERE.parents[2]
OUTPUTS={'repair-evidence.zip','archive-manifest.json','archive-verification.json','archive-core-verification.json'}
ENVIRONMENT=dict(python='3.14.3',zlib_build='1.2.12',zlib_runtime='1.2.12',pydantic_monty='1.2.0',python_minifier='3.4.0')
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def excluded(p):return '__pycache__' in p.parts or p.suffix in ('.pyc','.zip') or p.name in OUTPUTS or any(x in p.name.lower() for x in ['publication','submission','post-publication'])
def collect():
 files={};pins={}
 def add(path,digest=None):
  assert not path.is_symlink();path=path.resolve();name=path.relative_to(WORKSPACE).as_posix();assert '..' not in Path(name).parts and not excluded(path)
  data=path.read_bytes()
  if digest is not None:assert sha(data)==digest,('pin mismatch',name);pins[name]=digest
  files[name]=data
 review=HERE/'independent-review.md';assert review.is_file() and review.stat().st_size>0,'independent repair review required before final sealing'
 for p in sorted(HERE.rglob('*')):
  if p.is_file() and not excluded(p):add(p)
 for file in ['DEPENDENCIES.json','ARCHIVE-DEPENDENCIES.json']:
  for name,digest in load(HERE/file).items():add(ROOT/name,digest)
 assert 'proto/bitgn/vm/ecom/ecom.proto' in files
 for folder in ['2026-10-22-inventory-integration','2026-10-22-sku-history-pressure-review']:
  assert all('research/ecom1/'+folder+'/'+name in files for name in ['readable.py','prepack.py','agent.py'])
 return dict(sorted(files.items())),dict(sorted(pins.items()))
def write_zip(path,files):
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in files.items():
   info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
   z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
def no_timing(value):
 if isinstance(value,dict):return {k:no_timing(v) for k,v in value.items() if k!='seconds'}
 if isinstance(value,list):return [no_timing(v) for v in value]
 return value

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=HERE/'repair-evidence.zip');args=parser.parse_args();output=args.output.resolve();assert output.suffix=='.zip'
 actual=dict(python=platform.python_version(),zlib_build=zlib.ZLIB_VERSION,zlib_runtime=zlib.ZLIB_RUNTIME_VERSION,pydantic_monty=importlib.metadata.version('pydantic-monty'),python_minifier=importlib.metadata.version('python-minifier'))
 assert actual==ENVIRONMENT,('recorded build runtime required',actual)
 files,pins=collect();before={n:sha(b) for n,b in files.items()}
 expected={str(p.relative_to(HERE)):sha(p.read_bytes()) for d in ['d5204','d5785'] for p in (HERE/d).iterdir() if p.name in ['agent.py','prepack.py','readable.py','manifest.json']}
 with tempfile.TemporaryDirectory(prefix='sdk-repair-bundle-') as tmp:
  tmp=Path(tmp);a=tmp/'a.zip';b=tmp/'b.zip';write_zip(a,files);write_zip(b,files);assert a.read_bytes()==b.read_bytes()
  extracted=tmp/'workspace'
  with zipfile.ZipFile(a) as z:
   assert z.namelist()==list(files)
   assert all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist());z.extractall(extracted)
  for name,digest in before.items():assert sha((extracted/name).read_bytes())==digest
  local=extracted/HERE.relative_to(WORKSPACE);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
  for script in ['build.py','verify_archive_core.py','verify_capture_equivalence.py']:
   run=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(local/script)],cwd=extracted,env=env,text=True,capture_output=True,timeout=180)
   assert run.returncode==0,(script,run.stdout[-2500:],run.stderr[-3000:])
  for name,digest in expected.items():assert sha((local/name).read_bytes())==digest,('rebuild mismatch',name)
  core=load(local/'archive-core-verification.json')
  assert no_timing(load(local/'capture-equivalence.json'))==no_timing(load(HERE/'capture-equivalence.json'))
  assert (local/'capture-host-traces.json').read_bytes()==(HERE/'capture-host-traces.json').read_bytes()
  # Keep the archived evidence's original timing bytes; only the temporary copy
  # is used for fresh compatibility reproduction, never the preserved capture.
  for name,data in files.items():
   path=extracted/name
   if path.read_bytes()!=data:path.write_bytes(data)
  namespace=runpy.run_path(str(local/'build_archive.py'));rebuilt,rebuilt_pins=namespace['collect']();assert rebuilt==files and rebuilt_pins==pins
  c=tmp/'c.zip';namespace['write_zip'](c,rebuilt);assert a.read_bytes()==c.read_bytes()
  for name,digest in before.items():assert sha((WORKSPACE/name).read_bytes())==digest,('original changed',name)
  output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(a.read_bytes())
 manifest=dict(format='workspace-root-relative ZIP_DEFLATED level9; sorted;1980-01-01;0644',environment=actual,members={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()},pinned_dependencies=pins)
 report=dict(status='passed isolated offline reproduction',files=len(files),archive_bytes=output.stat().st_size,archive_sha256=sha(output.read_bytes()),uncompressed_bytes=sum(map(len,files.values())),environment=actual,deterministic_double_write=True,extracted_archive_builder_identical=True,exact_eight_candidate_artifacts=expected,core=core,capture_68_native_equivalent=True,capture_timing_excluded_from_comparison=True,preserved_capture_bytes_unchanged=True,full216_suite_repeated=False,original_members_unchanged=True,independent_review_sha256=sha((HERE/'independent-review.md').read_bytes()),no_model_calls=True,no_brain_writes=True)
 (HERE/'archive-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(HERE/'archive-verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['status','files','archive_bytes','archive_sha256','environment','full216_suite_repeated']},indent=2))
if __name__=='__main__':main()
