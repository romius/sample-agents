import ast,copy,hashlib,json,os,pathlib,shutil,subprocess,sys,tempfile
import pydantic_monty as m
P=pathlib.Path(__file__).resolve().parent;A=P.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
seal=json.loads((A/'SHA256SUMS.json').read_text())
assert sha((A/'SHA256SUMS.json').read_bytes())=='263ed08602ca41fa61c0d00e5e77acf7904f3e7f8a9b75a1cc9ee50bdcc38d8f'
for n,pin in seal.items():
 b=(A/n).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256'],n
with tempfile.TemporaryDirectory(prefix='h4-independent-') as tmp:
 q=pathlib.Path(tmp)/'package'
 for n in seal:
  dest=q/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(A/n,dest)
 subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(q/'reproduce.py')],check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.PIPE,text=True)
 # clean-reproduction is an author's status receipt; reproduced source/results
 # and every other sealed file must match, including original historical inputs.
 for n in seal:
  if n!='clean-reproduction.json':assert (q/n).read_bytes()==(A/n).read_bytes(),n
raw=(A/'agent.py').read_bytes();assert len(raw)==63380 and sha(raw)=='ae15cefc7d739ef6331ce646f24534ca90365a23133bdcf94103f6df6680c4af'
world=json.loads((A/'inputs/t063/world.json').read_text())
products=[]
for path,r in world['files'].items():
 assert sha(r['content'].encode())==r['sha256'],path
 if path.startswith('/proc/catalog/'):
  obj=json.loads(r['content']);obj['_path']=path;products.append(obj)
assert len(products)==101 and len({p['sku'] for p in products})==101
base=copy.deepcopy(next(p for p in products if p['sku']=='PT-SAW-MAK-DHS680-5AH'))
def make(sku,price=42990):
 p=copy.deepcopy(base);p['sku']=sku;p['price_cents']=price;p['_path']='/synthetic/'+sku+'.json';return p
key='PT-SAW-AK-DHS680-5.'
controls=[
 ('actual_h4',[base],key,42990,None,base['sku']),
 ('exact_other_price',[base,make('PT-SAW-AK-DHS680-5',42991)],key,42990,None,base['sku']),
 ('exact_other_price_reversed',[make('PT-SAW-AK-DHS680-5',42991),base],key,42990,None,base['sku']),
 ('exact_same_price',[base,make('PT-SAW-AK-DHS680-5')],key,42990,'PT-SAW-AK-DHS680-5','PT-SAW-AK-DHS680-5'),
 ('two_h4_matches',[base,make('PT-SAW-MAK-DHS680-5ZZ')],key,42990,None,None),
 ('duplicate_matching_record',[base,copy.deepcopy(base)],key,42990,None,None),
 ('wrong_price',[base],key,42989,None,None),
 ('string_price',[base],key,'42990',None,None),
 ('no_truncation_marker',[base],key[:-1],42990,None,None),
 ('trailing_semicolon',[base],key[:-1]+';',42990,None,None),
 ('too_short',[base],'PT-SAW-A.',42990,None,None),
 ('existing_prefix',[base],'PT-SAW-MAK-DHS680-5.',42990,base['sku'],base['sku']),
]
control_results=[]
with m.Monty() as pool:
 for arm,path in [('parent','inputs/parent-readable.py'),('H4','readable.py')]:
  source=(A/path).read_text();nodes=[]
  for n in ast.parse(source).body:
   if isinstance(n,ast.FunctionDef) and n.name in ['ocr_key','rcp_product','rcp_drop1']:nodes.append(n)
   if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='OCR_DIGITS' for x in n.targets):nodes.append(n)
  code='import re\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'
  for name,ps,fragment,cents,parent_expected,h4_expected in controls:
   ns={'WORLD':{'products':ps}};exec(code,ns);r=ns['rcp_product'](fragment,cents);cp=r['sku'] if r else None
   with pool.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as session:
    native=session.feed_run(code+'\nhit=rcp_product(FRAGMENT,CENTS)\nhit["sku"] if hit else None',inputs={'WORLD':{'products':ps},'FRAGMENT':fragment,'CENTS':cents})
   assert cp==native==(parent_expected if arm=='parent' else h4_expected),(arm,name,cp,native)
   control_results.append({'arm':arm,'case':name,'fragment':fragment,'cents':cents,'products':ps,'resolved':cp,'native_equal':True})
