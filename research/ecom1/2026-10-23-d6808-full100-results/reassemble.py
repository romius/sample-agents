"""Exact byte-offset assembly; certify a complete task only against official CAS."""
import json,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent
JOB='jb4798f05fa4941f88eacf20a40f42800'
def main():
 index={};parts={}
 for f in sorted(P.glob('index-t*.json')):
  for page in json.loads(f.read_text()):
   for e in page['items']:assert e['seq'] not in index;index[e['seq']]=(f.stem[6:],e)
 for f in sorted((P/'receipts').glob('full-initial-*.json')):
  r=json.loads(f.read_text());resp=r['response'];assert resp['code']==0 and not resp['data']['output_truncated']
  reqs=re.findall(r'trace_event\("'+JOB+r'",(\d+),offset=(\d+),limit=(\d+)\)',r['request']['source']);chunks=json.loads(resp['output']);assert len(reqs)==len(chunks)
  for (seq,off,lim),c in zip(reqs,chunks):
   seq,off,lim=map(int,(seq,off,lim));b=c['text'].encode();e=index[seq][1]
   assert seq==c['seq'] and len(b)<=lim and off+len(b)==c['next_offset'] and c['bytes']==e['data']['trace']['bytes'] and c['more']==(c['next_offset']<c['bytes'])
   parts.setdefault(seq,[]).append((off,b))
 trials={t['task_id']:t for t in json.loads((P/'result-initial.json').read_text())['result']['trials']};report=[]
 for task in sorted({t for t,e in index.values()}):
  out=b'';count=0
  for seq,(t,e) in sorted(index.items()):
   if t!=task:continue
   b=b''
   for off,chunk in sorted(parts[seq]):assert len(b)==off;b+=chunk
   assert len(b)==e['data']['trace']['bytes'];d=json.loads(b);assert d['seq']==seq and d['kind']==e['kind'] and d['data'].get('trial_id')==trials[t]['trial_id']
   assert e['data']['trace']['offset']==len(out);out+=b;count+=1
  trace=trials[task]['trace'];assert trace['sealed'] and trace['bytes']==len(out) and trace['blob']==hashlib.sha256(out).hexdigest();(P/(task+'-events.ndjson')).write_bytes(out)
  report.append({'task_id':task,'complete_events':count,'bytes':len(out),'sha256':trace['blob'],'official_CAS_match':True})
 (P/'reassembly-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
