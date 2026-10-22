"""One layout normalization on exact d3909r1; preserve its packing format."""
import ast
import base64
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
SOURCE = P.parent / '2026-10-23-stack-e-record-review/upstream'
parent = (SOURCE / 'readable.py').read_text()
packed = (SOURCE / 'agent.py').read_bytes()
assert hashlib.sha256(packed).hexdigest() == '56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c'
pattern = '(?m)^[ \\t]*#[# \\t]*[sS][cC][aA][nN][lL][iI][nN][eE][ \\t]*#[# \\t]*(?=[tT][oO][tT][aA][lL] [rR][eE][qQ][uU][eE][sS][tT][eE][dD] (?:[lL][iI][nN][eE][sS]|[uU][nN][iI][tT][sS]):[ \\t]*[0-9]+[ \\t]*$)'
old = 'def crosslist_parse_ocr(text):\n    text = crosslist_text(text)\n'
new = old + '    text = re.sub(' + repr(pattern) + ", '', text)\n"
assert parent.count(old) == 1
source = parent.replace(old, new, 1)
assert source.replace(new, old, 1) == parent
ast.parse(source)

# Extract the unchanged, reviewed record packing algorithm, not its CLI build.
builder = (SOURCE / 'build_e.py').read_text()
lz = next(n for n in ast.parse(builder).body if isinstance(n, ast.FunctionDef) and n.name == 'lz')
ns = {}
exec(ast.get_source_segment(builder, lz), ns)
header = packed.decode().split('exec(_lz("', 1)[0]
blob = base64.b85encode(ns['lz'](source.encode('ascii'))).decode()
candidate = (header + 'exec(_lz("' + blob + '"))\n').encode()
check = {}
exec(candidate.decode().replace('exec(_lz(', '_OUT=(_lz(', 1), check)
assert check['_OUT'] == source
assert len(candidate) <= 65536
for name, data in [('parent.py', packed), ('parent-readable.py', parent.encode()), ('readable.py', source.encode()), ('agent.py', candidate), ('parent-build.py', builder.encode())]:
    (P / name).write_bytes(data)
manifest = {'parent': 'd3909r1', 'change': 'Normalize only hash-delimited scanline prefixes on complete anchored numeric total records; retain strict parser and duplicate/quantity checks.',
            'files': {name: {'bytes': (P / name).stat().st_size, 'sha256': hashlib.sha256((P / name).read_bytes()).hexdigest()} for name in ['parent.py', 'parent-readable.py', 'parent-build.py', 'readable.py', 'agent.py']},
            'headroom_bytes': 65536-len(candidate), 'decoded_equal': True, 'evaluation': 'none'}
(P / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
