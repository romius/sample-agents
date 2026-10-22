"""Full inventory workflow on frozen d4955; remove only proven inactive definitions."""
import ast,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-record-integration'
PARENT=HERE.parent/'2026-10-22-clarification-integration'
REVIEW=HERE.parent/'2026-10-22-inventory-review'
sys.path.insert(0,str(BASE))
import pack5h
from lzpack_dp import pack,decode
import base64

def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def function_nodes(source):return [n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)]
def inert_definition(node):
    assert not node.decorator_list and not node.args.defaults and not any(node.args.kw_defaults)
    assert node.returns is None and all(a.annotation is None for a in node.args.args+node.args.kwonlyargs+node.args.posonlyargs)

def build():
    parent=(PARENT/'readable.py').read_text()
    assert sha(parent)=='e0825037ed9c8993df78ee122e084e34a35507ddab7559dc0cc575358b0b1e44'
    assert hashlib.sha256((PARENT/'agent.py').read_bytes()).hexdigest()=='2f145f03558a944c30398ec59aabb92ea7d891e05889b1a8f348d07d11cbfb20'
    tree=ast.parse(parent)
    cleanup=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='i2c_cleanup')
    inert_definition(cleanup)
    assert not any(isinstance(n,ast.Name) and n.id=='i2c_cleanup' for n in ast.walk(tree))
    assert not any(isinstance(n,ast.Constant) and isinstance(n.value,str) and 'i2c_cleanup' in n.value for n in ast.walk(tree))
    assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ['eval','exec','globals','locals','getattr','setattr'] for n in ast.walk(tree))
    lines=parent.splitlines(keepends=True);del lines[cleanup.lineno-1:cleanup.end_lineno]
    parent_without_cleanup=''.join(lines)
    donor=(REVIEW/'upstream/d4012r1').read_text()
    assert sha(donor)=='6dfb12462ba0ef5261c7c61c46d07735fca67dec25552f3124c8b4831a8bf179'
    engine=donor[donor.index('IX_POLICIES='):donor.index('IX_RESULT=')]
    nodes=ast.parse(engine).body;removed=[]
    for name in ['ix_request','ix_policy_key']:
        definitions=[(i,n) for i,n in enumerate(nodes) if isinstance(n,ast.FunctionDef) and n.name==name]
        assert len(definitions)==2
        first,second=definitions;inert_definition(first[1])
        # Calls inside later function bodies resolve the final global definition at runtime.
        for node in nodes[first[0]+1:second[0]]:
            if isinstance(node,ast.FunctionDef):
                evaluated=node.decorator_list+node.args.defaults+[x for x in node.args.kw_defaults if x is not None]
                evaluated+=[a.annotation for a in node.args.args+node.args.kwonlyargs+node.args.posonlyargs if a.annotation is not None]
                if node.returns is not None:evaluated.append(node.returns)
                assert not any(isinstance(n,ast.Name) and n.id==name for expr in evaluated for n in ast.walk(expr))
            else:assert not any(isinstance(n,ast.Name) and n.id==name for n in ast.walk(node))
        removed.append(first[1])
    lines=engine.splitlines(keepends=True)
    for node in sorted(removed,key=lambda n:n.lineno,reverse=True):del lines[node.lineno-1:node.end_lineno]
    engine=''.join(lines)
    marker='messages = [';assert parent_without_cleanup.count(marker)==1
    before,after=parent_without_cleanup.split(marker)
    source=before+engine+'\nIX_RESULT=ix_run(bitgn.task()["instruction"],bitgn.call)\nprint("inventory-csv:",IX_RESULT)\n'
    source+='if IX_RESULT["terminal"]:\n bitgn.answer(IX_RESULT["message"],outcome=IX_RESULT["outcome"],refs=IX_RESULT["refs"])\nelse:\n'
    source+='\n'.join(' '+line if line else '' for line in (marker+after).splitlines())+'\n'
    kept=[n for n in function_nodes(parent) if n.name!='i2c_cleanup']
    added=function_nodes(source)
    assert [ast.dump(n) for n in added[:len(kept)]]==[ast.dump(n) for n in kept]
    template=(BASE/'pack5h.py').read_text().replace('hoist_literals=True','hoist_literals=False')
    ns={'__name__':'packer'};exec(template,ns)
    prepack=ns['mini'](source).encode('ascii','backslashreplace').decode()
    packed=pack(prepack)
    payload=ast.parse(packed).body[-1].value.args[0].args[0].value
    assert decode(base64.b85decode(payload)).decode('ascii')==prepack
    assert len(packed.encode())<=65536
    (HERE/'readable.py').write_text(source);(HERE/'prepack.py').write_text(prepack);(HERE/'agent.py').write_text(packed)
    manifest={'verified_baseline':'d3200r2 / 0.9012601','code_parent':'d4955r1 (pending full100)',
      'donor':'d4012r1 (Viroopa compiler + twistednegatory adapters)',
      'removed_definitions':['i2c_cleanup (unreferenced and disabled)','ix_request first definition (overwritten before use)','ix_policy_key first definition (overwritten before use)'],
      'preserved_parent_function_nodes':len(kept),'bytes':len(packed.encode()),'headroom':65536-len(packed.encode()),
      'sha256':sha(packed),'readable_sha256':sha(source),'prepack_sha256':sha(prepack),
      'packed_decodes_exactly_to_prepack':True,'packing':'python-minifier3.4.0 record settings except hoist_literals=False, then minimum-cost LZ parse with unchanged runtime stub',
      'status':'built, integration verification required; not submitted'}
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
    return manifest

if __name__=='__main__':build()
