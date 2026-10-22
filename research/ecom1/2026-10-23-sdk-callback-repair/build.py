"""Exact single-site callback successors; original submission files are read-only."""
import ast,base64,hashlib,importlib.metadata,json,runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
PARENTS={
 'd5204':('2026-10-22-inventory-integration','0cb742d544039b1d9dc4a862021ee1bfe3967c2ced8082756525e075b6c1ca67','aef93a8c2b25feeb097e70a063d5ffff6c15f52622a3e4e058859901b0a921e1'),
 'd5785':('2026-10-22-sku-history-pressure-review','832be81a5fafec378320d42f3e5697cea00197dfe9bfbb061b2073880a203765','0f7925c41f2783b6617ec7777757bec6fee5971f483159e26b32fae8082f7c41')}
OLD='IX_RESULT=ix_run(bitgn.task()["instruction"],bitgn.call)'
NEW='def ix_rpc(method,args):\n return bitgn.call(method,args)\n\nIX_RESULT=ix_run(bitgn.task()["instruction"],ix_rpc)'
def sha(b):return hashlib.sha256(b).hexdigest()
def decode(source):
 tree=ast.parse(source)
 if not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='exec' for n in tree.body[-1:][0:1] for n in ast.walk(n)):return source
 values=[];exec(source,{'exec':values.append});assert len(values)==1;return values[0]

def main():
 assert importlib.metadata.version('python-minifier')=='3.4.0'
 pins=json.loads((HERE/'DEPENDENCIES.json').read_text())
 for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
 mini={};exec((ROOT/'2026-10-22-record-integration/pack5h.py').read_text().replace('hoist_literals=True','hoist_literals=False'),mini)
 lz=runpy.run_path(str(ROOT/'2026-10-22-inventory-integration/lzpack_dp.py'))
 huff=runpy.run_path(str(ROOT/'2026-10-22-huffman-packing-review/pack.py'))
 for name,(folder,packed_pin,readable_pin) in PARENTS.items():
  parent=ROOT/folder;source=(parent/'readable.py').read_text()
  assert sha(source.encode())==readable_pin and sha((parent/'agent.py').read_bytes())==packed_pin
  assert source.count(OLD)==1 and 'def ix_rpc(' not in source
  fixed=source.replace(OLD,NEW)
  # Remove the one wrapper definition and revert its sole callsite: identical AST.
  reverted=fixed.replace(NEW,OLD);assert reverted==source
  before={n.name:ast.dump(n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
  after={n.name:ast.dump(n) for n in ast.parse(fixed).body if isinstance(n,ast.FunctionDef)}
  assert {k:v for k,v in after.items() if k!='ix_rpc'}==before
  prepack=mini['mini'](fixed).encode('ascii','backslashreplace').decode()
  packed=(lz if name=='d5204' else huff)['pack'](prepack)
  assert decode(packed)==prepack and len(packed.encode())<=65536
  out=HERE/name;out.mkdir(exist_ok=True)
  for filename,value in [('readable.py',fixed),('prepack.py',prepack),('agent.py',packed)]: (out/filename).write_text(value)
  report=dict(parent=name+'r1',parent_directory=folder,parent_packed_sha256=packed_pin,parent_readable_sha256=readable_pin,change='Named ix_rpc wrapper; pass ix_rpc instead of loading bitgn.call. All existing function ASTs unchanged.',bytes=len(packed.encode()),headroom=65536-len(packed.encode()),packed_sha256=sha(packed.encode()),readable_sha256=sha(fixed.encode()),prepack_sha256=sha(prepack.encode()),packed_decodes_exactly=True,packing='minimum-cost LZ' if name=='d5204' else 'Huffman over minimum-cost LZ',status='offline successor; not submitted')
  (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
