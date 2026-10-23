"""Neutral exact resolver fixtures; reproduce guard bypass, do not silently repair."""
import hashlib,importlib.metadata,json,re,sys
from pathlib import Path
import pydantic_monty as m
from analyze import extracted,namespace,ARMS
P=Path(__file__).resolve().parent
key='PT-DRL-MAK-ABCDEF'
target={'fixture_id':'drop_candidate','sku':'PT-DRL-MAXK-ABCDEF','price_cents':100}
exact_rival={'fixture_id':'exact_other_price','sku':key,'price_cents':101}
tie={'fixture_id':'same_price_substitution','sku':'PT-DRL-MAK-ABCDGF','price_cents':100}
other_tie={**tie,'fixture_id':'other_price_substitution','price_cents':101}
second_drop={'fixture_id':'second_drop','sku':'PT-DRL-MAYK-ABCDEF','price_cents':100}
F=[
 {'case':'unique_truncated_drop','fragment':key+'.','cents':100,'catalogue':[target],'expected':[None,'drop_candidate','drop_candidate','drop_candidate'],'interpretation':'H4 broadens bare parent; unique X10 fuzzy target also accepted.'},
 {'case':'different_price_exact_rival','fragment':key+'.','cents':100,'catalogue':[target,exact_rival],'expected':[None,'drop_candidate',None,'drop_candidate'],'interpretation':'Composition bypasses X10 global-price closer-rival rejection.'},
 {'case':'same_price_equal_distance_rival','fragment':key+'.','cents':100,'catalogue':[target,tie],'expected':[None,'drop_candidate',None,'drop_candidate'],'interpretation':'Composition bypasses X10 same-price nearest-distance tie rejection.'},
 {'case':'different_price_equal_distance_rival','fragment':key+'.','cents':100,'catalogue':[target,other_tie],'expected':[None,'drop_candidate',None,'drop_candidate'],'interpretation':'Composition bypasses X10 all-price equal-distance rival rejection.'},
 {'case':'two_H4_hits','fragment':key+'.','cents':100,'catalogue':[target,second_drop],'expected':[None,None,None,None],'interpretation':'Ambiguous H4 hits remain rejected.'},
 {'case':'unique_nontruncated_drop','fragment':key,'cents':100,'catalogue':[target],'expected':[None,None,'drop_candidate','drop_candidate'],'interpretation':'H4 does not broaden nontruncated input; X10 fuzzy route unchanged.'},
 {'case':'nontruncated_exact_rival','fragment':key,'cents':100,'catalogue':[target,exact_rival],'expected':[None,None,None,None],'interpretation':'X10 global rival guard remains active without H4 cut trigger.'},
 {'case':'exact_same_price','fragment':key,'cents':100,'catalogue':[{'fixture_id':'exact','sku':key,'price_cents':100}],'expected':['exact']*4,'interpretation':'Clean exact match retained.'},
 {'case':'wrong_price_only','fragment':key+'.','cents':100,'catalogue':[{**target,'price_cents':101}],'expected':[None]*4,'interpretation':'No target at receipt price, all decline.'},
 {'case':'inherited_direct_prefix_other_price_rival','fragment':key+'.','cents':100,'catalogue':[{'fixture_id':'direct_prefix','sku':key+'-KIT','price_cents':100},exact_rival],'expected':['direct_prefix']*4,'interpretation':'All-price guard was never universal: direct-prefix route already bypasses it in parent/X10; this is not a new H4 regression.'}
]
(P/'resolver-fixtures.json').write_text(json.dumps({'scope':'Neutral synthetic resolver-only dictionaries, not whole ECOM records or actual observed catalogue. Expected outputs document current implementations; ambiguity expectations are X10 guard-preservation controls, not hidden human intent.','fixtures':F},indent=2)+'\n')
def lev(a,b):
 table=[[0]*(len(b)+1) for _ in range(len(a)+1)]
 for i in range(len(a)+1):table[i][0]=i
 for j in range(len(b)+1):table[0][j]=j
 for i in range(1,len(a)+1):
  for j in range(1,len(b)+1):table[i][j]=min(table[i-1][j]+1,table[i][j-1]+1,table[i-1][j-1]+(a[i-1]!=b[j-1]))
 return table[-1][-1]
allrows=[]
with m.Monty() as pool:
 for ai,arm in enumerate(ARMS):
  program='import re\nimport json\n'+extracted(arm)+'\nFIXTURES=json.loads('+repr(json.dumps(F))+')\nrows=[]\n'
  program+='''for fixture in FIXTURES:
 for order in ['forward','reverse']:
  products=fixture['catalogue'] if order=='forward' else list(reversed(fixture['catalogue']))
  WORLD={'products':products,'stores':[]}
  chosen=rcp_product(fixture['fragment'],fixture['cents'])
  rows.append({'case':fixture['case'],'order':order,'selected':chosen['fixture_id'] if chosen else None})
print(json.dumps(rows))
'''
  printed=[];exec(program,{'print':printed.append});cpu=json.loads(printed[0]);printed=[]
  with pool.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as session:session.feed_run(program,print_callback=lambda kind,text:printed.append(text))
  native=json.loads(''.join(printed));assert native==cpu
  for r in cpu:
   fixture=next(f for f in F if f['case']==r['case']);assert r['selected']==fixture['expected'][ai],(arm,r)
   allrows.append({'arm':arm,**r,'CPython_native_parity':True})
# Independent distance/normalization evidence for the three new counterexamples.
g=namespace('X10',[],[]);evidence=[]
for f in F:
 norm=g['ocr_key'](f['fragment']).rstrip('.');facts=[]
 for product in f['catalogue']:
  sku=g['ocr_key'](product['sku']);prefix=sku[:len(norm)+1]
  drops=[i for i in range(len(prefix)) if prefix[:i]+prefix[i+1:]==norm] if len(prefix)==len(norm)+1 else []
  facts.append({'fixture_id':product['fixture_id'],'sku':product['sku'],'price_cents':product['price_cents'],'normalized_SKU':sku,'full_edit_distance_to_key':lev(sku,norm),'H4_prefix_drop_positions':drops,'receipt_price_matches':product['price_cents']==f['cents']})
 evidence.append({'case':f['case'],'normalized_fragment_key':norm,'truncated_flag':f['fragment'].endswith(('.','-')),'catalogue_evidence':facts,'return_by_arm':dict(zip(ARMS,f['expected'])),'interpretation':f['interpretation']})
report={'status':'three H4-before-fuzzy guard bypass counterexamples reproduced; composition unqualified','source_pins':{a:hashlib.sha256((P/'arms'/a/'readable.py').read_bytes()).hexdigest() for a in ARMS},'fixtures':len(F),'arm_permutation_cells':len(allrows),'native_and_CPython_evaluations':len(allrows)*2,'python':sys.version.split()[0],'monty':importlib.metadata.version('pydantic-monty'),'all_permutations_same_identity':True,'rows':allrows,'evidence':evidence,'model_calls':0,'no_proposed_repair_applied':True}
(P/'resolver-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'fixtures':len(F),'cells':len(allrows),'native_and_CPython_evaluations':len(allrows)*2,'counterexamples':[e for e in evidence if e['case'] in ['different_price_exact_rival','same_price_equal_distance_rival','different_price_equal_distance_rival']]},indent=2))
