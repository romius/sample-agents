"""Validate exact offline plan structure; no semantic scoring or provider access."""
import copy
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parents[3]
def canon(x): return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def check_request(req):
    assert set(req)=={'args','kwargs'}
    assert len(req['args'])==2 and req['args'][0]=='openai/gpt-oss-120b'
    assert req['kwargs']=={'max_completion_tokens':2048,'reasoning':{'effort':'medium'},'temperature':0}
    assert isinstance(req['args'][1],list) and all(set(m)=={'role','content'} for m in req['args'][1])
def check_order(calls):
    assert len(calls)==20
    assert [r['ordinal'] for r in calls]==list(range(1,21))
    for fixture in ['A023','A063','B023','U063','V063']:
        group=[r for r in calls if r['fixture']==fixture]
        assert sorted((r['repeat'],r['arm']) for r in group)==[(1,'H'),(1,'P'),(2,'H'),(2,'P')]
        assert [r['arm'] for r in group] in [['P','H','H','P'],['H','P','P','H']]
    first=[calls[i]['fixture'] for i in range(0,10,2)]
    second=[calls[i]['fixture'] for i in range(10,20,2)]
    assert first==['A023','A063','B023','U063','V063'] and second==first[::-1]
def rejection(name,fn):
    try:fn()
    except AssertionError:return {'case':name,'rejected':True}
    raise AssertionError('counterexample accepted: '+name)
def main():
    pins=json.loads((P/'dependency-pins.json').read_text())
    for name,pin in pins.items():
        data=(ROOT/name).read_bytes()
        assert len(data)==pin['bytes'] and sha(data)==pin['sha256'],name
    rows=json.loads((P/'request-manifest.json').read_text())
    assert len(rows)==10
    reqs={}
    for r in rows:
        data=(P/r['path']).read_bytes();q=json.loads(data);check_request(q)
        assert sha(data)==r['file_sha256'] and sha(canon(q))==r['request_canonical_sha256']
        assert sha(canon(q['args'][1]))==r['messages_canonical_sha256']
        reqs[r['fixture'],r['arm']]=q
    calls=json.loads((P/'call-plan.json').read_text())['calls'];check_order(calls)
    for r in calls:
        expected=next(x for x in rows if (x['fixture'],x['arm'])==(r['fixture'],r['arm']))
        assert all(r[k]==v for k,v in expected.items())
    for fid in ['A023','A063','B023','U063']:
        assert reqs[fid,'P']['args'][1]==reqs[fid,'H']['args'][1][:-2]
    assert reqs['V063','P']==reqs['V063','H']==reqs['A063','H']
    assert reqs['A023','P']==reqs['B023','P']
    assert reqs['A063','P']==reqs['U063','P']
    base=reqs['A023','P'];tests=[]
    for label,key,value in [('model drift','model','other-model'),('provider override','provider',{'only':['other']}),('temperature drift','temperature',1),('completion cap drift','max_completion_tokens',4096)]:
        bad=copy.deepcopy(base)
        if key=='model':bad['args'][0]=value
        else:bad['kwargs'][key]=value
        tests.append(rejection(label,lambda:check_request(bad)))
    for label,mutate in [('missing cell',lambda c:c.pop()),('duplicate ordinal',lambda c:c[1].update(ordinal=1)),('unbalanced repeat',lambda c:c[10].update(repeat=1)),('wrong pair order',lambda c:c[10].update(arm=c[11]['arm']))]:
        bad=copy.deepcopy(calls);mutate(bad)
        tests.append(rejection(label,lambda:check_order(bad)))
    changed=copy.deepcopy(base);changed['args'][1][-1]['content']+=' changed'
    tests.append({'case':'message drift changes exact request hash','rejected':sha(canon(changed))!=sha(canon(base))})
    assert all(t['rejected'] for t in tests)
    report={'status':'PASS','dependency_pins':len(pins),'exact_request_files':len(rows),'planned_ordinals':len(calls),
            'counterexamples':tests,'model_calls_made':0,'semantic_scorer':False}
    (P/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='counterexamples'}))
if __name__=='__main__':main()
