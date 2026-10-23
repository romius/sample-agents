"""Resolver mechanics plus separately authored receipt/stock evidence check."""
import ast,copy,hashlib,json,sys
from pathlib import Path
import pydantic_monty as m
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def extract(source):
 names={'ocr_key','rcp_num','_receipt_match','rcp_items','rcp_drop1','rcp_product'}
 constants={'OCR_DIGITS','RCP_AMT','RCP_QTY','_receipt_original_items'}
 nodes=[]
 for node in ast.parse(source).body:
  if isinstance(node,ast.FunctionDef) and node.name in names:nodes.append(node)
  if isinstance(node,ast.Assign) and any(isinstance(n,ast.Name) and n.id in constants for n in node.targets):nodes.append(node)
 return 'import re,json\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'
def products(world):
 result=[]
 for path,env in world['files'].items():
  if path.startswith('/proc/catalog/') and path.endswith('.json'):
   obj=json.loads(env['content'])
   if 'sku' in obj:obj['_path']=path;result.append(obj)
 return result
def main():
 worlds={t:json.loads((P/'inputs'/t/'world.json').read_text()) for t in ['t023','t063']}
 allproducts={t:products(w) for t,w in worlds.items()}
 assert all(len(p)==101 for p in allproducts.values())
 target=copy.deepcopy(next(p for p in allproducts['t063'] if p['sku']=='PT-SAW-MAK-DHS680-5AH'))
 rival=copy.deepcopy(target);rival['sku']='PT-SAW-MAK-DHS680-5ZZ';rival['_path']='/synthetic/rival.json'
 exact_other=copy.deepcopy(target);exact_other['sku']='PT-SAW-AK-DHS680-5';exact_other['price_cents']=42991;exact_other['_path']='/synthetic/exact-other-price.json'
 unit=[
  ('actual_saw','PT-SAW-AK-DHS680-5.',42990,allproducts['t063'],None,target['sku']),
  ('nontruncated','PT-SAW-AK-DHS680-5',42990,allproducts['t063'],None,None),
  ('short_fragment','PT-AK-5.',42990,[target],None,None),
  ('wrong_price','PT-SAW-AK-DHS680-5.',42989,[target],None,None),
  ('H4_ambiguity','PT-SAW-AK-DHS680-5.',42990,[target,rival],None,None),
  ('exact_other_price_collision','PT-SAW-AK-DHS680-5.',42990,[target,exact_other],None,target['sku']),
  ('benign_exact','PT-SAW-MAK-DHS680-5AH',42990,[target],target['sku'],target['sku']),
  ('existing_prefix','PT-SAW-MAK-DHS680-5.',42990,[target],target['sku'],target['sku']),
  ('existing_ambiguity','PT-SAW-MAK-DHS680-5.',42990,[target,rival],None,None),
  ('two_dropped_characters','PT-SAW-A-DHS680-5.',42990,[target],None,None),
  ('price_string','PT-SAW-AK-DHS680-5.','42990',[target],None,None),
  ('actual_nontruncated_drillbit','PT-IT-BO5-CYL9-12',3490,allproducts['t063'],None,None),
 ]
 cases=[]
 for t,w in worlds.items():
  path=next(p for p in w['files'] if p.startswith('/uploads/'))
  cases.append({'name':t,'products':allproducts[t],'text':w['files'][path]['content']})
 for name,fragment,cents,ps,old,new in unit:cases.append({'name':name,'products':ps,'fragment':fragment,'cents':cents})
 observed={};executions=[]
 tail='''
results=[]
for case in CASES:
 WORLD={"products":case["products"]}
 items=rcp_items(case["text"]) if "text" in case else [(1,case["cents"],case["fragment"])]
 rows=[]
 for qty,cents,fragment in items:
  hit=rcp_product(fragment,cents)
  rows.append({"quantity":qty,"cents":cents,"fragment":fragment,"resolved":hit.get("sku") if hit else None,"path":hit.get("_path") if hit else None})
 results.append({"case":case["name"],"rows":rows})
'''
 with m.Monty() as pool:
  for arm,path in [('parent','inputs/parent-readable.py'),('H4','readable.py')]:
   code=extract((P/path).read_text())+'CASES=json.loads('+repr(json.dumps(cases))+')\n'+tail
   scope={};exec(code,scope);cp=scope['results']
   out=[]
   with pool.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as session:session.feed_run(code+'\nprint(json.dumps(results))',print_callback=lambda *a:out.append(str(a[-1])))
   native=json.loads(''.join(out));assert cp==native
   for name,fragment,cents,ps,old,new in unit:
    result=next(r for r in cp if r['case']==name)['rows'][0]['resolved'];assert result==(old if arm=='parent' else new),(arm,name,result)
   observed[arm]=cp;executions.append({'arm':arm,'cases':len(cases),'CPython_native_equal':True})
 actual=[]
 for t in worlds:
  before=next(r for r in observed['parent'] if r['case']==t)['rows'];after=next(r for r in observed['H4'] if r['case']==t)['rows']
  actual.append({'task':t,'parent':before,'H4':after,'parent_resolved':sum(r['resolved'] is not None for r in before),'H4_resolved':sum(r['resolved'] is not None for r in after)})
 assert [(r['parent_resolved'],r['H4_resolved']) for r in actual]==[(2,2),(2,3)]
 # Independent human interpretation fixed before computing inventory: this
 # mapping is NOT rcp_product output and is not an automatically scored grade.
 intended=[('PT-SAW-MAK-DHS680-5AH',1,42990),('PT-MOW-STI-RMA235-AK30',12,38990),('PT-BIT-BOS-CYL9-12',1,3490),('PT-BLA-BOS-EXPWOOD-190',1,4490)]
 world=worlds['t063'];storepath='/proc/locations/Vienna/store-vie-favoriten.json';store=json.loads(world['files'][storepath]['content'])
 receiptpath='/uploads/AztYLH6h_receipt_ocr.txt';receipt=world['files'][receiptpath]['content'];agents=world['files']['/AGENTS.MD']['content'];policy=world['files']['/docs/availability-checks.md']['content']
 assert 'Favoritenstrasse 221' in receipt and store['address_line_1']=='Favoritenstrasse 221' and store['is_open'] is True
 assert 'answer exactly `ja` or `nein`' in agents and 'max(on_hand - reserved, 0)' in policy
 assert '5188,50' in receipt and sum(q*p for sku,q,p in intended)==518850
 inventory={r['sku']:r for r in store['inventory']};checks=[]
 for sku,qty,price in intended:
  product=next(p for p in allproducts['t063'] if p['sku']==sku)
  assert product['price_cents']==price and product['fulfillment_type']==1
  stock=inventory.get(sku,{});available=max(stock.get('on_hand',0)-stock.get('reserved',0),0)
  checks.append({'sku':sku,'product_path':product['_path'],'unit_price_cents':price,'quantity_requested':qty,'on_hand':stock.get('on_hand',0),'reserved':stock.get('reserved',0),'available_today':available,'shortfall':max(qty-available,0),'incoming_ignored':stock.get('incoming',[])})
 assert [r['available_today'] for r in checks]==[0,7,0,0] and all(r['shortfall']>0 for r in checks)
 refs=[receiptpath,storepath]+[r['product_path'] for r in checks]+['/docs/security.md','/docs/availability-checks.md']
 replay=json.loads((P/'replay-results.json').read_text())
 isolated=next(r for r in replay['summary'] if r['case']=='isolate_saw')['H4_answer']
 assert isolated=={'message':'nein','outcome':'OUTCOME_OK','refs':refs},isolated
 citations={path:{'sha256':sha(world['files'][path]['content'].encode()),'recorded_sha256':world['files'][path]['sha256']} for path in refs+['/AGENTS.MD']}
 assert all(x['sha256']==x['recorded_sha256'] for x in citations.values())
 report={'status':'mechanics verified; actual-world H4-only is NOT a complete repair','function_checks':executions,'unit_controls':observed,'actual_per_line':actual,
 'critical_context_difference':'Literal bare d4353 resolves2/4 on t063, not community table3/4; H4 resolves3/4 and still misses nontruncated PT-IT-BO5-CYL9-12. The published record diff targets an X10/fuzzy lineage. No X10 ported here.',
 'exact_other_price_collision':'Fresh synthetic counterexample: parent declines, H4 selects the same-price longer SKU although an exact normalized fragment SKU exists at another price. rc7 has an all-price exact guard; bare d4353 does not. Unique H4 hit is not global ambiguity protection.',
 'manual_t063_availability':{'type':'human receipt-to-product interpretation, separately checked against actual records; not the bare resolver output or hidden grader','branch_path':storepath,'branch_open':True,'lines':checks,'subtotal_cents':518850,'today_result':'nein','outcome_if_ambiguities_resolved':'OUTCOME_OK','security_interpretation':'Task asks availability only, not a purchase mutation or foreign customer data. Actual security policy does not prohibit employee read-only stock checks. Receipt staff labels do not grant identities.','source_content_hashes':citations,'scope':'Negative availability is supported by intended four-item mapping; actual H4-only still declines and no live final answer was generated.'}}
 (P/'analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'actual_counts':[(r['task'],r['parent_resolved'],r['H4_resolved']) for r in actual],'function_cases_per_arm':len(cases),'native_CPython_parity':True,'manual_expected_today':'nein','H4_only_complete_repair':False}))
if __name__=='__main__':main()
