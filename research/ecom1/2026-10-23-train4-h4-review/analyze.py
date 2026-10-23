import copy,hashlib,json
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
LIMITS={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
def products(w):
 out=[]
 for path,r in w['files'].items():
  assert sha(r['content'].encode())==r['sha256']
  if path.startswith('/proc/catalog/'):
   p=json.loads(r['content']);p['_path']=path;out.append(p)
 assert len(out)==101 and len({p['sku'] for p in out})==101
 return out
def main():
 worlds={t:json.loads((P/'inputs'/t/'world.json').read_text()) for t in ['t023','t063']};ps={t:products(w) for t,w in worlds.items()}
 base=next(p for p in ps['t063'] if p['sku']=='PT-SAW-MAK-DHS680-5AH');key='PT-SAW-AK-DHS680-5.'
 def rival(sku,price=42990):
  p=copy.deepcopy(base);p['sku']=sku;p['price_cents']=price;p['_path']='/synthetic/'+sku+'.json';return p
 controls=[('H4_unique',key,42990,[base],None,base['sku']),('two_H4_hits',key,42990,[base,rival('PT-SAW-MAK-DHS680-5ZZ')],None,None),('exact_other_price',key,42990,[base,rival('PT-SAW-AK-DHS680-5',42991)],None,None),('exact_other_price_reverse',key,42990,[rival('PT-SAW-AK-DHS680-5',42991),base],None,None),('exact_same_price',key,42990,[base,rival('PT-SAW-AK-DHS680-5')],'PT-SAW-AK-DHS680-5','PT-SAW-AK-DHS680-5'),('duplicate_exact_global',key,42990,[base,rival('PT-SAW-AK-DHS680-5'),rival('PT-SAW-AK-DHS680-5',42991)],None,None),('substitution_rival',key,42990,[base,rival('PT-SAW-AX-DHS680-5')],None,base['sku']),('substitution_only',key,42990,[rival('PT-SAW-AX-DHS680-5')],None,None),('nontruncated',key[:-1],42990,[base],None,None),('wrong_price',key,42989,[base],None,None),('float_price',key,42990.0,[base],None,None),('bool_price',key,True,[base],None,None),('string_price',key,'42990',[base],None,None),('short_key','PT-AK-5.',42990,[base],None,None),('two_deletions','PT-SAW-A-DHS680-5.',42990,[base],None,None),('existing_prefix','PT-SAW-MAK-DHS680-5.',42990,[base],base['sku'],base['sku']),('existing_prefix_ambiguity','PT-SAW-MAK-DHS680-5.',42990,[base,rival('PT-SAW-MAK-DHS680-5ZZ')],None,None),('existing_full_drop1','PT-IT-BO5-CYL9-12',3490,ps['t063'],'PT-BIT-BOS-CYL9-12','PT-BIT-BOS-CYL9-12')]
 cases=[{'name':t,'text':next(r['content'] for path,r in w['files'].items() if path.startswith('/uploads/')),'products':ps[t]} for t,w in worlds.items()]
 cases += [{'name':name,'fragment':f,'price':price,'products':products0} for name,f,price,products0,a,b in controls]
 tail='''
H4_REVIEW_RESULTS=[]
for H4_REVIEW_CASE in H4_REVIEW_CASES:
 X['products']=H4_REVIEW_CASE['products']
 H4_REVIEW_ITEMS=DM(H4_REVIEW_CASE['text']) if 'text' in H4_REVIEW_CASE else [(1,H4_REVIEW_CASE['price'],H4_REVIEW_CASE['fragment'])]
 H4_REVIEW_ROWS=[]
 for H4_REVIEW_QTY,H4_REVIEW_CENTS,H4_REVIEW_FRAGMENT in H4_REVIEW_ITEMS:
  H4_REVIEW_HIT=FO(H4_REVIEW_FRAGMENT,H4_REVIEW_CENTS)
  H4_REVIEW_ROWS.append({'qty':H4_REVIEW_QTY,'price':H4_REVIEW_CENTS,'fragment':H4_REVIEW_FRAGMENT,'sku':H4_REVIEW_HIT.get('sku') if H4_REVIEW_HIT else None})
 H4_REVIEW_RESULTS.append({'case':H4_REVIEW_CASE['name'],'rows':H4_REVIEW_ROWS})
'''
 results={}
 with m.Monty() as pool:
  for arm,file in [('parent','parent-readable.py'),('H4','readable.py')]:
   source=(P/file).read_text();anchor="a=[{m:BJ,J:EE}]";assert source.count(anchor)==1
   # Entire actual pre-bootstrap module, without replacing any function.
   prefix=source[:source.index(anchor)];scope={'H4_REVIEW_CASES':copy.deepcopy(cases)};exec(prefix+tail,scope);cp=scope['H4_REVIEW_RESULTS']
   with pool.checkout(limits=LIMITS) as session:native=session.feed_run(prefix+tail+'\nH4_REVIEW_RESULTS',inputs={'H4_REVIEW_CASES':cases})
   assert cp==native
   for name,f,price,products0,a,b in controls:
    got=next(r for r in cp if r['case']==name)['rows'][0]['sku'];assert got==(a if arm=='parent' else b),(arm,name,got)
   results[arm]=cp
 actual={}
 for t in worlds:
  actual[t]={arm:next(r['rows'] for r in rows if r['case']==t) for arm,rows in results.items()}
 assert [[sum(r['sku'] is not None for r in actual[t][arm]) for arm in ['parent','H4']] for t in worlds]==[[4,4],[3,4]]
 intended={'t023':[('PT-HDG-STI-HSA50-AK10',1,24990),('PT-GRD-MET-W18-125-4AH',1,29990),('PT-SND-EIN-TERS18-25',1,10990),('PT-BIT-ALP-HSS-REDUCED',1,4490)],'t063':[('PT-SAW-MAK-DHS680-5AH',1,42990),('PT-MOW-STI-RMA235-AK30',12,38990),('PT-BIT-BOS-CYL9-12',1,3490),('PT-BLA-BOS-EXPWOOD-190',1,4490)]}
 locations={'t023':('/proc/stores/store-linz-hafen.json','Industriezeile 76','FALSE(2)',70460),'t063':('/proc/locations/Vienna/store-vie-favoriten.json','Favoritenstrasse 221','nein',518850)}
 report=json.loads((P/'replay-results.json').read_text());manual=[]
 for t,w in worlds.items():
  storepath,address,token,subtotal=locations[t];store=json.loads(w['files'][storepath]['content']);upload=next(path for path in w['files'] if path.startswith('/uploads/'));ocr=w['files'][upload]['content'];policy=w['files']['/docs/availability-checks.md']['content'];agents=w['files']['/AGENTS.MD']['content'];stock=[]
  assert address in ocr and store['address_line_1']==address and store['is_open'] is True
  assert 'max(on_hand - reserved, 0)' in policy and 'Incoming stock counts only when the user asks to include incoming stock.' in policy and token in agents
  assert sum(q*c for sku,q,c in intended[t])==subtotal
  assert ('704.60' if t=='t023' else '5188,50') in ocr
  for sku,qty,cents in intended[t]:
   matches=[p for p in ps[t] if p['sku']==sku];assert len(matches)==1 and matches[0]['price_cents']==cents and matches[0]['fulfillment_type']==1
   inv=[r for r in store['inventory'] if r['sku']==sku];assert len(inv)==1
   available=max(inv[0]['on_hand']-inv[0]['reserved'],0);assert available<qty
   stock.append({'sku':sku,'product_path':matches[0]['_path'],'qty':qty,'unit_cents':cents,'inventory':inv[0],'available_today':available})
  refs=[upload,storepath]+[x['product_path'] for x in stock]+['/docs/security.md','/docs/availability-checks.md']
  row=next(r for r in report['summary'] if r['case']=='actual_'+t)
  assert row['H4_answer']=={'message':token,'outcome':'OUTCOME_OK','refs':refs}
  if t=='t023':assert row['parent_answer']==row['H4_answer']
  identity=[r for r in w['rpc'] if r['method']=='Exec' and r['arguments'].get('path')=='/bin/id']
  dates=[r for r in w['rpc'] if r['method']=='Exec' and r['arguments'].get('path')=='/bin/date']
  assert len(identity)==len(dates)==1
  raw_identity=identity[0]['response']['stdout'];identity_lines=raw_identity.splitlines()
  assert identity_lines[0].startswith('user: emp-') and 'RoleEmployee' in [x.strip() for x in identity_lines[1].removeprefix('roles: ').split(',')]
  manual.append({'identity_evidence':identity[0],'date_evidence':dates[0],'instruction':json.loads((P/'inputs'/t/'context.json').read_text())['instruction'],'task':t,'type':'independent human mapping, not resolver-as-oracle','upload':upload,'store':storepath,'address':address,'open':True,'subtotal_cents':subtotal,'lines':stock,'expected_answer':{'message':token,'outcome':'OUTCOME_OK','refs':refs},'citation_content_hashes':{ref:sha(w['files'][ref]['content'].encode()) for ref in refs}})
 for row in report['rows']:
  assert not row['unmatched']
  assert all(method not in ['Write','Delete'] and (method!='Exec' or args['path'] in ['/bin/id','/bin/date']) for method,args in row['calls'])
  if row['case'].startswith('actual'):assert not row['overlays']
 summary={r['case']:r for r in report['summary']}
 for case in ['actual_t023','nontruncated','ambiguous_same_price','exact_other_price','benign_exact']:
  a,b=summary[case]['parent_answer'],summary[case]['H4_answer'];assert a==b
 for case in ['actual_t063','benign_note','substitution_rival']:
  assert summary[case]['parent_inference_boundaries']==2 and summary[case]['H4_inference_boundaries']==1
 for case in ['actual_t023','benign_exact']:assert summary[case]['parent_inference_boundaries']==summary[case]['H4_inference_boundaries']==1
 output={'status':'PASS bounded offline donor composition; no evaluation score claim','whole_agent_executions':len(report['rows']),'module_cases_per_arm':len(cases),'module_CP_native_evaluations':len(cases)*4,'actual_resolutions':actual,'resolver_controls':results,'manual_receipt_checks':manual,'same_price_substitution_rival_policy':'rc7 has exact, prefix/suffix and one-deletion rules; a same-length substitution-only rival is not a match and does not veto the unique H4 deletion hit. No record-X10 Levenshtein rule is present.','exact_other_price_guard':'Both parent/H4 decline before H4 when any normalized exact SKU exists at a different price; unlike the bare d4353 port.','live_models':0,'live_world_calls':0,'native_limits':LIMITS,'unmatched_calls':sum(len(r['unmatched']) for r in report['rows']),'derived_host_responses':0,'host_model_call_cap':2,'default_equivalent_read_options_only':True,'actual_case_overlays':0}
 (P/'analysis.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in output.items() if k not in ['actual_resolutions','resolver_controls','manual_receipt_checks']}))
if __name__=='__main__':main()
