"""Reassemble exact supplementary request events; no full-trial CAS claim."""
import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
plan=json.loads((P/'harvest-plan.json').read_text());bykey={(x['job'],x['seq']):x for x in plan};parts={};seqs=[]
for f in sorted((P/'receipts').glob('chunk-*.json')):
 x=json.loads(f.read_text());q,r=x['request'],x['response'];assert q['session']=='s8272' and q['seq']==r['data']['seq'] and r['code']==0 and not r['data']['output_truncated'];seqs.append(q['seq'])
 m=re.search(r'trace_event\("([a-z0-9]+)", (\d+), offset=(\d+), limit=(\d+)\)',q['source']);assert m
 job,s,o,lim=m.groups();s,o,lim=int(s),int(o),int(lim);c=json.loads(r['output']);b=c['text'].encode();p=bykey[job,s]
 assert c['seq']==s and c['bytes']==p['index']['data']['trace']['bytes'] and len(b)<=lim and c['next_offset']==o+len(b) and c['more']==(o+len(b)<c['bytes'])
 parts.setdefault((job,s),[]).append((o,b))
assert seqs==list(range(2,97)) and set(parts)==set(bykey)
out=[];(P/'supplementary').mkdir(exist_ok=True)
for key,p in bykey.items():
 b=b''
 for off,part in sorted(parts[key]):assert off==len(b);b+=part
 e=json.loads(b);idx=p['index'];assert len(b)==idx['data']['trace']['bytes'] and e['seq']==idx['seq'] and e['kind']==idx['kind'] and e['data']['trial_id']==idx['data']['trial_id'] and e['data']['call']==idx['data']['call']
 if 'time' in idx:assert e['time']==idx['time']
 rel=f"supplementary/{p['source']}-{p['task']}-{e['seq']}.json";(P/rel).write_bytes(b)
 out.append(dict(path=rel,job=p['job'],source=p['source'],task=p['task'],seq=e['seq'],call=e['data']['call'],bytes=len(b),sha256=sha(b),indexed_trace_offset=idx['data']['trace']['offset'],trace_scope=idx['data']['trace']['scope'],complete_event=True))
(P/'request-reassembly.json').write_text(json.dumps({'events':out,'receipt_chunks':95,'full_trial_CAS_reassembled':False,'scope':'Exact indexed selected event byte ranges; raw events matched lengths/identities/offset receipts. Original and supplementary selected bodies do not constitute all trial bytes.'},indent=2)+'\n')
print('PASS:31 exact request events from95 chunks; indexed byte ranges verified.')
