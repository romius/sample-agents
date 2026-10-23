"""Complete exact packed/readable agent execution with archived RPCs and explicit scripted LLM boundary."""
import ast,contextlib,copy,hashlib,io,json,platform
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
W=json.loads((P/'world.json').read_text());EXPECTED=(P/'expected.tsv').read_text()
LIMITS={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(x.encode()).hexdigest()
original=W['files'][W['upload']]['content'];clean=original.replace('## scanline ##  Total requested units:','Total requested units:')
CASES=[('original',original,False,True),('clean',clean,True,True),
 ('duplicate_plain',clean+'Total requested units: 36\n',False,False),
 ('duplicate_noisy',clean+'## scanline ## Total requested units: 36\n',True,False),
 ('contradictory_noisy',clean+'## scanline ## Total requested units: 37\n',True,False),
 ('wrong_units',clean.replace('Total requested units: 36','Total requested units: 37'),False,False),
 ('prose_prefix',original.replace('## scanline ##','customer note:'),False,False)]
fresh=(P/'fresh-two-row-ocr.txt').read_text()
CASES.extend([('fresh_two_row_clean',fresh,True,True),('fresh_two_row_noisy',fresh.replace('Total requested units: 5','## scanline ## Total requested units: 5'),False,True)])
absent=(P/'fresh-absent-inventory-ocr.txt').read_text()
CASES.extend([('fresh_absent_inventory_clean',absent,False,False),('fresh_absent_inventory_noisy',absent.replace('Total requested units: 5','## scanline ## Total requested units: 5'),False,False)])
for name,marker in [('dotless_i','scanlıne'),('dotted_I','scanlİne'),('long_s','ſcanline')]:
 CASES.append((name,original.replace('## scanline ##','## '+marker+' ##'),False,False))
class Host:
 def __init__(self,ocr):self.ocr=ocr;self.calls=[];self.answers=[];self.writes=[];self.llms=[];self.unmatched=[];self.derivations=[]
 def task(self):return copy.deepcopy(W['task'])
 def usage(self):return {'offline_replay':True,'model_calls':0,'reported_cost_usd':'0'}
 def answer(self,message,*,outcome,refs):self.answers.append({'message':message,'outcome':outcome,'refs':refs});return {}
 def call(self,method,args):
  self.calls.append([method,copy.deepcopy(args)])
  key=canon([method,args])
  if method=='Write':
   assert set(args)=={'path','content'} and args['path']==W['export']
   self.writes.append(copy.deepcopy(args));return {'path':args['path']}
  if key in W['rpc']:
   r=copy.deepcopy(W['rpc'][key])
   if method=='Read' and args.get('path')==W['upload']:
    r['content']=self.ocr;r['sha256']=sha(self.ocr)
   return r
  if key in W['derived_rpc']:
   self.derivations.append([method,copy.deepcopy(args)]);return copy.deepcopy(W['derived_rpc'][key])
  self.unmatched.append([method,copy.deepcopy(args)]);raise RuntimeError('UNMATCHED OFFLINE RPC '+key)
 def llm(self,*args,**kwargs):
  self.llms.append({'args':copy.deepcopy(args),'kwargs':copy.deepcopy(kwargs)})
  if len(self.llms)==1:return copy.deepcopy(W['router_response'])
  # Fixed terminal stub when deterministic handling declines; never attempts task solving.
  action={'tool':'report_completion','completed_steps_laconic':[],'message':'OFFLINE FALLBACK: deterministic handler declined.','outcome':'OUTCOME_NONE_UNSUPPORTED','grounding_refs':[]}
  return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(action)}}]}

rows=[]
with m.Monty() as pool:
 for version in ['parent','candidate']:
  for form in ['readable','packed']:
   filename=version+('-readable.py' if form=='readable' else '.py');source=(P/'upstream'/filename).read_text()
   if version=='candidate' and form=='packed':assert sha(source)==json.loads((P.parent/'manifest.json').read_text())['files']['agent.py']['sha256']
   if version=='candidate' and form=='readable':assert sha(source)==json.loads((P.parent/'manifest.json').read_text())['files']['readable.py']['sha256']
   for name,ocr,old_ok,new_ok in CASES:
    for engine in ['cpython','monty']:
     host=Host(ocr);output=io.StringIO();native_out=[]
     if engine=='cpython':
      with contextlib.redirect_stdout(output):exec(compile(source,filename,'exec'),{'bitgn':host})
     else:
      with pool.checkout(limits=LIMITS) as session:
       session.feed_run(source,inputs={'bitgn':m.ClassInstance(host,allowed_methods={'task','call','answer','llm','usage'})},print_callback=lambda *a:native_out.append(str(a[-1])))
     assert not host.unmatched,(version,form,name,engine,host.unmatched)
     assert len(host.answers)==1,(version,form,name,engine,host.answers)
     expect=old_ok if version=='parent' else new_ok
     expected=(P/'fresh-expected.tsv').read_text() if name.startswith('fresh_') else EXPECTED
     assert len(host.writes)==int(expect),(version,form,name,engine,host.writes,host.answers)
     if expect:
      assert host.writes[0]=={'path':W['export'],'content':expected},(version,form,name,engine,host.writes[0],expected)
      assert host.answers==[{'message':W['export'],'outcome':'OUTCOME_OK','refs':[W['upload'],'/docs/security.md','/docs/purchase-request-crosslist.md']}]
      assert len(host.llms)==1
     else:
      assert host.answers[0]['outcome']=='OUTCOME_NONE_UNSUPPORTED' and host.answers[0]['message'].startswith('OFFLINE FALLBACK')
      assert len(host.llms)==2
     assert all(method not in ['Delete'] and (method!='Write' or args['path']==W['export']) for method,args in host.calls)
     rows.append({'version':version,'form':form,'engine':engine,'case':name,'source_sha256':sha(source),'ocr_sha256':sha(ocr),
       'rpc_count':len(host.calls),'rpc_calls':host.calls,'writes':host.writes,'answers':host.answers,
       'scripted_llm_calls':len(host.llms),'router_request_sha256':sha(canon(host.llms[0])),'unmatched_calls':host.unmatched,'derived_tree_requests':host.derivations,
       'output':output.getvalue() if engine=='cpython' else ''.join(native_out)})
for version in ['parent','candidate']:
 for name,*_ in CASES:
  group=[r for r in rows if r['version']==version and r['case']==name]
  for k in ['rpc_calls','writes','answers','scripted_llm_calls','router_request_sha256']:
   assert all(r[k]==group[0][k] for r in group),(version,name,k)
result={'python':platform.python_version(),'monty':'1.2.0','limits':LIMITS,'executions':len(rows),'cases':len(CASES),'real_model_calls':0,'real_sdk_calls':0,
 'scope':'Whole exact packed/readable agents, CPython and native method-only ClassInstance. Frozen actual router response; fixed unsupported terminal stub after deterministic decline. No model quality or live score validated.',
 'mutation_response_note':'Write acknowledgement is a declared local report-write simulation with exact requested path; archived failing trial never wrote a report. All other RPC responses are exact archived responses or explicitly selected actual Tree subtrees.',
 'results':rows}
(P/'replay-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':'passed','executions':len(rows),'zero_unmatched':True,'all_four_forms_equal':True,'oracle_sha256':sha(EXPECTED)}))
