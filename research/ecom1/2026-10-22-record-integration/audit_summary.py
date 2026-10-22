import json,collections
from pathlib import Path
root=Path(__file__).parent
runs={'old':{},'new':{}}
for p in root.glob('audit-*.json'):
 obj=json.loads(p.read_text());label=obj['config']['label'][:3]
 for row in obj['rows']:runs[label][row['task_id']]=row
G={name:{t['task_id']:t for t in json.loads(root.joinpath(file).read_text())['trials']} for name,file in [('old','old-results.json'),('new','repair-results.json')]}
def extract(row,name):
 ev=row['events'];tid=row['task_id'];g=G[name][tid]
 starts=[e for e in ev if e['kind']=='rpc_response' and e['data'].get('method')=='StartTrial']
 answers=[e for e in ev if e['kind']=='rpc_request' and e['data'].get('method')=='Answer']
 finishes=[e for e in ev if e['kind']=='agent_finished']
 errors=[e for e in ev if e['kind'] in ['agent_error','llm_error','rpc_error']]
 mutations=[e for e in ev if e['kind']=='rpc_request' and e['data'].get('method') in ['Exec','Write','Delete','Rename']]
 assert len(starts)==1 and len(finishes)==1
 assert len(answers)==(0 if g['state']=='failed' else 1)
 methods=dict(collections.Counter(e['data'].get('method') for e in row['index'] if e['kind']=='rpc_request'))
 return {'instruction':starts[0]['data']['response']['instruction'],'answer':answers[0]['data']['arguments'] if answers else None,'output':finishes[0]['data'].get('output',''),'error_events':errors,'mutation_events':mutations,'grade':g['grade'],'state':g['state'],'methods':methods,'all_index_events':len(row['index']),'body_events':len(ev),'trace_ids':{'start':starts[0]['seq'],'finish':finishes[0]['seq'],'answer':answers[0]['seq'] if answers else None}}
review={}
for tid in sorted(set(runs['old'])|set(runs['new'])):
 row={label:extract(runs[label][tid],label) for label in runs if tid in runs[label]}
 if len(row)==2:row['same_instruction']=row['old']['instruction']==row['new']['instruction']
 review[tid]=row
root.joinpath('all-task-review.json').write_text(json.dumps(review,indent=2)+'\n')
print('Collected:',{k:len(v) for k,v in runs.items()},'paired:',sum('same_instruction' in r for r in review.values()))
if __name__=='__main__':
 import sys
 if len(sys.argv)>1:
  a=int(sys.argv[1]);b=int(sys.argv[2]);deep='--deep' in sys.argv
  for tid,row in review.items():
   if not a<=int(tid[1:])<=b:continue
   print('\n'+tid+' same='+str(row.get('same_instruction')))
   for name in ['old','new']:
    if name not in row:continue
    r=row[name];ans=r['answer'] or {};print(name,'score',r['grade']['score'],'state',r['state'])
    print('REQUEST:',r['instruction'])
    print('ANSWER:',ans.get('outcome'),ans.get('message'),'REFS:',ans.get('refs'))
    if deep:print('LOG:',r['output']);print('ERRORS:',r['error_events']);print('MUTATIONS:',r['mutation_events'])
    else:print('METHODS:',r['methods'],'MUTATIONS:',[(e['data']['method'],e['data'].get('arguments')) for e in r['mutation_events']])
