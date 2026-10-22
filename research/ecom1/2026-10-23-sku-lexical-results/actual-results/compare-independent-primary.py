"""Offline identity/content joins and descriptive review differences; no semantic scorer."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def read(name):
    raw = (ROOT / name).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()

independent, independent_sha = read('independent-semantic-review.json')
primary, primary_sha = read('primary-manual-review.json')
inputs, inputs_sha = read('manual-review-inputs.json')
assert independent_sha == '273cddfd855af0930735068a036392b3976936fdb46b4d01726b98357b9186a4'
assert len(independent['rows']) == len(primary) == len(inputs) == 68
fields = ['action_class', 'false_OK', 'unsupported_positive_assertion',
          'qualifier_loss', 'contradicted_option', 'positive_control_preserved',
          'targeted_deferred_lookup', 'malformed', 'provider_error', 'cancelled']
explanations = {
    ('E3_exact_unknown', 'contradicted_option'): 'Independent includes an offered B as contradicting the explicit A identity constraint. Primary records this as identity/qualifier loss without this additional flag. Both describe the same unsupported identity ambiguity.',
    ('F3_lexical_distractor', 'unsupported_positive_assertion'): 'Independent includes implicit full-request compatibility of the contradicted final choice. Primary records the known contradiction in contradicted_option and false_OK, without additionally flagging unsupported_positive_assertion. Both reject the flat final selection.',
    ('F4_false_missing_true', 'positive_control_preserved'): 'Independent reserves this flag for named positive controls and leaves F4 null, while separately recording local positive recognition. Primary also uses this flag for F4 local positive recognition. Both credit C=true and identify unresolved B/pool uniqueness.',
    ('F2_truncated_relevant_family', 'action_class'): 'Spelling alias only: deferred_catalogue and deferred_catalog both denote the identical supported catalog tool action. Both mark targeted_deferred_lookup true; neither claims executed lookup or task success.',
}
differences = []
for ordinal, (left, right, actual) in enumerate(zip(independent['rows'], primary, inputs), 1):
    assert left['step'] == right['step']
    assert left['step']['ordinal'] == actual['ordinal'] == ordinal
    for key in ['case_index', 'case', 'repeat', 'arm', 'request_sha256']:
        assert left['step'][key] == actual[key]
    assert left['full_content'] == right['cited_evidence']['raw_final_content'] == actual['content']
    assert left['action'] == json.loads(actual['content'])
    assert left['response_ref']['event_seq'] == right['response_ref']['event_seq'] == actual['response_event_seq']
    assert left['response_ref']['response_id'] == right['response_ref']['response_id'] == actual['response_id']
    assert left['response_ref']['event_sha256'] == right['response_ref']['sha256'] == actual['response_event_canonical_sha256']
    changes = []
    for field in fields:
        if left[field] != right[field]:
            changes.append({'field': field, 'independent': left[field], 'primary': right[field],
                            'interpretation': explanations[(left['step']['case'], field)]})
    if changes:
        differences.append({'step': left['step'], 'differences': changes,
                            'independent_rationale': left['rationale'], 'primary_rationale': right['rationale']})
assert len(differences) == 12
report = {
    'status': 'all_68_response_identity_and_full_content_joins_pass',
    'source_sha256': {'independent-semantic-review.json': independent_sha,
                      'primary-manual-review.json': primary_sha,
                      'manual-review-inputs.json': inputs_sha},
    'reviewed_ordinals': 68,
    'compared_fields': fields,
    'rows_with_flag_or_label_difference': len(differences),
    'differences': differences,
    'interpretation': 'Differences are retained, not resolved by rewriting either reviewer. Detailed rationales agree on material observed behavior; these field-definition differences prohibit treating the flags as interchangeable scores.',
    'additional_independent_observation': 'N3 all four actions quote excluded P-G1-A in an exclusion clause despite the literal shared no-quote policy. This is separate from offering/citing the excluded SKU; both reviews agree it is correctly excluded from offered/cited options.',
    'not_measured': ['overall semantic pass rate', 'full100 score change', 'causal treatment effect', 'post-action tool success'],
}
(ROOT / 'independent-primary-comparison.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('PASS: 68 exact identity/content joins; 12 retained flag/label difference rows; no semantic scoring.')
