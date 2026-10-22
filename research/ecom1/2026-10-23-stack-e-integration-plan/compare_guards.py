"""Offline boundary comparisons from exact sources; not whole-agent replay."""
import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PARENT = ROOT / 'research/ecom1/2026-10-23-stack-e-record-review/upstream/readable.py'
DONOR = ROOT / 'research/ecom1/2026-10-22-record-integration/readable.py'

def definition(source, name):
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, node)

parent, donor = PARENT.read_text(), DONOR.read_text()
namespaces = []
for source in (parent, donor):
    ns = {'json': json}
    exec(definition(source, 'recoverable_lookup_error'), ns)
    namespaces.append(ns)

cases = [
    ('missing-executable', 'exec', 'BitGN HTTP 404: {"code":"not_found","message":"runtime tool not found: not found"}'),
    ('missing-payment', 'exec', 'BitGN HTTP 404: {"code":"not_found","message":"payment not found"}'),
    ('missing-exec-generic', 'exec', 'BitGN HTTP 404: {"code":"not_found"}'),
    ('delete-404', 'delete', 'BitGN HTTP 404: {"code":"not_found","message":"delete failed: not found"}'),
    ('delete-malformed-404', 'delete', 'BitGN HTTP 404: {}'),
    ('read-404', 'read', 'BitGN HTTP 404: {"code":"not_found"}'),
    ('write-404', 'write', 'BitGN HTTP 404: {"code":"not_found"}'),
    ('wrong-code', 'exec', 'BitGN HTTP 404: {"code":"denied","message":"runtime tool not found"}'),
    ('malformed', 'exec', 'BitGN HTTP 404: bad json'),
    ('permission', 'exec', 'BitGN HTTP 403: denied'),
    ('server', 'exec', 'BitGN HTTP 500: unavailable'),
    ('unknown', 'exec', 'database is locked'),
]
lookup = []
for name, tool, error in cases:
    values = [ns['recoverable_lookup_error']({'tool': tool, 'path': '/bin/example'}, RuntimeError(error)) for ns in namespaces]
    lookup.append({'case': name, 'tool': tool, 'error': error, 'record': values[0], 'donor': values[1]})
assert lookup[0]['record'] and lookup[0]['donor']['unavailable_tool']
assert lookup[1]['record'] and lookup[1]['donor'] is None
assert lookup[2]['record'] and lookup[2]['donor'] is None
assert lookup[3]['record'] is None and lookup[3]['donor']['outcome_unconfirmed']
assert lookup[5]['record'] == lookup[5]['donor']
for row in lookup[6:]:
    assert row['record'] == row['donor'], row['case']

# Preserve exact main-loop exception guard and loop retry control. Stop at the
# first successful inference; action parsing/RPCs are deliberately out of scope.
tree = ast.parse(parent)
loop = next(n for n in tree.body if isinstance(n, ast.For) and 'MAX_STEPS' in ast.unparse(n.iter))
assert isinstance(loop.body[0], ast.While) and isinstance(loop.body[1], ast.Try)
guard = ast.unparse(loop.body[1])
main = 'for index in range(MAX_STEPS):\n' + '\n'.join(' ' + line for line in guard.splitlines()) + '\n break\n'
msr = definition(donor, 'MSR')

class Provider:
    def __init__(self, error, failures):
        self.error, self.failures = error, failures
        self.requests = []
    def llm(self, *args, **kwargs):
        self.requests.append([args, kwargs])
        if len(self.requests) <= self.failures:
            raise RuntimeError(self.error)
        return {'choices': [{'message': {'content': '{}'}}]}

retry = []
for error in ['HTTP 503 unavailable', 'Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out', 'HTTP 429 timeout', 'HTTP 400 connection', 'database is locked', 'cancelled']:
    for failures in [1, 99]:
        counts = {}
        for mode in ['record-main', 'naive-MSR-plus-record-main', 'MSR-alone']:
            provider = Provider(error, failures)
            ns = {'bitgn': provider, 're': re, 'MODEL': 'frozen-model', 'messages': [{'role': 'user', 'content': 'same'}], 'invalid_steps': 0, 'MAX_STEPS': 30, 'print': lambda *a: None}
            exec(msr, ns)
            code = main if mode == 'record-main' else main.replace('bitgn.llm(', 'MSR(')
            if mode == 'MSR-alone':
                code = "response=MSR(MODEL,messages,max_completion_tokens=2048,reasoning={'effort':'medium'},temperature=0)"
            raised = None
            try:
                exec(code, ns)
            except RuntimeError as exc:
                raised = str(exc)
            assert all(r == provider.requests[0] for r in provider.requests)
            counts[mode] = {'calls': len(provider.requests), 'success': 'response' in ns, 'raised': raised}
        retry.append({'error': error, 'failures': failures, 'modes': counts})
        transient = error.startswith('HTTP 503') or 'TimeoutError' in error
        assert counts['record-main']['calls'] == (2 if failures == 1 else 3)
        assert counts['naive-MSR-plus-record-main']['calls'] == (2 if failures == 1 else (9 if transient else 3))
        assert counts['MSR-alone']['calls'] == ((2 if failures == 1 else 3) if transient else 1)

result = {'scope': 'Exact function and main-loop guard extraction; excludes forced-report call, routing, action processing, SDK host retry and live inference. Not whole-agent success evidence.',
          'sources': {str(p.relative_to(ROOT)): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in [PARENT, DONOR]},
          'lookup_cases': lookup, 'retry_cases': retry,
          'conclusion': 'Do not stack MSR inside the existing main-loop all-exception retry guard. A main request may otherwise be attempted nine times before the separate forced report. Preserve narrow Exec missing-executable semantics; add unconfirmed Delete recovery independently; neither lookup recovery retries a mutation.'}
OUT.joinpath('guard-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS: 12 lookup boundaries and 12 retry scenarios across three exact-guard compositions')
