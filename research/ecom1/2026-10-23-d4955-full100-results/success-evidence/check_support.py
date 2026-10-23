"""Bounded checks over actual evidence; no automatic semantic grading."""
import csv,hashlib,io,json
from pathlib import Path
P=Path(__file__).resolve().parent
rows={r['task_id']:r for r in json.loads((P/'success-review.json').read_text())}
def event(t,s):return json.loads((P/f'events/{t}-{s}.ndjson').read_text())
def response(t,s):return event(t,s)['data']['response']
out={}
# Literal .tmp suffix and exactly acknowledged paths, no simulated filesystem.
entries=response('t039',4779)['entries'];wanted=sorted(e['path'] for e in entries if e['kind']=='NODE_KIND_FILE' and e['name'].endswith('.tmp'))
deleted=[event('t039',s)['data']['arguments']['path'] for s in [4782,4786,4790]]
assert deleted==wanted==rows['t039']['answer']['message'].splitlines()
for s in [4783,4787,4791]:assert response('t039',s)=={}
out['cleanup']={'task':'t039','listed_entries':len(entries),'matching_tmp_files':wanted,'acknowledged_deletes':deleted,'final_sorted_paths_match':True,'no_post_delete_readback_claim':True}
# Export format and acknowledgements, deliberately no independent forecast calculation.
w=event('t091',11134)['data']['arguments'];csvrows=list(csv.reader(io.StringIO(w['content'])))
assert len(csvrows)==6 and all(len(r)==7 for r in csvrows)
assert response('t091',11135)['path']==w['path']==response('t091',11139)['path']==rows['t091']['answer']['message']
assert response('t091',11139)['kind']=='NODE_KIND_FILE'
idx=json.loads(json.loads((P/'receipts/s8115-088.json').read_text())['receipt']['structuredContent']['output'])['supplemental_index']
assert not idx['more']
assert not [e for e in idx['items'] if e['seq']>11134 and e['kind']=='rpc_request' and e['data'].get('method')=='Read']
out['inventory_export']={'data_rows':5,'fields_each':7,'write_and_stat_acknowledged':True,'no_subsequent_read_in_complete_task_index':True,'forecast_values_independently_recomputed':False}
# Actual silent-step causes, not inferred from stdout line gaps.
trunc=[]
indices={}
for name in ['085','087','088','089']:
 x=json.loads(json.loads((P/f'receipts/s8115-{name}.json').read_text())['receipt']['structuredContent']['output']);indices[x['task_id']]=x['supplemental_index']['items']
for t,s in [('t025',3679),('t025',3685),('t081',10235),('t091',11127),('t094',11462)]:
 e=event(t,s);d=e['data'];c=d['response']['choices'][0];assert d['status']==200 and c['finish_reason']=='length'
 items=indices[t];i=next(i for i,e in enumerate(items) if e['seq']==s);assert items[i+1]['kind']=='llm_request'
 trunc.append({'task_id':t,'seq':s,'status':d['status'],'finish_reason':c['finish_reason'],'content_bytes':len((c['message'].get('content') or '').encode()),'executed_as_action':False})
out['targeted_length_responses']=trunc
assert event('t025',3677)['kind']=='rpc_error' and 'HTTP 400' in event('t025',3677)['data']['error'] and 'not a directory' in event('t025',3677)['data']['error']
out['list_file_error']='t025 seq3677: HTTP400 not a directory'
product=json.loads(response('t094',11474)['content']);assert str(product['price_cents'])==rows['t094']['answer']['message']
emp=json.loads(response('t081',10247)['content']);assert rows['t081']['answer']['message']==' | '.join([emp['display_name'],emp['title'],emp['store_id']]);out['employee_final_fields_match']=True
out['price_matches_source']=True
# Do not mistake JSON serialization escapes for literal malformed final output.
assert '\\u202f' not in rows['t001']['answer']['message'] and '\u202f' in rows['t001']['answer']['message']
out['unicode_json_escape_is_not_literal_output_defect']=True
(P/'support-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Targeted support checks passed')
