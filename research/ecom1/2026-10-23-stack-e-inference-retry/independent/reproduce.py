"""Rebuild/retest in an isolated offline copy; never rewrites author sources/results."""
import ast, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
P=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
root=Path(tempfile.mkdtemp(prefix='ecom1-retry-independent-'))/'ecom1'
q=root/P.name
shutil.copytree(P,q,ignore=shutil.ignore_patterns('independent','__pycache__'))
deps=json.loads((P/'DEPENDENCIES.json').read_text())
for rel,expected in deps.items():
 src=P.parent/rel
 assert sha(src)==expected,(rel,'dependency hash')
 dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
inputs={str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file() and 'independent' not in p.relative_to(P).parts and '__pycache__' not in p.relative_to(P).parts}
outputs=['parent.py','parent-readable.py','parent-build.py','readable.py','agent.py','candidate.diff','manifest.json','guest-owned/readable.py','guest-owned/agent.py','guest-owned/candidate.diff','guest-owned/manifest.json']
steps=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for name in ['build.py','test_native.py','test_guest.py','test_helper_whole.py']:
 r=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(q/name)],capture_output=True,text=True,env=env)
 steps.append({'script':name,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 assert r.returncode==0,steps[-1]
 if name=='build.py':
  for output in outputs:assert (q/output).read_bytes()==(P/output).read_bytes(),('build mismatch',output)
report_files=['test-results.json','fake-requests.json','guest-owned/test-results.json','guest-owned/fake-requests.json','helper-whole-results.json','helper-whole-fixture.json']
for output in report_files:
 assert (q/output).read_bytes()==(P/output).read_bytes(),('test result mismatch',output)
def functions(path):
 source=path.read_text()
 return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
parent=functions(P/'parent-readable.py');changes={}
for filename in ['readable.py','guest-owned/readable.py']:
 funcs=functions(P/filename)
 altered=sorted(name for name in parent if parent[name]!=funcs[name])
 assert altered==['i2c_dispatch','i2c_llm_narrow','route_policy_docs']
 assert set(parent)<=set(funcs)
 changes[filename]={'added':sorted(set(funcs)-set(parent)),'changed':altered,'dispatch_and_recoverable_lookup_unchanged':True}
for rel,expected in inputs.items():assert sha(P/rel)==expected,('author file changed during review',rel)
out={'status':'PASS','scope':'Offline exact isolated rebuild/native tests; no network/model/SDK backend executed','python':sys.version,'dependencies_verified':len(deps),'input_sha256':inputs,'build_files_byte_identical':outputs,'test_reports_byte_identical':report_files,'steps':steps,'function_ast_changes':changes,'temporary_copy':str(q)}
(P/'independent/reproduction.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS: isolated exact rebuild and all native controls; author files unchanged.')
