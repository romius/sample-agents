"""Prepare an offline source-applicability and evidence plan. No candidate changes."""
import ast,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
AUDIT=P.parent/'2026-10-23-d4702-full100-results'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,data):(P/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
parent=(AUDIT/'sources/d4353r1-readable.py').read_text()
observed=(AUDIT/'sources/d4702r1-readable.py').read_text()
assert sha(parent.encode())=='f898132a754187b0052a637e1ca4caaccdd3ac46f72df80bc11d2b37b3737d0b'
def functions(s):return {n.name:n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
a,b=functions(parent),functions(observed)
names=['receipt_availability','rcp_form','rcp_request','rcp_upload','rcp_items','rcp_product','rcp_store','receipt_refs','merged_refs','note_result','note_policy_read']
equal={name:ast.dump(a[name],include_attributes=False)==ast.dump(b[name],include_attributes=False) for name in names}
assert all(equal.values())
source_parts={name:{'line':a[name].lineno,'end_line':a[name].end_lineno,'sha256':sha(ast.get_source_segment(parent,a[name]).encode())} for name in names}
evidence=[]
for task,policyseq,uploadseq,requestseq in [('t023',3565,3571,3818),('t063',9363,9369,9616),('t043',6349,6351,6376)]:
 lines=(AUDIT/f'{task}-events.ndjson').read_bytes().splitlines(keepends=True)
 byseq={json.loads(line)['seq']:line for line in lines}
 # Select the actual availability policy Read by its response path, never by guessed ordinal.
 policies=[json.loads(line) for line in lines if json.loads(line)['kind']=='rpc_response' and json.loads(line)['data'].get('method')=='Read' and json.loads(line)['data']['response'].get('path')=='/docs/availability-checks.md']
 policy=policies[0];policyseq=policy['seq']
 upload=json.loads(byseq[uploadseq]);request=json.loads(byseq[requestseq])
 assert upload['kind']=='rpc_response' and request['kind']=='llm_request'
 for name,seq in [('policy',policyseq),('upload',uploadseq),('model-request',requestseq)]:
  (P/f'{task}-{name}.ndjson').write_bytes(byseq[seq])
 body=request['data']['request'];messages=body['messages'];content=upload['data']['response']['content'];path=upload['data']['response']['path']
 joined='\n'.join(str(m.get('content','')) for m in messages)
 # Size projection only: this is not a candidate or an SDK wire-conformance test.
 observations=[{'role':'user','content':json.dumps({'tool':'read','path':e['data']['response']['path']})+'\n'+e['data']['response']['content']} for e in [policy,upload]]
 proposed={**body,'messages':messages+observations}
 evidence.append({'task':task,'policy_read_seq':policyseq,'upload_read_seq':uploadseq,'model_request_seq':requestseq,
  'upload_path':path,'upload_content_sha256':sha(content.encode()),'upload_utf8_bytes':len(content.encode()),
  'full_upload_present_in_actual_messages':content in joined,'upload_path_present_in_actual_messages':path in joined,
  'actual_message_count':len(messages),'counterfactual_message_count':len(proposed['messages']),
  'actual_request_json_default_bytes':len(json.dumps(body).encode()),
  'hypothetical_policy_and_upload_request_json_default_bytes':len(json.dumps(proposed).encode()),
  'size_projection_limit':'Python default JSON serialization estimate only; actual SDK0.3.7/native request serialization must be checked before any candidate dispatch.',
  'case_role':'Lost helper-read source before first main request' if task!='t043' else 'Already-visible OCR control after explicit model reread; do not append duplicates'})
save('applicability.json',{'status':'Plan only; no candidate source, model calls or runtime experiment',
 'exact_parent':'d4353r1/d4354r1','parent_readable_sha256':sha(parent.encode()),'observed_source':'d4702r1',
 'same_function_AST':equal,'parent_function_locations':source_parts,
 'important_differences':['d4353 has direct bitgn.llm, d4702 wraps inference in MSR; all observed trigger replies were HTTP200.',
 'observation() differs in its Exec error branch; Read formatting and the receipt helper path are unchanged.',
 'Identical helper source establishes applicability of the boundary, not the same outcome in a different record-run world.'],
 'audit_seal_sha256':sha((AUDIT/'SHA256SUMS.json').read_bytes()),'evidence':evidence})
print(json.dumps(evidence,indent=2))
