"""Coordinator oracle correction; product code and all OCR labels stay immutable."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

P = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert sha(P / 'apply_recipe.py') == 'c4cfbd82d9e791ce9e4626645abdcfa7ad45ccbf2cb19d53ec5e68e56da1ba77'
    for name, record in json.loads((P / 'input-manifest.json').read_text()).items():
        assert sha(P / name) == record['sha256'], name
    assert sha(P / 'readable.py') == '9886cb40612a943d861d924a30e1d6709f6c191375a72735828408e3a50557f0'
    before = (sha(P / 'candidate.py'), sha(P / 'readable.py'))
    old = ast.parse((P / 'parent_decoded.py').read_text()).body
    new = ast.parse((P / 'readable.py').read_text()).body
    assert len(old) == len(new)
    changed = [(i, getattr(a, 'name', None)) for i, (a, b) in enumerate(zip(old, new)) if ast.dump(a) != ast.dump(b)]
    assert changed == [(353, 'FC'), (374, 'DM')]
    result = subprocess.run([sys.executable, str(P / 'run_all.py')], text=True, capture_output=True)
    (P / 'original-frozen-failure.txt').write_text(result.stdout + result.stderr)
    assert result.returncode != 0 and 'Only original DM and FC may change' in result.stderr
    frozen = (P / 'run_all.py').read_text()
    wrong = "== ['DM', 'FC'], 'Only original DM and FC may change'"
    right = "== ['FC', 'DM'], 'Only original FC and DM may change'"
    assert frozen.count(wrong) == 1
    corrected = frozen.replace(wrong, right)
    summary = "'changed_nodes': ['DM', 'FC']"
    assert corrected.count(summary) == 1
    corrected = corrected.replace(summary, "'changed_nodes': ['FC', 'DM']")
    (P / 'corrected_run_all.py').write_text(corrected)
    result = subprocess.run([sys.executable, str(P / 'corrected_run_all.py')], text=True, capture_output=True)
    (P / 'corrected-coordinator-output.txt').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    assert before == (sha(P / 'candidate.py'), sha(P / 'readable.py'))
    assert sha(P / 'candidate.py') == '2b4de83bbba8e18e9b7eab46bd5fb4512a6cc373cacd49bf87ce7333b26bca85'
    for name, record in json.loads((P / 'input-manifest.json').read_text()).items():
        assert sha(P / name) == record['sha256'], name
    verified = {'original_frozen_runner': 'FAIL, false coordinator node-order oracle retained',
                'actual_changed_nodes_in_order': changed,
                'coordinator_changes': ['correct order assertion FC then DM', 'correct display order only'],
                'product_and_fixture_labels_changed': False, 'all_original_input_pins': 12,
                'corrected_runner': 'PASS', 'summary': json.loads((P / 'summary.json').read_text()),
                'open_code_new_inference_or_extension': False,
                'agent63_mcp_events_this_local_run': 0,
                'identity_note': 'same model/session/profile forced by continue.py; local-only run has no fresh MCP identity event, root publishes under identity50',
                'verdict': 'SCOPED ADOPT of exact owner-recipe composition for integrator review'}
    (P / 'independent-proof.json').write_text(json.dumps(verified, indent=2) + '\n')
    print(json.dumps(verified))


if __name__ == '__main__':
    main()
