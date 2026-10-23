import ast, hashlib, json, subprocess, tempfile
from pathlib import Path
import lzpack

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def function(src,name):
 t=ast.parse(src);n=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name==name)
 return ast.get_source_segment(src,n)
def decode(s):
 ns={};exec(s[:s.index('exec(_lz(')],ns)
 return ns['_lz'](s.split('exec(_lz("',1)[1].split('"))',1)[0])
def normalized(s):return ast.dump(ast.parse(s),include_attributes=False)
assert sha('record_agent.py')=='1e6a0ae3505593c380fbc1d3010295cef58e2b2a7a8aaf0cfe6a47da8591a86f'
assert sha('record_readable.py')=='481491dc90e3f959838f11bfc9a4f877f7568120dc67de7ae2324b84e5356684'
# The historical record uses renamed identifiers and hoisted literals; its packer is checked separately.
# Reconstruct the integration donor from the strongest verified record and the reviewed patch.
with tempfile.TemporaryDirectory() as tmp:
 rebuilt=Path(tmp)/'parent.py'
 subprocess.run(['patch','-s','-o',str(rebuilt),'record_readable.py','record-to-integration-parent.patch'],check=True)
 assert rebuilt.read_bytes()==Path('parent_readable.py').read_bytes()
parent=Path('parent_readable.py').read_text()
packed_parent=Path('parent_agent.py').read_text()
assert sha('parent_agent.py')=='588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
assert sha('parent_readable.py')=='f898132a754187b0052a637e1ca4caaccdd3ac46f72df80bc11d2b37b3737d0b'
assert normalized(parent)==normalized(decode(packed_parent))
assert sha('retry_donor.py')=='5c9fd63873d8c709ed6e74fbc7a444a3bbeeeb76ccb448e4b6360652c4f955b8'
assert sha('lzpack.py')=='d93f463bd68d03438854f283ef7c478d72a8de236e71eba27a6bb10a7d50e02a'
assert sha('recovery_donor.py')=='93c84f03c11cc567510510c53d49d124af02272127ac5b28d6a6d9e785470892'
retry=function(Path('retry_donor.py').read_text(),'MSR')
assert 'def MSR' not in parent
assert parent.count('bitgn.llm(')==4
source=parent.replace('bitgn.llm(', 'MSR(')
cleanup_route='I2C_MODULES = [\n ["cleanup", i2c_cleanup],\n ["stock_butnot", i2c_stock_butnot]\n]'
assert source.count(cleanup_route)==1
source=source.replace(cleanup_route,'I2C_MODULES = [["stock_butnot", i2c_stock_butnot]]')
source=source.replace('def normalize_action(',retry+'\n\ndef normalize_action(',1)
# Port only the explicit missing-executable branch, preserving the record's Delete-404 containment.
old='  if message.startswith("BitGN HTTP 4") and not message.startswith("BitGN HTTP 404: "):'
repair=Path('recovery_donor.py').read_text()
fn=function(repair,'recoverable_lookup_error')
branch=fn[fn.index('  if function["tool"] == "exec"'):fn.index(old)]
assert source.count(old)==1
source=source.replace(old,branch+old)
old='if function["tool"] == "exec" and (result.get("exitCode") or "lookup_error" in result):'
assert source.count(old)==1
source=source.replace(old,'if function["tool"] == "exec" and not result.get("unavailable_tool") and (result.get("exitCode") or "lookup_error" in result):')
Path('readable.py').write_text(source)
# LZ uses latin-1 source. AST unparse preserves constants and escapes Unicode deterministically.
portable=ast.unparse(ast.parse(source)).encode('ascii','backslashreplace').decode()
assert normalized(portable)==normalized(source)
packed=lzpack.pack(portable,lazy=True)
assert normalized(decode(packed))==normalized(source)
assert len(packed.encode())<=65536
Path('agent.py').write_text(packed)
changes=[]
a=ast.parse(parent).body;b=ast.parse(source).body
assert len(b)==len(a)+1
b=[n for n in b if not(isinstance(n,ast.FunctionDef) and n.name=='MSR')]
for n,m in zip(a,b):
 if ast.dump(n)!=ast.dump(m):changes.append(getattr(n,'name',type(n).__name__))
assert set(changes)=={'route_policy_docs','recoverable_lookup_error','observation','i2c_llm_narrow','Assign','For','If'},changes
manifest={'parent':'d4353r1/d4354r1 on d3200r2','retry_donor':'d4445r1 MSR exact AST','recovery_donor':'d3513r1 explicit missing Exec branch only','sources':{f:sha(f) for f in ['parent_agent.py','parent_readable.py','retry_donor.py','lzpack.py']},'agent_sha256':sha('agent.py'),'bytes':len(packed.encode()),'changed_parent_nodes':changes,'all_other_parent_nodes_preserved':True,'four_llm_sites_wrapped':True,'delete_404_preserved':True}
Path('manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
