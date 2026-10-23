import json,re
source=brain.read_bytes('d5204').decode()
source_line=json.dumps(source.splitlines()[10])[1:-1]
def encode(text):
 patterns=[source_line,source_line[:1800],source_line[:300]]+sorted(set(re.findall(r'~{100,}|\^{100,}',text)))
 encoded=text;meta=[]
 for i,value in enumerate(patterns):
  token='@@D5204_PATTERN_'+str(i)+'@@'
  assert token not in text
  count=encoded.count(value)
  meta.append({'index':i,'kind':'source' if i==0 else 'prefix' if i<3 else 'repeat','length':len(value),'char':value[0] if i>2 else '', 'count':count})
  encoded=encoded.replace(value,token)
 return {'patterns':meta,'encoded':encoded,'bytes':len(text.encode())}
def read_trial(task):
 index=brain.sandbox.trace('j2f9717b672c04c9a94f1df3219579692',trial=task,limit=100)
 assert not index['more']
 chunks=[]
 for item in index['items']:
  offset=0
  while True:
   part=brain.sandbox.trace_event('j2f9717b672c04c9a94f1df3219579692',item['seq'],offset=offset,limit=16000)
   chunks.append(part['text']);offset=part['next_offset']
   if not part['more']:break
  assert offset==item['data']['trace']['bytes']
 return {'task_id':task,'index':encode(json.dumps(index)),'trace':encode(''.join(chunks))}
