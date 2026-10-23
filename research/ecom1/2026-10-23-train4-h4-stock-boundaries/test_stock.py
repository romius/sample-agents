"""Explicit synthetic stock overlays; exact unmodified TRAIN-4/H4 agent bytes."""
import copy,hashlib,importlib.util,json,pathlib,sys
sys.dont_write_bytecode=True
P=pathlib.Path(__file__).resolve().parent
U=P/'upstream'
spec=importlib.util.spec_from_file_location('review_host',U/'replay.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
MANUAL={r['task']:r for r in json.loads((U/'analysis.json').read_text())['manual_receipt_checks']}
POLICY='If a SKU is absent from a branch inventory record, treat that SKU as `0`\nsame-day availability at that branch.'
VARIANTS=['threshold','reserved_threshold']+[f'{k}_{i}' for k in ['short','incoming_only','absent'] for i in range(4)]
CASES=[{'name':f'{t}_{mode}_{v}','task':t,'mode':mode,'variant':v} for t in ['t023','t063'] for mode in (['archived_ocr'] if t=='t023' else ['archived_ocr','exact_saw_control']) for v in VARIANTS]
CASE_MAP={c['name']:c for c in CASES}
OriginalHost=base.Host
class Host(OriginalHost):
 def __init__(self,task,case):
  super().__init__(task,'stock_boundary');self.case=case;c=CASE_MAP[case];manual=MANUAL[task]
  policy=self.world['files']['/docs/availability-checks.md']['content']
  assert POLICY in policy and 'max(on_hand - reserved, 0)' in policy
  assert 'Incoming stock counts only when the user asks to include incoming stock.' in policy
  assert 'today' in self.ctx['instruction'].lower()
  self.before_store=json.loads(self.world['files'][manual['store']]['content'])
  store=copy.deepcopy(self.before_store);assert store['is_open'] is True
  targeted={r['sku']:r['qty'] for r in manual['lines']}
  for item in manual['lines']:
   product=json.loads(self.world['files'][item['product_path']]['content'])
   assert product['sku']==item['sku'] and product['price_cents']==item['unit_cents'] and product['fulfillment_type']==1
  assert manual['expected_answer']['refs']==[manual['upload'],manual['store']]+[r['product_path'] for r in manual['lines']]+['/docs/security.md','/docs/availability-checks.md']
  # Set unrelated existing rows to zero too: a wrong matched SKU must not
  # accidentally pass a positive test because unrelated stock happens to exist.
  for row in store['inventory']:
   row.update(on_hand=targeted.get(row['sku'],0),reserved=0,incoming=[])
  for sku in targeted:assert sum(r['sku']==sku for r in store['inventory'])==1
  variant=c['variant']
  if variant=='reserved_threshold':
   for row in store['inventory']:
    if row['sku'] in targeted:row.update(on_hand=targeted[row['sku']]+3,reserved=3)
  elif variant!='threshold':
   kind,index=variant.rsplit('_',1);sku=manual['lines'][int(index)]['sku'];qty=targeted[sku]
   row=next(r for r in store['inventory'] if r['sku']==sku)
   if kind=='short':row.update(on_hand=qty+2,reserved=3)
   elif kind=='incoming_only':row.update(on_hand=0,reserved=0,incoming=[{'quantity':qty,'arrival_in_days':0},{'quantity':qty,'arrival_in_days':1}])
   elif kind=='absent':store['inventory']=[r for r in store['inventory'] if r['sku']!=sku]
   else:raise AssertionError(kind)
  self.replace_file(manual['store'],json.dumps(store,ensure_ascii=False))
  if c['mode']=='exact_saw_control':
   path=manual['upload'];text=self.world['files'][path]['content'];assert text.count('PT-SAW-AK-DHS680-5.')==1
   self.replace_file(path,text.replace('PT-SAW-AK-DHS680-5.','PT-SAW-MAK-DHS680-5AH'))
  # Oracle reads explicit intended SKUs and policy, never agent matching output.
  self.oracle_lines=[]
  for item in manual['lines']:
   rows=[r for r in store['inventory'] if r['sku']==item['sku']];assert len(rows)<=1
   available=max(rows[0]['on_hand']-rows[0]['reserved'],0) if rows else 0
   self.oracle_lines.append({'sku':item['sku'],'qty':item['qty'],'row_present':bool(rows),'inventory':rows[0] if rows else None,'available_today':available,'sufficient':available>=item['qty']})
  self.positive=all(r['sufficient'] for r in self.oracle_lines)
  assert self.positive==(variant in ['threshold','reserved_threshold'])
  self.expected={'message':({'t023':'TRUE(1)','t063':'ja'} if self.positive else {'t023':'FALSE(2)','t063':'nein'})[task],'outcome':'OUTCOME_OK','refs':manual['expected_answer']['refs']}
  for ref in self.expected['refs']:assert ref in self.world['files']
  self.citation_hashes={ref:base.sha(self.world['files'][ref]['content'].encode()) for ref in self.expected['refs']}
base.Host=Host
def main():
 for pin in json.loads((P/'input-pins.json').read_text()):
  data=(P/pin['path']).read_bytes();assert len(data)==pin['bytes'] and base.sha(data)==pin['sha256']
 rows=[];parity={};summaries=[]
 with base.m.Monty() as pool:
  for arm,forms in [('parent',{'readable':'parent-readable.py','packed':'parent.py'}),('H4',{'readable':'readable.py','packed':'agent.py'})]:
   for form,path in forms.items():
    source=(U/path).read_text()
    for c in CASES:
     oracle=Host(c['task'],c['name'])
     for engine in ['CPython','native']:
      r=base.execute(source,c['task'],c['name'],engine,pool)
      r.update(arm=arm,form=form,source_sha256=base.sha(source.encode()))
      assert not r['unmatched']
      assert all(method not in ['Write','Delete'] and (method!='Exec' or args['path'] in ['/bin/id','/bin/date']) for method,args in r['calls'])
      reached=arm=='H4' or c['task']=='t023' or c['mode']=='exact_saw_control'
      assert len(r['requests'])==(1 if reached else 2),(c,arm,engine)
      if reached:assert r['answers']==[oracle.expected],(c,arm,engine,r['answers'],oracle.expected)
      else:
       # The unchanged archived denial is a fixed fallback fixture, not an
       # assertion that changed stock would cause a model to deny access.
       responses=[e['data']['response'] for e in oracle.ctx['llm_events'] if e['kind']=='llm_response']
       assert len(responses)==2
       assert r['answers']==[oracle.ctx['answer'][0]['arguments']]
      r['helper_reached']=reached;r['stock_oracle']=oracle.expected;r['oracle_lines']=oracle.oracle_lines;r['citation_content_hashes']=oracle.citation_hashes
      comparable={k:r[k] for k in ['calls','requests','answers','overlays','stdout']}
      key=(arm,c['name'])
      if key in parity:assert comparable==parity[key],key
      else:parity[key]=comparable
      rows.append(r)
 for c in CASES:
  parent=next(r for r in rows if r['case']==c['name'] and r['arm']=='parent' and r['form']=='packed' and r['engine']=='native')
  h4=next(r for r in rows if r['case']==c['name'] and r['arm']=='H4' and r['form']=='packed' and r['engine']=='native')
  assert parent['calls']==h4['calls'] and parent['requests'][0]==h4['requests'][0]
  summaries.append({**c,'synthetic':True,'expected_answer':h4['stock_oracle'],'oracle_lines':h4['oracle_lines'],'parent_answer':parent['answers'][0],'H4_answer':h4['answers'][0],'parent_helper_reached':parent['helper_reached'],'H4_helper_reached':True,'ECOM_calls_identical':True})
 report={'status':'PASS bounded synthetic stock overlays','cases':len(CASES),'executions':len(rows),'native_executions':sum(r['engine']=='native' for r in rows),'unmatched':0,'mutations':0,'live_calls':0,'derived_trees':0,'source_limit':65536,'limits':base.LIMITS,'model_reply_cap':2,'summary':summaries,'rows':rows}
 (P/'results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ['summary','rows']}))
if __name__=='__main__':main()
