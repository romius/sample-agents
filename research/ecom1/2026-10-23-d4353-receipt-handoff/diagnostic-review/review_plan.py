"""Independent frozen-plan identities and source-data isolation; no semantic scorer."""
import collections,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;Q=P.parent/'diagnostic-plan';ROOT=Q.parents[3]
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
load=lambda f:json.loads(f.read_text())
seal=load(Q/'SHA256SUMS.json')
for n,pin in seal.items():
 b=(Q/n).read_bytes();assert sha(b)==pin['sha256']
 if 'bytes' in pin:assert len(b)==pin['bytes']
deps=load(Q/'dependency-pins.json')
for n,pin in deps.items():b=(ROOT/n).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256']
manifest=load(Q/'request-manifest.json');calls=load(Q/'call-plan.json')['calls'];caps=load(Q/'whole-agent-captures.json')['captures']
assert len(manifest)==10 and len(calls)==20 and len(caps)==8
requests={};groups=collections.defaultdict(list)
for row in manifest:
 b=(Q/row['path']).read_bytes();r=json.loads(b);key=(row['fixture'],row['arm']);assert key not in requests;requests[key]=r
 assert b==canon(r)+b'\n' and sha(b)==row['file_sha256'] and sha(canon(r))==row['request_canonical_sha256']
 assert sha(canon(r['args'][1]))==row['messages_canonical_sha256']
 assert r['args'][0]=='openai/gpt-oss-120b' and r['kwargs']=={'max_completion_tokens':2048,'reasoning':{'effort':'medium'},'temperature':0}
 groups[sha(canon(r))].append('-'.join(key))
expected=[(1,'A023','P'),(1,'A023','H'),(1,'A063','H'),(1,'A063','P'),(1,'B023','P'),(1,'B023','H'),(1,'U063','H'),(1,'U063','P'),(1,'V063','P'),(1,'V063','H'),(2,'V063','H'),(2,'V063','P'),(2,'U063','P'),(2,'U063','H'),(2,'B023','H'),(2,'B023','P'),(2,'A063','P'),(2,'A063','H'),(2,'A023','H'),(2,'A023','P')]
for i,(c,expected_key) in enumerate(zip(calls,expected),1):
 assert c['ordinal']==i and (c['repeat'],c['fixture'],c['arm'])==expected_key
 assert c['request_canonical_sha256']==sha(canon(requests[c['fixture'],c['arm']]))
 for field in manifest[0]:assert c[field]==next(r for r in manifest if (r['fixture'],r['arm'])==(c['fixture'],c['arm']))[field]
for fixture in ['A023','A063','B023','U063']:
 p,h=requests[fixture,'P'],requests[fixture,'H'];assert h['args'][1][:-2]==p['args'][1]
 assert [json.loads(m['content'].split('\n',1)[0])['tool'] for m in h['args'][1][-2:]]==['read','read']
 for arm in ['P','H']:
  cap=next(c for c in caps if (c['fixture'],c['arm'])==(fixture,arm))
  assert cap['requests'][1]==requests[fixture,arm] and len(cap['requests'])==2 and cap['engine']=='native'
  assert not cap['derivations'] and all(call[0] not in ['Write','Delete'] for call in cap['calls'])
 assert next(c for c in caps if (c['fixture'],c['arm'])==(fixture,'P'))['calls']==next(c for c in caps if (c['fixture'],c['arm'])==(fixture,'H'))['calls']
assert requests['V063','P']==requests['V063','H']==requests['A063','H']
assert requests['A023','P']==requests['B023','P'] and requests['A063','P']==requests['U063','P']
# Ensure declared synthetic overlays alter only content/hash of the actual Read.
overlays=[]
for fixture,base in [('B023','A023'),('U063','A063')]:
 for arm in ['P','H']:
  cap=next(c for c in caps if (c['fixture'],c['arm'])==(fixture,arm));assert len(cap['overlays'])==1
  o=cap['overlays'][0];before,after=o['before'],o['after']
  assert {k:v for k,v in before.items() if k not in ['content','sha256']}=={k:v for k,v in after.items() if k not in ['content','sha256']}
  assert after['content'].startswith(before['content']) and sha(before['content'].encode())==before['sha256'] and sha(after['content'].encode())==after['sha256']
  suffix=after['content'][len(before['content']):]
  if arm=='H':
   req=requests[fixture,arm];prior=requests[base,arm];assert req['args'][1][:-1]==prior['args'][1][:-1]
   assert suffix in req['args'][1][-1]['content'] and req['args'][1][-1]['role']=='user'
   assert all(suffix not in m['content'] for m in req['args'][1][:-1])
  else:assert suffix not in str(requests[fixture,arm])
 overlays.append({'fixture':fixture,'before_after_content_hashes_verified':True,'only_upload_content_hash_changed':True,'H_only_final_user_read_exposure':True,'P_prompt_identical_to_primary':True})
template=load(Q/'manual-review-template.json');assert len(template)==20
for t,c in zip(template,calls):assert all(t[k]==c[k] for k in ['ordinal','fixture','arm','repeat','request_canonical_sha256'])
logicalgroups=collections.Counter(c['request_canonical_sha256'] for c in calls)
settings={'model':'openai/gpt-oss-120b','reasoning':{'effort':'medium'},'temperature':0,'max_tokens':2048,'stream':False,'provider':{'only':['deepinfra/bf16'],'quantizations':['bf16'],'allow_fallbacks':False,'require_parameters':True}}
request_sizes=[{'request':'-'.join(k),'SDK_arguments_default_bytes':len(json.dumps(v).encode()),'observed_envelope_projection_default_bytes':len(json.dumps({**settings,'messages':v['args'][1]}).encode())} for k,v in requests.items()]
result={'status':'frozen plan structural and causal-scope review passed; no model-result claim','plan_seal_sha256':sha((Q/'SHA256SUMS.json').read_bytes()),'sealed_files':len(seal),'dependency_files':len(deps),'exact_logical_cells':20,'unique_request_hashes':len(groups),'prompt_alias_groups':[{'requests':v,'logical_calls':logicalgroups[k],'sha256':k} for k,v in groups.items()],'captured_native_executions_checked':8,'native_executions_rerun_here':0,'overlays':overlays,'sizes':request_sizes,'manual_rubric_not_auto_scored':True,'provider_wire_unverified':True,'ordered_plan_preserved':True,'model_calls':0,'mutation_of_frozen_plan':False}
(P/'plan-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['sizes','prompt_alias_groups','overlays']},indent=2))
