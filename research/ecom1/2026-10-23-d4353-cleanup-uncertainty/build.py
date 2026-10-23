"""Stop deterministic cleanup on the first unconfirmed deletion; exact d4353."""
import ast, difflib, hashlib, json
from pathlib import Path
import lzpack
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
norm=lambda s:ast.dump(ast.parse(s),include_attributes=False)
def decode(s):
 ns={};exec(s[:s.index('exec(_lz(')],ns)
 return ns['_lz'](s.split('exec(_lz("',1)[1].split('"))',1)[0])
parent=(P/'parent-readable.py').read_text();packed=(P/'parent.py').read_text();payload=decode(packed)
assert sha(packed.encode())=='588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
assert sha(parent.encode())=='f898132a754187b0052a637e1ca4caaccdd3ac46f72df80bc11d2b37b3737d0b'
assert sha((P/'lzpack.py').read_bytes())=='d93f463bd68d03438854f283ef7c478d72a8de236e71eba27a6bb10a7d50e02a'
assert lzpack.pack(payload,lazy=True)==packed and norm(payload)==norm(parent)
old='            print("i2c cleanup: delete failed", p, str(exc)[:120])\n'
new=old+'''            return {"message": "Cleanup stopped: deletion outcome unconfirmed for " + p
                    + ". Confirmed deleted paths:" + ("\\n" + "\\n".join(done) if done else " none"),
                    "outcome": "OUTCOME_ERR_INTERNAL", "refs": [root, "/docs/security.md"],
                    "why": "stopped after unconfirmed Delete; no retry"}
'''
assert parent.count(old)==1 and payload.count(old)==1
readable=parent.replace(old,new,1);portable=payload.replace(old,new,1)
assert norm(readable)==norm(portable)
agent=lzpack.pack(portable,lazy=True)
assert norm(decode(agent))==norm(readable) and len(agent.encode())<=65536
for n,s in [('readable.py',readable),('portable.py',portable),('agent.py',agent),('parent-decoded.py',payload)]: (P/n).write_text(s)
(P/'candidate.diff').write_text(''.join(difflib.unified_diff(parent.splitlines(True),readable.splitlines(True),fromfile='d4353r1',tofile='cleanup-uncertainty')))
meta={'parent':'d4353r1','change':'Only i2c_cleanup exception handling: report confirmed prefix and uncertain path, return internal error immediately, no retry/fallback/later deletions. Healthy success unchanged.','bytes':len(agent.encode()),'sha256':sha(agent.encode()),'headroom':65536-len(agent.encode()),'exact_parent_repack':True,'readable_packed_ast_equal':True,'evaluation':'none'}
(P/'build-result.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
