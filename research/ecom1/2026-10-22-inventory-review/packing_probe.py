"""Measure a full compiler integration; artifacts are feasibility probes, not submissions."""
import ast,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-record-integration'
PARENT=HERE.parent/'2026-10-22-clarification-integration'
sys.path.insert(0,str(BASE))
import lzpack,pack5h

def sha(data):return hashlib.sha256(data.encode()).hexdigest()
parent=(PARENT/'readable.py').read_text()
assert hashlib.sha256((PARENT/'agent.py').read_bytes()).hexdigest()=='2f145f03558a944c30398ec59aabb92ea7d891e05889b1a8f348d07d11cbfb20'
donor=(HERE/'upstream/d4012r1').read_text()
assert sha(donor)=='6dfb12462ba0ef5261c7c61c46d07735fca67dec25552f3124c8b4831a8bf179'
engine=donor[donor.index('IX_POLICIES='):donor.index('IX_RESULT=')]
marker='messages = ['
assert parent.count(marker)==1
before,after=parent.split(marker)
source=before+engine+'\nIX_RESULT=ix_run(bitgn.task()["instruction"],bitgn.call)\nprint("inventory-csv:",IX_RESULT)\n'
source+='if IX_RESULT["terminal"]:\n bitgn.answer(IX_RESULT["message"],outcome=IX_RESULT["outcome"],refs=IX_RESULT["refs"])\nelse:\n'
source+='\n'.join(' '+line if line else '' for line in (marker+after).splitlines())+'\n'
old=[n for n in ast.parse(parent).body if isinstance(n,ast.FunctionDef)]
new=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)]
assert [ast.dump(n) for n in new[:len(old)]]==[ast.dump(n) for n in old]
assert not {n.name for n in old}&{n.name for n in new[len(old):]}
out=HERE/'packing-probe';out.mkdir(exist_ok=True)
(out/'readable.py').write_text(source)
variants={'ast_only':ast.unparse(ast.parse(source)),'record_minifier':pack5h.mini(source)}
results={}
for name,variant in variants.items():
    portable=variant.encode('ascii','backslashreplace').decode()
    assert ast.dump(ast.parse(portable))==ast.dump(ast.parse(variant))
    packed=lzpack.pack(portable,lazy=True)
    ns={};exec(packed[:packed.index('exec(_lz(')],ns)
    decoded=ns['_lz'](packed.split('exec(_lz("',1)[1].split('"))',1)[0])
    assert ast.dump(ast.parse(decoded))==ast.dump(ast.parse(variant))
    (out/(name+'-prepack.py')).write_text(portable)
    (out/(name+'-agent.py')).write_text(packed)
    results[name]={'bytes':len(packed.encode()),'sha256':sha(packed),'headroom':65536-len(packed.encode()),
        'decoded_ast_equals_prepack':True,'readable_ast_equal':ast.dump(ast.parse(variant))==ast.dump(ast.parse(source))}
results['status']='Sizing experiment only. Whole-agent integration regression and minifier semantic validation remain required; not eligible for submission.'
results['pins']={'parent':'d4955r1','donor':'d4012r1','packer':'d3268r2','minifier':'python-minifier3.4.0, record pack5h d2829r1'}
(HERE/'packing-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
