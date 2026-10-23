"""Verify completed capture only; does not imply a finished all100 audit."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
result=load(P/'result.json');pages=load(P/'receipts/final-result-pages.json')
raw=''.join(pages['parts']);assert len(raw.encode())==91665 and json.loads(raw)==result
assert result['job']['state']=='completed' and result['result']['completed_trials']==100
trials={t['task_id']:t for t in result['result']['trials']};rows=[]
for file in sorted(list((P/'receipts').glob('lifecycle-*.json'))+list((P/'final-receipts').glob('lifecycle-*.json'))):
 receipt=load(file);r=receipt['response'];assert r['code']==0 and not r['data']['output_truncated']
 for item in json.loads(r['output']):
  task=item['task'];trial=trials[task];assert trial['trace']['sealed'] and item['indexed_bytes']==trial['trace']['bytes']
  idx={e['seq']:e for e in item['selected_index']};parts={};events=[];pins=[]
  for entry in item['chunks']:
   c=entry['response'];seq=entry['request_seq'];b=c['text'].encode();off=entry['offset']
   assert seq==c['seq'] and c['bytes']==idx[seq]['data']['trace']['bytes'] and len(b)<=entry['limit']
   assert off+len(b)==c['next_offset'] and c['more']==(c['next_offset']<c['bytes'])
   parts.setdefault(seq,[]).append((off,b))
  for seq in sorted(idx):
   b=b''
   for off,chunk in sorted(parts[seq]):assert off==len(b);b+=chunk
   assert len(b)==idx[seq]['data']['trace']['bytes'];e=json.loads(b)
   assert e['seq']==seq and e['kind']==idx[seq]['kind'] and e['data']['trial_id']==trial['trial_id']
   events.append(e);pins.append({'seq':seq,'bytes':len(b),'sha256':sha(b),'offset':idx[seq]['data']['trace']['offset']})
  def only(kind,method=None):
   hits=[e for e in events if e['kind']==kind and (method is None or e['data'].get('method')==method)];assert len(hits)==1
   return hits[0]
  start=only('rpc_response','StartTrial')['data']['response'];answer=only('rpc_request','Answer');finished=only('agent_finished')['data']
  assert start['taskId']==task and start['trialId']==trial['trial_id'] and start['runId']==result['job']['run_id']
  assert len(finished['output'].encode())==trial['output_bytes']
  for kind,method in [('rpc_request','StartTrial'),('rpc_response','Answer'),('rpc_request','EndTrial'),('rpc_response','EndTrial')]:only(kind,method)
  assert not [e for e in events if e['kind']=='agent_error']
  rows.append({'task_id':task,'trial_id':trial['trial_id'],'instruction':start['instruction'],'instruction_sha256':sha(start['instruction'].encode()),'official_grade':trial['grade'],'answer':answer['data']['arguments'],'full_stdout':finished['output'],'stdout_sha256':sha(finished['output'].encode()),'receipt':str(file.relative_to(P)),'events':pins,'scope':'Selected lifecycle events only; no business correctness or full-trial CAS verification.'})
rows.sort(key=lambda r:r['task_id']);assert [r['task_id'] for r in rows]==['t'+str(n).zfill(3) for n in range(1,92)]
losses=[t for t in result['result']['trials'] if t['grade']['score']<1]
assert [t['task_id'] for t in losses]==[x['task_id'] for x in load(P/'loss-list.json')]
seal=load(P/'PARTIAL-SHA256SUMS.json')
for row in seal['files']:
 b=(P/row['path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256']
(P/'captured91-review.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
summary={'status':'PASS captured evidence, audit unfinished','official_completed_trials':100,'official_score':result['result']['run_score'],'captured_lifecycle_tasks':91,'retained_lifecycle_events':sum(len(r['events']) for r in rows),'missing_lifecycle_tasks':['t'+str(n).zfill(3) for n in range(92,101)],'graded_losses':len(losses),'complete_loss_indexes_captured':0,'full_trial_CAS_reassemblies':0,'final_result_print_bytes':len(raw.encode()),'final_result_print_sha256':sha(raw.encode()),'initial_partial_seal_unchanged':True}
(P/'handover-verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
