"""Inspect the exact per-world catalogue, not a union catalogue; reproduce predicate counterexamples."""
import hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE/'clar_refilter_d4545r3.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
worlds={}
for trial in ['t021','t041']:
    events=sorted(sum([json.loads(p.read_text()) for p in HERE.glob(trial+'-part*.json')],[]),key=lambda e:e['seq'])
    reads={e['data']['response']['path']:e['data']['response'] for e in events if e['kind']=='rpc_response' and e['data'].get('method')=='Read'}
    products=[]
    for path,response in reads.items():
        if path.startswith('/proc/catalog/'):
            product=json.loads(response['content']);product['_path']=path;products.append(product)
    assert len(products)==101
    tree=json.loads((HERE/(trial+'-tree.json')).read_text())['data']['response']['root']
    def leaves(node,parent=''):
        path=parent+'/'+node['name']
        if node['kind']=='NODE_KIND_FILE':return [path]
        return sum([leaves(child,path) for child in node.get('children',[])],[])
    tree_catalog={path for path in leaves(tree) if path.startswith('/proc/catalog/')}
    assert tree_catalog=={p['_path'] for p in products},'catalogue coverage differs from complete Tree'

    start=next(e for e in events if e['kind']=='rpc_response' and e['data'].get('method')=='StartTrial')
    answer=next(e for e in events if e['kind']=='rpc_request' and e['data'].get('method')=='Answer')
    worlds[trial]=dict(instruction=start['data']['response']['instruction'],products=products,
                      answer=answer['data']['arguments'],policy=reads['/docs/catalogue-lookup.md'],
                      start_seq=start['seq'],answer_seq=answer['seq'],catalogue_tree_paths=len(tree_catalog),catalogue_read_coverage_complete=True)
dewalt=[p for p in worlds['t021']['products'] if p.get('family_id')=='fam-dewalt-dcf887-xr']
assert len(dewalt)==3
kits=[p for p in dewalt if 'batteries and case' in p.get('properties',{}).get('kit','')]
assert {p['sku'] for p in kits}=={'PT-IMP-DEW-DCF887-2AH','PT-IMP-DEW-DCF887-5AH'}
metabo=[p for p in worlds['t041']['products'] if p.get('family_id')=='fam-metabo-w-18-ltx-125']
assert len(metabo)==3
names=[p['name']+' '+p['sku'] for p in metabo]
actual=gate.decide(worlds['t041']['instruction'],names,True)
assert actual[0]=='decisive' and 'FLAT' in actual[1]
contradictions=[gate.decide(q,['Acme drill red','Acme drill blue'],True) for q in
               ['code for Acme drill red blue','code for Acme drill blue red']]
assert contradictions[0][1]!=contradictions[1][1]
assert all(r[0]=='decisive' for r in contradictions)
incomplete=gate.decide('code for Acme drill red',['Acme drill red'],False)
assert incomplete[0]=='single'
(HERE/'world-fixtures.json').write_text(json.dumps(worlds,indent=2)+'\n')
result=dict(source_job='j110adb6ab262405f85363cc00efee623',source_revision='d3200r2',
 task021_candidates=[dict(sku=p['sku'],kit=p['properties']['kit']) for p in kits],
 task021_decision='Preserve clarification and display both cited SKUs. No unique kit is established.',
 task041_predicate_counterexample={'request':worlds['t041']['instruction'],'survivors':names,'actual':actual},
 task041_decision='Do not convert clarification to flat-head OK. Existing record OK was itself graded wrong; standard head remains unresolved.',
 contradictory_qualifier_order_results=contradictions,incomplete_single_survivor=incomplete,
 boundary='Do not integrate the CLAR-to-OK predicate. No live grade recomputed; exact source data and settled grades retained.')
(HERE/'review-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
