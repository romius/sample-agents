import ast,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;S=P/'sources'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,v in json.loads((P/'source-pins.json').read_text()).items():assert sha(P/n)==v['sha256'] and (P/n).stat().st_size==v['bytes'],n
folders=['2026-10-22-record-integration','2026-10-22-receipt-header-review','2026-10-22-clarification-integration']
assert sha(S/folders[-1]/'agent.py')==json.loads((P/'result.json').read_text())['result']['source']['sha256']
with tempfile.TemporaryDirectory(prefix='d4955-source-build-') as tmp:
 q=Path(tmp)/'sources';shutil.copytree(S,q)
 for d in folders:
  r=subprocess.run([sys.executable,'build.py'],cwd=q/d,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
  assert r.returncode==0,(d,r.stderr,r.stdout)
  for n in ['agent.py','readable.py']:assert sha(q/d/n)==sha(S/d/n),(d,n)
a=ast.parse((S/folders[0]/'readable.py').read_text()).body;b=ast.parse((S/folders[-1]/'readable.py').read_text()).body
new=[n.name for n in b if isinstance(n,ast.FunctionDef) and n.name not in [getattr(x,'name',None) for x in a]]
b=[n for n in b if getattr(n,'name',None) not in new]
assert len(a)==len(b)
changed=[getattr(x,'name',type(x).__name__) for x,y in zip(a,b) if ast.dump(x)!=ast.dump(y)]
assert new==['clarification_skus'] and changed==['dispatch','rcp_items'],(new,changed)
report={'status':'PASS','pins':len(json.loads((P/'source-pins.json').read_text())),'exact_builds':folders,'new_functions_vs_d4702':new,'changed_nodes_vs_d4702':changed,'official_source_hash_matched':True,'runtime':sys.version,'no_live_or_model_calls':True}
(P/'source-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
