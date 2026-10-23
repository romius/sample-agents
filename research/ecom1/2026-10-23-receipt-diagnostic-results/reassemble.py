"""Byte-exact reconstruction from immutable, read-only Brain receipts."""
import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def unpack(p):
 r=load(p);assert r['code']==0 and not r['data']['output_truncated'];return json.loads(r['output'])
def save(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
settled=unpack(P/'receipts/result.json');job,summary=settled['job'],settled['result']
assert job['id']=='j9c4eb06afb6e42e690ff96d0b75c47bd' and job['state']=='completed'
assert job['source_blob']==summary['source']['sha256']=='4237825f66d2215a805d6ddd1823b9bf0e803798ce34b63aeb3b60696673626f'
assert job['document']==summary['source']['document']=='d6954' and job['revision']==summary['source']['revision']==1
assert job['sdk_version']==summary['source']['sdk_version']=='0.3.7'
assert job['run_id']==summary['run_id']=='run-22rM18dbDxwob346TiHAkFEfi'
summary['job_id']=job['id']
pages=[unpack(P/f'receipts/index-{i}.json') for i in range(2)]
index=[e for page in pages for e in page['items']]
assert [e['seq'] for e in index]==list(range(1,54))
assert pages[0]['more'] and not pages[1]['more'] and [p['next_after'] for p in pages]==[50,53]
parts={};sequences=[]
for p in sorted((P/'receipts').glob('chunk-*.json')):
 r=load(p);req,res=r['request'],r['response'];assert res['code']==0 and not res['data']['output_truncated']
 assert req['session']=='s8221' and req['seq']==res['data']['seq'];sequences.append(req['seq'])
 m=re.search(r'trace_event\("j9c4eb06afb6e42e690ff96d0b75c47bd", (\d+), offset=(\d+), limit=(\d+)\)',req['source']);assert m
 seq,off,limit=map(int,m.groups());chunk=json.loads(res['output']);b=chunk['text'].encode()
 assert chunk['seq']==seq and len(b)<=limit and chunk['next_offset']==off+len(b)
 assert chunk['more']==(chunk['next_offset']<chunk['bytes']) and chunk['bytes']==index[seq-1]['data']['trace']['bytes']
 parts.setdefault(seq,[]).append((off,b))
assert sequences==list(range(8,82)) and sorted(parts)==list(range(1,54))
scopes={};manifest=[]
(P/'events').mkdir(exist_ok=True)
for e in index:
 b=b''
 for off,part in sorted(parts[e['seq']]):assert off==len(b);b+=part
 assert len(b)==e['data']['trace']['bytes'] and b.endswith(b'\n')
 v=json.loads(b);assert all(v[k]==e[k] for k in ['seq','time','kind'])
 scope=e['data']['trace']['scope'];scopes.setdefault(scope,bytearray());assert len(scopes[scope])==e['data']['trace']['offset'];scopes[scope].extend(b)
 path=f"events/{e['seq']:03d}.json";(P/path).write_bytes(b);manifest.append(dict(path=path,seq=e['seq'],kind=e['kind'],scope=scope,bytes=len(b),sha256=sha(b)))
for t in summary['traces']:
 b=bytes(scopes[t['scope']]);assert t['sealed'] and len(b)==t['bytes'] and sha(b)==t['blob']
 (P/('trial-trace.ndjson' if t['scope']=='trial-1' else 'run-trace.ndjson')).write_bytes(b)
save('summary.json',summary)
save('reassembly-verification.json',dict(events=manifest,chunks=74,read_batches=74,complete_index=True,trace_receipts=summary['traces'],job_id=job['id'],run_id=job['run_id'],source=summary['source'],summary_blob_receipt=job['summary_blob'],summary_blob_independently_reconstructed=False,raw_trace_bytes_preserved=True,real_model_calls_in_harvest=0,brain_writes=False))
print('PASS: all 53 immutable events, 74 chunks; both official CAS hashes matched.')
