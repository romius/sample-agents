"""Mechanical census and exact event linkage; no inference or semantic score."""
import ast,hashlib,json
from decimal import Decimal
from pathlib import Path
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();canon=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
FORCED='Stop working now. Reply with report_completion only:'
def phase(q):
 if q['messages'][-1]['content'].startswith(FORCED):return 'forced'
 if q['max_tokens']==1024:return 'router'
 assert q['max_tokens']==2048 and q['messages'][0]['content'].startswith('You are a pragmatic ecommerce operations assistant.');return 'main'
def brief(e):
 if e is None:return None
 d=e['data'];v=dict(seq=e['seq'],kind=e['kind'])
 if e['kind']=='llm_response':
  c=d['response']['choices'][0];v.update(call=d['call'],finish_reason=c['finish_reason'],content=c['message'].get('content'))
 elif e['kind']=='rpc_request':v.update(method=d['method'],arguments=d['arguments'])
 return v
rows=[];trials=[];population=[];verified=0
for source in ['d4702','d4955']:
 root=P/'upstream'/source;official=json.loads((root/'result.json').read_text());job=official['job']['id']
 for f in sorted(root.glob('t*-events.ndjson')):
  task=f.name[:4];raws=f.read_bytes().splitlines(keepends=True);es=[json.loads(b) for b in raws];idx=[e for page in json.loads((root/f'index-{task}.json').read_text()) for e in page['items']];ix={e['seq']:e for e in idx};provenance={e['seq']:{'path':str(f.relative_to(P)),'raw_event_sha256':sha(b),'bytes':len(b),'indexed_offset':ix[e['seq']]['data']['trace']['offset']} for e,b in zip(es,raws)}
  assert all(len(b)==ix[e['seq']]['data']['trace']['bytes'] for e,b in zip(es,raws));verified+=len(es)
  pages=json.loads((root/f'index-{task}.json').read_text());assert all(p['more'] for p in pages[:-1]) and not pages[-1]['more']
  off=0
  for entry in idx:assert entry['data']['trace']['offset']==off;off+=entry['data']['trace']['bytes']
  official_trial=next(t for t in official['result']['trials'] if t['task_id']==task);assert off==official_trial['trace']['bytes']
  for z in sorted((P/'supplementary').glob(source+'-'+task+'-*.json')):
   b=z.read_bytes();e=json.loads(b);assert e['seq'] not in provenance;es.append(e);provenance[e['seq']]={'path':str(z.relative_to(P)),'raw_event_sha256':sha(b),'bytes':len(b),'indexed_offset':ix[e['seq']]['data']['trace']['offset']};verified+=1
  es.sort(key=lambda e:e['seq']);byseq={e['seq']:e for e in es};responses=[e for e in es if e['kind']=='llm_response'];requests={e['data']['call']:e for e in es if e['kind']=='llm_request'}
  assert {e['seq'] for e in responses}=={e['seq'] for e in idx if e['kind']=='llm_response'}
  assert {e['seq'] for e in es if e['kind']=='rpc_request'}=={e['seq'] for e in idx if e['kind']=='rpc_request'}
  selected=[e for e in responses if e['data']['response']['choices'][0]['message'].get('content') is None or e['data']['response']['choices'][0]['finish_reason']=='length']
  population.append(dict(source=source,task=task,job=job,response_count=len(responses),selected_count=len(selected),all_indexed_responses_present=True,all_indexed_RPC_requests_present=True))
  if not selected:continue
  mutations=[brief(e) for e in es if e['kind']=='rpc_request' and (e['data']['method'] in ['Write','Delete'] or e['data']['method']=='Exec' and e['data']['arguments'].get('path') not in ['/bin/id','/bin/date'])]
  stdout=next(e for e in es if e['kind']=='agent_finished');answer=next(e for e in es if e['kind']=='rpc_request' and e['data']['method']=='Answer')
  finalreq=requests[responses[-1]['data']['call']];finalphase=phase(finalreq['data']['request']);totalmain=len(responses)-1-(finalphase=='forced')
  trials.append(dict(source=source,task=task,job=job,anomalies=len(selected),main_iterations=totalmain,final_phase=finalphase,final_request_event=finalreq['seq'],final_model_response=brief(responses[-1]),final_Answer=brief(answer),mutation_RPCs=mutations,stdout_event=stdout['seq'],stdout=stdout['data']['output'],all_indexed_RPCs_present=True))
  for e in selected:
   d=e['data'];c=d['response']['choices'][0];qev=requests[d['call']];q=qev['data']['request'];nextr=next((z for z in responses if z['seq']>e['seq']),None);nextqev=requests[nextr['data']['call']] if nextr else None;nextq=nextqev['data']['request'] if nextqev else None
   nextdispatch=next((z for z in es if z['seq']>e['seq'] and z['kind']=='rpc_request' and z['data']['method'] not in ['StartTrial','EndTrial']),None)
   before_next=[brief(z) for z in es if e['seq']<z['seq']<(nextqev['seq'] if nextqev else 10**9) and z['kind']=='rpc_request']
   assert not before_next
   old=q['messages'];new=nextq['messages'];prefix=0
   while prefix<min(len(old),len(new)) and old[prefix]==new[prefix]:prefix+=1
   kept=None
   if old==new[:len(old)]:kept={'type':'append_only','appended':new[len(old):]}
   else:
    for remove in range(2,len(old)-prefix+1,2):
     candidate=old[:prefix]+old[prefix+remove:]
     if candidate==new[:len(candidate)]:kept={'type':'deleted_contiguous_even_message_block','prefix':prefix,'removed_count':remove,'removed':old[prefix:prefix+remove],'appended':new[len(candidate):]};break
   usage=d['response']['usage'];m=c['message'];row=dict(source=source,task=task,job=job,trial_id=d['trial_id'],response_seq=e['seq'],full_response_id=d['response']['id'],call=d['call'],attempt=d.get('attempt'),status=d['status'],provider=d['response']['provider'],phase=phase(q),main_iteration=responses.index(e),request_seq=qev['seq'],request_pin=provenance[qev['seq']],response_pin=provenance[e['seq']],max_tokens=q['max_tokens'],reasoning=q['reasoning'],temperature=q['temperature'],finish_reason=c['finish_reason'],null_content=m.get('content') is None,content=m.get('content'),reasoning_text=m.get('reasoning'),native_tool_calls=m.get('tool_calls'),usage=usage,request_canonical_sha256=sha(canon(q)),message_json_bytes=len(json.dumps(old).encode()),message_count=len(old),next_request_seq=nextqev['seq'],next_request_pin=provenance[nextqev['seq']],next_phase=phase(nextq),next_request_canonical_sha256=sha(canon(nextq)),exact_repeat_request=q==nextq,next_message_json_bytes=len(json.dumps(new).encode()),next_message_count=len(new),message_delta=kept,next_model_response=brief(nextr),next_observed_dispatch=brief(nextdispatch),RPCs_before_next_inference=before_next,trial_mutation_RPCs=mutations)
   rows.append(row)
