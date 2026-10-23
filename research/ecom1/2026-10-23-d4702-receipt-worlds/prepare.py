"""Reconstruct exact archived traces and read-only response fixtures, offline."""
import collections, hashlib, json
from pathlib import Path
D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads((D/p).read_text())
def write(p,v):
 q=D/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
plan=read('harvest-plan.json');parts=collections.defaultdict(list)
for i,group in enumerate(plan['groups']):
 responses=read(f'receipts/group-{i}.json');assert len(group)==len(responses)
 for (seq,offset,count),r in zip(group,responses):
  assert r['seq']==seq
  raw=r['text'].encode();assert len(raw)==count,(seq,offset,count,len(raw))
  assert r['next_offset'] in [None,offset+count]
  parts[seq].append((offset,raw))
new={}
for seq,chunks in parts.items():
 b=b''
 for offset,chunk in sorted(chunks):assert offset==len(b);b+=chunk
 new[seq]=b
result=read('upstream/result.json');reports=[]
for task in ['t023','t063']:
 index=[e for page in read(f'upstream/index-{task}.json') for e in page['items']]
 original={json.loads(b)['seq']:b for b in (D/f'upstream/{task}-events.ndjson').read_bytes().splitlines(keepends=True)}
 assert not set(original)&set(new)
 trace=b'';events=[]
 for item in index:
  seq=item['seq'];b=original.get(seq,new.get(seq));assert b is not None
  e=json.loads(b);assert e['seq']==seq and e['kind']==item['kind'];assert len(b)==item['data']['trace']['bytes'];assert len(trace)==item['data']['trace']['offset']
  trace+=b;events.append(e)
 trial=next(t for t in result['result']['trials'] if t['task_id']==task)
 assert len(trace)==trial['trace']['bytes'] and sha(trace)==trial['trace']['blob'] and trial['trace']['sealed']
 assert {e['data']['trial_id'] for e in events if 'trial_id' in e['data']}=={trial['trial_id']}
 (D/f'{task}-trace.ndjson').write_bytes(trace)
 files={};rpc=[];pending=None;fileledger=[];trees=[]
 for e in events:
  if e['kind']=='rpc_request':assert pending is None;pending=e
  elif e['kind']=='rpc_response':
   assert pending is not None and pending['data']['method']==e['data']['method']
   method=e['data']['method'];args=pending['data']['arguments'];response=e['data']['response']
   rpc.append({'request_seq':pending['seq'],'response_seq':e['seq'],'method':method,'arguments':args,'response':response});pending=None
   if method=='Read':
    path=args['path'];assert response['path']==path
    if path in files:assert files[path]==response
    files[path]=response;fileledger.append({'path':path,'request_seq':rpc[-1]['request_seq'],'response_seq':e['seq'],'content_bytes':len(response['content'].encode()),'content_sha256':sha(response['content'].encode())})
   if method=='Tree':trees.append({'request_seq':rpc[-1]['request_seq'],'response_seq':e['seq'],'arguments':args,'response':response})
 assert pending is None
 write(f'{task}/world.json',{'task_id':task,'trial_id':trial['trial_id'],'job_id':plan['job'],'files':files,'rpc':rpc,'trees':trees})
 write(f'{task}/read-ledger.json',fileledger)
 uploads={p:r for p,r in files.items() if p.startswith('/uploads/')}
 for p,r in uploads.items():(D/task/Path(p).name).write_text(r['content'])
 starts=[r for r in rpc if r['method']=='StartTrial'];answers=[r for r in rpc if r['method']=='Answer']
 write(f'{task}/context.json',{'instruction':starts[0]['response']['instruction'],'uploads':list(uploads),'identity':[r for r in rpc if r['method']=='Exec'],'answer':answers,'llm_events':[e for e in events if e['kind'].startswith('llm_')],'official_trial':trial})
 reports.append({'task_id':task,'trial_id':trial['trial_id'],'trace_bytes':len(trace),'trace_sha256':sha(trace),'events':len(events),'reused_events':len(original),'new_events':len(index)-len(original),'rpc_pairs':len(rpc),'unique_read_files':len(files),'read_calls':len(fileledger),'tree_calls':len(trees),'uploads':list(uploads),'event_kinds':dict(collections.Counter(e['kind'] for e in events))})
write('verification.json',{'status':'PASS','missing_only_harvest':True,'downloaded_events':len(new),'downloaded_bytes':sum(map(len,new.values())),'complete_traces':reports,'scope':'Archived read observations only; not a snapshot of unread world nodes or a new model/task evaluation.'})
print(json.dumps(reports,indent=2))
