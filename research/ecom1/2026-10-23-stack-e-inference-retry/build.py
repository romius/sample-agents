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
 text = str(exc)
 for prefix in ("Inference outcome/cost unconfirmed: ", "TimeoutError: ", "ConnectionError: ", "ConnectionResetError: ", "ConnectionAbortedError: ", "ConnectionRefusedError: ", "RemoteDisconnected: "):
  if text.startswith(prefix):
   text = text[len(prefix):]
 http = re.match(r"^(?:OpenRouter )?HTTP [0-9]{3}(?::| |$)", text)
 if http:
  text = text[http.end():].strip()
  if text.startswith("{"):
   try:
    body = json.loads(text)
   except (ValueError, TypeError):
    return False
   error = body.get("error") if isinstance(body, dict) else None
   text = error.get("message", "") if isinstance(error, dict) else ""
   if not isinstance(text, str):
    return False
 return re.match(r"(?i)^(?:(?:cancelled|canceled)(?:$|[: ])|(?:sandbox )?(?:job|request) (?:was )?(?:cancelled|canceled)\\b|cancellation requested(?:$|[: ]))", text) is not None
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

# Independent comparison: one guest owner for explicitly recognized transport
# failures. 429 remains SDK-owned; exhausted main inference never nests retries
# or starts the separate forced-report request.
guest=P/'guest-owned';guest.mkdir(exist_ok=True)
assert source.count('bitgn.llm(')==4
guest_source=source.replace('bitgn.llm(', 'inference_call(')
guest_source=guest_source.replace('def normalize_action(function):',(P/'guest_retry.py').read_text()+'\ndef normalize_action(function):',1)
ast.parse(guest_source)
assert guest_source.count('bitgn.llm(')==1 and guest_source.count('inference_call(')==5
assert definition(guest_source,'dispatch')==definition(parent,'dispatch')
assert definition(guest_source,'recoverable_lookup_error')==definition(parent,'recoverable_lookup_error')
guest_packed=(header+'exec(_lz("'+base64.b85encode(ns['lz'](guest_source.encode('ascii'))).decode()+'"))\n').encode()
check={};exec(guest_packed.decode().replace('exec(_lz(', '_OUT=(_lz(',1),check)
assert check['_OUT']==guest_source and len(guest_packed)<=65536
(guest/'readable.py').write_text(guest_source)
(guest/'agent.py').write_bytes(guest_packed)
(guest/'candidate.diff').write_text(''.join(difflib.unified_diff(parent.splitlines(True),guest_source.splitlines(True),fromfile='d3909r1/readable.py',tofile='single-guest-owner/readable.py')))
guest_manifest=dict(parent='d3909r1',scope='Single guest inference retry owner, maximum3 recognized transient attempts; SDK-only429; not yet evaluated',
    no_exec404_change=True,no_action_dispatch_change=True,headroom=65536-len(guest_packed),packed_readable_equal=True,
    files={n:dict(bytes=(guest/n).stat().st_size,sha256=hashlib.sha256((guest/n).read_bytes()).hexdigest()) for n in ['readable.py','agent.py','candidate.diff']})
(guest/'manifest.json').write_text(json.dumps(guest_manifest,indent=2)+'\n')
print(json.dumps(guest_manifest))
