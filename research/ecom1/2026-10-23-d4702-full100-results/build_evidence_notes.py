"""Extract readable evidence without interpreting grades as a semantic oracle."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
rows={x['task_id']:x for x in load(P/'all100-review.json')}
counterexamples=[];lines=['# Loss action and final-content evidence','',
 'Exact full event bytes remain in the corresponding task NDJSON and raw receipts. This view omits reasoning text and repetitive Read requests. Null final content is reported explicitly.','']
for review in load(P/'loss-review.json'):
 task=review['task'];events=[json.loads(x) for x in (P/f'{task}-events.ndjson').read_text().splitlines()]
 lines+=['## '+task+' — '+review['category'],'',rows[task]['instruction'],'',review['finding'],'','Uncertainty: '+review['uncertainty'],'']
 for e in events:
  d=e['data']
  if e['kind']=='llm_response':
   lines+=['- Event '+str(e['seq'])+', HTTP '+str(d.get('status'))+': '+json.dumps([(c['finish_reason'],c['message'].get('content')) for c in d['response'].get('choices',[])],ensure_ascii=False)]
  if e['kind']=='rpc_request' and d['method'] in ['Write','Delete','Exec','Answer']:
   lines+=['- Event '+str(e['seq'])+', '+d['method']+': '+json.dumps(d['arguments'],ensure_ascii=False)]
  if e['kind']=='agent_finished':
   lines+=['','Actual stdout before usage snapshot:','','```text',d['output'].split("{'job':",1)[0].rstrip(),'```','']
 if task in ['t022','t042','t062']:
  answer=next(e for e in events if e['kind']=='rpc_request' and e['data']['method']=='Answer')
  final=next(e for e in reversed(events) if e['kind']=='llm_response')
  action=json.loads(final['data']['response']['choices'][0]['message']['content'])
  policy=next(e for e in events if e['kind']=='rpc_response' and e['data']['method']=='Read' and e['data']['response'].get('path')=='/docs/catalogue-lookup.md')
  model_refs=action['grounding_refs'];final_refs=answer['data']['arguments']['refs']
  counterexamples.append({'task':task,'instruction':rows[task]['instruction'],
   'policy_event_seq':policy['seq'],'exact_policy':policy['data']['response']['content'],
   'model_event_seq':final['seq'],'model_grounding_refs':model_refs,
   'answer_event_seq':answer['seq'],'actual_answer_refs':final_refs,
   'added_after_model':[x for x in final_refs if x not in model_refs],
   'official_grade':rows[task]['official_grade'],
   'finding':review['finding'],'uncertainty':review['uncertainty'],
   'source_mechanism':'merged_refs adds seen/read /proc path whose basename appears in tokens_of(message + INSTRUCTION); policy context differs between cases.'})
(P/'excluded-sku-counterexamples.json').write_text(json.dumps(counterexamples,indent=2,ensure_ascii=False)+'\n')
(P/'loss-action-summary.md').write_text('\n'.join(lines)+'\n')
fallback=[]
for task,ocrseq,reqseq in [('t016',2628,2629),('t023',3571,3818),('t043',6351,6376),('t063',9369,9616)]:
 es={e['seq']:e for e in [json.loads(x) for x in (P/f'{task}-events.ndjson').read_text().splitlines()]}
 assert es[ocrseq]['kind']=='rpc_response' and es[reqseq]['kind']=='llm_request'
 ocr=es[ocrseq]['data']['response'];request=es[reqseq]['data']['request'];messages=request['messages']
 joined='\n'.join(str(x.get('content','')) for x in messages)
 fallback.append({'task':task,'ocr_read_response_seq':ocrseq,'ocr_path':ocr['path'],
  'ocr_sha256':hashlib.sha256(ocr['content'].encode()).hexdigest(),'model_request_seq':reqseq,
  'entire_ocr_visible_in_model_messages':ocr['content'] in joined,
  'ocr_path_visible_in_model_messages':ocr['path'] in joined,'model_messages':len(messages),
  'selection':'first main request after helper decline' if task!='t043' else 'last main request, after model explicitly reread OCR'})
(P/'fallback-context-review.json').write_text(json.dumps(fallback,indent=2)+'\n')
print('Saved all17 loss action summaries and three policy-sensitive reference counterexamples.')
