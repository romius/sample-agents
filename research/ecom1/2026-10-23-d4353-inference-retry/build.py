"""Exact d4353 retry-boundary comparison; no OCR or action-recovery changes."""
import ast, difflib, hashlib, json
from pathlib import Path
from lzpack import pack
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(s):return ast.dump(ast.parse(s),include_attributes=False)
def fn(s,name):return ast.get_source_segment(s,next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name))
def transform(s,guest=False):
    original_source=s
    # Insert catch around the call statement only: parsing and action dispatch
    # are deliberately outside this transport boundary.
    tree=ast.parse(s); edits=[]
    for n in ast.walk(tree):
        if not isinstance(n,ast.Assign) or not isinstance(n.value,ast.Call):continue
        c=n.value
        if not (isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Name) and c.func.value.id=='bitgn' and c.func.attr=='llm'):continue
        if not any(isinstance(t,ast.Name) and t.id=='response' for t in n.targets):continue
        lines=s.splitlines(True); indent=' '*n.col_offset
        original=''.join(lines[n.lineno-1:n.end_lineno])
        if any(k.arg=='max_completion_tokens' and isinstance(k.value,ast.Constant) and k.value.value==1024 for k in c.keywords):
            tail='print("llm-guard: router", str(exc)[:200])\n'+indent+'  return []\n'
        elif n.col_offset==2:
            tail='print("llm-guard: main", str(exc)[:200])\n'+indent+'  inference_failed = True\n'+indent+'  break\n'
        else:
            # Forced response: no retry/catch spans dispatch or answer side effects.
            tail='print("llm-guard: forced", str(exc)[:200])\n'+indent+'  inference_failed = True\n'+indent+'  response = {"choices": [{"message": {"content": ""}}]}\n'
        replacement=indent+'try:\n'+''.join('  '+line for line in original.splitlines(True))+indent+'except Exception as exc:\n'+indent+'  if inference_cancelled(exc):\n'+indent+'    raise\n'+indent+'  '+tail
        edits.append((n.lineno-1,n.end_lineno,replacement))
    assert len(edits)==3
    lines=s.splitlines(True)
    for start,end,replacement in sorted(edits,reverse=True):lines[start:end]=[replacement]
    s=''.join(lines)
    def replace(old,new):
        nonlocal s
        assert s.count(old)==1,old
        s=s.replace(old,new,1)
    # Edit only named helper catches using their exact source segment.
    old=fn(s,'i2c_llm_narrow')
    new=old.replace('    except Exception:\n        return None\n    a, b = body.find','    except Exception as exc:\n        if inference_cancelled(exc):\n            raise\n        return None\n    a, b = body.find',1)
    assert old!=new
    replace(old,new)
    old=fn(s,'i2c_dispatch');new=old.replace('        except Exception as exc:\n','        except Exception as exc:\n            if inference_cancelled(exc):\n                raise\n',1);replace(old,new)
    replace('  except Exception as exc:\n    print("i2c: dispatch failed, falling back",','  except Exception as exc:\n    if inference_cancelled(exc):\n      raise\n    print("i2c: dispatch failed, falling back",')
    replace('answered = False\ninvalid_steps = 0','answered = False\ninference_failed = False\ninvalid_steps = 0')
    replace('if not answered:\n  messages.append({"role": "user", "content": "Stop working now.','if not answered and not inference_failed:\n  messages.append({"role": "user", "content": "Stop working now.')
    replace('  bitgn.answer("The sample reached its 30-step limit without completing the task.",','  bitgn.answer("Inference failed; no further model request was issued." if inference_failed else "The sample reached its 30-step limit without completing the task.",')
    if guest:
        assert s.count('bitgn.llm(')==4
        s=s.replace('bitgn.llm(','inference_call(')
    helpers=(P/'cancellation.py').read_text()+'\n'+((P/'guest_retry.py').read_text()+'\n' if guest else '')
    replace('def normalize_action(function):',helpers+'def normalize_action(function):')
    for name in ('dispatch','recoverable_lookup_error','crosslist_parse_ocr','i2c_cleanup'):
        assert fn(s,name)==fn(original_source,name)
    return s
parent=(P/'parent-readable.py').read_text();decoded=(P/'parent-decoded.py').read_text();packed=(P/'parent.py').read_bytes()
assert sha(packed)=='588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
assert dump(parent)==dump(decoded)
assert pack(decoded,lazy=True).encode()==packed
results={}
for name,guest in [('sdk-only',False),('guest-owned',True)]:
    readable=transform(parent,guest);payload=transform(decoded,guest)
    assert dump(readable)==dump(payload)
    candidate=pack(payload,lazy=True).encode();assert len(candidate)<=65536
    dst=P/name;dst.mkdir(exist_ok=True)
    files={'readable.py':readable.encode(),'decoded.py':payload.encode(),'agent.py':candidate,'candidate.diff':''.join(difflib.unified_diff(parent.splitlines(True),readable.splitlines(True),fromfile='d4353r1',tofile=name)).encode()}
    for file,data in files.items():(dst/file).write_bytes(data)
    results[name]={'files':{f:{'bytes':len(b),'sha256':sha(b)} for f,b in files.items()},'headroom':65536-len(candidate)}
(P/'build-result.json').write_text(json.dumps({'parent':'d4353r1','parent_reproduced':True,'readable_payload_ast_equal':True,'unchanged_functions':['dispatch','recoverable_lookup_error','crosslist_parse_ocr','i2c_cleanup'],'candidates':results},indent=2)+'\n')
print(json.dumps(results))