src={n:(P/'sources'/f'{n}-readable.py').read_text() for n in ['d4353','d4702','d4955']};tails={n:s[s.index('for index in range(0 if answered else MAX_STEPS):'):].replace('MSR(', 'bitgn.llm(') for n,s in src.items()};assert tails['d4353']==tails['d4702']==tails['d4955']
functions={}
for name,s in src.items():
 tree=ast.parse(s);functions[name]={n.name:{'line':n.lineno,'end_line':n.end_lineno,'source':ast.get_source_segment(s,n),'sha256':sha(ast.get_source_segment(s,n).encode())} for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['parse_step','first_action_object','route_policy_docs','MSR']}
context_old=json.loads((P/'supplementary/d4955-t076-9539.json').read_text())['data']['request']['messages'];context_new=json.loads((P/'supplementary/d4955-t076-9559.json').read_text())['data']['request']['messages']
assert context_old[:9]+context_old[13:]==context_new[:40]
context={'source':'d4955','task':'t076','request_events':[9539,9559],'old_message_count':44,'new_message_count':50,'unchanged_bootstrap_prefix':9,'removed_count':4,'removed_messages':context_old[9:13],'appended_count':10,'appended_messages':context_new[40:],'interpretation':'Exact endpoints show initial OCR Read pair and catalogue Tree pair removed; later OCR re-read present. Trimming call-by-call instant and semantic effect not inferred.'}
for name,obj in [('context-pressure.json',context),('decision-table.json',rows),('trial-boundaries.json',trials),('population.json',population),('source-comparison.json',{'normalized_main_forced_tails_identical':True,'normalization':'Only MSR( replaced by bitgn.llm( to compare guest transport wrapper call spelling; no other normalization.','functions':functions,'tail_sha256':sha(tails['d4353'].encode()),'selected_body_count_verified':verified})]: (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
lines=['# Every matching response in the archived loss-model population','', '| Source / task | Response / call / main step | Final content / finish | Completion tokens | Exact request → next request | Next model response / phase | Next actual RPC |','|---|---|---|---|---|---|---|']
for r in rows:
 n=r['next_observed_dispatch'];state=('null' if r['null_content'] else 'nonempty')+'/'+r['finish_reason'];lines.append(f"| {r['source']} {r['task']} | {r['response_seq']} / {r['call']} / {r['main_iteration']} | {state} | {r['usage']['completion_tokens']} | {r['request_seq']} → {r['next_request_seq']} | {r['next_model_response']['seq']} / {r['next_phase']} | {n['seq']} {n['method']} |")
lines+=['','All25 exact requests and immediate next requests are preserved. No RPC occurs between any selected response and its next inference request. The next RPC may follow further failed replies. No state-changing RPC is present in any of these six complete trial RPC-request indexes. See decision-table.json for full next action/arguments, response text, hashes, offsets, settings, usage and feedback.','']
(P/'decision-table.md').write_text('\n'.join(lines))
print(json.dumps({'population_responses':sum(x['response_count'] for x in population),'rows':len(rows),'phases':sorted(set(x['phase'] for x in rows)),'null_stop':sum(x['null_content'] and x['finish_reason']=='stop' for x in rows),'length':sum(x['finish_reason']=='length' for x in rows),'exact_repeat_requests':sum(x['exact_repeat_request'] for x in rows),'mutation_RPCs':sum(len(t['mutation_RPCs']) for t in trials),'tail_equivalent':True}))
