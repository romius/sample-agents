"""Frozen source/request/response accounting checks; no semantic text scorer."""
import ast,base64,contextlib,hashlib,importlib.util,io,json
from verify_wire import verify_wire
from decimal import Decimal
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name):return json.loads((HERE/name).read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,obj):(HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':')).encode()
def decode(source):
    tree=ast.parse(source)
    payload=ast.literal_eval(tree.body[-1].value.args[0].args[0])
    t=base64.b85decode(payload);out=[];i=0
    while i<len(t):
        c=t[i];i+=1
        if c<128:out.extend(t[i:i+c+1]);i+=c+1
        else:
            p=len(out)-((t[i]<<8)|t[i+1]);i+=2;out.extend(out[p:p+c-124])
    return ''.join(chr(x) for x in out)
manifest=load('upstream/manifest.json');continuation=load('upstream/continuation-manifest.json')
frozen=load('frozen.json');oracles=load('upstream/oracles.json')
assert sha((HERE/'frozen.json').read_bytes())==manifest['fixtures_sha256']
assert sha((HERE/'upstream/oracles.json').read_bytes())==manifest['oracles_sha256']
class Host:
    def __init__(self):self.requests=[];self.answers=[]
    def llm(self,model,messages,**kwargs):
        self.requests.append(dict(model=model,messages=messages,**kwargs))
        return {'id':'offline-stub','choices':[{'finish_reason':'stop','message':{'content':'{}'}}]}
    def answer(self,*a,**k):self.answers.append([a,k]);return {}
    def usage(self):return {}
requests={}
for filename,pin,start in [('agent.py',manifest['source_sha256'],0),('continuation-agent.py',continuation['source_sha256'],17)]:
    source=(HERE/'upstream'/filename).read_text();assert sha(source.encode())==pin
    decoded=decode(source);tree=ast.parse(decoded)
    embedded=json.loads(ast.literal_eval(tree.body[1].value.args[0]));assert embedded==frozen
    assert decoded==(HERE/'upstream'/(filename+'.decoded')).read_text()
    host=Host()
    with contextlib.redirect_stdout(io.StringIO()):exec(source,{'bitgn':host})
    assert len(host.requests)==60-start and len(host.answers)==1
    for request,step in zip(host.requests,frozen['plan'][start:]):
        assert sha(canonical(request))==step['request_sha256']
    requests[filename]=host.requests
assert requests['agent.py'][17:]==requests['continuation-agent.py']
for i in range(30):
    pair={s['arm']:r for s,r in zip(frozen['plan'],requests['agent.py']) if s['case_index']==i}
    parent=pair['parent'];treatment=pair['treatment']
    assert {k:v for k,v in parent.items() if k!='messages'}=={k:v for k,v in treatment.items() if k!='messages'}
    assert parent['messages'][:-1]==treatment['messages'][:-1]
    ph,pb=parent['messages'][-1]['content'].split('\n',1);th,tb=treatment['messages'][-1]['content'].split('\n',1)
    po=json.loads(pb);to=json.loads(tb);assert ph==th
    assert to.pop('sku_lookup_evidence')==frozen['cases'][i]['evidence'] and to==po

initial=load('upstream/initial-response-events.json')
following=[e for p in sorted(HERE.glob('continuation-events-*.json')) for e in json.loads(p.read_text())]
initial_responses=[e for e in initial if e['kind']=='llm_response']
assert len(initial_responses)==21 and len(following)==47
aa=[e for e in initial_responses if e['data']['status']==200];bb=[e for e in following if e['data']['status']==200]
assert len(aa)==17 and len(bb)==43
assert all(e['data']['status'] in [200,429] for e in initial_responses+following)
records=load('records.json');assert len(records)==60
for i,(record,step,event) in enumerate(zip(records,frozen['plan'],aa+bb)):
    assert record['step']==step and record['response']==event['data']['response']
    assert record['trace_event']==event['seq'] and record['job']==('initial' if i<17 else 'continuation')
assert len({r['response']['id'] for r in records})==60
spec=importlib.util.spec_from_file_location('upstream_analyze',HERE/'upstream/analyze.py')
analysis=importlib.util.module_from_spec(spec);spec.loader.exec_module(analysis)
assert analysis.analyze(records,frozen,oracles)==load('mechanical-report.json')
wire=verify_wire()
spec2=importlib.util.spec_from_file_location('author_r2',HERE/'author-final/analyze-r2.py')
analysis2=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(analysis2)
report2=analysis2.analyze(records,frozen,oracles)
save('author-final/reproduced-report-r2.json',report2)
report1=load('mechanical-report.json')
diffs=[]
for oldrow,newrow in zip(report1['rows'],report2['rows']):
    for key in set(oldrow)|set(newrow):
        if oldrow.get(key)!=newrow.get(key):diffs.append(dict(case=oldrow['case'],arm=oldrow['arm'],field=key,before=oldrow.get(key),after=newrow.get(key)))
