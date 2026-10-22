"""Offline audit of frozen result exports; no network/model calls."""
import ast
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys
import pydantic_monty as monty

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE_SHA = 'ced402b531e213bef9959b6956006a8d967c0998eb7e31f0e34901f26b0eb3c1'
GUARDS = ROOT / '2026-10-22-inventory-integration/readable.py'
GUARD_SHA = 'aef93a8c2b25feeb097e70a063d5ffff6c15f52622a3e4e058859901b0a921e1'
CURRENT = ROOT / '2026-10-22-sku-history-pressure-review/readable.py'
CURRENT_SHA = '0f7925c41f2783b6617ec7777757bec6fee5971f483159e26b32fae8082f7c41'
LIMITS = dict(max_feed_duration_secs=10,max_turn_duration_secs=10,max_suspensions=1000)
def load(name): return json.loads((HERE / name).read_text())
def sha(b): return hashlib.sha256(b).hexdigest()
def save(name,obj): (HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def instructions(pattern):
    rows = [r for p in sorted(HERE.glob(pattern)) for r in json.loads(p.read_text())]
    assert len(rows)==100 and len({r['task_id'] for r in rows})==100
    return {r['task_id']:r['event']['data']['response']['instruction'] for r in rows}

new = load('new-result.json'); old = load('old-result.json')
assert sha((HERE/'d2499r1.py').read_bytes())==SOURCE_SHA
for run in [old,new]:
    assert run['job']['source_blob']==run['result']['source']['sha256']==SOURCE_SHA
    assert run['job']['revision']==run['result']['source']['revision']==1
    assert len(run['result']['trials'])==100
    assert len({r['task_id'] for r in run['result']['trials']})==100
    assert all(r['grade']['available'] and r['grade']['error'] is None for r in run['result']['trials'])
    assert run['result']['run_score_available']
N={t['task_id']:t for t in new['result']['trials']};O={t['task_id']:t for t in old['result']['trials']}
NI=instructions('new-instructions-*.json');OI=instructions('old-instructions-*.json')
rows=[]
for task in sorted(N):
    rows.append(dict(task_id=task,old_score=O[task]['grade']['score'],new_score=N[task]['grade']['score'],
        old_state=O[task]['state'],new_state=N[task]['state'],new_grade_detail=N[task]['grade']['detail'],
        old_instruction=OI[task],new_instruction=NI[task],
        old_instruction_sha256=sha(OI[task].encode()),new_instruction_sha256=sha(NI[task].encode()),
        exact_instruction_equal=OI[task]==NI[task],
        old_trace=O[task]['trace'],new_trace=N[task]['trace']))
save('all100-review.json',rows)
(HERE/'all100-review.tsv').write_text('task\told_score\tnew_score\told_state\tnew_state\tinstruction_equal\tnew_detail\n'+
    ''.join('\t'.join(str(r[k]).replace('\t',' ').replace('\n',' ') for k in
    ['task_id','old_score','new_score','old_state','new_state','exact_instruction_equal','new_grade_detail'])+'\n' for r in rows))

categories={
 'inference_timeout':['t003','t045','t056','t059'],
 'catalogue_reference_mismatch':['t022','t027','t042','t062','t065'],
 'ambiguous_SKU_false_OK':['t001','t061'],
 'crosslist_outcome_or_export':['t016','t036','t076'],
 'receipt_denied_security':['t023'],
 'file_change_mismatch':['t038','t039','t060'],
 'count_answer':['t047'], 'inventory_export':['t091'], 'security_false_OK':['t093']}
assert sorted(t for ts in categories.values() for t in ts)==sorted(t for t in N if N[t]['grade']['score']==0)

# Evaluate exact observed exceptions with unchanged, pinned existing guard code.
source=GUARDS.read_text();assert sha(source.encode())==GUARD_SHA
defs={n.name:ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
assert sha(CURRENT.read_bytes())==CURRENT_SHA
current_defs={n.name:n for n in ast.parse(CURRENT.read_text()).body if isinstance(n,ast.FunctionDef)}
for name in ['MSR','recoverable_lookup_error']:
    assert ast.dump(ast.parse(defs[name]).body[0])==ast.dump(current_defs[name])
guard_code='import re,json\n'+defs['MSR']+'\n'+defs['recoverable_lookup_error']+'\n'
ns={};exec(guard_code,ns)
class Host:
    def __init__(self,message,permanent): self.message=message;self.permanent=permanent;self.calls=[]
    def llm(self,*a,**k):
        self.calls.append(copy.deepcopy([a,k]))
        if self.permanent or len(self.calls)<3: raise RuntimeError(self.message)
        return {'ok':True}
guard_rows=[]
for task in categories['inference_timeout']:
    failure=load('new-failure-'+task+'.json')
    errors=[e for e in failure['events'] if e['kind']=='llm_error']
    assert len(errors)==1 and errors[0]['data']['outcome_unconfirmed']
    assert not [e for e in failure['events'] if e['kind']=='rpc_error']
    message=N[task]['error'].split('\n')[-1].removeprefix('RuntimeError: ')
    assert message=='Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out'
    for permanent in [False,True]:
        host=Host(message,permanent);ns['bitgn']=host
        raised=False
        try: result=ns['MSR']('openai/gpt-oss-120b',[{'role':'user','content':'fixed request'}],max_completion_tokens=2048,reasoning={'effort':'medium'},temperature=0)
        except RuntimeError: raised=True
        assert raised==permanent and len(host.calls)==3 and host.calls[0]==host.calls[1]==host.calls[2]
        guard_rows.append(dict(task=task,permanent=permanent,attempts=3,identical_requests=True))
for message in ['HTTP 429 timeout','HTTP 400 connection','database is locked']:
    host=Host(message,True);ns['bitgn']=host
    try: ns['MSR']('m',[])
    except RuntimeError: pass
    else: raise AssertionError('must propagate')
    assert len(host.calls)==1
exec_events=load('old-failure-t079.json')
action={'tool':'exec',**exec_events[0]['data']['arguments']};exec_error=exec_events[1]['data']['error']
recovery=ns['recoverable_lookup_error'](action,RuntimeError(exec_error))
assert recovery['unavailable_tool']=='/bin/ls'
for error in ['BitGN HTTP 404: malformed','BitGN HTTP 404: {"code":"not_found","message":"path not found"}','BitGN HTTP 500: unavailable']:
    assert ns['recoverable_lookup_error'](action,RuntimeError(error)) is None
native_code=guard_code+'''
class Fake:
 def __init__(self): self.calls=0
 def llm(self,*a,**k):
  self.calls+=1
  if self.calls<3: raise RuntimeError(message)
  return {'ok':True}
bitgn=Fake()
assert MSR('model',[])=={'ok':True} and bitgn.calls==3
assert recoverable_lookup_error(action,RuntimeError(exec_error))['unavailable_tool']=='/bin/ls'
'''
with monty.Monty() as engine:
    with engine.checkout(limits=LIMITS) as session:
        session.feed_run(native_code,inputs=dict(message=N['t003']['error'].split('\n')[-1].removeprefix('RuntimeError: '),action=action,exec_error=exec_error))
save('guard-verification.json',dict(status='passed',source_sha256=GUARD_SHA,guards=['MSR','recoverable_lookup_error'],
    current_readable_sha256=CURRENT_SHA,current_guard_AST_equal=True,
    cases=guard_rows,native_limits=LIMITS,native_pass=True,old_Exec404_recovery=recovery,
    limitation='Simulated inference recovery only. Three agent-level attempts are not a guarantee of three provider attempts under SDK host retries. No live recovery, later-task completion or score effect established.'))

old_score=Decimal(str(old['result']['run_score']));new_score=Decimal(str(new['result']['run_score']))
summary=dict(source_sha256=SOURCE_SHA,python=sys.version,pydantic_monty='1.2.0',old_job=old['job'],new_job=new['job'],
    old_official_score=str(old_score),new_official_score=str(new_score),delta_points=str((new_score-old_score)*100),
    official_record='0.9012601',promotion=False,
    old_trial_grade_sum=str(sum(Decimal(str(t['grade']['score'])) for t in O.values())),
    new_trial_grade_sum=str(sum(Decimal(str(t['grade']['score'])) for t in N.values())),
    note='Official run scores are authoritative; sums of individually rounded trial grades differ slightly.',
    new_full_credit=sum(t['grade']['score']==1 for t in N.values()),new_zeros=21,new_partials=5,
    zero_categories=categories,same_instruction_tasks=[r['task_id'] for r in rows if r['exact_instruction_equal']],
    changed_instructions=sum(not r['exact_instruction_equal'] for r in rows),
    instruction_pairing_limit='Six exact instruction matches all score1 in both; world files, policies, identities and provider outputs not proved identical. No fully paired causal comparison.',
    failures=[dict(task_id=t,trace=N[t]['trace'],error=N[t]['error']) for t in categories['inference_timeout']],
    old_reported_cost=old['result']['reported_cost_usd'],new_reported_cost=new['result']['reported_cost_usd'],
    old_unknown_cost_calls=old['result']['unknown_cost_calls'],new_unknown_cost_calls=new['result']['unknown_cost_calls'],
    limitations='Same source bytes, changed provider Cerebras FP16→DeepInfra BF16 and SDK0.3.6→0.3.7, 94 changed instructions, time/load and generated worlds. No code fix or isolated provider causal effect. All100 result rows reviewed; complete traces not exhaustively read. Four failure selected trace events and all100 StartTrial instructions inspected.')
save('summary.json',summary)
deps={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted((ROOT/'2026-10-22-record-integration').glob('audit-old*-chunk*.json'))}
deps[str(GUARDS.relative_to(ROOT))]=GUARD_SHA
deps[str(CURRENT.relative_to(ROOT))]=CURRENT_SHA
save('DEPENDENCIES.json',deps)
manifest={p.name:sha(p.read_bytes()) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='SHA256SUMS.json'}
save('SHA256SUMS.json',manifest)
print(json.dumps({k:summary[k] for k in ['old_official_score','new_official_score','delta_points','new_full_credit','new_zeros','new_partials','same_instruction_tasks','changed_instructions']}))
print('PASS all100 result rows and instruction pairs; exact guard checks; native Monty; no live/model calls')
