"""Synthetic syntax controls only: no inference, dispatch or semantic pass score."""
import json,runpy
from pathlib import Path
from strict_schema import validate
P=Path(__file__).resolve().parent
cases=[
 ('read','{"tool":"read","path":"/AGENTS.MD"}',True,True),
 ('report','{"tool":"report_completion","message":"not yet complete","outcome":"OUTCOME_NONE_CLARIFICATION"}',True,True),
 ('false_completion','{"tool":"report_completion","message":"export written","outcome":"OUTCOME_OK"}',True,True),
 ('write','{"tool":"write","path":"/exports/test.tsv","content":"invented"}',True,True),
 ('missing_path','{"tool":"read"}',False,False),('unknown','{"tool":"shell","path":"/bin/sh"}',False,False),
 ('extra_field','{"tool":"read","path":"/x","extra":1}',False,False),
 ('boolean_integer','{"tool":"tree","level":true}',False,False),
 ('nonstring_refs','{"tool":"report_completion","message":"x","outcome":"OUTCOME_OK","grounding_refs":[1]}',False,False),
 ('fence','```json\n{"tool":"read","path":"/x"}\n```',True,False),
 ('wrapper','{"function":{"tool":"read","path":"/x"}}',True,False),
 ('search_alias','{"tool":"search","pattern":"x","path":"/proc"}',True,False),
 ('search_conflict','{"tool":"search","pattern":"x","path":"/a","root":"/b"}',False,False),
 ('find_alias','{"tool":"find","name":"x","kind":"file"}',True,False),
 ('trailing_second','{"tool":"read","path":"/x"}{"tool":"delete","path":"/y"}',True,False),
 ('trailing_partial','{"tool":"read","path":"/x"}{"tool":',True,False),
 ('duplicate_key','{"tool":"read","path":"/x","path":"/y"}',True,False),
 ('null_final',None,False,False),('empty','',False,False),('prose','I will read a file.',False,False),
 ('incomplete','{"tool":"read","path":"/x"',False,False),('array','[{"tool":"read","path":"/x"}]',False,False),
 ('bad_outcome','{"tool":"report_completion","message":"x","outcome":"SUCCESS"}',False,False),
]
rows=[]
for source in ['d4702','d4955','d4353']:
 parse=runpy.run_path(str(P/'parsers'/f'{source}.py'))['parse_step']
 for name,text,expected_source,expected_strict in cases:
  out={}
  for label,fn in [('source',lambda v:parse(v or '')),('strict',validate)]:
   try:action=fn(text);out[label]={'accepted':True,'normalized_action':action}
   except Exception as e:out[label]={'accepted':False,'error_type':type(e).__name__}
  assert out['source']['accepted']==expected_source and out['strict']['accepted']==expected_strict,(source,name,out)
  rows.append({'source':source,'case':name,'input':text,**out})
# Finish reason is deliberately not a parser input: main guards before parsing.
finish_controls=[{'finish_reason':f,'source_parser_accepted':True,'main_would_reach_dispatch':f!='length'} for f in ['stop','length']]
report={'status':'PASS synthetic syntax controls only','parser_evaluations':len(rows),'strict_evaluations':len(rows),'whole_agent_executions':0,'real_inference_calls':0,'cases':rows,'phase_controls':finish_controls,'semantic_adjudication':'Manual only; false_completion and invented Write intentionally pass both syntactic checks.'}
(P/'test-results.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(rows),'source-parser controls and independent strict checks.')
