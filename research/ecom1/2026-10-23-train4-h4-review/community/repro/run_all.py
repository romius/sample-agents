"""Frozen exact rc7 recipe assembly plus component and whole-agent replay checks."""
import ast
import base64
import contextlib
import hashlib
import io
import json
from pathlib import Path
import apply_recipe
import lzopt
import owner_host

P = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode(source):
    tree = ast.parse(source)
    g = {}
    exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), '<decoder>', 'exec'), g)
    return g['_lz'](tree.body[-1].value.args[0].args[0].value)


class SDK:
    def task(self):
        raise RuntimeError('LOAD_STOP')
    def call(self, *args, **kwargs):
        return {}
    def usage(self):
        return {}


def load(source):
    ns = {'bitgn': SDK(), 'print': lambda *a, **k: None}
    try:
        exec(source, ns)
    except RuntimeError as error:
        assert str(error) == 'LOAD_STOP'
    assert callable(ns['FC']) and callable(ns['DM'])
    return ns


def parse(fn, text):
    try:
        return {'status': 'parsed', 'value': fn(text)}
    except ValueError as error:
        return {'status': 'declined', 'error': str(error)}


def replay(source, text):
    host = owner_host.Host(text)
    with contextlib.redirect_stdout(io.StringIO()):
        exec(source, {'bitgn': host})
    assert not host.unmatched
    assert len(host.answers) == 1
    assert all(m != 'Delete' and (m != 'Write' or a['path'] == owner_host.W['export']) for m, a in host.calls)
    return {'calls': host.calls, 'answers': host.answers, 'writes': host.writes,
            'scripted_model_calls': len(host.llms), 'unmatched': host.unmatched}


def main():
    for name, record in json.loads((P / 'input-manifest.json').read_text()).items():
        assert sha((P / name).read_bytes()) == record['sha256'], name
    parent = (P / 'parent.py').read_text()
    original = (P / 'parent_decoded.py').read_text()
    assert sha(parent.encode()) == 'a25dc3c06a794616730b81d6c09fec8801192520feb43e398e3de7f2607c3616'
    assert decode(parent) == original
    recipe = json.loads((P / 'rc7_edits.json').read_text())
    readable = apply_recipe.apply(original, recipe)
    assert sha(readable.encode()) == recipe['result_sha256'], 'Must reproduce owner decoded SHA exactly'
    # Negative applicator contracts: missing selector or duplicate selector fails before packaging.
    for text in ['', recipe['edits'][0]['old'] * 2]:
        try:
            apply_recipe.apply(text, recipe)
        except (ValueError, AssertionError):
            pass
        else:
            raise AssertionError('Applicator must reject missing/duplicate selectors')
    oldnodes = ast.parse(original).body
    newnodes = ast.parse(readable).body
    assert len(oldnodes) == len(newnodes)
    changed = [i for i, (a, b) in enumerate(zip(oldnodes, newnodes)) if ast.dump(a) != ast.dump(b)]
    assert [oldnodes[i].name for i in changed] == ['DM', 'FC'], 'Only original DM and FC may change'
    packed = (P / 'parent_stub.txt').read_text() + 'exec(_lz("' + base64.b85encode(lzopt.lz(readable.encode('ascii'))).decode() + '"))\n'
    assert len(packed.encode()) <= 65536
    assert decode(packed) == readable
    (P / 'readable.py').write_text(readable)
    (P / 'candidate.py').write_text(packed)
    variants = {'parent_readable': original, 'parent_packed': parent,
                'candidate_readable': readable, 'candidate_packed': packed}
    loaded = {name: load(code) for name, code in variants.items()}
    component = []
    for name, text, expected in json.loads((P / 'parser-fixtures.json').read_text()):
        rows = {v: parse(g['FC'], text) for v, g in loaded.items()}
        assert rows['parent_readable'] == rows['parent_packed']
        assert rows['candidate_readable'] == rows['candidate_packed']
        actual = rows['candidate_packed']
        assert actual['status'] == ('parsed' if expected == 'parsed' else 'declined') if expected != 'unchanged' else actual == rows['parent_packed'], (name, expected, rows)
        component.append({'kind': 'crosslist', 'name': name, 'expected': expected, 'rows': rows})
    for case in json.loads((P / 'receipt_cases.json').read_text()):
        rows = {v: json.loads(json.dumps(g['DM'](case['text']))) for v, g in loaded.items()}
        assert rows['candidate_readable'] == rows['candidate_packed'] == case['expected'], case['name']
        assert rows['parent_readable'] == rows['parent_packed']
        if case['kind'] in ('parity', 'decline'):
            assert rows['candidate_packed'] == rows['parent_packed']
        component.append({'kind': 'receipt', 'name': case['name'], 'rows': rows})
    owner_host.W = json.loads((P / 'world.json').read_text())
    noisy = owner_host.W['files'][owner_host.W['upload']]['content']
    clean = noisy.replace('## scanline ##  Total requested units:', 'Total requested units:')
    flow_cases = [('clean', clean, True, True), ('noisy', noisy, False, True),
                  ('duplicate-noisy', clean + '## scanline ## Total requested units: 36\n', True, False),
                  ('wrong-units', clean.replace('Total requested units: 36', 'Total requested units: 37'), False, False),
                  ('unicode-lookalike', noisy.replace('scanline', 'scanlıne'), False, False)]
    full = []
    expected_tsv = (P / 'expected.tsv').read_text()
    for case, text, parent_ok, candidate_ok in flow_cases:
        rows = {v: replay(code, text) for v, code in variants.items()}
        assert rows['parent_readable'] == rows['parent_packed']
        assert rows['candidate_readable'] == rows['candidate_packed']
        for name, row in rows.items():
            ok = candidate_ok if name.startswith('candidate') else parent_ok
            assert len(row['writes']) == int(ok), (case, name, row)
            if ok:
                assert row['writes'] == [{'path': owner_host.W['export'], 'content': expected_tsv}]
                assert row['answers'] == [{'message': owner_host.W['export'], 'outcome': 'OUTCOME_OK',
                                          'refs': [owner_host.W['upload'], '/docs/security.md', '/docs/purchase-request-crosslist.md']}]
                assert row['scripted_model_calls'] == 1
            else:
                assert row['answers'][0]['outcome'] == 'OUTCOME_NONE_UNSUPPORTED'
                assert row['answers'][0]['message'] == 'OFFLINE FALLBACK: deterministic handler declined.'
        if parent_ok == candidate_ok:
            assert rows['parent_packed'] == rows['candidate_packed']
        full.append({'case': case, 'rows': rows})
    result = {'components': component, 'full_replays': full}
    (P / 'results.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    summary = {'candidate_bytes': len(packed.encode()), 'candidate_sha256': sha(packed.encode()),
               'readable_sha256': sha(readable.encode()), 'owner_recipe_exact': True, 'changed_nodes': ['DM', 'FC'],
               'other_ordered_ast_identical': True, 'roundtrip_exact': True,
               'actual_module_loads': 4, 'crosslist_cases_per_representation': 31,
               'receipt_cases_per_representation': 9, 'component_calls': 160,
               'full_agent_replay_executions': 20, 'zero_unmatched_rpc': True,
               'full_export_tsv_and_human_answers_exact': True, 'real_generations_or_live_jobs': 0,
               'native_proof': 'coordinator pending', 'verdict': 'SCOPED ADOPT for owner integration review only'}
    (P / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
