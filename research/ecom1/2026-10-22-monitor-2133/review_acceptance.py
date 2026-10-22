"""Check the frozen community scorer's metric scope; no live outputs or calls."""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('community_acceptance',HERE/'upstream/acceptance.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
frozen=json.loads((HERE.parent/'2026-10-22-sku-paired-diagnostic/fixtures.json').read_text())
fixture=next(f for f in frozen['fixtures'] if f['case']=='archived_standard_head')
def record(action):return {'response':{'choices':[{'message':{'content':json.dumps(action)},'finish_reason':'stop'}]}}
examples=[
 ('unrelated_clarification',record({'tool':'report_completion','message':'Which delivery date would you like?','outcome':'OUTCOME_NONE_CLARIFICATION','grounding_refs':[]})),
 ('missing_read_path',record({'tool':'read'})),
 ('unrelated_lookup',record({'tool':'read','path':'/docs/refunds.md'})),
 ('empty_choices',{'response':{'choices':[]}}),
]
rows=[]
for name,value in examples:
 try:result=m.judge(value,fixture)
 except Exception as e:result={'raised':type(e).__name__,'detail':str(e)}
 rows.append({'name':name,'record':value,'scorer':result})
assert rows[0]['scorer']['correct_final'] is True
assert rows[1]['scorer']['status']=='deferred_lookup' and rows[2]['scorer']['status']=='deferred_lookup'
assert rows[3]['scorer']['raised']=='IndexError'
(HERE/'acceptance-scope-checks.json').write_text(json.dumps(dict(rows=rows,
 interpretation='PLAN d5832 explicitly declares outcome-only standard-head assessment. First case confirms that boundary, not a contradiction of its stated metric. Do not call that semantic correctness. Missing path is invalid schema; irrelevant lookup is not necessarily progress; empty choices needs malformed/error handling. Keep frozen counts and separately review every raw action against original preregistration. No live outputs inspected.'),indent=2)+'\n')
print('Confirmed: standard-head metric is outcome-only; deferred label does not validate arguments/relevance; empty choices raises IndexError. No live outcomes or source changes.')
