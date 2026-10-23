import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text());sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
ins={x['task_id']:json.loads(x['event']['text'])['data']['response']['instruction'] for x in load(P/'instructions-all100.json')}
def events(t):return [json.loads(s) for s in (P/(t+'-events.ndjson')).read_text().splitlines()]
def reads(t):return [e for e in events(t) if e['kind']=='rpc_response' and e['data']['method']=='Read']
counts=[]
for t,n in [('t005',3),('t065',2)]:
 e=next(e for e in reads(t) if '/locations/' in e['data']['response']['path']);d=e['data']['response'];store=json.loads(d['content']);inventory={x['sku']:x for x in store['inventory']};rows=[]
 for sku in re.findall(r'PT-[A-Z0-9-]+',ins[t]):
  observed=inventory.get(sku);on=(observed or {}).get('on_hand',0);reserved=(observed or {}).get('reserved',0)
  rows.append(dict(sku=sku,observed_row=observed,same_day=max(on-reserved,0),matches=on>=n and max(on-reserved,0)<n))
 count=sum(x['matches'] for x in rows);assert count==(0 if t=='t005' else 1)
 counts.append(dict(task=t,read_seq=e['seq'],path=d['path'],sha256=d['sha256'],threshold=n,rows=rows,recomputed_count=count,missing_catalogue_reads=True,scope='Arithmetic checked on actual store records; missing product rows count zero. No product path is inferred or fetched.'))
(P/'inventory-count-verification.json').write_text(json.dumps(counts,indent=2)+'\n')
uploads=[]
for t in ('t043','t056','t063','t076'):
 es=events(t);rs=[e for e in reads(t) if e['data']['response']['path'].startswith('/uploads/')];d=rs[0]['data']['response'];assert all(e['data']['response']==d for e in rs)
 (P/(t+'-uploaded-ocr.txt')).write_text(d['content'])
 req=[e for e in es if e['kind']=='llm_request'];contexts=[]
 for e in [req[1],req[-1]]:
  msgs=e['data']['request']['messages'];contexts.append(dict(seq=e['seq'],messages=len(msgs),path_present=any(d['path'] in m['content'] for m in msgs),full_exact_ocr_present=any(d['content'] in m['content'] for m in msgs)))
 uploads.append(dict(task=t,path=d['path'],read_response_seqs=[e['seq'] for e in rs],content_sha256=d['sha256'],utf8_bytes=len(d['content'].encode()),envelope_keys=sorted(d),truncation_fields={k:v for k,v in d.items() if 'trunc' in k.lower()},identical_observed_rereads=True,first_and_final_main_requests=contexts,scope='No truncation field is different from an explicit false field. These exact captured Read envelopes and visible contexts do not establish hidden world completeness.'))
(P/'upload-context-review.json').write_text(json.dumps(uploads,indent=2)+'\n')
video=[]
for e in reads('t047'):
 d=e['data']['response']
 if 'PT-DIG-VIDEO-' in d['path']:
  x=json.loads(d['content']);video.append(dict(seq=e['seq'],path=d['path'],sha256=d['sha256'],sku=x['sku'],family_id=x['family_id'],price_cents=x['price_cents'],properties=x['properties'],below_4024=x['price_cents']<4024))
assert len(video)==3 and len({v['family_id'] for v in video})==1 and sum(v['below_4024'] for v in video)==1
(P/'video-family-review.json').write_text(json.dumps({'observed_records':video,'scope':'Three actual observed family records; no universal matcher or hidden oracle reconstructed.'},indent=2)+'\n')
def canonical_trial(t):
 es=events(t);return {'reads':[(e['data']['response']['path'],e['data']['response']['sha256']) for e in reads(t)],'rpc':[(e['kind'],e['data']['method'],e['data'].get('arguments',e['data'].get('response'))) for e in es if e['kind'] in ('rpc_request','rpc_response') and e['data']['method'] not in ('StartTrial','EndTrial')],'model_requests':[e['data']['request'] for e in es if e['kind']=='llm_request']}
control={t:canonical_trial(t) for t in ('t004','t014','t024')}
comparison={'tasks':list(control),'instruction_bytes_equal':len({ins[t] for t in control})==1,'comparisons':{k:all(control[t][k]==control['t004'][k] for t in control) for k in ('reads','rpc','model_requests')},'observed_read_path_hashes':{t:v['reads'] for t,v in control.items()},'scope':'Within this run only; equality covers listed observed Read bytes, all nonlifecycle RPC arguments/responses and exact model requests. No unobserved-world or cross-source causal claim.'}
(P/'dispatch-repeated-world-comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
print(json.dumps({'inventory_counts':[(x['task'],x['recomputed_count']) for x in counts],'uploads':uploads,'dispatch':comparison['comparisons']},indent=2))
