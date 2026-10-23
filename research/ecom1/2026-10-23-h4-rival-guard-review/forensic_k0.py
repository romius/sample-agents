"""Reproduce only k0's three seeded cells, preserving every lost inherited hit.
This is not a reproduction of the full robustness/cross-price/old-receipt suite.
"""
import json,random,hashlib
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
W=json.loads((P/'inputs/t063-world.json').read_text());products=[]
for path,f in W['files'].items():
 if path.startswith('/proc/catalog/'):
  x=json.loads(f['content']);products.append({'sku':x['sku'],'price_cents':x['price_cents']})
ARMS={};prefixes={}
for name,path in [('parent','inputs/parent-readable.py'),('H4','inputs/h4-readable.py'),('guard','upstream/d7019r1-cand_h4g2_dec.py')]:
 src=(P/path).read_text();pre=src[:src.index('a=[{m:BJ,J:EE}]')];ns={};exec(pre,ns);ns['X']['products']=products;ARMS[name]=ns;prefixes[name]=pre
# Separate general edit-distance implementation for rival descriptions.
def ed(a,b):
 row=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  nr=[i]
  for j,y in enumerate(b,1):nr.append(min(nr[-1]+1,row[j]+1,row[j-1]+(x!=y)))
  row=nr
 return row[-1]
random.seed(11);counts={};lost=[]
for cut in ['.','-','']:
 count={a:{'right':0,'wrong':0,'none':0} for a in ARMS}
 for p in products:
  for k in range(20):
   sku=p['sku'];L=random.randrange(max(10,len(sku)-6),len(sku)+1) if cut=='' else random.randrange(max(10,len(sku)-6),len(sku))
   fragment=sku[:L]+cut;hits={a:ns['FO'](fragment,p['price_cents']) for a,ns in ARMS.items()}
   for a,h in hits.items():count[a]['none' if h is None else 'right' if h['sku']==sku else 'wrong']+=1
   if cut=='' and hits['parent'] and hits['parent']['sku']==sku and hits['guard'] is None:
    norm=ARMS['guard']['n'];key=norm(fragment).rstrip('.')
    rivals=[dict(q,normalized_edit_distance=ed(key,norm(q['sku']))) for q in products if q is not hits['H4'] and ed(key,norm(q['sku']))<=1]
    lost.append({'intended_source_sku':sku,'fragment':fragment,'source_length':len(sku),'fragment_length':L,'price':p['price_cents'],'results':{a:h['sku'] if h else None for a,h in hits.items()},'all_price_near_rivals':rivals})
 counts['k0'+(cut or 'full')]=count
published=json.loads((P/'upstream/d7021r1-guard_test.json').read_text())['robust'];mapping={'parent':'rc7(d6855)','H4':'rc7+H4','guard':'rc7+H4+guard'}
for k,arms in counts.items():
 for a,row in arms.items():assert row==published[k][mapping[a]],(k,a,row)
assert len(lost)==31
# Native recheck all31 witnesses, all three arms; results by explicit row identity.
with m.Monty() as pool:
 for arm in ARMS:
  tail="\nX['products']=PRODS\nOUT=[]\nfor R in CASES:\n H=FO(R['fragment'],R['price'])\n OUT.append(H['sku'] if H else None)\nOUT\n"
  with pool.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as s:got=s.feed_run(prefixes[arm]+tail,inputs={'PRODS':products,'CASES':lost})
  assert got==[r['results'][arm] for r in lost]
result={'scope':'Exact d7020 seeded k0 cells only; source-product identity is generator intent, not ground truth for ambiguous OCR. No full18,180/cross20,000/older8 claim.','generated_cases':6060,'CPython_resolver_evaluations':18180,'additional_native_lost_hit_evaluations':93,'counts':counts,'lost_inherited_without_marker':lost,'note':'The author mode named full randomly shortens the SKU even when k=0. These31 are inherited resolver acceptances now declined; not31 independently verified valid customer requests. They are not new wrong SKU selections.'}
(P/'forensic-k0-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'counts':counts,'lost':len(lost),'first':lost[0]}))
