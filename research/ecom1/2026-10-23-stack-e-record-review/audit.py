"""Offline audit of exact source/data; no SDK, network, model or production writes."""
import ast,base64,contextlib,hashlib,io,json,platform
from collections import Counter
from decimal import Decimal
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,o):(P/n).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def load(n):return json.loads((P/n).read_text())
def events(task,kind):return [json.loads(l) for l in (P/(kind+'-'+task+'.jsonl')).read_text().splitlines()]
def defs(s):return {n.name:n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
def namespace(s):
    nodes=[]
    for n in ast.parse(s).body:
        if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)):nodes.append(n)
        elif isinstance(n,ast.Assign):
            try:ast.literal_eval(n.value)
            except (ValueError,TypeError):continue
            nodes.append(n)
    ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<fixed-source-definitions>','exec'),ns);return ns
def unpack(b):
    tree=ast.parse(b); node=tree.body[-1]
    assert isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and node.value.func.id=='exec'
    data=base64.b85decode(ast.literal_eval(node.value.args[0].args[0]));out=bytearray();i=0
    while i<len(data):
        c=data[i];i+=1
        if c<128:out.extend(data[i:i+c+1]);i+=c+1
        else:
            d=data[i]*256+data[i+1];i+=2;n=c-124
            assert 4<=n<=131 and n<=d<=len(out)
            out.extend(out[-d:len(out)-d+n])
    return bytes(out)

source=(P/'upstream/readable.py').read_text();packed=(P/'upstream/agent.py').read_bytes()
assert len(packed)==62475 and sha(packed)=='56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c'
assert unpack(packed)==source.encode()
parent=unpack((P/'upstream/parent-r1.py').read_bytes()).decode()
donor=(P/'upstream/parserdonor-r2.py').read_text()
pd,sd,dd=defs(parent),defs(source),defs(donor)
changed=[n for n in pd.keys()&sd.keys() if ast.dump(pd[n])!=ast.dump(sd[n])]
assert changed==['i2c_crosslist']
for n in ['crosslist_text','crosslist_uint','crosslist_parse_ocr']:assert ast.dump(sd[n])==ast.dump(dd[n])
ours=(P/'upstream/our-d5789-readable.py').read_text();od=defs(ours)
shared=sorted(sd.keys()&od.keys());same=[n for n in shared if ast.dump(sd[n])==ast.dump(od[n])]
save('source-comparison.json',{'record_sha':sha(source.encode()),'our_successor_sha':sha(ours.encode()),
 'parent_to_record_changed_definitions':changed,'parent_removed':sorted(pd.keys()-sd.keys()),'record_added':sorted(sd.keys()-pd.keys()),
 'parser_donor':'d3585r2','identical_shared_definitions':same,'changed_shared_definitions':sorted(set(shared)-set(same)),
 'our_only_definitions':sorted(od.keys()-sd.keys()),'record_only_definitions':sorted(sd.keys()-od.keys()),
 'limit':'Function AST comparison; does not establish equivalent initialization or dispatch order.'})

run=load('result.json');trials=run['result']['trials'];assert len(trials)==100
instructions={r['task_id']:r for f in sorted(P.glob('instructions-*.json')) for r in json.loads(f.read_text())}
assert len(instructions)==100
oldins={r['task_id']:r['event']['data']['response']['instruction'] for r in load('comparison-d2499-instructions.json')}
rows=[]
for t in trials:
    i=instructions[t['task_id']]['event'];assert i['data']['method']=='StartTrial' and i['data']['trial_id']==t['trial_id']
    text=i['data']['response']['instruction'];row={**t,'instruction':text,'instruction_sha256':sha(text.encode())}
    if oldins:row.update(d2499_provider_control_instruction_equal=text==oldins[t['task_id']],d2499_instruction_sha256=sha(oldins[t['task_id']].encode()))
    rows.append(row)
