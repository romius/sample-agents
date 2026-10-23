import ast,copy,hashlib,json
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
LIMITS={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
K='PT-DRL-MAK-ABCDEF';C='PT-DRL-MAXK-ABCDEF';E=C+'GH'
def p(s,price=100):return {'sku':s,'price_cents':price}
cases=[]
def add(name,key,ps,expected,price=100,note='',alias=False):cases.append({'name':name,'fragment':key,'price':price,'products':ps,'expected':expected,'oracle_scope':note,'alias_duplicate':alias})
# Published original six versus six BOTH-extended cells, separately frozen.
for group,candidate,extend in [('original',C,False),('both_extended',E,True),('candidate_only_extended',E,False)]:
 for r,pr,tag in [(K,101,'exact'),('PT-DRL-MAK-ABCDGF',100,'sub_same'),('PT-DRL-MAK-ABCDGF',101,'sub_other')]:
  rival=r+('GH' if extend else '')
  expect=[None,None,None] if tag=='exact' and not extend else ([C,C,None] if group=='original' else [None,E,None])
  for reverse in [False,True]:
   ps=[p(candidate),p(rival,pr)];ps=ps[::-1] if reverse else ps
   add(group+'_'+tag+('_reverse' if reverse else ''),K+'.',ps,expect,note='Resolver identity oracle, not a claim which OCR source is true.')
add('old_full_drop1_alone',K,[p(C)],[C,C,C])
for tag,rival in [('substitution','PT-DRL-MAK-ABCDGF'),('insertion','PT-DRL-MAYK-ABCDEF'),('deletion','PT-DRL-MAK-ABCDE')]:
 for price in [100,101]:
  expected=[None,None,None] if tag=='insertion' and price==100 else [C,C,None]
  add('old_full_drop1_'+tag+'_'+str(price),K,[p(C),p(rival,price)],expected,note='Demonstrates guard also reaches inherited nontruncated drop-one path.')
  add('new_H4_'+tag+'_'+str(price),K+'.',[p(E),p(rival+'GH',price)],[None,None,None] if tag=='insertion' and price==100 else [None,E,None],note='Prefix rival at edit distance one; all-price veto expected.')
for name,ps,expected in [
 ('H4_unique',[p(E)],[None,E,E]),('H4_far_rival',[p(E),p('PT-DRL-MAK-AGHTUF',101)],[None,E,E]),
 ('H4_equal_value_duplicate',[p(E),p(E)],[None,None,None]),
 ('H4_other_price_duplicate',[p(E),p(E,101)],[None,E,None]),
 ('H4_two_distinct_hits',[p(E),p('PT-DRL-MAYK-ABCDEFGH')],[None,None,None]),
 ('H4_wrong_price',[p(E,101)],[None,None,None]),
 ('H4_substitution_only',[p('PT-DRL-MAK-ABCDGF')],[None,None,None]),
 ('exact',[p(K)],[K,K,K]),
 ('exact_duplicate',[p(K),p(K)],[None,None,None]),
 ('direct_prefix_alone',[p(K+'GH')],[K+'GH']*3),
 ('direct_prefix_with_near_otherprice',[p(K+'GH'),p('PT-DRL-MAK-ABCDGFGH',101)],[K+'GH']*3),
 ('direct_prefix_two_prices_same_sku',[p(K+'GH'),p(K+'GH',101)],[K+'GH']*3),
 ('direct_prefix_two_same_price',[p(K+'GH'),p(K+'ZZ')],[None]*3),
]:add(name,K+'.',ps,expected,note='Exact and direct-prefix branches bypass fuzzy rival guard by design.')
add('same_object_alias_duplicate',K+'.',[p(E)],[None]*3,alias=True,note='Runtime appends same dict object twice, not JSON-created equal copies; both hits still counted.')
for value in [True,100.0,'100',0,-1]:add('invalid_price_'+repr(value),K+'.',[p(E)],[None]*3,price=value)
add('nontruncated_long_candidate',K,[p(E)],[None]*3)
add('short_fragment','PT-AK.',[p(E)],[None]*3)
# Exact observed catalogue and OCR, original source facts/hash checked.
world_cases=[]
for task in ['t023','t063']:
 w=json.loads((P/'inputs'/(task+'-world.json')).read_text());ps=[]
 for path,f in w['files'].items():
  assert hashlib.sha256(f['content'].encode()).hexdigest()==f['sha256']
  if path.startswith('/proc/catalog/'):
   x=json.loads(f['content']);x['_path']=path;ps.append(x)
 text=next(f['content'] for path,f in w['files'].items() if path.startswith('/uploads/'))
 for benign in [False,True]:world_cases.append({'name':task+('_benign_note' if benign else ''),'text':text+('\nReceipt note: Reprinted at service desk. Amounts unchanged.\n' if benign else ''),'products':ps})
(P/'fixtures.json').write_text(json.dumps({'neutral':cases,'actual_and_benign':world_cases},indent=2,ensure_ascii=False)+'\n')
tail='''
REVIEW_OUT=[]
for RC in REVIEW_CASES:
 X['products']=RC['products']
 if RC.get('alias_duplicate'):X['products']=X['products']+[X['products'][0]]
 RR=DM(RC['text']) if 'text' in RC else [(1,RC['price'],RC['fragment'])]
 ROW=[]
 for Q,V,F in RR:
  HIT=FO(F,V)
  ROW.append({'fragment':F,'price':V,'quantity':Q,'sku':HIT['sku'] if HIT else None,'identity_indices':[j for j,x in enumerate(X['products']) if x is HIT] if HIT else []})
 REVIEW_OUT.append({'case':RC['name'],'rows':ROW})
'''
results={};pins={}
with m.Monty() as pool:
 for arm,file in [('parent','inputs/parent-readable.py'),('H4','inputs/h4-readable.py'),('guard','upstream/d7019r1-cand_h4g2_dec.py')]:
  src=(P/file).read_text();pins[arm]=hashlib.sha256(src.encode()).hexdigest();anchor='a=[{m:BJ,J:EE}]';assert src.count(anchor)==1;prefix=src[:src.index(anchor)]
  inputs=copy.deepcopy(cases+world_cases);ns={'REVIEW_CASES':inputs};exec(prefix+tail,ns);cp=ns['REVIEW_OUT']
  with pool.checkout(limits=LIMITS) as s:np=s.feed_run(prefix+tail+'\nREVIEW_OUT',inputs={'REVIEW_CASES':copy.deepcopy(cases+world_cases)})
  assert cp==np,(arm,'native mismatch')
  for case,row in zip(cases,cp):
   got=row['rows'][0]['sku'];want=case['expected'][['parent','H4','guard'].index(arm)]
   assert got==want,(arm,case['name'],got,want)
  results[arm]=cp
# Every actual parse including benign note agrees with published d7021 held line identities.
held=dict(json.loads((P/'upstream/d7021r1-guard_test.json').read_text())['held'])
for arm,rows in results.items():
 for task in held:
  for suffix in ['', '_benign_note']:
   got=next(x for x in rows if x['case']==task+suffix)
   assert [x['sku'] for x in got['rows']]==[x[['parent','H4','guard'].index(arm)] for x in held[task]]
report={'scope':'Exact complete pre-bootstrap modules; resolver/parser only, not whole agent or live inference. Neutral oracles state rule behavior, not arbitrary OCR truth.','source_pins':pins,'cases_per_arm':len(cases)+len(world_cases),'CPython_native_evaluations':(len(cases)+len(world_cases))*6,'native_limits':LIMITS,'native_parity':True,'results':results}
(P/'results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='results'}))
