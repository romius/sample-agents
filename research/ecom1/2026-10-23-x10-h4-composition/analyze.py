"""Explicit manual receipt oracle plus occurrence-aware resolver extraction."""
import ast,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
ARMS=['d4353','d4353_H4','X10','X10_H4']
NAMES={'ocr_key','rcp_items','rcp_product','rcp_dist','rcp_drop1','rcp_num','_receipt_match','rcp_store'}
ASSIGNS={'OCR_DIGITS','RCP_AMT','RCP_QTY','_receipt_original_items'}
def extracted(arm):
 source=(P/'arms'/arm/'readable.py').read_text();nodes=[]
 for n in ast.parse(source).body:
  if isinstance(n,ast.FunctionDef) and n.name in NAMES:nodes.append(ast.get_source_segment(source,n))
  elif isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ASSIGNS for t in n.targets):nodes.append(ast.get_source_segment(source,n))
 return '\n\n'.join(nodes)
def namespace(arm,products,stores):
 g={'re':re,'WORLD':{'products':products,'stores':stores}};exec(extracted(arm),g);return g
# These mappings/quantities are a manual transcription of each actual OCR receipt,
# checked against full product names, price and branch address, not model answers.
MANUAL={
 't023':{'store':'store-linz-hafen','subtotal_cents':70460,'negative_token':'FALSE(2)','items':[(1,24990,'PT-HDG-ST1-HSA50-AK10','PT-HDG-STI-HSA50-AK10'),(1,29990,'PT-GRD-MET-W18-125-4AH','PT-GRD-MET-W18-125-4AH'),(1,10990,'PT-SND-E1N-TRS18-25','PT-SND-EIN-TERS18-25'),(1,4490,'PT-B1T-ALP-HSS-REUCED','PT-BIT-ALP-HSS-REDUCED')]},
 't063':{'store':'store-vie-favoriten','subtotal_cents':518850,'negative_token':'nein','items':[(1,42990,'PT-SAW-AK-DHS680-5.','PT-SAW-MAK-DHS680-5AH'),(12,38990,'PT-MOW-STI-RMA235-A.','PT-MOW-STI-RMA235-AK30'),(1,3490,'PT-IT-BO5-CYL9-12','PT-BIT-BOS-CYL9-12'),(1,4490,'PT-BLA-BOS-EXPWOOD-.','PT-BLA-BOS-EXPWOOD-190')]}}
def main():
 replay=json.loads((P/'replay-results.json').read_text())['rows'];report=[]
 for task,oracle in MANUAL.items():
  world=json.loads((P/'upstream'/task/'world.json').read_text());products=[];stores=[]
  for path,env in world['files'].items():
   assert sha(env['content'].encode())==env['sha256']
   try:obj=json.loads(env['content'])
   except ValueError:continue
   if isinstance(obj,dict) and 'sku' in obj and 'price_cents' in obj:products.append(dict(obj,_path=path))
   if isinstance(obj,dict) and 'inventory' in obj:stores.append(dict(obj,_path=path))
  policy=world['files']['/docs/availability-checks.md'];assert 'max(on_hand - reserved, 0)' in policy['content'] and 'Availability checks are read-only' in policy['content']
  upload_path=next(k for k in world['files'] if k.startswith('/uploads/'));upload=world['files'][upload_path]
  store=[s for s in stores if s['id']==oracle['store']];assert len(store)==1;store=store[0];assert store['address_line_1'] in upload['content'] and store['is_open'] is True
  assert sum(q*price for q,price,fragment,sku in oracle['items'])==oracle['subtotal_cents']
  proof=[]
  for qty,price,fragment,sku in oracle['items']:
   ps=[p for p in products if p['sku']==sku];assert len(ps)==1 and ps[0]['price_cents']==price and fragment in upload['content']
   rows=[r for r in store['inventory'] if r['sku']==sku];assert len(rows)==1 # no implicit absent-record zeros
   stock=rows[0];available=max(stock.get('on_hand',0)-stock.get('reserved',0),0)
   proof.append({'quantity':qty,'unit_cents':price,'OCR_fragment':fragment,'manual_resolved_SKU':sku,'product_name':ps[0]['name'],'product_path':ps[0]['_path'],'product_content_sha256':world['files'][ps[0]['_path']]['sha256'],'actual_inventory_row':stock,'same_day_available':available,'short':available<qty})
  assert any(r['short'] for r in proof)
  arms=[]
  for arm in ARMS:
   g=namespace(arm,products,stores);parsed=g['rcp_items'](upload['content']);assert parsed==[(q,p,f) for q,p,f,s in oracle['items']]
   selected=[g['rcp_product'](fragment,price) for q,price,fragment in parsed]
   row=next(r for r in replay if (r['task'],r['case'],r['arm'],r['engine'])==(task,'actual',arm,'native_packed'))
   identities=[r['sku'] if r else None for r in selected];resolved=sum(p is not None for p in selected)
   if resolved==4:
    assert identities==[s for q,p,f,s in oracle['items']]
    assert len(row['requests'])==1 and row['answers'][0]['message']==oracle['negative_token'] and row['answers'][0]['outcome']=='OUTCOME_OK'
    needed=[upload_path,store['_path']]+[r['product_path'] for r in proof]+['/docs/security.md','/docs/availability-checks.md'];assert row['answers'][0]['refs']==needed
    readpaths=[args['path'] for method,args in row['calls'] if method=='Read'];assert all(path in readpaths for path in needed)
   else:assert len(row['requests'])==2
   arms.append({'arm':arm,'parsed_items':parsed,'resolved_SKUs':identities,'resolved_count':resolved,'router_plus_fallback_boundaries':len(row['requests']),'deterministic_all_rows_resolved':resolved==4,'answer':row['answers'][0],'frozen_fallback_not_new_model_output':resolved<4})
  report.append({'task':task,'upload_path':upload_path,'upload_content_sha256':upload['sha256'],'policy_content_sha256':policy['sha256'],'branch_path':store['_path'],'branch_content_sha256':world['files'][store['_path']]['sha256'],'branch_is_open':True,'manual_transcription_subtotal':oracle['subtotal_cents'],'items':proof,'all_selected_inventory_rows_explicit':True,'availability_oracle':'negative; one or more required quantities exceeds max(on_hand-reserved,0), incoming excluded for today','arms':arms})
 out={'status':'manual source-fact oracle verified; not benchmark regrading','cases':report,'scope':'actual archived worlds only; manual SKU/quantity transcription independently checked against source facts; no synthetic inventory or absent-row guessing'}
 (P/'availability-analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps([{'task':r['task'],'available':[x['same_day_available'] for x in r['items']],'required':[x['quantity'] for x in r['items']],'arms':[(a['arm'],a['resolved_count']) for a in r['arms']]} for r in report]))
if __name__=='__main__':main()
