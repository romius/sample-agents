"""Build all100 descriptive ledger from exact official grades and actual instructions."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
own=load(P/'result.json')['result'];record=load(P/'comparison/d4353-official-result.json')['result']
instr={x['task_id']:json.loads(x['event']['text'])['data']['response']['instruction'] for x in load(P/'instructions-all100.json')}
ri={x['task_id']:x['instruction'] for x in load(P/'comparison/d4353-instructions.json')}
rt={x['task_id']:x for x in record['trials']}
success={x['task_id']:x for x in load(P/'success-evidence/success-review.json')}
loss_reviews={x['task']:x for x in load(P/'loss-review.json')}
scope={x['task']:x for x in load(P/'reassembly-verification.json')}
assert len(success)==83
# Families manually assigned after reading every actual instruction, not inferred from score.
groups={
 'SKU identification':[1,21,41,61], 'stock with excluded SKU':[2,22,42,62],
 'receipt basket availability':[3,23,43,63], 'dispatch wave':[4,14,24,44,64],
 'inventory count':[5,25,45,65], 'product existence':[6,26,46,66],
 'catalogue count under price':[7,27,47,67], 'company history':[8,28,48,68],
 'checkout':[9,10,11,12,13,29,30,31,32,33,49,50,51,52,53,69,70,71,72,73],
 'archived fraud sum':[15,35,55,75], 'OCR crosslist export':[16,36,56,76],
 'refund workflow':[17,18,37,38,57,58,77,78], 'staff identity/privacy':[19,81,82,88,92],
 'date calculation':[20], 'cat executable marker':[34], 'scoped cleanup':[39,60],
 'Salesforce case':[40], 'basket store field':[54], 'staff count':[59,89],
 'open branches in city':[74], 'add basket item':[79], 'receipt price comparison':[80],
 '3DS recovery':[83,84,85,86,87], 'product property lookup':[90,94],
 'inventory CSV':[91], 'store property lookup':[93], 'discount policy':[95,96,97,98,99,100]}
family={f't{n:03}':k for k,v in groups.items() for n in v};assert len(family)==100
rows=[]
for t in own['trials']:
 k=t['task_id'];r=rt[k];s=t['grade']['score']
 trace=P/f'{k}-events.ndjson'
 raw_lines=trace.read_bytes().splitlines(keepends=True) if trace.exists() else []
 events=[json.loads(line) for line in raw_lines]
 answers=[e for e in events if e['kind']=='rpc_request' and e['data']['method']=='Answer']
 assert len(answers)<=1
 answer=answers[0] if answers else None
 if s==1:
  reviewed=success[k]
  assert reviewed['instruction']==instr[k] and reviewed['official_grade']==t['grade'] and reviewed['trial_id']==t['trial_id']
  answer=load(P/'success-evidence'/reviewed['answer_event']['path'])
  finished=load(P/'success-evidence'/reviewed['agent_finished_event']['path'])
  evidence_level=reviewed['evidence_level'];observation=reviewed['observation'];diagnosis=reviewed['diagnosis'];uncertainty=reviewed['uncertainty'];flags=reviewed['flags']
  answer_ref=dict(reviewed['answer_event']);answer_ref['path']='success-evidence/'+answer_ref['path']
  finished_ref=dict(reviewed['agent_finished_event']);finished_ref['path']='success-evidence/'+finished_ref['path']
 else:
  reviewed=loss_reviews[k];finished=next(e for e in events if e['kind']=='agent_finished')
  evidence_level='Complete immutable trial CAS, all actions/model responses and stdout' if scope[k]['complete_scope'] else 'Complete trial index; selected immutable events including all RPC requests/model responses, exact Answer and stdout'
  observation=reviewed['finding'];diagnosis=reviewed['category'];uncertainty=reviewed['uncertainty'];flags=['official_grade_loss']
  if s>0:flags.append('dispatch_partial')
  raw_by_seq={json.loads(line)['seq']:line for line in raw_lines}
  answer_ref={'path':trace.name,'seq':answer['seq'],'sha256':hashlib.sha256(raw_by_seq[answer['seq']]).hexdigest()}
  finished_ref={'path':trace.name,'seq':finished['seq'],'sha256':hashlib.sha256(raw_by_seq[finished['seq']]).hexdigest()}
 assert answer['data']['trial_id']==finished['data']['trial_id']==t['trial_id']
 rows.append({
  'task_id':k,'family':family[k],'instruction':instr[k],'instruction_sha256':sha(instr[k]),
  'official_score':s,'official_grade':t['grade'],'state':t['state'],'usage':t['usage'],
  'record_same_ordinal_score':r['grade']['score'],'record_same_ordinal_instruction':ri[k],
  'identical_instruction_bytes':instr[k]==ri[k],
  'answer_event_seq':answer['seq'] if answer else None,
  'answer':answer['data']['arguments'],'outcome':answer['data']['arguments']['outcome'],
  'answer_event':answer_ref,'agent_finished_event':finished_ref,'agent_finished_stdout':finished['data']['output'],
  'answer_evidence_level':evidence_level,'observation':observation,'diagnosis':diagnosis,'uncertainty':uncertainty,'flags':flags,
  'review_basis':'Actual instruction, official grade, exact final Answer and full agent_finished stdout reviewed for all100. Supporting primary evidence is scoped per row. Full credit is not independent action-by-action correctness certification.',
  'comparison_limit':'Same ordinal and even identical instruction wording do not prove identical world/input or causal source effect.'})
assert len(rows)==100 and sum(x['official_score']==1 for x in rows)==83
(P/'all100-review.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
text=['# All100 descriptive review','','Every actual StartTrial instruction, official grade, final Answer RPC and complete agent_finished stdout was reviewed. The 83 full-credit cases remain official grader successes, not independent action-by-action certification. All 17 losses have a separate primary-evidence review. Exact instruction hashes, raw grades, answers, logs, evidence levels, observations, diagnoses and uncertainty are recorded for every row in all100-review.json.','','Same-ordinal record scores are descriptive only: 95 instructions differ, and identical wording does not prove equal world state.','','| Task | Actual family | Score | Record ordinal score | Same instruction bytes | Calls | Actual outcome |','|---|---|---:|---:|---|---:|---|']
for x in rows:text.append(f"| {x['task_id']} | {x['family']} | {x['official_score']:.8g} | {x['record_same_ordinal_score']:.8g} | {x['identical_instruction_bytes']} | {x['usage']['model_calls']} | {x['outcome'] or 'Official state/grade only'} |")
text+=['','## Per-task review','']
for x in rows:text+=['### '+x['task_id']+' — '+x['family'],'',x['instruction'],'','Observation: '+x['observation'],'','Evidence: '+x['answer_evidence_level'],'','Uncertainty: '+x['uncertainty'],'']
(P/'all100-review.md').write_text('\n'.join(text))
stats={k:{'tasks':[x['task_id'] for x in rows if x['family']==k],'score_sum':sum(x['official_score'] for x in rows if x['family']==k),'full_credit':sum(x['official_score']==1 for x in rows if x['family']==k)} for k in groups}
(P/'family-summary.json').write_text(json.dumps(stats,indent=2)+'\n')
print('PASS: all100 actual instructions and official grades retained;83 full,12zero,5partial.')