assert diffs==[dict(case='glasses__exclude_ambiguous',arm='parent',field='excluded_quoted_or_cited',before=False,after=True)]
author_manual=load('author-final/manual-grounding-audit.json')['rows']
assert len(author_manual)==60
for manualrow,record in zip(author_manual,records):
    action=json.loads(record['response']['choices'][0]['message']['content'])
    assert manualrow['case']==record['step']['case'] and manualrow['arm']==record['step']['arm']
    assert manualrow['trace_seq']==record['trace_event']
    assert (manualrow['message'],manualrow['refs'],manualrow['outcome'])==(action['message'],action['grounding_refs'],action['outcome'])
save('author-final/comparison.json',dict(manual_response_joins=60,mechanical_row_differences=diffs,
    all_other_mechanical_row_fields_equal=True,initial_scorer_revision=1,final_scorer_revision=2,
    note='Post-observation Unicode-hyphen diagnostic correction; original report retained. Both manual audits agree on four dropped waterproof qualifiers and saw conflict omission. Independent review additionally notes compressor named-reference omission/narrowed alternatives.'))
manual=load('manual-review.json');assert len(manual)==60
foreign=[]
for i,(m,r) in enumerate(zip(manual,records),1):
    content=r['response']['choices'][0]['message']['content']
    assert m['record']==i and m['response_sha256']==sha(content.encode())
    assert m['full_action']==json.loads(content) and m['case']==r['step']['case'] and m['arm']==r['step']['arm']
    c=frozen['cases'][r['step']['case_index']]
    original_paths={x['path'] for x in c['base']['matches']}
    visible_paths=original_paths|{x['path'] for x in c['evidence']['siblings']}
    assert set(m['full_action']['grounding_refs'])<=visible_paths
    oracle=oracles[r['step']['case_index']];assert oracle['case']==m['case']
    family_paths={x['_path'] for x in oracle['source_records']}
    outsiders=[p for p in m['full_action']['grounding_refs'] if p not in family_paths]
    if outsiders:
        assert set(outsiders)<=original_paths
        foreign.append(dict(record=i,case=m['case'],arm=m['arm'],refs=outsiders,already_in_shared_base_matches=True))
assert len(foreign)==4
save('foreign-reference-provenance.json',foreign)
new=load('continuation-index-result.json')['result'];old=load('upstream/initial-settled-result.json')
assert old['result']['model_calls']==21 and new['result']['model_calls']==47
assert old['result']['cost_complete'] and new['result']['cost_complete']
assert old['result']['unknown_cost_calls']==new['result']['unknown_cost_calls']==0
stats=dict(status='passed',frozen_cases=30,logical_calls=60,successful_responses=60,attempts=68,
    initial=dict(job=old['job'],logical_responses=17,attempts=21,reported_cost=old['result']['reported_cost_usd']),
    continuation=dict(job=new['job'],logical_responses=43,attempts=47,reported_cost=new['result']['reported_cost_usd']),
    total_reported_cost=str(Decimal(old['result']['reported_cost_usd'])+Decimal(new['result']['reported_cost_usd'])),
    cost_complete=True,host_429_responses=8,matched_request_hashes=60,continuation_matches_plan_slice=True,
    matched_source_pairs=30,manual_annotations=60,foreign_ref_responses_all_preexisting_in_shared_base=True,
    actual_wire_requests_verified=wire['actual_wire_events'],actual_retry_payloads_verified=wire['identical_retry_payloads'],
    no_real_model_calls_by_review=True,no_semantic_pass_aggregate=True,
    limitations='Request replays are offline stubs; full model traces are not reexecuted. Manual annotations apply to exact outputs, not arbitrary future text. Fixed one-world development holdouts, one pair each; no full100 or C/L result.')
save('verification.json',stats)
listing=json.loads(load('brain-session.json')['output'].split('\n')[0]);deps=[]
for doc in listing:
    name=Path(doc['path']).name;p=HERE/'upstream'/name
    if p.is_file():
        assert len(p.read_bytes())==doc['size'],name
        deps.append(dict(document=doc['id'],revision=doc['revision'],path=doc['path'],local='upstream/'+name,bytes=doc['size'],sha256=sha(p.read_bytes())))
save('DEPENDENCIES.json',deps)
author_docs=load('author-final/directory-snapshot.json');author_deps=[]
for doc in author_docs:
    name=Path(doc['path']).name
    local='analyze-r2.py' if name=='analyze.py' else name
    path=HERE/'author-final'/local
    if path.is_file():
        assert len(path.read_bytes())==doc['size'],name
        author_deps.append(dict(document=doc['id'],revision=doc['revision'],path=doc['path'],local='author-final/'+local,bytes=doc['size'],sha256=sha(path.read_bytes())))
save('author-final/DEPENDENCIES.json',author_deps)
save('SHA256SUMS.json',{str(p.relative_to(HERE)):sha(p.read_bytes()) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json' and '__pycache__' not in p.parts and 'publication' not in p.parts})
print(json.dumps({k:stats[k] for k in ['status','logical_calls','attempts','total_reported_cost','matched_request_hashes','manual_annotations']}))
