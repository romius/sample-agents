"""Losslessly restore transport-factored trace text using exact submitted source."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'closure/2026-10-22-inventory-integration/agent.py').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=='0cb742d544039b1d9dc4a862021ee1bfe3967c2ced8082756525e075b6c1ca67'
source_line=json.dumps(source.splitlines()[10])[1:-1]
def decode(obj):
 text=obj['encoded']
 for pattern in obj['patterns']:
  token='@@D5204_PATTERN_'+str(pattern['index'])+'@@'
  assert text.count(token)==pattern['count']
  value=(source_line if pattern['kind']=='source' else source_line[:pattern['length']] if pattern['kind']=='prefix' else pattern['char']*pattern['length'])
  assert len(value)==pattern['length'] and token not in value
  text=text.replace(token,value)
 assert len(text.encode())==obj['bytes']
 return text
if __name__=='__main__':
 seen=set()
 for f in sorted((P/'evidence').glob('trial-batch-*.json')):
  for item in json.loads(f.read_text()):
   task=item['task_id'];assert task not in seen;seen.add(task)
   (P/'traces'/f'{task}.ndjson').write_text(decode(item['trace']))
   (P/'traces'/f'{task}-index.json').write_text(decode(item['index']))
 print('Restored',len(seen),'complete traces/indexes; validation against official CAS is audit.py')
 parts=sorted([json.loads(f.read_text()) for f in (P/'evidence').glob('result-part-*.json')],key=lambda x:x['offset'])
 packed=''
 for part in parts:
  assert part['offset']==len(packed);packed+=part['text']
 assert len(packed)==parts[0]['chars'] and all(p['chars']==len(packed) for p in parts)
 obj=json.loads(packed);text=obj['encoded']
 for p in obj['patterns']:
  token='@@D5204_RESULT_PATTERN_'+str(p['index'])+'@@';assert text.count(token)==p['count'];text=text.replace(token,p['value'])
 assert len(text)==obj['original_chars']
 (P/'official-result.json').write_text(text+'\n')
 print('Restored full official result API object',len(text),'characters')