save('all100-review.json',rows)
assert sum(t['grade']['score']==1 for t in trials)==90
assert sorted(t['task_id'] for t in trials if t['grade']['score']==0)==['t027','t048','t062','t076','t091']
summary={'source_sha256':sha(packed),'run_score':run['result']['run_score'],'model_calls':run['result']['model_calls'],
 'reported_cost_usd':run['result']['reported_cost_usd'],'unknown_cost_calls':run['result']['unknown_cost_calls'],
 'full_scores':90,'zeros':5,'partials':5,'failed_trials':run['result']['failed_trials'],
 'previous_record_score':'0.9012601','record_delta_points':str((Decimal('0.9411366')-Decimal('0.9012601'))*100),
 'same_instructions_as_d2499_provider_control':sum(r.get('d2499_provider_control_instruction_equal',False) for r in rows),
 'dispatch_headroom_points':str(sum(1-Decimal(str(t['grade']['score'])) for t in trials if 0<t['grade']['score']<1)),
 'limit':'Task IDs alone are not paired; instruction equality also does not establish identical worlds.'}
save('summary.json',summary)

ns=namespace(source);checks={}
def products(task):
    out=[]
    for e in events(task,'responses'):
        r=e['data'].get('response',{})
        if r.get('contentType')=='application/json':
            obj=json.loads(r['content'])
            if obj.get('sku'):obj['_path']=r['path'];out.append(obj)
    return out
request=next(r['instruction'] for r in rows if r['task_id']=='t027')
prods=products('t027');selected=ns['i2c_select'](request,prods)
assert [p['sku'] for p in selected]==['PT-BLA-MAK-SPEC-190']
checks['negative_diameter']={'request':request,'parsed_diameter':ns['i2c_diam_of'](request),'actual_selection':[p['sku'] for p in selected],
 'manual_expected':'PT-BLA-MAK-SPEC-165','evidence':'all three actual Makita SPEC product JSONs; grader expected ref; outside190 negation'}
checks['diameter_counterexamples']=[{'request':q,'parsed':ns['i2c_diam_of'](q)} for q in ['190mm blade','outside 190mm listing','not 190mm blade','190mm excluded','above 165mm blade']]
ocr=next(e['data']['response']['content'] for e in events('t076','responses') if e['seq']==10098)
variants=[('actual',ocr),('remove_totals_noise_only',ocr.replace('## scanline ##  Total requested units:','Total requested units:')),
 ('remove_totals_and_memo_prefix_noise',ocr.replace('## scanline ##  Total requested units:','Total requested units:').replace('  %%  MEMO:','MEMO:'))]
checks['crosslist_decline']=[]
for name,text in variants:
    try:r=ns['crosslist_parse_ocr'](text);out={'parsed':r}
    except Exception as e:out={'exception_type':type(e).__name__,'message':str(e)}
    checks['crosslist_decline'].append({'variant':name,'sha256':sha(text.encode()),**out})
assert checks['crosslist_decline'][0]['message']=='OCR must identify one branch and both complete totals'
oldns=namespace(ours);parentns=namespace(parent)
checks['parser_lineage']={}
for label,parser in [('record_crosslist',ns['crosslist_parse_ocr']),('our_d5789_crosslist',oldns['crosslist_parse_ocr']),('bobcat_pre_inara_i2c_xparse',parentns['i2c_xparse'])]:
    try:r=parser(ocr);out={'result':r}
    except Exception as e:out={'exception_type':type(e).__name__,'message':str(e)}
    checks['parser_lineage'][label]=out
# These are tests of explicit synthetic edits, not an implemented permissive repair.
clean=variants[1][1]
checks['crosslist_counterexamples']=[]
for label,text in [('duplicate_units',clean+'Total requested units: 36\n'),('wrong_units',clean.replace('Total requested units: 36','Total requested units: 37')),
 ('embedded_second_units',clean+'customer note: Total requested units: 36\n')]:
    try:r=ns['crosslist_parse_ocr'](text);out={'parsed_rows':len(r['lines'])}
    except Exception as e:out={'exception_type':type(e).__name__,'message':str(e)}
    checks['crosslist_counterexamples'].append({'case':label,**out})
checks['CL_scope']=[{'request':q,'recognized_description':oldns['sku_lookup_description'](q)} for q in
 [request,next(r['instruction'] for r in rows if r['task_id']=='t062'),'sku for makita blade outside 190mm listing. sku only','sku for karcher k4 outside the home car reel listings. sku only']]
