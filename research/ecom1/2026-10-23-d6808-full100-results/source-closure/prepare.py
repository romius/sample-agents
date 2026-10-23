"""Reassemble exact byte-ranged old2 t079 trace and prepare same-world RPC map."""
import collections,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;E=P/'evidence';sha=lambda b:hashlib.sha256(b).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
plan=json.loads((E/'harvest-plan.json').read_text());chunks=collections.defaultdict(list)
for i,group in enumerate(plan):
 data=json.loads((E/f'chunk-{i}.json').read_text());assert len(data)==len(group)
 for (seq,offset,size),c in zip(group,data):
  assert c['seq']==seq and c['next_offset']==offset+len(c['text'].encode())==offset+size
  chunks[seq].append((offset,c['text']))
index=json.loads((E/'index-t079.json').read_text());events=[];raw=[]
for item in index:
 seq=item['seq'];data=b''
 for offset,text in sorted(chunks[seq]):assert offset==len(data);data+=text.encode()
 assert len(data)==item['data']['trace']['bytes']
 event=json.loads(data);assert event['seq']==seq and event['kind']==item['kind']
 assert event['data'].get('trial_id')=='vm2-M6xEUVY5beJJgp3UfkqdSuq1zaJ'
 raw.append(data);events.append(event)
trace=b''.join(raw);assert len(events)==274 and len(trace)==370247
official=json.loads((E/'official-t079.json').read_text());assert official['trial']['trace']['blob']==sha(trace) and official['trial']['trace']['bytes']==len(trace) and official['trial']['trace']['sealed']
(E/'trace-t079.ndjson').write_bytes(trace)
byseq={e['seq']:e for e in events};rpc={};files={};errors={};lineage=[]
for e in events:
 if e['kind'] not in ('rpc_response','rpc_error'):continue
 q=byseq[e['seq']-1];assert q['kind']=='rpc_request' and q['data']['method']==e['data']['method']
 method=q['data']['method'];args=q['data']['arguments'];k=canon([method,args]);d=e['data']
 if e['kind']=='rpc_error':errors[k]=d['error'];continue
 r=d['response']
 if k in rpc:assert rpc[k]==r
 rpc[k]=r
 if method=='Read':
  assert sha(r['content'].encode())==r['sha256'];files[r['path']]=r
 lineage.append({'request_seq':q['seq'],'response_seq':e['seq'],'method':method,'arguments':args})
task=byseq[10341]['data']['response'];router=byseq[10353]['data']['response'];model=[byseq[s]['data']['response'] for s in (10357,10605,10607)]
# Derive only the catalogue subtree needed by current d4353, from exact original Tree.
q=byseq[10358]['data'];tree=byseq[10359]['data']['response'];print('actual full Tree',q['arguments'])
assert not any(tree.get(k) for k in ('truncated','more','next','next_cursor'))
derived={};derivations=[]
root=q['arguments']['root']
def depth(n):return max([1+depth(c) for c in n.get('children',[])]+[0])
if root=='/proc':
 for node in tree['root'].get('children',[]):
  if node.get('kind')!='NODE_KIND_DIR':continue
  path='/proc/'+node['name'];d=depth(node);assert d<=3
  derived[canon(['Tree',{'root':path,'level':3}])]={'root':node}
  derivations.append({'root':path,'level':3,'actual_depth':d,'source_response_seq':10359,'method':'Exact existing child subtree of complete archived /proc Tree; no relabeling.'})
world={'task':task,'rpc':rpc,'files':files,'errors':errors,'derived_rpc':derived,'router_response':router,'model_responses':model,'original_exec':byseq[10608]['data']['arguments'],'original_error':byseq[10609]['data']['error'],'original_agent_error':byseq[10610]['data']['error']}
(P/'world.json').write_text(json.dumps(world,indent=2)+'\n')
report={'job':'jd8713c77f6ab4a0e9f67bcd614d8d2e9','task_id':'t079','trial_id':task['trialId'],'trace_bytes':len(trace),'trace_sha256':sha(trace),'events':len(events),'read_files':len(files),'rpc_responses':len(lineage),'lineage':lineage,'derived_trees':derivations,'models':'Archived router +3 actual response bodies; current source requests differ from archived requests; continuation is explicitly scripted.'}
(P/'world-provenance.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ('lineage','derived_trees')})