# Independently authored receipt interpretation; never call resolver for mapping.
intended=[('PT-SAW-MAK-DHS680-5AH',1,42990),('PT-MOW-STI-RMA235-AK30',12,38990),('PT-BIT-BOS-CYL9-12',1,3490),('PT-BLA-BOS-EXPWOOD-190',1,4490)]
storepath='/proc/locations/Vienna/store-vie-favoriten.json';store=json.loads(world['files'][storepath]['content']);upload='/uploads/AztYLH6h_receipt_ocr.txt';ocr=world['files'][upload]['content']
assert store['is_open'] is True and store['address_line_1']=='Favoritenstrasse 221' and store['address_line_1'] in ocr
stock=[]
for sku,qty,price in intended:
 hits=[p for p in products if p['sku']==sku];assert len(hits)==1 and hits[0]['price_cents']==price
 inv=[r for r in store['inventory'] if r['sku']==sku];assert len(inv)==1
 avail=max(inv[0]['on_hand']-inv[0]['reserved'],0);stock.append({'sku':sku,'qty':qty,'price':price,'row':inv[0],'available':avail,'product_path':hits[0]['_path']})
assert [r['available'] for r in stock]==[0,7,0,0]
assert sum(q*p for sku,q,p in intended)==518850 and '5188,50' in ocr
policy=world['files']['/docs/availability-checks.md']['content'];agents=world['files']['/AGENTS.MD']['content']
assert 'max(on_hand - reserved, 0)' in policy and 'Incoming stock counts only when the user asks to include incoming stock.' in policy
assert 'answer exactly `ja` or `nein`' in agents
report=json.loads((A/'replay-results.json').read_text());rows=report['rows']
assert len(rows)==64
for case in ['actual_t023','actual_t063']:
 parent=next(r for r in rows if (r['case'],r['arm'],r['form'],r['engine'])==(case,'parent','packed','native'))
 h4=next(r for r in rows if (r['case'],r['arm'],r['form'],r['engine'])==(case,'H4','packed','native'))
 assert not parent['overlays'] and not h4['overlays']
 assert parent['calls']==h4['calls'] and parent['requests']==h4['requests'] and parent['answers']==h4['answers']
 assert len(parent['requests'])==len(h4['requests'])==2
assert all(not r['unmatched'] and all(method not in ['Write','Delete'] and (method!='Exec' or args['path'] in ['/bin/id','/bin/date']) for method,args in r['calls']) for r in rows)
isolated=next(r for r in rows if (r['case'],r['arm'],r['form'],r['engine'])==('isolate_saw','H4','packed','native'))
assert len(isolated['overlays'])==1
change=isolated['overlays'][0];assert change['path']==upload and change['after']['content']==change['before']['content'].replace('PT-IT-BO5-CYL9-12','PT-BIT-BOS-CYL9-12')
assert isolated['answers']==[{'message':'nein','outcome':'OUTCOME_OK','refs':[upload,storepath]+[r['product_path'] for r in stock]+['/docs/security.md','/docs/availability-checks.md']}]
assert len(isolated['requests'])==1
out={'status':'PASS evidence/reproduction; H4-only not a complete repair and collision concern retained','author_seal_sha256':sha((A/'SHA256SUMS.json').read_bytes()),'sealed_files':len(seal),'candidate_bytes':len(raw),'candidate_sha256':sha(raw),'whole_agent_reproduced':64,'new_resolver_evaluations':len(control_results)*2,'new_controls':control_results,'manual_stock':stock,'manual_expected_today':'nein','actual_world_helper_takeover':False,'new_exact_other_price_acceptance_confirmed':True,'scope':'Pure resolver controls plus exact author whole-agent reproduction; synthetic identity collision is not demonstrated wrong final yes/no and fixed replies are not live inference.'}
(P/'results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['new_controls','manual_stock']}))
