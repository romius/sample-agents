"""Verify local provenance, exact parent build and archived fixture derivations."""
import copy,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
for n,pin in json.loads((P/'INPUT-PINS.json').read_text()).items():
 b=(P/n).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256'],n
with tempfile.TemporaryDirectory(prefix='d4353-parent-rebuild-') as tmp:
 d=Path(tmp);shutil.copytree(P/'parent-build',d/'parent');d=d/'parent'
 subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(d/'build_combined.py')],check=True,capture_output=True)
 for out,local in [('agent.py','parent.py'),('readable.py','parent-readable.py'),('decoded.py','parent-decoded.py')]:assert (d/out).read_bytes()==(P/local).read_bytes(),out
 assert (d/'build-receipt.json').read_bytes()==(P/'parent-build/build-receipt.json').read_bytes()
f=P/'fixture';w=json.loads((f/'world.json').read_text());provenance=json.loads((f/'world-provenance.json').read_text())
requests={e['seq']:e for e in map(json.loads,(f/'events-t076.jsonl').read_text().splitlines())}
raw={e['seq']:line for n in ('initial-rpc-responses.jsonl','remaining-rpc-responses.jsonl') for line in (f/n).read_text().splitlines(keepends=True) for e in [json.loads(line)]}
index=json.loads((f/'index-t076.json').read_text())
assert set(raw)=={e[0] for e in index if e[1]=='rpc_response'}
for seq,kind,method,size in index:
 if kind=='rpc_response':assert len(raw[seq].encode())==size
rpc={};files={};lineage=[]
for seq,line in sorted(raw.items()):
 e=json.loads(line);q=requests[seq-1]['data'];d=e['data'];assert q['method']==d['method'];r=d['response'];key=canon([q['method'],q['arguments']])
 if key in rpc:assert rpc[key]==r
 rpc[key]=r
 if d['method']=='Read':
  assert sha(r['content'].encode())==r['sha256'];files[r['path']]=r
 lineage.append({'request_seq':seq-1,'response_seq':seq,'method':d['method'],'arguments':q['arguments'],'raw_response_sha256':sha(line.encode()),'raw_bytes':len(line.encode())})
assert rpc==w['rpc'] and files==w['files'] and lineage==provenance['lineage']
assert w['task']==next(json.loads(l)['data']['response'] for l in raw.values() if json.loads(l)['data']['method']=='StartTrial')
assert w['router_response']==requests[10092]['data']['response']
tree=rpc[canon(['Tree',{'root':'/proc','level':0}])];derived={}
for root in ['/proc/catalog','/proc/locations']:
 node=next(n for n in tree['root']['children'] if n['name']==root.split('/')[-1])
 def depth(n):return max([1+depth(c) for c in n.get('children',[])]+[0])
 assert depth(node)==2
 for level in [0,3]:derived[canon(['Tree',{'root':root,'level':level}])]={'root':node}
assert derived==w['derived_rpc']
assert len(raw)==135 and len(files)==126
report={'status':'PASS','pinned_inputs':len(json.loads((P/'INPUT-PINS.json').read_text())),'parent_build_exact':True,'archived_rpc_responses':len(raw),'archived_read_files':len(files),'derived_trees':4,'derivation':'Exact children of complete archived /proc Tree; actual depth2 satisfies current parent requested level3. No node relabeling.'}
(P/'input-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
