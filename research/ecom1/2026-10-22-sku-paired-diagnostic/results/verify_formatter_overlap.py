"""Replay all 16 frozen actions through the actual d4955-lineage formatter.

No model calls, Brain access or ECOM RPCs. This does not run the whole agent or grader.
"""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
records=json.loads((HERE/'records.json').read_text())
verified=json.loads((HERE/'verified-calls.json').read_text())
scorer=json.loads((HERE/'frozen-scorer-report.json').read_text())
fixtures=json.loads((HERE.parent/'fixtures.json').read_text())
worlds=json.loads((ROOT/'2026-10-22-clarification-review/world-fixtures.json').read_text())
source_path=ROOT/'2026-10-22-clarification-integration/readable.py'
source=source_path.read_text()
# Same actual definitions and dispatch used in the original integration verifier.
prefix=source[:source.index('\nmessages = [')]
class AnswerOnly:
    def __init__(self):self.calls=0
    def answer(self,message,outcome=None,refs=None):
        self.calls+=1
        return dict(message=message,outcome=outcome,refs=refs)
    def call(self,*args,**kwargs):
        raise AssertionError('Formatter replay must not issue an ECOM RPC')
rows=[]
assert len(records)==len(verified)==len(scorer['rows'])==16
for i,record in enumerate(records):
    step=record['step'];assert step==fixtures['plan'][i]
    choice=record['response']['choices'][0];assert choice['finish_reason']=='stop'
    raw=choice['message']['content'].strip()
    action=json.loads(raw)  # All captured responses are complete bare JSON actions.
    assert action==scorer['rows'][i]['action'] and step==scorer['rows'][i]['step']
    assert verified[i]['call']==i+1 and verified[i]['request_verified'] and verified[i]['attempts']==1
    ns={};exec(prefix,ns)
    tid='t041' if step['case']=='archived_standard_head' else 't021'
    pool=copy.deepcopy(worlds[tid]['products'])
    ns['WORLD'].update(built=True,products=pool)
    ns['LEDGER']['read']=[p['_path'] for p in pool]
    ns['POLICY_REFS']=['/docs/security.md','/docs/catalogue-lookup.md']
    ns['INSTRUCTION']=fixtures['fixtures'][step['case_index']]['arms']['parent']['messages'][7]['content']
    host=AnswerOnly();ns['bitgn']=host
    with contextlib.redirect_stdout(io.StringIO()):answer=ns['dispatch'](copy.deepcopy(action))
    assert host.calls==1 and answer['outcome']==action['outcome']
    if i+1 in [1,10]:
        assert all(sku in answer['message'] for sku in ['PT-IMP-DEW-DCF887-2AH','PT-IMP-DEW-DCF887-5AH'])
    rows.append(dict(call=i+1,step=step,model_action=action,formatted_answer=answer,
                     message_changed=answer['message']!=action['message']))
assert [r['call'] for r in rows if r['message_changed']]==[1,10]
report=dict(status='passed',calls_checked=16,changed_messages=[1,10],
            source=str(source_path.relative_to(ROOT)),source_sha256=hashlib.sha256(source.encode()).hexdigest(),
            runtime='CPython actual parent definitions; answer-only stub, no ECOM RPCs',
            rows=rows,limits='Action/formatter replay only. No full-agent model regeneration, grade, or claim that semantic issues are repaired.')
(HERE/'formatter-overlap-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('PASS all16 actions; actual formatter appends both already-cited kit SKUs only for parent calls1/10; no outcome changes or ECOM RPCs.')
