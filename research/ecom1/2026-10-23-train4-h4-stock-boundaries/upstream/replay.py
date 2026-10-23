"""Whole-agent replay on sealed observed worlds; model replies are scripted."""
import contextlib,copy,hashlib,io,json,sys
from pathlib import Path
import pydantic_monty as m
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
LIMITS={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
sha=lambda b:hashlib.sha256(b).hexdigest()
CASES=[('actual_t023','t023'),('actual_t063','t063'),('nontruncated','t063'),('ambiguous_same_price','t063'),('exact_other_price','t063'),('benign_exact','t063'),('benign_note','t063'),('substitution_rival','t063')]
class Host:
 def __init__(self,task,case):
  self.world=json.loads((P/'inputs'/task/'world.json').read_text());self.ctx=json.loads((P/'inputs'/task/'context.json').read_text());self.case=case
  self.calls=[];self.answers=[];self.requests=[];self.overlays=[];self.unmatched=[]
  upload=next(p for p in self.world['files'] if p.startswith('/uploads/'))
  if case in ['nontruncated','benign_exact','benign_note']:
   env=copy.deepcopy(self.world['files'][upload]);text=env['content']
   # These fresh upload overlays are explicit controls. Actual cases remain
   # byte-identical to the archived receipt.
   # No drill-bit edit: rc7's existing whole-SKU drop1 already resolves it.
   if case=='nontruncated':text=text.replace('PT-SAW-AK-DHS680-5.','PT-SAW-AK-DHS680-5')
   elif case=='benign_exact':text=text.replace('PT-SAW-AK-DHS680-5.','PT-SAW-MAK-DHS680-5AH')
   elif case=='benign_note':text+='\nReceipt note: Paper copy reprinted at the service desk.\n'
   assert text!=env['content'];self.replace_file(upload,text)
  if case in ['ambiguous_same_price','exact_other_price','substitution_rival']:
   # Explicit synthetic catalogue overlay at an already enumerated unrelated
   # file; no tree entry is invented or silently omitted.
   path='/proc/catalog/Alpen/PT-BIT-ALP-HSS-19.json'
   obj=json.loads(self.world['files'][path]['content'])
   obj['sku']={'ambiguous_same_price':'PT-SAW-MAK-DHS680-5ZZ','exact_other_price':'PT-SAW-AK-DHS680-5','substitution_rival':'PT-SAW-AX-DHS680-5'}[case]
   obj['price_cents']=42991 if case=='exact_other_price' else 42990
   self.replace_file(path,json.dumps(obj))
 def replace_file(self,path,text):
  before=copy.deepcopy(self.world['files'][path]);after=copy.deepcopy(before);after['content']=text;after['sha256']=sha(text.encode())
  self.world['files'][path]=after;self.overlays.append({'path':path,'before':before,'after':after,'synthetic':True})
 def task(self):return {'instruction':self.ctx['instruction']}
 def usage(self):return {'offline':True}
 def answer(self,message,*,outcome,refs):self.answers.append({'message':message,'outcome':outcome,'refs':refs});return {}
 def call(self,method,args):
  self.calls.append([method,copy.deepcopy(args)])
  assert method not in ['Write','Delete'],'mutation forbidden in this availability replay'
  if method=='Read' and args.get('path') in self.world['files'] and all(k=='path' or v in (0,False) for k,v in args.items()):return copy.deepcopy(self.world['files'][args['path']])
  matches=[r for r in self.world['rpc'] if canon([r['method'],r['arguments']])==canon([method,args])]
  if matches:
   assert all(r['response']==matches[0]['response'] for r in matches);return copy.deepcopy(matches[0]['response'])
  self.unmatched.append([method,args]);raise RuntimeError('UNMATCHED '+canon([method,args]))
 def llm(self,*args,**kwargs):
  self.requests.append({'args':copy.deepcopy(args),'kwargs':copy.deepcopy(kwargs)})
  replies=[e['data']['response'] for e in self.ctx['llm_events'] if e['kind']=='llm_response']
  assert len(self.requests)<=2,'unexpected inference continuation'
  return copy.deepcopy(replies[len(self.requests)-1])
def execute(source,task,case,engine,pool):
 host=Host(task,case);out=[];stream=io.StringIO();error=None
 try:
  if engine=='native':
   with pool.checkout(limits=LIMITS) as session:session.feed_run(source,inputs={'bitgn':m.ClassInstance(host,allowed_methods={'task','call','llm','answer','usage'})},print_callback=lambda *a:out.append(str(a[-1])))
  else:
   with contextlib.redirect_stdout(stream):exec(compile(source,'agent.py','exec'),{'bitgn':host})
 except Exception as e:error=str(e)
 assert not error and not host.unmatched,(task,case,engine,error)
 assert len(host.answers)==1
 return {'case':case,'task':task,'engine':engine,'calls':host.calls,'requests':host.requests,'answers':host.answers,'overlays':host.overlays,'stdout':''.join(out) if engine=='native' else stream.getvalue(),'unmatched':host.unmatched}
def main():
 rows=[];parity={}
 with m.Monty() as pool:
  for arm,forms in [('parent',{'readable':'parent-readable.py','packed':'parent.py'}),('H4',{'readable':'readable.py','packed':'agent.py'})]:
   for form,path in forms.items():
    source=(P/path).read_text()
    for case,task in CASES:
     for engine in ['CPython','native']:
      r=execute(source,task,case,engine,pool);r.update(arm=arm,form=form,source_sha256=sha(source.encode()));rows.append(r)
      comparable={k:r[k] for k in ['calls','requests','answers','overlays','stdout']}
      key=arm,case
      if key in parity:assert comparable==parity[key],key
      else:parity[key]=comparable
 summary=[]
 for case,task in CASES:
  p=next(r for r in rows if (r['case'],r['arm'],r['form'],r['engine'])==(case,'parent','packed','native'))
  h=next(r for r in rows if (r['case'],r['arm'],r['form'],r['engine'])==(case,'H4','packed','native'))
  assert p['calls']==h['calls'],case
  assert p['requests'][0]==h['requests'][0],case
  summary.append({'case':case,'task':task,'synthetic':not case.startswith('actual'),'parent_inference_boundaries':len(p['requests']),'H4_inference_boundaries':len(h['requests']),'parent_answer':p['answers'][0],'H4_answer':h['answers'][0],'ECOM_calls_identical':True})
 report={'status':'PASS offline replay mechanics, semantic review separate','executions':len(rows),'limits':LIMITS,'summary':summary,'rows':rows,'no_live_model_calls':True,'router_and_fallback_replies':'fixed historical response bodies; not generated on changed source/context','host_derivations':0}
 (P/'replay-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'executions':len(rows),'summary':[{'case':r['case'],'parent_calls':r['parent_inference_boundaries'],'H4_calls':r['H4_inference_boundaries'],'H4_outcome':r['H4_answer']['outcome'],'H4_message':r['H4_answer']['message']} for r in summary]},ensure_ascii=False))
if __name__=='__main__':main()
