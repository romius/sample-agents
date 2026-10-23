"""Independent literal cleanup selection and CSV shape checks for selected witnesses."""
import csv,io,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
rows={r['task_id']:r for r in json.loads((P/'success-review.json').read_text())}
def event(task,seq):return json.loads((P/f'events/{task}-{seq}.ndjson').read_text())
out={'status':'passed','cleanup':[]}
for task,listing,first,last,count in [('t039',5273,5274,5286,7),('t060',8054,8055,8061,4)]:
 entries=event(task,listing)['data']['response']['entries'];assert all(e['kind']=='NODE_KIND_FILE' for e in entries)
 expected=sorted(e['path'] for e in entries if task=='t060' or e['name'].endswith('.tmp'))
 assert len(expected)==count
 requests=[event(task,s)['data']['arguments']['path'] for s in range(first,last+1,2)]
 assert requests==expected==rows[task]['answer']['message'].splitlines()
 for s in range(first,last+1,2):assert event(task,s+1)['data']['response']=={}
 # Supplemental index is the complete ordered index for these short trials.
 indexes=[]
 for f in (P/'receipts').glob('s8064-*.json'):
  if 'start' in f.name or 'discard' in f.name:continue
  x=json.loads(json.loads(f.read_text())['receipt']['structuredContent']['output'])
  if x.get('task_id')==task and 'supplemental_index' in x:indexes=x['supplemental_index']['items'];assert not x['supplemental_index']['more']
 assert indexes[0]['kind']=='rpc_request' and indexes[0]['data']['method']=='StartTrial'
 assert [e['seq'] for e in indexes]==list(range(indexes[0]['seq'],indexes[-1]['seq']+1))
 mutations=[e for e in indexes if e['kind']=='rpc_request' and e['data'].get('method') in ['Delete','Write']]
 assert [e['seq'] for e in mutations]==list(range(first,last+1,2))
 out['cleanup'].append({'task_id':task,'listed':len(entries),'selected':count,'exact_delete_requests_and_success_acknowledgements':True,'only_matching_delete_requests_in_complete_index':True,'exact_sorted_final_answer':True,'simulated_acknowledgements':False,'post_delete_readback':False})
a=event('t091',12708)['data']['arguments'];b=event('t091',12712)['data']['arguments'];aa=list(csv.reader(io.StringIO(a['content'])));bb=list(csv.reader(io.StringIO(b['content'])))
assert a['path']==b['path']==rows['t091']['answer']['message']
assert aa[0]==bb[0] and len(bb[0])==7
assert len(aa)==len(bb)==6 and all(len(r)==8 for r in aa[1:]) and all(len(r)==7 for r in bb[1:])
assert all(x[:-1]==y and x[-1]=='0' for x,y in zip(aa[1:],bb[1:]))
for s in [12709,12713]:assert event('t091',s)['data']['response']=={'path':a['path']}
err=event('t091',12705)['data'];assert 'HTTP 404' in err['error'] and 'list failed: not found' in err['error']
out['export']={'task_id':'t091','first_successfully_written_row_field_counts':[len(r) for r in aa],'corrected_successfully_written_row_field_counts':[len(r) for r in bb],'change_is_removal_of_one_trailing_zero_per_data_row':True,'both_write_acknowledgements_actual':True,'list_exports_404_recovered':True,'forecast_numbers_independently_validated':False}
for task,n in [('t015',23),('t035',19),('t055',6),('t075',11)]:
 refs=rows[task]['answer']['refs'];assert len(refs)==len(set(refs))==n and all('#row=AR-' in p for p in refs)
assert sum(len(r['recovered_invalid_action_lines']) for r in rows.values())==8
out['scope']='Literal archived List selection, actual mutation acknowledgement and CSV shape checks only; no automatic grading of arbitrary text or full CAS reconstruction.'
(P/'targeted-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
