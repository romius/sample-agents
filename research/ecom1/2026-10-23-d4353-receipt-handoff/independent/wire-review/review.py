"""Saved request value analysis; no private encoder or provider invocation."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;I=P/'inputs'
sha=lambda b:hashlib.sha256(b).hexdigest()
provenance=json.loads((P/'input-provenance.json').read_text())
for n,pin in provenance.items():assert sha((I/n).read_bytes())==pin['sha256']
guide=json.loads((I/'sdk-guide.json').read_text())['output']
assert 'BitGN SDK 0.3.7' in guide and 'Model requests: <=64 KiB' in guide
assert 'Brain pins DeepInfra BF16' in guide and 'Omit provider: overrides raise' in guide
G={'json':json,'note_policy_read':lambda f,r:None}
exec((I/'observation.py').read_text()+'\n'+(I/'handoff.py').read_text(),G)
def encoded(x,ascii=True,compact=False):return json.dumps(x,ensure_ascii=ascii,**({'separators':(',',':')} if compact else {})).encode()
def variants(x):return {'escaped_default':len(encoded(x)),'escaped_compact':len(encoded(x,compact=True)),'utf8_default':len(encoded(x,ascii=False)),'utf8_compact':len(encoded(x,ascii=False,compact=True))}
requests={};reports=[]
for task in ['t023','t063','t043']:
 event=json.loads((I/f'{task}-model-request.ndjson').read_bytes());request=event['data']['request'];requests[task]=request
 policy=json.loads((I/f'{task}-policy.ndjson').read_bytes())['data']['response'];upload=json.loads((I/f'{task}-upload.ndjson').read_bytes())['data']['response']
 G['RECEIPT_PENDING'].clear();assert G['receipt_capture'](policy['path'],policy);assert G['receipt_capture'](upload['path'],upload)
 changed=G['receipt_handoff'](request['messages']);proposed={**request,'messages':changed}
 assert {k:v for k,v in proposed.items() if k!='messages'}=={k:v for k,v in request.items() if k!='messages'}
 if task=='t043':assert changed is request['messages']
 # Byte sizes of reserializations, not captured HTTP bodies.
 reports.append({'task_id':task,'actual_trace_seq':event['seq'],'actual_request_fields':list(request),'actual_messages':len(request['messages']),'projected_messages':len(changed),'source_events_seq':[json.loads((I/f'{task}-{kind}.ndjson').read_bytes())['seq'] for kind in ['policy','upload']], 'actual_request_serializations':variants(request),'projected_request_serializations':variants(proposed),'projected_messages_serializations':variants(changed),'default_envelope_overhead':len(encoded(request))-len(encoded(request['messages'])),'projected_default_envelope_overhead':len(encoded(proposed))-len(encoded(changed)),'unchanged_nonmessage_values':True,'hypothetical_not_wire':True})
settings={k:v for k,v in requests['t023'].items() if k!='messages'}
assert all({k:v for k,v in r.items() if k!='messages'}==settings for r in requests.values())
def envelope(messages):return {**settings,'messages':messages}
# Explicit additive decomposition for observed model/provider/settings envelope.
empty_msgs=[];cumulative={'messages':empty_msgs};overhead=[{'added_field':'messages object wrapper','default_bytes_increment':len(encoded(cumulative))-len(encoded(empty_msgs))}];previous=len(encoded(cumulative))
for key in ['model','reasoning','temperature','max_tokens','stream','provider']:
 cumulative[key]=settings[key];now=len(encoded(cumulative));overhead.append({'added_field':key,'default_bytes_increment':now-previous});previous=now
assert previous==len(encoded(envelope(empty_msgs)))
# Default JSON includes spaces and escapes every non-ASCII codepoint; for this
# four-serialization family it is the largest, not a universal wire upper bound.
stress=[]
for name,body in [('ascii','A'*8900),('CJK','中'*2200),('emoji','😀'*1100),('quotes_backslashes','"\\'*3500),('newlines','row\n'*2200)]:
 messages=[{'role':'system','content':'policy'},{'role':'user','content':body}]
 s=variants(envelope(messages));assert s['escaped_default']==max(s.values())
 stress.append({'case':name,'content_characters':len(body),'content_utf8_bytes':len(body.encode()),'envelope_serializations':s})
# The exact conservative bound is conditional on this observed envelope and
# Python default (or one of the measured no-larger) JSON serializations.
overhead_bytes=len(encoded(envelope([])))-len(encoded([]));assert overhead_bytes==reports[0]['default_envelope_overhead']
limits=[]
for cap in [54000,56000]:limits.append({'message_list_default_byte_cap':cap,'envelope_default_bytes_at_cap':cap+overhead_bytes,'margin_to_65536':65536-cap-overhead_bytes,'conditional_on_observed_fields_and_serialization':True})
# Original source-derived history witness, rerun with the full archived envelope.
base=[{'role':'system','content':'policy'},{'role':'user','content':'b'*44000}]
policy={'path':'/docs/availability-checks.md','content':'max(on_hand - reserved, 0); absent from a branch inventory','sha256':'x'*64,'contentType':'text/plain'}
upload={'path':'/uploads/receipt.txt','content':'x'*8900,'sha256':'x'*64,'contentType':'text/plain'}
G['RECEIPT_PENDING'].clear();G['receipt_capture'](policy['path'],policy);G['receipt_capture'](upload['path'],upload);handed=G['receipt_handoff'](base)
f={'tool':'read','path':'/docs/next.txt'};pair=[{'role':'assistant','content':json.dumps(f)},{'role':'user','content':G['observation'](f,{'content':'中'*2200})}]
old=handed+pair;new,bc,added=G['receipt_pressure'](old,len(handed),2);assert new==base+pair
stop={'role':'user','content':'Stop working now. Reply with report_completion only: the best supported answer, the matching outcome and the exact refs you read.'}
forced,b2,a2=G['receipt_pressure'](old+[stop],len(handed),2);assert forced==base+pair+[stop]
large=[{'role':'assistant','content':'read'},{'role':'user','content':'中'*10000}]
inherited,b3,a3=G['receipt_pressure'](handed+large,len(handed),2);assert inherited==base+large
histories={name:{'messages_bytes':len(encoded(messages)),'full_observed_envelope_bytes':len(encoded(envelope(messages))),'under_65536_default':len(encoded(envelope(messages)))<=65536} for name,messages in [('parent',base+pair),('initial_prototype',old),('revision2_main',new),('revision2_forced',forced),('parent_forced',base+pair+[stop]),('inherited_parent_oversize',inherited)]}
assert histories['initial_prototype']['under_65536_default'] is False and histories['revision2_main']['under_65536_default'] is True
r={'status':'offline request-value projections pass bounded conditional size checks; private encoder unverified','guide':'SDK0.3.7','observed_nonmessage_request_values':settings,'actual_request_projections':reports,'overhead_decomposition':overhead,'default_nonmessage_envelope_overhead':overhead_bytes,'conditional_cap_envelopes':limits,'serialization_stress':stress,'long_history_and_forced':histories,'what_is_observed':['actual llm_request event request object values','provider/model/settings as recorded','Read bytes transferred in counterfactual projected objects'],'what_is_not_observed':['raw HTTP body bytes sent to OpenRouter','private SDK serializer/transport implementation','whether 64KiB guard measures exactly the trace request serialization','HTTP headers or provider-internal forwarding encodings'],'no_private_encoder_claim':True,'no_global_request_bound_claim':True,'model_calls':0,'network_calls':0,'input_pins':{n:x['sha256'] for n,x in provenance.items()}}
(P/'results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'projection':reports,'overhead':overhead_bytes,'limits':limits,'history':histories},indent=2))
