"""Expose every answer for manual review; calculate no semantic scores."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
report = json.loads((HERE / 'validation.json').read_text())
assert report['status'] == 'reconciled' and len(report['rows']) == 68
answers = []
for row in report['rows']:
    message = row['raw_final_event']['data']['response']['choices'][0]['message']
    answers.append(dict(**row['step'], transport_call_ids=row['transport_call_ids'],
        request_event_seq=row['attempts'][0]['request_event_seq'][0],
        response_event_seq=row['raw_final_event']['seq'],
        response_id=row['raw_final_event']['data']['response']['id'],
        response_event_canonical_sha256=row['raw_final_event_sha256'],
        finish_reason=row['finish_reason'], content=row['raw_content'],
        reasoning=message.get('reasoning'), manual_review='pending'))
(HERE / 'manual-review-inputs.json').write_text(json.dumps(answers, indent=2, ensure_ascii=False)+'\n')
lines = ['# All 68 answers for manual review', '',
    'These are complete actual response contents, grouped by case then execution ordinal. No semantic grades are computed. Request hashes, full response IDs and immutable event sequences link to `trial-trace.ndjson`; the full raw events, costs and wire checks are in `validation.json`.', '',
    'Use only evidence visible in each exact frozen request. Hidden F2 N15/O15 facts are not expected answer facts; justified continuation or uncertainty can be correct. A supported compatible option does not alone establish uniqueness. The carrier grade is irrelevant to this diagnostic.', '']
for case in dict.fromkeys(row['case'] for row in answers):
    lines += ['## '+case, '']
    for answer in [a for a in answers if a['case']==case]:
        lines += [f"### Ordinal {answer['ordinal']} — {answer['arm']}, repeat {answer['repeat']}", '',
                  f"Request event {answer['request_event_seq']}; response event {answer['response_event_seq']}; finish `{answer['finish_reason']}`.", '',
                  f"Request SHA-256: `{answer['request_sha256']}`", '']
        content = answer['content'] or ''
        fence = '`' * max(4, max((len(t) for t in __import__('re').findall(r'`+',content)),default=0)+1)
        lines += [fence+'text',content,fence,'']
(HERE / 'manual-review-inputs.md').write_text('\n'.join(lines)+'\n')
print('Prepared68 raw answers; all manual judgments remain pending.')
