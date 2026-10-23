"""Reassemble exact selected completed-task events from bounded Brain receipts."""
import ast,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 raw=json.loads((P/'receipts/result-initial-raw.json').read_text());result=ast.literal_eval(raw['output'].splitlines()[0]);assert result==json.loads((P/'result-initial.json').read_text())
 trials={t['task_id']:t for t in result['result']['trials'] if t.get('trace',{}).get('sealed')};assert len(trials)==21
 rows=[]
 for f in sorted((P/'receipts').glob('selected-index-*.json')):
  r=json.loads(f.read_text())['response']
  if r['code']==0:
   assert not r['data']['output_truncated'];rows+=json.loads(r['output'])
 assert len(rows)==21;idx={e['seq']:(r['task_id'],e) for r in rows for e in r['selected_index']};got={}
 for f in sorted((P/'receipts').glob('tail-initial-*.json')):
  receipt=json.loads(f.read_text());r=receipt['response'];assert r['code']==0 and not r['data']['output_truncated']
  reqs=re.findall(r'trace_event\("jb4798f05fa4941f88eacf20a40f42800",(\d+),offset=(\d+),limit=(\d+)\)',receipt['request']['source']);chunks=json.loads(r['output']);assert len(reqs)==len(chunks)
  for (seq,off,lim),c in zip(reqs,chunks):
   seq,off,lim=map(int,(seq,off,lim));task,e=idx[seq];b=c['text'].encode();d=json.loads(b)
   assert seq==c['seq']==d['seq'] and off==0 and len(b)<=lim and len(b)==c['bytes']==c['next_offset']==e['data']['trace']['bytes'] and not c['more']
   assert d['data']['trial_id']==trials[task]['trial_id'] and d['kind']==e['kind'];assert (P/'events'/f'{task}-{seq}.json').read_bytes()==b
   assert seq not in got;got[seq]=d
 assert set(got)==set(idx)
 review=[]
 for task,t in sorted(trials.items()):
  es=[got[e['seq']] for r in rows if r['task_id']==task for e in r['selected_index']]
  def one(kind,method=None):
   matches=[e for e in es if e['kind']==kind and (method is None or e['data'].get('method')==method)];assert len(matches)==1;return matches[0]
  start=one('rpc_response','StartTrial');answer=one('rpc_request','Answer');ack=one('rpc_response','Answer');finish=one('agent_finished');end=one('rpc_response','EndTrial');instruction=start['data']['response']['instruction'];assert start['data']['response']['taskId']==task and start['data']['response']['runId']==result['result']['run_id']
  assert finish['data']['task_id']==task and len(finish['data']['output'].encode())==finish['data']['output_bytes']==t['output_bytes']
  review.append({'task_id':task,'trial_id':t['trial_id'],'official_trial_snapshot':t,'instruction':instruction,'instruction_sha256':sha(instruction.encode()),'answer':answer['data']['arguments'],'answer_ack':ack['data'],'agent_finished':finish['data'],'events':{'StartTrial':start['seq'],'Answer':answer['seq'],'Answer_ack':ack['seq'],'agent_finished':finish['seq'],'EndTrial_ack':end['seq']},'evidence_level':'Exact StartTrial/Answer/ack/complete stdout/end events from sealed task trace; full action-world/CAS not certified.'})
 (P/'completed-initial-evidence.json').write_text(json.dumps(review,indent=2,ensure_ascii=False)+'\n')
 check={'completed_sealed_tasks':21,'exact_events':len(got),'all_stdout_bytes_match':True,'instruction_identities_match':True,'full_trace_CAS_reassembled':False,'grades_pending':True,'source_sha256':sha((P/'source-closure/agent.py').read_bytes()),'reported_trial_model_calls':sum(t['usage']['model_calls'] for t in trials.values()),'agent_finished_model_calls':sum(r['agent_finished']['usage']['model_calls'] for r in review),'warning':'agent_finished usage is a zero placeholder, not paid accounting. Job summary is a partial snapshot; no score or loss classification yet.'}
 (P/'verification-initial.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps(check))
if __name__=='__main__':main()
