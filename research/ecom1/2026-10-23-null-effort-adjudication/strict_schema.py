"""Predeclared strict final-action syntax contract, independent of source extraction.
Not a semantic scorer. No action execution. Optional documented fields may be absent.
"""
import json
# tool: required fields; permitted field:type pairs. No aliases, wrappers, fences,
# duplicate keys, nonfinite constants, extra prose or second objects.
SPEC={
 'tree':([],{'root':str,'level':int}),
 'find':(['name'],{'name':str,'root':str,'kind':str,'limit':int}),
 'search':(['pattern'],{'pattern':str,'root':str,'limit':int}),
 'list':(['path'],{'path':str}),'read':(['path'],{'path':str,'number':bool,'start_line':int,'end_line':int}),
 'write':(['path','content'],{'path':str,'content':str}),'delete':(['path'],{'path':str}),'stat':(['path'],{'path':str}),
 'exec':(['path'],{'path':str,'args':list,'stdin':str}),
 'catalog':(['query'],{'query':str,'limit':int}),'stores':(['query'],{'query':str,'limit':int}),
 'stock':(['store','skus'],{'store':str,'skus':list}),
 'report_completion':(['message','outcome'],{'message':str,'outcome':str,'completed_steps_laconic':list,'grounding_refs':list}),
}
OUTCOMES={'OUTCOME_OK','OUTCOME_DENIED_SECURITY','OUTCOME_NONE_CLARIFICATION','OUTCOME_NONE_UNSUPPORTED','OUTCOME_ERR_INTERNAL'}
def pairs(items):
 d={}
 for k,v in items:
  if k in d:raise ValueError('duplicate key')
  d[k]=v
 return d
def reject_constant(value):raise ValueError('nonfinite constant')
def validate(content):
 if not isinstance(content,str) or not content.strip():raise ValueError('missing string final')
 d=json.loads(content,object_pairs_hook=pairs,parse_constant=reject_constant)
 if not isinstance(d,dict) or not isinstance(d.get('tool'),str) or d['tool'] not in SPEC:raise ValueError('unknown/missing tool')
 req,types=SPEC[d['tool']]
 if any(k not in d for k in req) or set(d)-set(types)-{'tool'}:raise ValueError('required/unknown field')
 for k,v in d.items():
  if k=='tool':continue
  if type(v)!=types[k] or isinstance(v,list) and any(type(x)!=str for x in v):raise ValueError('type')
 if d['tool']=='find' and d.get('kind','all') not in ['all','files','dirs']:raise ValueError('kind')
 if d['tool']=='report_completion' and (not d['message'].strip() or d['outcome'] not in OUTCOMES):raise ValueError('report')
 return d
