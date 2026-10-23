"""Independent archive/seal verification and isolated cross-runtime repack; no agent tests."""
import hashlib, json, pathlib, subprocess, tarfile, tempfile
P=pathlib.Path(__file__).resolve().parent
ROOT=P.parents[3]
archive=P/'complete.tar.gz';data=archive.read_bytes()
expected='e19207c4e4373c516f5e470c7ad3b1a0dd159924e6abc66da3cafc4be8600ebd'
assert len(data)==1187491 and hashlib.sha256(data).hexdigest()==expected
assert data[:10]==bytes.fromhex('1f8b08000000000002ff')
base=pathlib.Path(tempfile.mkdtemp(prefix='d4353-ocr-archive-independent-'))
with tarfile.open(archive,'r:gz') as tar:
 members=tar.getmembers();assert len(members)==495
 names=[m.name for m in members];assert len(names)==len(set(names)) and names==sorted(names,key=lambda n:pathlib.PurePosixPath(n).parts)
 for m in members:
  path=pathlib.PurePosixPath(m.name)
  assert not path.is_absolute() and '..' not in path.parts and m.isfile()
  assert path.parts[:2]==('research','ecom1') and path.parts[2] in ('2026-10-23-d4353-record-review','2026-10-23-d4353-ocr-repair')
  assert m.uid==m.gid==m.mtime==0 and m.mode==0o644 and not m.uname and not m.gname
  out=base/m.name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(tar.extractfile(m).read())
port=base/'research/ecom1/2026-10-23-d4353-ocr-repair'
record=base/'research/ecom1/2026-10-23-d4353-record-review'
seal=port/'BUNDLE-SHA256SUMS.json';manifest=json.loads(seal.read_text());assert len(manifest)==494
assert set(names)==set(manifest)|{str(seal.relative_to(base))}
for name,pin in manifest.items():
 raw=(base/name).read_bytes();assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256'],name
 assert raw==(ROOT/name).read_bytes(),('working tree differs',name)
record_seal=json.loads((record/'SHA256SUMS.json').read_text());assert len(record_seal)==440
for name,pin in record_seal.items():
 raw=(record/name).read_bytes();assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256'],name
prior=json.loads((port/'independent-build-verification.json').read_text())
for name,pin in prior['tested_files'].items():
 raw=(port/name).read_bytes();assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256'],name
assert hashlib.sha256((port/'agent.py').read_bytes()).hexdigest()=='420e904a4cb502221f8609f99bd0f62370deda775abb41b5be9880042f0b7bf8'
assert (port/'parent.py').read_bytes()==(record/'upstream/agent.py').read_bytes()
runtimes=['/usr/bin/python3','/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python']
# Use configured local Python3.12 explicitly; /usr/bin/python3 can vary by host.
runtimes[0]=subprocess.check_output(['which','python3'],text=True).strip()
repack=[]
for executable in runtimes:
 result=subprocess.run([executable,str(port/'package_bundle.py')],capture_output=True,text=True)
 assert result.returncode==0,result.stderr
 packed=(port/'publication/complete.tar.gz').read_bytes();assert packed==data
 assert (port/'BUNDLE-SHA256SUMS.json').read_bytes()==seal.read_bytes()
 version=subprocess.check_output([executable,'--version'],text=True).strip()
 repack.append({'python':version,'identical_archive_bytes':True,'stdout':result.stdout.strip()})
for name,pin in manifest.items():assert hashlib.sha256((base/name).read_bytes()).hexdigest()==pin['sha256'],('repack changed input',name)
assert seal.read_bytes()==(P.parent/'BUNDLE-SHA256SUMS.json').read_bytes()
out={'status':'PASS','archive':str(archive.name),'sha256':expected,'bytes':len(data),'members':495,'bundle_manifest_entries':494,'record_seal_entries':440,'regular_files_only':True,'safe_paths_unique_sorted':True,'metadata_normalized':True,'all_members_match_current_reviewed_tree':True,'prior_tested_source_and_report_pins_unchanged':True,'candidate_parent_relationship_verified':True,'cross_runtime_repacks':repack,'tests_repeated':False,'reason_no_test_repeat':'Extracted source/fixtures/reports exactly match independently reproduced 300parser+112whole-agent tree; only reviewed documentation and independent reviews/packager were added.','temporary_extraction':str(base)}
(P/'independent-archive-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='cross_runtime_repacks'},indent=2))
