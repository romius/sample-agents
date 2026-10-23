from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
A=P.parent/'2026-10-23-train4-h4-stock-boundaries'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=A/'SHA256SUMS.json'
assert sha(seal)=='714c2ba48319ad1bd43c8863730bf65444c154ba32eea1dc4262e2ad9efffdf8'
for r in json.loads(seal.read_text())['files']:
 p=A/r['path'];assert len(p.read_bytes())==r['bytes'] and sha(p)==r['sha256']
for r in json.loads((A/'input-pins.json').read_text()):
 p=A/r['path'];assert sha(p)==r['sha256']
 upstream=P.parent.parent.parent/r['source'];assert p.read_bytes()==upstream.read_bytes()
d=json.loads((A/'results.json').read_text());assert len(d['rows'])==336 and len(d['summary'])==42
assert sum(x['helper_reached'] for x in d['rows'])==280
assert sum(x['engine']=='native' for x in d['rows'])==168
for r in d['rows']:
 assert len(r['answers'])==1 and not r['unmatched']
 if not r['helper_reached']:continue
 positive=all(x['available_today']>=x['qty'] for x in r['oracle_lines'])
 assert r['answers'][0]['message']==({'t023':'TRUE(1)','t063':'ja'} if positive else {'t023':'FALSE(2)','t063':'nein'})[r['task']]
 assert [x['qty'] for x in r['oracle_lines']]==([1,1,1,1] if r['task']=='t023' else [1,12,1,1])
 assert len(r['answers'][0]['refs'])==8
 assert all(method not in ['Write','Delete'] for method,args in r['calls'])
print(json.dumps({'sealed_files':20,'executions':336,'helper_cells':280,'fixed_fallback_cells':56,'result_sha256':sha(A/'results.json'),'status':'PASS'}))
