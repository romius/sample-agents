import json,sys,re
from pathlib import Path
exec(Path('audit_summary.py').read_text().split("if __name__=='__main__':")[0])
a,b=map(int,sys.argv[1:3])
for tid,row in review.items():
 if not a<=int(tid[1:])<=b:continue
 print('\n'+tid+' same_request='+str(row.get('same_instruction')))
 for label in ['old','new']:
  if label not in row:continue
  r=row[label];ans=r['answer'] or {};msg=ans.get('message','<no answer>')
  if msg.startswith('{"assignments"'):
   z=json.loads(msg)['assignments'];msg='DISPATCH '+str(len(z))+' assignments; priorities='+str([x['priority'] for x in z])
  print(label,'GRADE',r['grade']['score'],'STATE',r['state'],'REQUEST',r['instruction'])
  print('ANSWER',ans.get('outcome'),msg,'REF_COUNT',len(ans.get('refs',[])))
  if r['grade']['score']<1:print('GRADE_DETAIL',r['grade']['detail'])
  lines=r['output'].splitlines()
  logs=[l for l in lines if not l.startswith(("{'job':",'Final answer','Routed policy docs','Step '))]
  steps=[]
  for l in lines:
   if l.startswith('Step '):
    try:z=json.loads(l[l.index('{'):]);steps.append({k:v for k,v in z.items() if k not in ['grounding_refs','completed_steps_laconic','message']})
    except ValueError:steps.append(l)
  print('LOG',logs,'STEPS',steps)
  print('MUTATIONS',[(e['data']['method'],e['data'].get('arguments')) for e in r['mutation_events']])
  if r['error_events']:print('ERRORS',r['error_events'])
