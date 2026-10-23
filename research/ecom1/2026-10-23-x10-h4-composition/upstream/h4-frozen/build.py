"""Adapt only bobcat d6929 H4 fallback to exact bare d4353, no X10."""
import ast,difflib,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def tree(s):return ast.dump(ast.parse(s),include_attributes=False)
def transform(s):
    anchor='def rcp_product(fragment, cents):\n'
    helper='def rcp_drop1(a, b):\n  return len(a) == len(b) + 1 and any(a[:i] + a[i + 1:] == b for i in range(len(a)))\n\n\n'
    assert s.count(anchor)==1
    s=s.replace(anchor,helper+anchor,1)
    begin=s.index(anchor);end=s.index('\ndef rcp_store(',begin)
    original=s[begin:end]
    target='  return hits[0] if len(hits) == 1 else None'
    fallback='  if not hits and cut and len(key) >= 10:\n    hits = [p for p in WORLD["products"] if p.get("price_cents") == cents and rcp_drop1(ocr_key(p.get("sku", ""))[:len(key) + 1], key)]\n'
    assert original.count(target)==1
    return s[:begin]+original.replace(target,fallback+target)+s[end:]
def main():
    deps=json.loads((P/'DEPENDENCIES.json').read_text())
    for name,pin in deps['files'].items():assert sha((P/name).read_bytes())==pin['sha256'],name
    packer=runpy.run_path(str(P/'inputs/lzpack.py'));pack=packer['pack']
    parent=(P/'inputs/parent-readable.py').read_text();decoded=(P/'inputs/parent-decoded.py').read_text();raw=(P/'inputs/parent.py').read_bytes()
    assert sha(raw)=='588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
    assert tree(parent)==tree(decoded) and pack(decoded,lazy=True).encode()==raw
    readable=transform(parent);newdecoded=transform(decoded);packed=pack(newdecoded,lazy=True)
    assert tree(readable)==tree(newdecoded)
    extracted=[];exec(packed,{'exec':extracted.append});assert extracted==[newdecoded]
    assert len(packed.encode())<=65536
    # Exact AST delta: one new helper and one modified function, all other
    # top-level executable statements/functions retained in order.
    before=ast.parse(parent).body;after=ast.parse(readable).body
    assert len(after)==len(before)+1
    filtered=[n for n in after if not(isinstance(n,ast.FunctionDef) and n.name=='rcp_drop1')]
    changed=[]
    for a,b in zip(before,filtered):
        if ast.dump(a,include_attributes=False)!=ast.dump(b,include_attributes=False):
            assert isinstance(a,ast.FunctionDef) and a.name==b.name=='rcp_product';changed.append(a.name)
    assert changed==['rcp_product']
    outputs={'readable.py':readable,'decoded.py':newdecoded,'agent.py':packed,'candidate.diff':''.join(difflib.unified_diff(parent.splitlines(True),readable.splitlines(True),fromfile='exact-d4353r1',tofile='d4353-H4-only'))}
    for name,text in outputs.items():(P/name).write_text(text)
    report={'status':'offline adapted H4 only, not evaluated','parent':'d4353r1','parent_rebuild_exact':True,'parent_sha256':sha(raw),'community_source':'d6929r1 record_h4.diff; context adapted because parent has no X10/fuzzy fallback','AST_changes':['new rcp_drop1','rcp_product fallback before original unique return'],'packed_bytes':len(packed.encode()),'files':{n:{'bytes':len(t.encode()),'sha256':sha(t.encode())} for n,t in outputs.items()}}
    (P/'build-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'packed_bytes':len(packed.encode()),'sha256':sha(packed.encode())}))
if __name__=='__main__':main()
