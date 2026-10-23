"""Add only narrow missing-executable observation recovery to exact d4353."""
import ast,difflib,hashlib,json
from pathlib import Path
from lzpack import pack,decode
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def fn(s,name):return ast.get_source_segment(s,next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name))
def key(s):return ast.dump(ast.parse(s),include_attributes=False)
BRANCH='''  if function["tool"] == "exec" and message.startswith("BitGN HTTP 404: "):
    try:
      detail = json.loads(message[len("BitGN HTTP 404: "):])
    except (ValueError, TypeError):
      return None
    if (isinstance(detail, dict) and detail.get("code") == "not_found"
        and isinstance(detail.get("message"), str)
        and detail["message"].startswith("runtime tool not found:")):
      return {"lookup_error": {"status": 404, "code": "not_found", "detail": detail},
          "unavailable_tool": function.get("path", ""),
          "guidance": "This executable is unavailable; the runtime did not run it. "
                      "Exec is not a shell. Use native tree/list/find/search/read actions "
                      "to discover and read records, or discover supported /bin tools. "
                      "Do not repeat this executable or infer missing records from this error."}
    return None
'''
def transform(s):
 old=fn(s,'recoverable_lookup_error');anchor='  if message.startswith("BitGN HTTP 4")'
 assert old.count(anchor)==1
 new=old.replace(anchor,BRANCH+anchor,1);assert s.count(old)==1;s=s.replace(old,new,1)
 old='  if function["tool"] == "exec" and (result.get("exitCode") or "lookup_error" in result):'
 new='  if function["tool"] == "exec" and not result.get("unavailable_tool") and (result.get("exitCode") or "lookup_error" in result):'
 assert s.count(old)==1;s=s.replace(old,new,1)
 return s
parent=(P/'parent-readable.py').read_text();payload=(P/'parent-decoded.py').read_text();original=(P/'parent.py').read_bytes()
assert sha(original)=='588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
assert key(parent)==key(payload) and pack(payload,lazy=True).encode()==original
readable=transform(parent);decoded=transform(payload);assert key(readable)==key(decoded)
# Exactly two existing functions change; all other top-level nodes are identical.
for a,b in zip(ast.parse(parent).body,ast.parse(readable).body):
 if isinstance(a,ast.FunctionDef) and a.name in ('recoverable_lookup_error','observation'):continue
 assert ast.dump(a)==ast.dump(b)
assert len(ast.parse(parent).body)==len(ast.parse(readable).body)
# Remove the inserted branch / conjunct to prove the whole original functions remain.
assert fn(readable,'recoverable_lookup_error').replace(BRANCH,'',1)==fn(parent,'recoverable_lookup_error')
assert fn(readable,'observation').replace(' and not result.get("unavailable_tool")','',1)==fn(parent,'observation')
candidate=pack(decoded,lazy=True).encode();assert len(candidate)<=65536
files={'readable.py':readable.encode(),'decoded.py':decoded.encode(),'agent.py':candidate,'candidate.diff':''.join(difflib.unified_diff(parent.splitlines(True),readable.splitlines(True),fromfile='d4353r1',tofile='narrow-exec404')).encode()}
for n,b in files.items():(P/n).write_bytes(b)
report={'parent':'d4353r1','parent_reproduced':True,'modified_functions':['recoverable_lookup_error','observation'],'all_other_nodes_identical':True,'Delete404_original_branch_identical':True,'packed_readable_ast_equal':True,'headroom':65536-len(candidate),'files':{n:{'bytes':len(b),'sha256':sha(b)} for n,b in files.items()}}
(P/'build-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
