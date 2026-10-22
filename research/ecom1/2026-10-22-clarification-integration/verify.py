import contextlib,hashlib,io,json,sys
from pathlib import Path
import pydantic_monty as m
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-record-integration'
HEADER=HERE.parent/'2026-10-22-receipt-header-review'
REVIEW=HERE.parent/'2026-10-22-clarification-review'
sys.path.insert(0,str(BASE))
import test_combined as rc,replay,run_suite
packed=(HERE/'agent.py').read_text();readable=(HERE/'readable.py').read_text()
code=rc.decoded_source(packed);prefix=code[:code.index('\nmessages = [')]
def namespace(source):
    src=rc.decoded_source(source);ns={};exec(src[:src.index('\nmessages = [')],ns)
    ns.update(DM=ns['rcp_items'],FP=ns['receipt_availability'],FU=ns['receipt_price_drift'])
    return ns
rc.namespace=namespace
ns=namespace(packed);fn=ns['clarification_skus']
products=[{'sku':'SKU-A','_path':'/catalog/a.json'},{'sku':'SKU-B','_path':'/catalog/b.json'}]
ns['WORLD']['products']=products
refs=[p['_path'] for p in products]
cases=[('Which one?','OUTCOME_NONE_CLARIFICATION',refs,'Which one? Candidates: SKU-A, SKU-B'),
 ('Choose SKU-A or SKU-B.','OUTCOME_NONE_CLARIFICATION',refs,'Choose SKU-A or SKU-B.'),
 ('Choose sku-a or sku-b.','OUTCOME_NONE_CLARIFICATION',refs,'Choose sku-a or sku-b.'),
 ('Choose SKU-ABC.','OUTCOME_NONE_CLARIFICATION',refs,'Choose SKU-ABC. Candidates: SKU-A, SKU-B'),
 ('Choose SKU-A.','OUTCOME_NONE_CLARIFICATION',refs,'Choose SKU-A. Candidates: SKU-B'),
 ('Quantity?','OUTCOME_NONE_CLARIFICATION',refs[:1],'Quantity?'),
 ('Which?','OUTCOME_NONE_CLARIFICATION',['/tmp/PT-FAKE.json'],'Which?'),
 ('Which?','OUTCOME_NONE_CLARIFICATION',[],'Which?'),
 ('Which?','OUTCOME_NONE_CLARIFICATION',[refs[0],refs[0]],'Which?'),
 ('Which?','OUTCOME_NONE_CLARIFICATION',[r+'#properties' for r in refs],'Which? Candidates: SKU-A, SKU-B')]
for outcome in ['OUTCOME_OK','OUTCOME_DENIED_SECURITY','OUTCOME_NONE_UNSUPPORTED','OUTCOME_ERR_INTERNAL']:
    cases.append(('Unchanged',outcome,refs,'Unchanged'))
for message,outcome,paths,expected in cases:assert fn(message,outcome,paths)==expected
native_code=prefix+'\nWORLD["products"]='+repr(products)+'\nCASES='+repr(cases)+'\nprint("RESULT "+json.dumps([clarification_skus(a,b,c) for a,b,c,d in CASES]))'
out=[]
with m.Monty() as pool:
    with pool.checkout() as session:session.feed_run(native_code,print_callback=lambda *a:out.append(a))
text=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in out)
assert json.loads(next(line[7:] for line in text.splitlines() if line.startswith('RESULT ')))==[e for a,b,c,e in cases]

worlds=json.loads((REVIEW/'world-fixtures.json').read_text());direct=[]
class AnswerSDK:
    def answer(self,message,outcome=None,refs=None):return dict(message=message,outcome=outcome,refs=refs)
    def call(self,*args):raise AssertionError('no additional runtime call expected')
for trial,world in worlds.items():
    scope=namespace(packed);scope['WORLD'].update(built=True,products=world['products'])
    scope['LEDGER']['read']=[p['_path'] for p in world['products']]
    scope['POLICY_REFS']=['/docs/security.md','/docs/catalogue-lookup.md']
    scope['INSTRUCTION']=world['instruction'];scope['bitgn']=AnswerSDK()
    a=world['answer'];action=dict(tool='report_completion',message=a['message'],outcome=a['outcome'],grounding_refs=a['refs'])
    with contextlib.redirect_stdout(io.StringIO()):answer=scope['dispatch'](action)
    assert answer['outcome']==a['outcome'] and answer['refs']==a['refs']
    if trial=='t021':
        assert all(s in answer['message'] for s in ['PT-IMP-DEW-DCF887-2AH','PT-IMP-DEW-DCF887-5AH'])
    else:assert answer==a # Known wrong-answer case is intentionally not rewritten by the display repair.
    direct.append(dict(trial=trial,before=a,after=answer))

replays=[]
for path in sorted((BASE/'worlds').glob('*.json')):
    parent=run_suite.run_world(replay,str(HEADER/'agent.py'),str(path))
    candidate=run_suite.run_world(replay,str(HERE/'agent.py'),str(path))
    assert parent['error']==candidate['error']
    for key in ['calls','llm_calls','rpc_misses','llm_requests_match','llm_requests_checked','first_llm_difference']:
        assert parent[key]==candidate[key],(path.name,key)
    a=parent['answer'];b=candidate['answer']
    assert a['outcome']==b['outcome'] and a['refs']==b['refs']
    changed=a['message']!=b['message']
    if changed:assert a['outcome']=='OUTCOME_NONE_CLARIFICATION' and b['message'].startswith(a['message']+' Candidates: ')
    replays.append(dict(world=path.name,task=parent['task'],message_changed=changed,before=a,after=b,
                        error=candidate['error'],rpc_misses=candidate['rpc_misses'],llm_requests_match=candidate['llm_requests_match']))
archive=json.loads((BASE/'archived_receipt.json').read_text())['response']['content']
parser=rc.parser_checks((BASE/'receipt_parent.py').read_text(),packed,archive)
handlers=[rc.handler_checks((BASE/'parent_agent.py').read_text(),packed,g) for g in ['handlers-0','handlers-1','handlers-2','handlers-3','drift']]
assert namespace(packed)['DM']((HEADER/'archived-ocr.txt').read_text())==namespace((HEADER/'agent.py').read_text())['DM']((HEADER/'archived-ocr.txt').read_text())
result=dict(candidate_sha256=hashlib.sha256(packed.encode()).hexdigest(),native_display_cases=len(cases),
 exact_record_action_replays=direct,archived_replays=replays,parser=parser,handlers=handlers,
 scope='Display-only repair preserves outcome,refs and runtime calls. Archived replays remain advisory; no changed model replies or hidden grade recomputation. t041 semantic failure remains open.')
(HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS:',len(cases),'native display controls; two exact-world completion actions;27 advisory replays;408parser/20handler controls; damaged receipt preserved')
print('Changed archived messages:',[r['task'] for r in replays if r['message_changed']])
