"""Offline bounded receipt handoff prototype; not evaluation qualified."""
import ast, difflib, hashlib, json
from pathlib import Path
from lzpack import pack
P = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
key = lambda s: ast.dump(ast.parse(s), include_attributes=False)
parent = (P / 'parent-readable.py').read_text()
payload = (P / 'parent-decoded.py').read_text()
original = (P / 'parent.py').read_bytes()
assert sha(original) == '588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
assert key(parent) == key(payload) and pack(payload, lazy=True).encode() == original
helper = (P / 'handoff.py').read_text()
def transform(s):
    edits = [
        ('def receipt_availability(instruction, identity):\n', helper + '\n\ndef receipt_availability(instruction, identity):\n  RECEIPT_PENDING.clear()\n'),
        ('    policy = " ".join((bitgn.call("Read", {"path": "/docs/availability-checks.md"}).get("content") or "").split())',
         '    policy_result = bitgn.call("Read", {"path": "/docs/availability-checks.md"})\n    policy = " ".join((policy_result.get("content") or "").split())'),
        ('    text = (bitgn.call("Read", {"path": upload}).get("content") or "") if upload else ""',
         '    upload_result = bitgn.call("Read", {"path": upload}) if upload else {}\n    text = upload_result.get("content") or ""\n    if upload and receipt_capture("/docs/availability-checks.md", policy_result):\n      if not receipt_capture(upload, upload_result):\n        RECEIPT_PENDING.clear()'),
        ('for index in range(0 if answered else MAX_STEPS):',
         'receipt_added = 0\nif not answered:\n  receipt_before = len(messages)\n  messages = receipt_handoff(messages)\n  receipt_added = len(messages) - receipt_before\n  bootstrap_count = len(messages)\nfor index in range(0 if answered else MAX_STEPS):\n  messages, bootstrap_count, receipt_added = receipt_pressure(messages, bootstrap_count, receipt_added)'),
        ('  try:\n    response = bitgn.llm(MODEL, messages, max_completion_tokens=2048,',
         '  messages, bootstrap_count, receipt_added = receipt_pressure(messages, bootstrap_count, receipt_added)\n  try:\n    response = bitgn.llm(MODEL, messages, max_completion_tokens=2048,'),
    ]
    for a, b in edits:
        assert s.count(a) == 1, (a, s.count(a))
        s = s.replace(a, b, 1)
    return s
readable, decoded = transform(parent), transform(payload)
assert key(readable) == key(decoded)
candidate = pack(decoded, lazy=True).encode()
unpacked = []
exec(candidate.decode(), {'exec': unpacked.append})
assert unpacked == [decoded]
files = {'readable.py': readable.encode(), 'decoded.py': decoded.encode(), 'agent.py': candidate,
         'candidate.diff': ''.join(difflib.unified_diff(parent.splitlines(True), readable.splitlines(True), fromfile='d4353r1', tofile='receipt-handoff-prototype')).encode()}
for n, data in files.items(): (P/n).write_bytes(data)
report = {'status': 'OFFLINE PROTOTYPE; tests and independent review pending', 'parent': 'd4353r1', 'parent_exact_repack': True,
          'AST_equal': True, 'fits_source_limit': len(candidate) <= 65536, 'headroom': 65536-len(candidate),
          'files': {n: {'bytes':len(b), 'sha256':sha(b)} for n,b in files.items()}}
(P/'build-result.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report))
