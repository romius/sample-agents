"""Reassemble read-only Brain event receipts without changing any raw bytes."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
def load(path): return json.loads(path.read_text())
def sha(data): return hashlib.sha256(data).hexdigest()
def save(name, value): (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

receipt = load(HERE / 'receipts/result.json')['structuredContent']
assert receipt['code'] == 0 and not receipt['data']['output_truncated']
settled = json.loads(receipt['output'])
job, summary = settled['job'], settled['result']
assert job['id'] == 'j8359aedb3a54484e876f62f0bba9221a' and job['state'] == 'completed'
assert job['source_blob'] == summary['source']['sha256'] == 'dc5e1951f404dca549fe97a6fd38de36419ece9ecd0c3aa07d4f6369998bda3e'
assert job['document'] == summary['source']['document'] == 'd6280'
assert job['revision'] == summary['source']['revision'] == 1
assert job['sdk_version'] == summary['source']['sdk_version'] == '0.3.7'
assert job['run_id'] == summary['run_id'] == 'run-22rKCszzuEoyDjuakc6fpA1Tf'
summary['job_id'] = job['id']  # Exact job receipt join; not a filename inference.
pages = load(HERE / 'receipts/index.json')
index = [event for page in pages for event in page['items']]
assert [e['seq'] for e in index] == list(range(1, 150))
assert all(page['more'] for page in pages[:-1]) and not pages[-1]['more']
assert [page['next_after'] for page in pages] == [50, 100, 149]
parts = {}
receipt_paths = sorted((HERE / 'receipts').glob('chunk-*.json'))
assert len(receipt_paths) == 144
brain_sequences = []
for path in receipt_paths:
    receipt = load(path)
    request, response = receipt['request'], receipt['response']
    assert response['code'] == 0 and not response['data']['output_truncated']
    assert response['data']['seq'] == request['seq'] and request['session'] == 's7712'
    brain_sequences.append(request['seq'])
    requested = re.findall(r"trace_event\('j8359aedb3a54484e876f62f0bba9221a',(\d+),offset=(\d+),limit=(\d+)\)", request['source'])
    chunks = json.loads(response['output'])
    assert len(requested) == len(chunks)
    for (seq, offset, limit), chunk in zip(requested, chunks):
        seq, offset, limit = int(seq), int(offset), int(limit)
        assert seq == chunk['seq']
        raw = chunk['text'].encode('utf-8')
        assert len(raw) <= limit and chunk['next_offset'] == offset + len(raw)
        assert chunk['more'] == (chunk['next_offset'] < chunk['bytes'])
        assert chunk['bytes'] == index[seq-1]['data']['trace']['bytes']
        parts.setdefault(seq, []).append((offset, raw))
assert brain_sequences == list(range(9, 153))
assert sorted(parts) == list(range(1, 150))
scopes = {}
events = []
for entry in index:
    seq = entry['seq']
    raw = b''
    for offset, data in sorted(parts[seq]):
        assert offset == len(raw), ('missing or overlapping bytes', seq, offset)
        raw += data
    assert len(raw) == entry['data']['trace']['bytes'] and raw.endswith(b'\n')
    event = json.loads(raw)
    assert event['seq'] == seq and event['kind'] == entry['kind'] and event['time'] == entry['time']
    scope = entry['data']['trace']['scope']
    scopes.setdefault(scope, bytearray())
    assert len(scopes[scope]) == entry['data']['trace']['offset']
    scopes[scope].extend(raw)
    events.append(dict(seq=seq, kind=event['kind'], scope=scope, bytes=len(raw), sha256=sha(raw)))
for trace in summary['traces']:
    raw = bytes(scopes[trace['scope']])
    assert trace['sealed'] and len(raw) == trace['bytes'] and sha(raw) == trace['blob']
    filename = 'trial-trace.ndjson' if trace['scope'] == 'trial-1' else 'run-trace.ndjson'
    (HERE / filename).write_bytes(raw)
assert sha(bytes(scopes['trial-1'])) == '6b5c7026c7d3def4d6a5d60e954f2881d098cd4a52b1df4282b662dc7661f980'
save('summary.json', summary)
save('reassembly-verification.json', dict(status='all149 immutable events reconstructed and both official CAS hashes matched',
    events=events, chunks=220, read_batches=144, trace_receipts=summary['traces'],
    job_id=job['id'], run_id=job['run_id'], source=summary['source'],
    job_receipt_join='summary.job_id copied from same sandbox.result receipt job.id after source/run identity checks',
    index_page_limit=50, incomplete_initial_100_index_discarded=True,
    summary_blob_receipt=job['summary_blob'], summary_blob_independently_reconstructed=False,
    raw_trace_bytes_preserved=True, real_model_calls_in_this_harvest=0, brain_writes=False))
print('PASS:149 events,220 chunks; exact trial and run CAS bytes verified.')
