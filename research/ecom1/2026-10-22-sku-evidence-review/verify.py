"""Frozen real catalogue observations and bounded-port counterexamples, no model calls."""
import ast,copy,hashlib,io,json,sys
from pathlib import Path
import pydantic_monty as m
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-record-integration'
PARENT=HERE.parent/'2026-10-22-inventory-integration'
source=(PARENT/'readable.py').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=='aef93a8c2b25feeb097e70a063d5ffff6c15f52622a3e4e058859901b0a921e1'
names=['words','haystack','best_matches','product_view']
functions='\n\n'.join(ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names)
helper=(HERE/'bounded_lookup_evidence.py').read_text();scope={};exec(functions+'\n'+helper,scope)
worlds=json.loads((HERE.parent/'2026-10-22-clarification-review/world-fixtures.json').read_text())
prompts=json.loads((HERE/'upstream/prompts').read_text())
def captured(event):
    for message in event['data']['request']['messages'][::-1]:
        text=message['content']
        if text.startswith('{"tool": "catalog"') and '\n' in text:
            action,body=text.split('\n',1);return json.loads(action)['query'],json.loads(body)
    raise AssertionError('missing catalog observation')

def apply(base,query,pool,scope_name='sku_lookup',budget=9500,native=False):
    originals=copy.deepcopy([base,pool])
    if not native:
        result=scope['bounded_lookup_evidence'](base,query,pool,scope_name,budget)
        assert originals==[base,pool]
        return result
    output=[]
    code=functions+'\n'+helper+'\nresult=bounded_lookup_evidence(base,query,pool,scope_name,budget)\nprint(json.dumps(result))'
    with m.Monty() as engine:
        with engine.checkout() as session:
            session.feed_run(code,inputs=dict(base=base,query=query,pool=pool,scope_name=scope_name,budget=budget),
                print_callback=lambda *a:output.append(a))
    text=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in output)
    assert originals==[base,pool]
    return json.loads(text)

results={'record_worlds':[],'counterexamples':[]}
for event,trial in [('3116','t021'),('5648','t041')]:
    query,base=captured(prompts[event]);pool=worlds[trial]['products']
    reproduced=scope['best_matches'](pool,query,['sku','name','brand','family_id','kind_id','category_id'],8)
    assert [(s,p['sku']) for s,p in reproduced]==[(p['score'],p['sku']) for p in base['matches']]
    row=apply(base,query,pool);assert row==apply(base,query,pool,native=True)
    assert all(row[k]==v for k,v in base.items())
    e=row['sku_lookup_evidence'];assert not e['pool_complete']
    if trial=='t041':
        target=[p for p in e['siblings'] if p['family_id']=='fam-metabo-w-18-ltx-125']
        assert len(target)==3 and all('standard' in p['lexical_query_tokens_absent'] for p in target)
        assert [p['sku'] for p in target if 'head' in p['lexical_query_tokens_found']]==['PT-GRD-MET-W18-125-FLAT']
    else:
        target=[p for p in e['siblings'] if p['family_id']=='fam-dewalt-dcf887-xr']
        assert sum('case' in p['lexical_query_tokens_found'] for p in target)==2
    results['record_worlds'].append(dict(trial=trial,query=query,original_bytes=len(json.dumps(base).encode()),
        amended_bytes=len(json.dumps(row).encode()),indexed_pool_size=len(pool),rank_reproduced=True,observation=row))
    # Reordering, arbitrary scores, narrower display and original-request qualifiers.
    reverse=apply(base,query,list(reversed(pool)));assert reverse==row
    score=copy.deepcopy(base)
    for p in score['matches']:p['score']=999-p['score']
    assert apply(score,query,pool)['sku_lookup_evidence']==e
    narrow=dict(base,matches=base['matches'][:1]);n=apply(narrow,query,pool)
    family=base['matches'][0]['family_id']
    assert len([p for p in n['sku_lookup_evidence']['siblings'] if p['family_id']==family])==3
    results['counterexamples'].append(dict(case=trial+'-order-score-hidden-sibling',passed=True))
    # All unestablished/nonlookup scopes leave the observation byte-equivalent.
    for other in ['stock','count','security','receipt','mutation','unknown','']:
        assert apply(base,query,pool,other)==base
        assert apply(base,query,pool,other,native=True)==base
    # Bound every serialized attachment; when even metadata cannot fit leave base untouched.
    for budget in range(0,9501,37):
        bounded=apply(base,query,pool,budget=budget)
        if bounded!=base:
            assert len(json.dumps(bounded).encode())<=budget
            ev=bounded['sku_lookup_evidence']
            assert ev['returned_siblings']==len(ev['siblings'])
            assert ev['evidence_truncated']==(len(ev['siblings'])<ev['eligible_indexed_siblings'])
        assert all(bounded[k]==v for k,v in base.items())
    for budget in [0,1024,3000,5000,8000,9500]:assert apply(base,query,pool,budget=budget)==apply(base,query,pool,budget=budget,native=True)
# Synthetic malformed, giant, unicode and missing-attribute records.
base={'matches':[{'sku':'A','family_id':'f','score':2}],'indexed_products':1}
pool=[{'sku':'A','_path':'/catalog/a.json','family_id':'f','name':'Acme flat-head tool'},
      {'sku':'B','_path':'/catalog/b.json','family_id':'f','name':'Acme tool'}]
row=apply(base,'Acme standard head tool',pool);assert row==apply(base,'Acme standard head tool',pool,native=True)
e=row['sku_lookup_evidence'];assert len(e['siblings'])==2 and all('properties' not in p for p in e['siblings'])
assert all('standard' in p['lexical_query_tokens_absent'] for p in e['siblings'])
invalid=apply(base,'tool',pool+[None,{'family_id':'f'}]);assert invalid['sku_lookup_evidence']['invalid_indexed_records']==2
huge=copy.deepcopy(pool);huge[0]['properties']={'label':'雪"\\'*5000}
row=apply(base,'tool',huge);assert len(json.dumps(row).encode())<=9500 and row['sku_lookup_evidence']['evidence_truncated']
assert apply({'matches':[]},'tool',pool)=={'matches':[]}
assert apply(base,'x'*4097,pool)==base
assert apply(base,'tool',pool*1025)==base
for budget in [True,-1,9501,'9000']:
    try:apply(base,'tool',pool,budget=budget)
    except ValueError:pass
    else:raise AssertionError(budget)
results['counterexamples'].append(dict(case='missing-attribute-unicode-size-malformed-limit-scope',passed=True))
results['budget_checks']=len(range(0,9501,37))*2
results['native_cases']=2*(1+7+6)+1
results['limits']='Observation construction only. No model call, answer rewrite, measured outcome improvement or shipping intent parser. Pool completeness is explicitly unverified despite independently complete archived fixtures. Oversized base observation is preserved and no extra evidence is attached. Original matches/ranking preserved; token coverage is diagnostic.'
(HERE/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS:2 exact-world ranks and native observations;516 budget checks;29 native cases; order/score/hidden-sibling/scope/malformed/size controls. No LLM-outcome claim.')
