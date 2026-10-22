"""Compose the reviewed receipt header and clarification-display changes on the record lineage."""
import ast,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
HEADER=HERE.parent/'2026-10-22-receipt-header-review'
BASE=HERE.parent/'2026-10-22-record-integration'
sys.path.insert(0,str(BASE))
import lzpack
sha=lambda data:hashlib.sha256(data).hexdigest()
assert sha((HEADER/'agent.py').read_bytes())=='1d8bc31179aff6845244cf366ddfcaec119cc964e57f90dd799529f37e1ebaf3'
source=(HEADER/'readable.py').read_text()
helper=(HERE/'clarification_skus.py').read_text()
assert 'def clarification_skus(' not in source
candidate=source.replace('def dispatch(function):',helper+'\n\ndef dispatch(function):',1)
old='    print("Final answer", json.dumps([message, refs]))'
assert candidate.count(old)==1
candidate=candidate.replace(old,'    message = clarification_skus(message, function["outcome"], refs)\n'+old)
a=ast.parse(source).body
b=[n for n in ast.parse(candidate).body if not(isinstance(n,ast.FunctionDef) and n.name=='clarification_skus')]
assert len(a)==len(b)
changes=[getattr(x,'name',type(x).__name__) for x,y in zip(a,b) if ast.dump(x)!=ast.dump(y)]
assert changes==['dispatch']
portable=ast.unparse(ast.parse(candidate)).encode('ascii','backslashreplace').decode()
packed=lzpack.pack(portable,lazy=True)
scope={};exec(packed[:packed.index('exec(_lz(')],scope)
decoded=scope['_lz'](packed.split('exec(_lz("',1)[1].split('"))',1)[0])
assert ast.dump(ast.parse(decoded))==ast.dump(ast.parse(candidate))
assert len(packed.encode())<=65536
(HERE/'readable.py').write_text(candidate);(HERE/'agent.py').write_text(packed)
manifest={'verified_baseline':'d3200r2 / 0.9012601','integration_parent':'d4702r1 (pending full100)',
 'header_parent':'d4848r1 (offline)', 'header_parent_sha256':sha((HEADER/'agent.py').read_bytes()),
 'candidate_sha256':sha(packed.encode()),'bytes':len(packed.encode()),'headroom':65536-len(packed.encode()),
 'changed_nodes_vs_header_parent':['clarification_skus (new)','dispatch'],
 'hypothesis':'Preserve ambiguous outcomes while displaying the actual already-cited candidate SKU values; recover damaged receipt quantity headers.',
 'readable_packed_ast_equal':True,'dependencies':{'lzpack':'d3268r2','rider_design_credit':'thingy H1d R2, d4485r1; adapted to actual product records'}}
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
