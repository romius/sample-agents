"""Apply existing history bound at the forced-report call; separate successor."""
import ast,hashlib,json,runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
parent=ROOT/'2026-10-22-sku-evidence-integration/readable.py'
source=parent.read_text();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(source.encode())=='e46d7d860a1b4c6dc1f7a876a2ee56ecde2df8bffdac041bc8562e71572e503e'
old='''   try:
     response = MSR(MODEL, messages, max_completion_tokens=2048,
               reasoning={"effort": "medium"}, temperature=0)'''
new='''   try:
     while len(json.dumps(messages).encode("utf-8")) > 56000 and len(messages) > bootstrap_count + 2:
       messages = messages[:bootstrap_count] + messages[bootstrap_count + 2:]
     response = MSR(MODEL, messages, max_completion_tokens=2048,
               reasoning={"effort": "medium"}, temperature=0)'''
assert source.count(old)==1
fixed=source.replace(old,new)
old_funcs={x.name:ast.dump(x) for x in ast.parse(source).body if isinstance(x,ast.FunctionDef)}
new_funcs={x.name:ast.dump(x) for x in ast.parse(fixed).body if isinstance(x,ast.FunctionDef)}
assert old_funcs==new_funcs
mini={};exec((ROOT/'2026-10-22-record-integration/pack5h.py').read_text().replace('hoist_literals=True','hoist_literals=False'),mini)
prepack=mini['mini'](fixed).encode('ascii','backslashreplace').decode()
packed=runpy.run_path(str(ROOT/'2026-10-22-huffman-packing-review/pack.py'))['pack'](prepack)
assert len(packed.encode())<=65536
for name,value in [('readable.py',fixed),('prepack.py',prepack),('agent.py',packed)]: (HERE/name).write_text(value)
manifest=dict(parent='d5620r1 / readable d5635r1 (offline, ungraded)',parent_readable_sha256=sha(source.encode()),
 hypothesis='Apply the same56k history window before forced report so additional catalogue evidence cannot bypass the existing normal-call bound.',
 bytes=len(packed.encode()),headroom=65536-len(packed.encode()),source_sha256=sha(packed.encode()),readable_sha256=sha(fixed.encode()),prepack_sha256=sha(prepack.encode()),
 changed_functions=[],change='Only two-line existing window copied before forced-report MSR call.',status='Separate offline successor; no paid submission',
 limitations='Does not establish model decision benefit. Bootstrap plus irreducible final messages can still exceed limits under pathological input; this preserves existing trimming semantics.')
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
