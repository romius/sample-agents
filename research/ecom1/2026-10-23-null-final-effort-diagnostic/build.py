from pathlib import Path
import ast,copy,hashlib,json,runpy
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda v:json.dumps(v,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
for n,pin in json.loads((P/'DEPENDENCIES.json').read_text())['files'].items():
 b=(P/n).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256']
plan=json.loads((P/'call-plan.json').read_text());requests={}
for f in plan['fixtures']:
 name=f['fixture'];raw=(P/'inputs'/(name+'-request-event.json')).read_bytes();assert sha(raw)==f['request_file_sha256']
 e=json.loads(raw);q=e['data']['request'];assert sha(canon(q))==f['canonical_wire_sha256'] and e['seq']==f['request_seq']
 trigger=json.loads((P/'inputs'/(name+'-trigger-event.json')).read_text());choice=trigger['data']['response']['choices'][0]
 assert trigger['seq']==f['trigger_response'] and choice['message'].get('content') is None and choice['finish_reason']=='stop'
 assert q['model']=='openai/gpt-oss-120b' and q['reasoning']=={'effort':'medium'} and q['max_tokens']==2048 and q['temperature']==0
 assert q['provider']=={'only':['deepinfra/bf16'],'quantizations':['bf16'],'allow_fallbacks':False,'require_parameters':True} and q['stream'] is False
 assert set(q)=={'model','messages','reasoning','temperature','max_tokens','stream','provider'}
 for arm,effort in [('M','medium'),('L','low')]:requests[name+'-'+arm]={'args':[q['model'],q['messages']],'kwargs':{'max_completion_tokens':2048,'reasoning':{'effort':effort},'temperature':0}}
for arm in ['M','L']:requests['V016-'+arm]=copy.deepcopy(requests['A016-M'])
assert plan['logical_calls']==20 and len(plan['calls'])==20
for i,s in enumerate(plan['calls'],1):
 assert i==s['ordinal'] and sha(canon(requests[s['fixture']+'-'+s['arm']]))==s['request_canonical_sha256']
assert plan['visible_argument_bytes']=={k:len(json.dumps(v).encode()) for k,v in requests.items()} and max(plan['visible_argument_bytes'].values())<65536
bundle={'plan_sha256':sha((P/'call-plan.json').read_bytes()),'requests':requests,'steps':plan['calls']}
runtime=(P/'runner.py').read_text();original=(P/'inputs/original-runner-d6954.py').read_text()
assert runtime==original.replace('RECEIPT_','NULL_FINAL_').replace('Receipt first-action diagnostic finished.','Null-final effort diagnostic finished.')
tree=ast.parse(runtime);parents={c:n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
attrs=[n for n in ast.walk(tree) if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='bitgn']
assert sorted(n.attr for n in attrs)==['answer','llm'] and all(isinstance(parents[n],ast.Call) and parents[n].func is n for n in attrs)
source='import json\nFROZEN=json.loads('+repr(json.dumps(bundle,ensure_ascii=True,separators=(',',':')))+')\n'+runtime
packed=runpy.run_path(str(P/'inputs/lzpack.py'))['pack'](source);captured=[];exec(packed,{'exec':captured.append});assert captured==[source]
manifest=json.loads((P/'manifest.json').read_text());assert sha(packed.encode())==manifest['source_sha256'] and sha(source.encode())==manifest['readable_sha256'] and len(packed.encode())==manifest['source_bytes']<=65536
(P/'agent.py').write_text(packed);(P/'readable.py').write_text(source);(P/'frozen.json').write_text(json.dumps(bundle,indent=2)+'\n')
print('PASS exact requests, single effort intervention, original runner, source pins and packing')
