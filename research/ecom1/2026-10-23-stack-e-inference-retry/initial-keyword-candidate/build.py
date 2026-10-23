"""Bounded SDK-owned inference retry experiment on exact d3909r1 only."""
import ast
import base64
import difflib
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent
UP=P.parent/'2026-10-23-stack-e-record-review/upstream'
parent=(UP/'readable.py').read_text()
packed=(UP/'agent.py').read_bytes()
assert hashlib.sha256(packed).hexdigest()=='56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c'
source=parent
def replace(old,new):
    global source
    assert source.count(old)==1,old
    source=source.replace(old,new,1)

replace('def normalize_action(function):', '''def inference_cancelled(exc):
 return re.search(r"(?i)\\b(?:cancelled|canceled|cancellation)\\b", str(exc)) is not None
def normalize_action(function):''')
replace(' except Exception as exc:\n  print("llm-guard: router",', ' except Exception as exc:\n  if inference_cancelled(exc):\n   raise\n  print("llm-guard: router",')
replace('    except Exception:\n        return None\n    a, b = body.find', '    except Exception as exc:\n        if inference_cancelled(exc):\n            raise\n        return None\n    a, b = body.find')
replace('        except Exception as exc:\n            print("i2c:", name,', '        except Exception as exc:\n            if inference_cancelled(exc):\n                raise\n            print("i2c:", name,')
replace(' except Exception as exc:\n  print("i2c: dispatch failed, falling back",', ' except Exception as exc:\n  if inference_cancelled(exc):\n   raise\n  print("i2c: dispatch failed, falling back",')
replace('answered = False\ninvalid_steps = 0', 'answered = False\ninference_failed = False\ninvalid_steps = 0')
replace(''' except Exception as exc:
  print("llm-guard:", str(exc)[:200])
  invalid_steps += 1
  if invalid_steps >= 3:
   break
  continue
 choice = response["choices"][0]''', ''' except Exception as exc:
  if inference_cancelled(exc):
   raise
  print("llm-guard:", str(exc)[:200])
  inference_failed = True
  break
 choice = response["choices"][0]''')
replace('if not answered:\n messages.append({"role": "user", "content": "Stop working now.', 'if not answered and not inference_failed:\n messages.append({"role": "user", "content": "Stop working now.')
replace(' except (ValueError, KeyError, IndexError, TypeError, RuntimeError) as exc:\n  print("Forced report failed",', ' except (ValueError, KeyError, IndexError, TypeError, RuntimeError) as exc:\n  if inference_cancelled(exc):\n   raise\n  print("Forced report failed",')
replace(' bitgn.answer("The sample reached its 30-step limit without completing the task.",', ' bitgn.answer("Inference failed; no further model request was issued." if inference_failed else "The sample reached its 30-step limit without completing the task.",')
ast.parse(source)
def definition(src,name):
    node=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return ast.get_source_segment(src,node)
assert definition(source,'recoverable_lookup_error')==definition(parent,'recoverable_lookup_error')
assert definition(source,'dispatch')==definition(parent,'dispatch')
builder=(UP/'build_e.py').read_text()
ns={};exec(definition(builder,'lz'),ns)
header=packed.decode().split('exec(_lz("',1)[0]
candidate=(header+'exec(_lz("'+base64.b85encode(ns['lz'](source.encode('ascii'))).decode()+'"))\n').encode()
check={};exec(candidate.decode().replace('exec(_lz(', '_OUT=(_lz(',1),check)
assert check['_OUT']==source and len(candidate)<=65536
for name,data in [('parent.py',packed),('parent-readable.py',parent.encode()),('parent-build.py',builder.encode()),('readable.py',source.encode()),('agent.py',candidate)]:
    (P/name).write_bytes(data)
(P/'candidate.diff').write_text(''.join(difflib.unified_diff(parent.splitlines(True),source.splitlines(True),fromfile='d3909r1/readable.py',tofile='sdk-owner/readable.py')))
manifest=dict(parent='d3909r1',scope='SDK-only retry owner; no new guest transient retry; cancellation propagation; suppress forced inference after main inference error',
    no_exec404_change=True,no_action_dispatch_change=True,headroom=65536-len(candidate),packed_readable_equal=True,
    files={n:dict(bytes=(P/n).stat().st_size,sha256=hashlib.sha256((P/n).read_bytes()).hexdigest()) for n in ['parent.py','parent-readable.py','parent-build.py','readable.py','agent.py','candidate.diff']})
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest))
