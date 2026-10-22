"""Freeze a paired prompt diagnostic; never a production benchmark agent."""
import copy
import hashlib
import json
import runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda obj:json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
upstream=ROOT/'2026-10-22-sku-evidence-review/upstream/prompts'
assert sha(upstream.read_bytes())=='1fca953f29e93d16870ad0c215591bfd83207b1f1f7277bc6d14c36955eeab47'
archive=json.loads(upstream.read_text())
worlds=json.loads((ROOT/'2026-10-22-clarification-review/world-fixtures.json').read_text())
ns={};exec((ROOT/'2026-10-22-sku-evidence-integration/readable.py').read_text().split('\nIX_RESULT=')[0],ns)
parent={};exec((ROOT/'2026-10-22-inventory-integration/readable.py').read_text().split('\nIX_RESULT=')[0],parent)
fixtures=[]
for name,event,tid,instruction,query,criteria in [
 ('archived_case_ambiguity','3116','t021',None,None,dict(kind='clarify',skus=['PT-IMP-DEW-DCF887-2AH','PT-IMP-DEW-DCF887-5AH'],reason='Both actual kit properties contain case; no battery size specified.')),
 ('archived_standard_head','5648','t041',None,None,dict(kind='unresolved',forbidden_sku='PT-GRD-MET-W18-125-FLAT',reason='Flat-head is not standard head. No record positively states standard head; clarify or retrieve instead of choosing from score.')),
 ('derived_exact_sku','3116','t021','need code: PT-IMP-DEW-DCF887-2AH. answer only with sku.','PT-IMP-DEW-DCF887-2AH',dict(kind='exact',sku='PT-IMP-DEW-DCF887-2AH',path='/proc/catalog/DeWalt/PT-IMP-DEW-DCF887-2AH.json',reason='Exact existing SKU with no contradictory qualifier.')),
 ('derived_unique_variant','3116','t021','need code: dewalt dcf887 xr kit 2x2.0Ah batteries and case. answer only with sku.','dewalt dcf887 xr kit 2x2.0Ah batteries case',dict(kind='exact',sku='PT-IMP-DEW-DCF887-2AH',path='/proc/catalog/DeWalt/PT-IMP-DEW-DCF887-2AH.json',reason='Actual 2AH kit explicitly has 2x2.0Ah batteries and case; 5AH and body differ.')),
]:
 request=copy.deepcopy(archive[event]['data']['request'])
 msgs=request['messages'];original=copy.deepcopy(request)
 pool=copy.deepcopy(worlds[tid]['products'])
 for scope in [ns,parent]:scope['WORLD'].update(dict(built=True,products=pool,stores=[],evidence=[]))
 if instruction is not None:
  msgs[7]['content']=instruction
  action=dict(tool='catalog',query=query)
  msgs[8]['content']=json.dumps(action)
  parent['INSTRUCTION']=instruction
  base=parent['world_tool'](action)
  msgs[9]['content']=json.dumps(action)+'\n'+json.dumps(base)
 else:
  instruction=msgs[7]['content'];action=json.loads(msgs[8]['content'])
  header,raw=msgs[9]['content'].split('\n',1);base=json.loads(raw)
  assert json.loads(header)==action
  parent['INSTRUCTION']=instruction
  assert parent['world_tool'](action)==base,(name,'archived catalogue differs')
  assert request==original
 ns['INSTRUCTION']=instruction
 enriched=ns['world_tool'](action)
 assert {k:v for k,v in enriched.items() if k!='sku_lookup_evidence'}==base
 assert 'sku_lookup_evidence' in enriched
 treated=copy.deepcopy(request)
 header=msgs[9]['content'].split('\n',1)[0]
 treated['messages'][9]['content']=header+'\n'+json.dumps(enriched)
 # The transport's pinned provider and non-streaming SDK preserve these settings.
 assert request.pop('stream') is False
 assert request.pop('provider')==dict(only=['deepinfra/bf16'],quantizations=['bf16'],allow_fallbacks=False,require_parameters=True)
 treated.pop('stream');treated.pop('provider')
 assert len(canonical(request))<65536 and len(canonical(treated))<65536
 fixtures.append(dict(case=name,provenance='exact archived request content' if name.startswith('archived') else 'derived request on frozen archived catalogue/policy/identity',
  archive_event=event,criteria=criteria,arms={'parent':request,'treatment':treated},
  request_sha256={'parent':sha(canonical(request)),'treatment':sha(canonical(treated))},
  attachment=dict(returned=enriched['sku_lookup_evidence']['returned_siblings'],eligible=enriched['sku_lookup_evidence']['eligible_indexed_siblings'],truncated=enriched['sku_lookup_evidence']['evidence_truncated'])))
# Balance arm order within each case: AB then BA. No outcome-driven adaptation.
plan=[]
for repeat in range(2):
 for index,fixture in enumerate(fixtures):
  arms=['parent','treatment'] if (repeat+index)%2==0 else ['treatment','parent']
  for arm in arms:plan.append(dict(case_index=index,case=fixture['case'],repeat=repeat,arm=arm,request_sha256=fixture['request_sha256'][arm]))
assert len(plan)==16
bundle=dict(fixtures=fixtures,plan=plan)
(HERE/'fixtures.json').write_text(json.dumps(bundle,indent=2)+'\n')
runtime=(HERE/'runner.py').read_text()
readable='import json\nFROZEN=json.loads('+repr(json.dumps(bundle))+')\n'+runtime
# ASCII escaping without changing runtime strings; packer operates on ASCII.
readable=readable.encode('ascii','backslashreplace').decode()
packed=runpy.run_path(str(ROOT/'2026-10-22-huffman-packing-review/pack.py'))['pack'](readable)
assert len(packed.encode())<=65536
(HERE/'readable.py').write_text(readable);(HERE/'agent.py').write_text(packed)
manifest=dict(purpose='16-call paired next-action diagnostic; not a task-solving agent, full100, score or promotion candidate',
 candidate_sha256=sha((ROOT/'2026-10-22-sku-evidence-integration/agent.py').read_bytes()),
 packed_bytes=len(packed.encode()),packed_sha256=sha(packed.encode()),readable_sha256=sha(readable.encode()),fixtures_sha256=sha((HERE/'fixtures.json').read_bytes()),
 model='openai/gpt-oss-120b',provider='deepinfra/bf16 pinned by SDK0.3.7',
 trials=1,queue='short',logical_model_calls=16,repeats=2,
 limitations=['Next action only: no subsequent model-requested tools executed.','Two repeats are not independent tasks or a full outcome estimate.','SDK may automatically retry eligible 429s; no custom retry.','Grade of carrier trial is irrelevant and must never be used for a record.'])
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
