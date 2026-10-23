"""One parser change on frozen d4702r1. No submitted source is modified."""
import ast, hashlib, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-record-integration'
sys.path.insert(0,str(BASE))
import lzpack

def sha(data):return hashlib.sha256(data).hexdigest()
def normalized(source):return ast.dump(ast.parse(source))

assert sha((BASE/'agent.py').read_bytes())=='b5bf80e4eb3eb4f5ee86dfad2442606e33da8102a9edbac85222ecc395d507f8'
source=(BASE/'readable.py').read_text()
old='"C" if "ITEM QTY UNIT TOTAL" in " ".join(up.split()) else None'
new='"C" if ("ITEM QTY UNIT TOTAL" in " ".join(up.split()) or any(re.fullmatch("ITEM [A-Z0-9|]+ UNIT TOTAL", " ".join(line.split())) for line in up.splitlines())) else None'
assert source.count(old)==1
candidate=source.replace(old,new)
a=ast.parse(source).body;b=ast.parse(candidate).body
assert len(a)==len(b)
changed=[getattr(x,'name',type(x).__name__) for x,y in zip(a,b) if ast.dump(x)!=ast.dump(y)]
assert changed==['rcp_items'],changed
portable=ast.unparse(ast.parse(candidate)).encode('ascii','backslashreplace').decode()
assert normalized(portable)==normalized(candidate)
packed=lzpack.pack(portable,lazy=True)
scope={};exec(packed[:packed.index('exec(_lz(')],scope)
decoded=scope['_lz'](packed.split('exec(_lz("',1)[1].split('"))',1)[0])
assert normalized(decoded)==normalized(candidate)
assert len(packed.encode())<=65536
(HERE/'readable.py').write_text(candidate)
(HERE/'agent.py').write_text(packed)
manifest=dict(parent='d4702r1 (record d3200r2 lineage; pending full100)',
 parent_sha256=sha((BASE/'agent.py').read_bytes()),baseline='d3200r2 / 90.12601',
 hypothesis='A damaged quantity heading is still a standalone Item / Unit / Total table heading. Accept it only with the existing SKU, quantity, line-total and subtotal checks.',
 source_sha256=sha(packed.encode()),source_bytes=len(packed.encode()),changed_nodes=changed,
 readable_packed_ast_equal=True,base_directory=str(BASE.relative_to(HERE.parent)),
 lzpack_revision='d3268r2',lzpack_sha256=sha((BASE/'lzpack.py').read_bytes()))
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