assert all(r['recognized_description'] is None for r in checks['CL_scope'][:2])
checks['CL_scope_note']='The scope helper has no outside/negation solver. Supported SKU-only outside descriptions are admitted verbatim; lexical metadata does not invert excluded properties. Neither actual count nor stock request reaches this attachment, and early deterministic answers precede it.'

class CleanupHost:
    def __init__(self,fail=False,dirs=False):self.calls=[];self.fail=fail;self.remaining=['a.txt','b.txt'];self.dirs=dirs
    def call(self,method,args):
        self.calls.append([method,args])
        if method=='List':return {'entries':[{'name':n,'path':'/tmp/review/'+n,'kind':'NODE_KIND_DIR' if self.dirs else 'NODE_KIND_FILE'} for n in self.remaining]}
        assert method=='Delete'
        name=args['path'].split('/')[-1]
        if self.fail and name=='b.txt':raise RuntimeError('BitGN HTTP 404: {"code":"not_found","message":"delete failed: not found"}')
        self.remaining.remove(name);return {}
cleanup_request='Please clean out every temporary file under /tmp/review. Delete all files there and nothing else. Return only the deleted paths, one per line, sorted alphabetically.'
checks['cleanup']=[]
for label,fail,dirs in [('success',False,False),('partial_delete_404',True,False),('directory_decline',False,True)]:
    host=CleanupHost(fail,dirs);ns['bitgn']=host
    with contextlib.redirect_stdout(io.StringIO()):result=ns['i2c_cleanup'](cleanup_request)
    checks['cleanup'].append({'case':label,'result':result,'calls':host.calls,'remaining':host.remaining})
assert checks['cleanup'][0]['result']['message']=='/tmp/review/a.txt\n/tmp/review/b.txt'
assert checks['cleanup'][1]['result']['outcome']=='OUTCOME_OK' and checks['cleanup'][1]['remaining']==['b.txt']
assert checks['cleanup'][2]['result'] is None and len(checks['cleanup'][2]['calls'])==1

# Independent CSV oracle from saved live source records and actual dates (not the candidate compiler).
es=events('t091','events');rs=events('t091','responses')
write=next(e['data']['arguments'] for e in es if e['data'].get('method')=='Write')
answer=next(e['data']['arguments'] for e in es if e['data'].get('method')=='Answer')
store=json.loads(next(e['data']['response']['content'] for e in rs if e['seq']==11957))
from datetime import date
dates=write['content'].splitlines()[0].split(',')[1:];today=next(e['data']['response']['stdout'] for e in rs if e['seq']==11939).strip()[:10]
inv={r['sku']:r for r in store['inventory']};expected=[write['content'].splitlines()[0]]
for p in sorted(products('t091'),key=lambda p:p['sku']):
    r=inv.get(p['sku'],{});vals=[]
    for d in dates:
        offset=(date.fromisoformat(d)-date.fromisoformat(today)).days
        vals.append(max(r.get('on_hand',0)-r.get('reserved',0),0) if offset==0 else sum(i['quantity'] for i in r.get('incoming',[]) if i['arrival_in_days']==offset))
    expected.append(p['sku']+','+','.join(map(str,vals)))
assert '\n'.join(expected)==write['content']
readpaths={e['data']['arguments']['path'] for e in es if e['data'].get('method')=='Read'}
checks['inventory']={'csv_matches_independent_oracle':True,'rows':len(expected)-1,'write_count':sum(e['data'].get('method')=='Write' for e in es),
 'destination_readback':write['path'] in readpaths,'refs_not_read':[r for r in answer['refs'] if r not in readpaths],
 'all_other_refs_were_read':all(r in readpaths for r in answer['refs'] if r!=write['path']),
 'grade_detail':next(r['grade']['detail'] for r in rows if r['task_id']=='t091'),
 'limit':'Grader gives no per-ref invalidity list; omission of report readback is a testable hypothesis, not established sole cause.'}
save('mechanism-checks.json',{'python':platform.python_version(),'real_sdk_calls':0,'model_calls':0,'checks':checks})
print(json.dumps({'status':'passed','all100':len(rows),'mechanism_groups':len(checks),'delta':summary['record_delta_points']}))
