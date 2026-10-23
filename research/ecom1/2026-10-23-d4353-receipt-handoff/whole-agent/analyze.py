import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
rows=json.loads((P/'results.json').read_text())['results'];gates=json.loads((P/'gate-results.json').read_text())['results']
summary=[]
def get(task,case,arm):return next(r for r in rows if (r['task'],r['case'],r['arm'],r['form'],r['engine'])==(task,case,arm,'packed','native'))
for task in ['t023','t063']:
 world=json.loads((P/'upstream'/task/'world.json').read_text());upload=next(p for p in world['files'] if p.startswith('/uploads/'))
 for case in ['archived','fixed_ok','fixed_denial','fixed_clarification']:
  p,c,x,v=[get(task,case,a) for a in ['parent','combined','context_only','provenance_only']]
  assert p['calls']==c['calls']==x['calls']==v['calls']
  assert p['requests']==v['requests'] and c['requests']==x['requests']
  assert p['answers']==x['answers'] and c['answers']==v['answers']
  assert p['requests'][0]==c['requests'][0]
  pm=p['requests'][1]['args'][1];cm=c['requests'][1]['args'][1]
  assert cm[:-2]==pm
  for item,path in zip(cm[-2:],['/docs/availability-checks.md',upload]):
   result=world['files'][path];metadata={k:result[k] for k in ('path','sha256','contentType','truncated') if k in result}
   assert result['sha256']==hashlib.sha256(result['content'].encode()).hexdigest()
   assert item=={'role':'user','content':json.dumps({'tool':'read','path':path})+'\n'+result['content']+'\n[Observed Read metadata: '+json.dumps(metadata)+']'}
  for a,b in zip(p['answers'],c['answers']):assert (a['message'],a['outcome'])==(b['message'],b['outcome'])
  summary.append({'task':task,'case':case,'main_messages_parent':len(pm),'main_messages_combined':len(cm),'rpc_calls_all_arms':len(p['calls']),'parent_answer':p['answers'],'combined_answer':c['answers'],'context_only_equals_parent_answer':True,'provenance_only_equals_combined_answer':True,'transferred_contents_exact':True})
for row in gates:
 if row['arm']!='combined' or row['form']!='packed' or row['engine']!='native':continue
 task=row['task'];name=row['case'];world=json.loads((P/'upstream'/task/'world.json').read_text());upload=next(p for p in world['files'] if p.startswith('/uploads/'))
 if name in ['policy_truncated','upload_truncated']:
  target='/docs/availability-checks.md' if name=='policy_truncated' else upload
  message=next(m['content'] for m in row['requests'][1]['args'][1][-2:] if json.loads(m['content'].split('\n',1)[0])['path']==target)
  assert 'content_omitted' in message and 'source incomplete or too large' in message
  assert world['files'][target]['content'] not in message
  assert target not in row['answers'][0]['refs']
 if name=='helper_success':
  assert len(row['requests'])==1 and row['answers'][0]['outcome']=='OUTCOME_OK'
  assert '/docs/availability-checks.md' in row['answers'][0]['refs'] and upload in row['answers'][0]['refs']
assert all(not r['derivations'] for r in rows+gates)
(P/'analysis.json').write_text(json.dumps({'status':'PASS','whole_agent_executions':len(rows)+len(gates),'native_executions':(len(rows)+len(gates))//2,'no_rpc_changes_between_arms':True,'no_derived_tree_used':True,'mechanistic_ablation':summary,'scope':'Fixed outputs; no actual task score or model response improvement established.'},indent=2)+'\n');print('PASS',len(rows)+len(gates))
