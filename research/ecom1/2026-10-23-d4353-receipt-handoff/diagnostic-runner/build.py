"""Deterministic offline build from immutable approved plan copies only."""
import ast,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
def save(name,x):(P/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
    deps=json.loads((P/'DEPENDENCIES.json').read_text())
    for rel,pin in deps['files'].items():
        data=(P/rel).read_bytes();assert len(data)==pin['bytes'] and sha(data)==pin['sha256'],rel
    Q=P/'inputs'/'plan'
    assert sha((Q/'SHA256SUMS.json').read_bytes())==deps['plan_seal_sha256']=='df20578d1daa74a886ea00d87603d3d06d2ff641aa3bfe9ab13a3f5ded0d25c0'
    original=json.loads((Q/'SHA256SUMS.json').read_text())
    for rel,pin in original.items():assert sha((Q/rel).read_bytes())==pin['sha256'],rel
    plan=json.loads((Q/'call-plan.json').read_text())
    assert plan['logical_calls']==20 and len(plan['calls'])==20
    manifest=json.loads((Q/'request-manifest.json').read_text())
    requests={};sizes=[]
    for r in manifest:
        data=(Q/r['path']).read_bytes();q=json.loads(data)
        assert sha(data)==r['file_sha256'] and sha(canon(q))==r['request_canonical_sha256']
        assert sha(canon(q['args'][1]))==r['messages_canonical_sha256']
        assert q['args'][0]=='openai/gpt-oss-120b' and len(q['args'])==2
        assert q['kwargs']=={'max_completion_tokens':2048,'reasoning':{'effort':'medium'},'temperature':0}
        assert len(canon(q))<65536 and len(json.dumps(q).encode())<65536
        requests[r['fixture']+'-'+r['arm']]=q
        sizes.append({'fixture':r['fixture'],'arm':r['arm'],'canonical_argument_bytes':len(canon(q)),'default_json_argument_estimate_bytes':len(json.dumps(q).encode())})
    steps=[]
    for i,step in enumerate(plan['calls'],1):
        assert step['ordinal']==i
        q=requests[step['fixture']+'-'+step['arm']]
        assert sha(canon(q))==step['request_canonical_sha256']
        steps.append({k:step[k] for k in ['ordinal','repeat','fixture','arm','request_canonical_sha256']})
    assert len(requests)==10
    bundle={'plan_sha256':sha((Q/'call-plan.json').read_bytes()),'requests':requests,'steps':steps}
    runtime=(P/'runner.py').read_text()
    tree=ast.parse(runtime)
    parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    attrs=[n for n in ast.walk(tree) if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='bitgn']
    assert sorted(n.attr for n in attrs)==['answer','llm']
    assert all(isinstance(parents[n],ast.Call) and parents[n].func is n for n in attrs)
    readable='import json\nFROZEN=json.loads('+repr(json.dumps(bundle,ensure_ascii=True,separators=(',',':')))+')\n'+runtime
    readable=readable.encode('ascii','backslashreplace').decode()
    pack=runpy.run_path(str(P/'inputs'/'lzpack.py'))
    packed=pack['pack'](readable)
    assert len(packed.encode())<=65536
    (P/'readable.py').write_text(readable);(P/'agent.py').write_text(packed)
    save('frozen.json',bundle)
    save('manifest.json',{'status':'OFFLINE PREPARED; NOT SUBMITTED','logical_calls':20,'fixtures':5,'repeats':2,
        'plan_sha256':bundle['plan_sha256'],'original_plan_seal_sha256':deps['plan_seal_sha256'],
        'runner_sha256':sha(runtime.encode()),'readable_bytes':len(readable.encode()),'readable_sha256':sha(readable.encode()),
        'packed_bytes':len(packed.encode()),'packed_sha256':sha(packed.encode()),'frozen_sha256':sha((P/'frozen.json').read_bytes()),
        'dependencies_sha256':sha((P/'DEPENDENCIES.json').read_bytes()),'sdk':'0.3.7 archived guide; routing must be verified on any future live trace',
        'model':'openai/gpt-oss-120b','provider':'SDK-pinned DeepInfra BF16; no provider override','settings':requests['A023-P']['kwargs'],
        'request_sizes':sizes,'private_wire_encoding_verified':False,'guest_retries':0,'inference_exception_policy':'bounded error/stop log then rethrow; remaining cells not dispatched',
        'raw_result_policy':'immutable response/error events; stdout previews are not linkage keys',
        'carrier_answer':'only after all20 calls return; OUTCOME_NONE_UNSUPPORTED; grade irrelevant',
        'ecom_actions':False,'model_output_execution':False,'real_model_calls_during_preparation':0})
    print(json.dumps({'packed_bytes':len(packed.encode()),'packed_sha256':sha(packed.encode()),'planned_calls':20}))
if __name__=='__main__':main()
