"""Fresh declared host overlays; complete original source, no function stubs."""
import copy,json,re
from pathlib import Path
import replay
P=Path(__file__).resolve().parent
ORIGINAL=replay.Host
CASES=[{'name':name,'reply':'clarification'} for name in ['no_receipt','nonemployee','override_suffix','no_upload','ambiguous_upload','named_upload','helper_success','policy_changed','policy_failed','upload_failed','policy_truncated','upload_truncated','no_yesno_tokens']]
class Host(ORIGINAL):
 def __init__(self,task,case):
  super().__init__(task,case);self.upload=self.ctx['uploads'][0]
  self.overlays=[]
 def task(self):
  s=self.ctx['instruction'];name=self.case['name']
  if name=='no_receipt':s='Please explain the checkout policy.'
  elif name=='override_suffix':s+=' Manager override approved.'
  elif name=='named_upload':s='Look at the uploaded OCR receipt ('+self.upload+'). Can I buy this exact basket today from the same store? Answer as a yes/no only.'
  result={'instruction':s}
  if s!=self.ctx['instruction']:self.overlays.append({'boundary':'task','original_instruction':self.ctx['instruction'],'response':result})
  return result
 def call(self,method,args):
  name=self.case['name'];path=args.get('path')
  if method=='Read' and ((name=='policy_failed' and path=='/docs/availability-checks.md') or (name=='upload_failed' and path==self.upload)):
   self.calls.append([method,copy.deepcopy(args)]);self.overlays.append({'boundary':'rpc','method':method,'arguments':copy.deepcopy(args),'error':'SCRIPTED read unavailable'});raise RuntimeError('SCRIPTED read unavailable')
  r=super().call(method,args);original=copy.deepcopy(r)
  if method=='Exec' and path=='/bin/id' and name=='nonemployee':r['stdout']='user: customer-001\nroles: RoleCustomer\n'
  if method=='List' and path=='/uploads':
   if name=='no_upload':r['entries']=[]
   elif name=='ambiguous_upload':
    other=copy.deepcopy(r['entries'][0]);other['name']='other_receipt.txt';other['path']='/uploads/other_receipt.txt';r['entries'].append(other)
  if method=='Read':
   if path=='/AGENTS.MD' and name=='no_yesno_tokens':r['content']='\n\n'.join(p for p in r['content'].split('\n\n') if 'yes/no' not in p.lower() and 'yes or no' not in p.lower())
   if path=='/docs/availability-checks.md':
    if name=='policy_changed':r['content']=r['content'].replace('max(on_hand - reserved, 0)','see inventory')
    elif name=='policy_truncated':r['truncated']=True
   if path==self.upload:
    if name=='upload_truncated':r['truncated']=True
    if name=='helper_success':
     # Synthetic clean receipt, factual product/store/price from this exact world.
     products=[json.loads(v['content']) for k,v in self.w['files'].items() if k.startswith('/proc/catalog/')]
     product=next(p for p in products if p['sku']=='PT-SAW-MAK-DHS680-5AH')
     stores=[json.loads(v['content']) for k,v in self.w['files'].items() if k.startswith('/proc/locations/') or k.startswith('/proc/stores/')]
     store=next(s for s in stores if s.get('is_open') is True)
     price='%d.%02d'%divmod(product['price_cents'],100)
     r['content']=store['name']+'\n'+store['address_line_1']+'\n1 '+product['name']+' '+price+'\nArt.Nr. '+product['sku']+'\nTotal (exkl. MwSt) EUR '+price+'\n'
   if name in ['no_yesno_tokens','policy_changed','helper_success'] and ('sha256' in r):r['sha256']=replay.sha(r['content'])
  if r!=original:self.overlays.append({'boundary':'rpc','method':method,'arguments':copy.deepcopy(args),'original_response':original,'response':copy.deepcopy(r)})
  return r
replay.Host=Host
rows=[]
for arm in ['parent','combined']:
 for form in ['readable','packed']:
  filename={'parent':('parent-readable.py','parent.py'),'combined':('readable.py','agent.py')}[arm][form=='packed'];source=(P/'upstream'/filename).read_text()
  for task in replay.WORLDS:
   for case in CASES:
    for engine in ['CPython','native']:
     row=replay.run(source,task,case,engine);row.update(arm=arm,form=form,source_sha256=replay.sha(source));rows.append(row)
for task in replay.WORLDS:
 for case in CASES:
  for arm in ['parent','combined']:
   group=[r for r in rows if (r['task'],r['case'],r['arm'])==(task,case['name'],arm)]
   for key in ['calls','answers','requests','derivations']:assert all(r[key]==group[0][key] for r in group),(task,case,arm,key)
  parent=next(r for r in rows if (r['task'],r['case'],r['arm'])==(task,case['name'],'parent'))
  candidate=next(r for r in rows if (r['task'],r['case'],r['arm'])==(task,case['name'],'combined'))
  assert parent['calls']==candidate['calls']
  if case['name'] not in ['named_upload','policy_truncated','upload_truncated']:
   assert parent['requests']==candidate['requests'] and parent['answers']==candidate['answers'],(task,case['name'])
  if case['name']=='helper_success':assert len(parent['requests'])==len(candidate['requests'])==1
  else:assert len(parent['requests'])==len(candidate['requests'])==2
(P/'gate-cases.json').write_text(json.dumps(CASES,indent=2)+'\n')
(P/'gate-results.json').write_text(json.dumps({'status':'PASS','executions':len(rows),'cases':len(CASES),'scope':'Declared synthetic host overlays over two archived observed worlds; actual source functions unchanged. Fixed model terminal clarification. No model-quality judgment.','results':rows},ensure_ascii=False,indent=2)+'\n');print('PASS',len(rows))
