from pathlib import Path
import copy,hashlib,json,runpy,shutil,ast
P=Path(__file__).resolve().parent
A=P.parent/'2026-10-23-output-budget-boundaries'
OLD=P.parent/'2026-10-23-d4353-receipt-handoff/diagnostic-runner'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda v:json.dumps(v,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
(P/'inputs').mkdir(exist_ok=True)
rows=json.loads((A/'decision-table.json').read_text())
requests={};pins=[]
for name,source,seq in [('A016','d4702',2642),('A074','d4702',10888),('B056','d4955',6732),('B076','d4955',9256)]:
 r=next(r for r in rows if r['source']==source and r['response_seq']==seq)
 assert r['null_content'] and r['finish_reason']=='stop' and r['next_phase']=='main'
 pin=r['next_request_pin'];file=A/pin['path']
 if file.suffix=='.ndjson':raw=next(b for b in file.read_bytes().splitlines(keepends=True) if json.loads(b)['seq']==r['next_request_seq'])
 else:raw=file.read_bytes()
 assert sha(raw)==pin['raw_event_sha256'] and len(raw)==pin['bytes']
 ev=json.loads(raw);q=ev['data']['request']
 assert q['model']=='openai/gpt-oss-120b' and q['reasoning']=={'effort':'medium'} and q['max_tokens']==2048 and q['temperature']==0
 assert q['provider']=={'only':['deepinfra/bf16'],'quantizations':['bf16'],'allow_fallbacks':False,'require_parameters':True} and q['stream'] is False
 assert set(q)=={'model','messages','reasoning','temperature','max_tokens','stream','provider'}
 (P/'inputs'/f'{name}-request-event.json').write_bytes(raw)
 (P/'inputs'/f'{name}-previous-boundary.json').write_text(json.dumps(r,indent=2)+'\n')
 pins.append({'fixture':name,'source':source,'job':r['job'],'trial_id':r['trial_id'],'trigger_response':seq,'request_seq':ev['seq'],'request_file_sha256':sha(raw),'canonical_wire_sha256':sha(canon(q)),'source_pin':pin})
 for arm,effort in [('M','medium'),('L','low')]:requests[name+'-'+arm]={'args':[q['model'],q['messages']],'kwargs':{'max_completion_tokens':2048,'reasoning':{'effort':effort},'temperature':0}}
for arm in ['M','L']:requests['V016-'+arm]=copy.deepcopy(requests['A016-M'])
steps=[]
for repeat in [1,2]:
 fixtures=['A016','A074','B056','B076','V016']
 if repeat==2:fixtures.reverse()
 for j,fixture in enumerate(fixtures):
  arms=['M','L'] if (j+repeat)%2 else ['L','M']
  for arm in arms:steps.append({'ordinal':len(steps)+1,'repeat':repeat,'fixture':fixture,'arm':arm,'request_canonical_sha256':sha(canon(requests[fixture+'-'+arm]))})
assert len(steps)==20
for fixture in ['A016','A074','B056','B076']:
 a=copy.deepcopy(requests[fixture+'-M']);a['kwargs']['reasoning']['effort']='low';assert a==requests[fixture+'-L']
assert requests['V016-M']==requests['V016-L']==requests['A016-M']
plan={'logical_calls':20,'calls':steps,'fixtures':pins,'visible_argument_bytes':{k:len(json.dumps(v).encode()) for k,v in requests.items()},'private_wire_encoding_verified':False}
assert max(plan['visible_argument_bytes'].values())<65536
(P/'call-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
bundle={'plan_sha256':sha((P/'call-plan.json').read_bytes()),'requests':requests,'steps':steps}
runner=(OLD/'runner.py').read_text().replace('RECEIPT_','NULL_FINAL_').replace('Receipt first-action diagnostic finished.','Null-final effort diagnostic finished.')
(P/'runner.py').write_text(runner)
shutil.copyfile(OLD/'inputs/lzpack.py',P/'inputs/lzpack.py')
tree=ast.parse(runner);parents={c:n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
attrs=[n for n in ast.walk(tree) if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='bitgn']
assert sorted(n.attr for n in attrs)==['answer','llm'] and all(isinstance(parents[n],ast.Call) and parents[n].func is n for n in attrs)
source='import json\nFROZEN=json.loads('+repr(json.dumps(bundle,ensure_ascii=True,separators=(',',':')))+')\n'+runner
packed=runpy.run_path(str(P/'inputs/lzpack.py'))['pack'](source)
captured=[];exec(packed,{'exec':captured.append});assert captured==[source] and len(packed.encode())<=65536
(P/'readable.py').write_text(source);(P/'agent.py').write_text(packed);(P/'frozen.json').write_text(json.dumps(bundle,indent=2)+'\n')
manifest={'status':'OFFLINE PREPARED NOT SUBMITTED','source_bytes':len(packed.encode()),'source_sha256':sha(packed.encode()),'readable_sha256':sha(source.encode()),'packer_sha256':sha((P/'inputs/lzpack.py').read_bytes()),'packer_Brain_revision':'d3268r2','logical_calls':20,'guest_retry':0,'ecom_actions':False,'max_visible_argument_bytes':max(plan['visible_argument_bytes'].values()),'private_wire_encoding_verified':False}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
