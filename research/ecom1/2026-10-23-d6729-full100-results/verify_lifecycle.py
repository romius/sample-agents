"""Reassemble bounded lifecycle receipts; no semantic grades inferred."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 receipt=load(P/'receipts/seq-3.json')['response']
 assert receipt['data']['output_bytes']==69143 and receipt['data']['output_truncated']
 raw=receipt['output'][:24000]+''.join(load(P/f'receipts/seq-{n}.json')['response']['output'][:-1] for n in [4,5,6])
 assert len(raw.encode())==69143
 snapshot=load(P/'receipts/snapshot-01.json');assert json.loads(raw)==snapshot
 trials={r['task_id']:r for r in snapshot['result']['trials']};rows=[]
 dest=P/'lifecycle';dest.mkdir(exist_ok=True)
 for file in sorted((P/'receipts').glob('lifecycle-*.json')):
  receipt=load(file);response=receipt['response']
  assert response['code']==0 and not response['data']['output_truncated']
  assert "jc2949c1cd1b84139a2eac424ef598966" in receipt['request']['source']
  for record in json.loads(response['output']):
   task=record['task'];trial=trials[task];assert trial['trace']['sealed']
   assert record['index_complete_traversal'] and record['indexed_bytes']==trial['trace']['bytes']
   indexed={e['seq']:e for e in record['selected_index']};parts={}
   for entry in record['chunks']:
    c=entry['response'];seq=entry['request_seq'];off=entry['offset'];b=c['text'].encode()
    assert c['seq']==seq and c['bytes']==indexed[seq]['data']['trace']['bytes']
    assert len(b)<=entry['limit'] and off+len(b)==c['next_offset'] and c['more']==(c['next_offset']<c['bytes'])
    parts.setdefault(seq,[]).append((off,b))
   events=[];lines=[]
   for seq in sorted(indexed):
    b=b''
    for off,chunk in sorted(parts[seq]):assert off==len(b);b+=chunk
    assert len(b)==indexed[seq]['data']['trace']['bytes'];e=json.loads(b)
    assert e['seq']==seq and e['kind']==indexed[seq]['kind'] and e['data']['trial_id']==trial['trial_id']
    events.append(e);lines.append(b)
   (dest/f'{task}.ndjson').write_bytes(b''.join(lines))
   def only(kind,method=None):
    hit=[e for e in events if e['kind']==kind and (method is None or e['data'].get('method')==method)]
    assert len(hit)==1,(task,kind,method,len(hit));return hit[0]
   start=only('rpc_response','StartTrial');startdata=start['data']['response']
   assert startdata['taskId']==task and startdata['trialId']==trial['trial_id'] and startdata['runId']==snapshot['job']['run_id']
   answer=only('rpc_request','Answer');finished=only('agent_finished');only('rpc_request','StartTrial');only('rpc_response','Answer');only('rpc_request','EndTrial');only('rpc_response','EndTrial')
   stdout=finished['data']['output'];assert len(stdout.encode())==trial['output_bytes']==finished['data']['output_bytes']
   assert not [e for e in events if e['kind']=='agent_error']
   refs={str(e['seq']):{'sha256':sha(b),'bytes':len(b),'path':f'lifecycle/{task}.ndjson','trace_offset':indexed[e['seq']]['data']['trace']['offset']} for e,b in zip(events,lines)}
   rows.append({'task_id':task,'trial_id':trial['trial_id'],'instruction':startdata['instruction'],'instruction_sha256':sha(startdata['instruction'].encode()),'official_grade_at_snapshot':trial['grade'],'answer':answer['data']['arguments'],'full_stdout':stdout,'stdout_sha256':sha(stdout.encode()),'usage_at_snapshot':trial['usage'],'events':refs,'event_seqs':{'StartTrial_response':start['seq'],'Answer_request':answer['seq'],'agent_finished':finished['seq']},'indexed_events':record['indexed_event_count'],'retained_events':len(events),'sealed_trial_CAS':trial['trace'],'full_trial_CAS_reassembled':False,'evidence_scope':'Complete selected lifecycle events; no full-trial CAS or business-correctness verification yet.'})
 rows.sort(key=lambda r:r['task_id']);assert len({r['task_id'] for r in rows})==len(rows)==73
 assert {r['task_id'] for r in rows}=={t for t,r in trials.items() if r.get('trace',{}).get('sealed')}
 (P/'partial-review.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
 report={'status':'PASS partial lifecycle capture','completed_at_snapshot':73,'selected_trials':100,'captured_tasks':len(rows),'retained_lifecycle_events':sum(r['retained_events'] for r in rows),'grades_available':False,'snapshot_state':'running','snapshot_bytes':69143,'snapshot_sha256':sha(raw.encode()),'loss_capture_pending':'Grades unavailable until SubmitRun; no loss classification yet.','full_trial_CAS_reassemblies':0}
 (P/'partial-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
