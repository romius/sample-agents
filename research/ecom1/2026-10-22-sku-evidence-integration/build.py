"""Pinned observation-only integration; pending lineage, not a verified record."""
import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARENT = ROOT / '2026-10-22-inventory-integration'
source = (PARENT / 'readable.py').read_text()
sha = lambda value: hashlib.sha256(value).hexdigest()
assert sha(source.encode()) == 'aef93a8c2b25feeb097e70a063d5ffff6c15f52622a3e4e058859901b0a921e1'
scope = (HERE / 'scope.py').read_text()
helper = (ROOT / '2026-10-22-sku-evidence-review/bounded_lookup_evidence.py').read_text()
old = "evidence={'pool_complete':False"
assert helper.count(old) == 1
helper = helper.replace(old, "evidence={'request_description':query,'query_source':'original SKU-only request','pool_complete':False")
candidate = source.replace('def world_tool(function):', scope + '\n' + helper + '\n\ndef world_tool(function):', 1)
old = '''    return {"matches": views,
        "indexed_products": len(WORLD["products"]),
        "note": "Read or cite the exact paths. Several close matches may mean the request is ambiguous."}'''
new = '''    result = {"matches": views,
        "indexed_products": len(WORLD["products"]),
        "note": "Read or cite the exact paths. Several close matches may mean the request is ambiguous."}
    description = sku_lookup_description(INSTRUCTION)
    if description is not None:
      try:
        return bounded_lookup_evidence(result, description, WORLD["products"], "sku_lookup")
      except Exception:
        return result
    return result'''
assert candidate.count(old) == 1
candidate = candidate.replace(old, new)
parent_functions = {n.name: n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
child_functions = {n.name: n for n in ast.parse(candidate).body if isinstance(n, ast.FunctionDef)}
changed = [name for name, node in parent_functions.items() if ast.dump(node) != ast.dump(child_functions[name])]
assert changed == ['world_tool'], changed
mini = {}
exec((ROOT / '2026-10-22-record-integration/pack5h.py').read_text().replace('hoist_literals=True', 'hoist_literals=False'), mini)
prepack = mini['mini'](candidate).encode('ascii', 'backslashreplace').decode()
packer = runpy.run_path(str(ROOT / '2026-10-22-huffman-packing-review/pack.py'))
packed = packer['pack'](prepack)
assert len(packed.encode()) <= 65536
for name, text in [('readable.py', candidate), ('prepack.py', prepack), ('agent.py', packed)]:
    (HERE / name).write_text(text)
manifest = dict(verified_baseline='d3200r2', source_parent='d5204r1 (pending, not a record)',
    hypothesis='Original-request sibling evidence helps SKU resolution without choosing a product or rewriting outcomes.',
    changed_existing_functions=changed, new_functions=['sku_lookup_description', 'bounded_lookup_evidence'],
    bytes=len(packed.encode()), headroom=65536-len(packed.encode()),
    source_sha256=sha(packed.encode()), readable_sha256=sha(candidate.encode()), prepack_sha256=sha(prepack.encode()),
    status='Not submitted; validation results are stored in separate JSON files',
    limits='No measured LLM outcome improvement. Source parent has independent ungraded changes. Scope rejects unsupported syntax and known action verbs; not a complete semantic intent classifier or authorization boundary.')
(HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(json.dumps(manifest, indent=2))
