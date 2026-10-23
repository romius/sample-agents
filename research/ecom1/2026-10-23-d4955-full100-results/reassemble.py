"""Verify selected immutable receipts; complete scopes must match official CAS."""
import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def assemble(task):
    index=[e for p in load(P/f'index-{task}.json') for e in p['items']]
    byseq={e['seq']:e for e in index};parts={}
    for file in sorted((P/'receipts').glob(f'{task}-*.json')):
        receipt=load(file);r=receipt['response'];request=receipt['request']
        assert r['code']==0 and not r['data']['output_truncated']
        reqs=re.findall(r"trace_event\('j37e3df7ac8564c0899c81a706e0aea9a',(\d+),offset=(\d+),limit=(\d+)\)",request['source'])
        chunks=json.loads(r['output']);assert len(reqs)==len(chunks)
        for (seq,off,lim),c in zip(reqs,chunks):
            seq,off,lim=map(int,(seq,off,lim));raw=c['text'].encode()
            assert seq==c['seq'] and len(raw)<=lim and off+len(raw)==c['next_offset']
            assert c['bytes']==byseq[seq]['data']['trace']['bytes']
            assert c['more']==(c['next_offset']<c['bytes'])
            parts.setdefault(seq,[]).append((off,raw))
    events=[];raws=[]
    for seq in sorted(parts):
        raw=b''
        for off,b in sorted(parts[seq]):
            assert off==len(raw),(task,seq,off,len(raw));raw+=b
        assert len(raw)==byseq[seq]['data']['trace']['bytes']
        event=json.loads(raw);assert event['seq']==seq and event['kind']==byseq[seq]['kind']
        events.append(event);raws.append(raw)
    complete=set(parts)==set(byseq)
    raw=b''.join(raws);h=hashlib.sha256(raw).hexdigest()
    if complete:
        offset=0
        for e in index:
            assert e['data']['trace']['offset']==offset
            offset+=e['data']['trace']['bytes']
        trial=next(t for t in load(P/'result.json')['result']['trials'] if t['task_id']==task)
        assert trial['trace']['sealed'] and trial['trace']['bytes']==len(raw) and trial['trace']['blob']==h
    (P/f'{task}-events.ndjson').write_bytes(raw)
    return {'task':task,'events':len(events),'indexed_events':len(index),'complete_scope':complete,'bytes':len(raw),'sha256':h,'cas_matched':complete}
if __name__=='__main__':
    import sys
    results=[assemble(t) for t in (sys.argv[1:] or [p.stem.removeprefix('index-') for p in sorted(P.glob('index-t*.json'))])]
    (P/'reassembly-verification.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
