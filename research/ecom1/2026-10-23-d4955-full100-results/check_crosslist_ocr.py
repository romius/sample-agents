"""Actual captured uploads through exact parsers only; no task/model calls."""
import ast,hashlib,json,re
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
sources={'d4353':P/'sources/2026-10-22-record-integration/parent_readable.py','d4955':P/'sources/2026-10-22-clarification-integration/readable.py','published_d6729_hash_scanline':P/'comparison/d4353-ocr-readable.py'}
cases=[(t,(P/(t+'-uploaded-ocr.txt')).read_text()) for t in ('t056','t076')]
runner='''
out=[]
for task,text in CASES:
 try:out.append({'task':task,'parsed':crosslist_parse_ocr(text)})
 except ValueError as exc:out.append({'task':task,'error':str(exc)})
'''
reports={}
for name,path in sources.items():
 source=path.read_text();defs='\n\n'.join(ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in {'crosslist_text','crosslist_uint','crosslist_parse_ocr'})
 ns={'re':re,'CASES':cases};exec(defs+'\n'+runner,ns);outputs=[]
 code='import re\nimport json\n'+defs+'\nCASES='+repr(cases)+'\n'+runner+'\nprint("RESULT "+json.dumps(out))'
 with m.Monty() as pool:
  with pool.checkout() as session:session.feed_run(code,print_callback=lambda *a:outputs.append(str(a[-1])))
 native=json.loads(next(line[7:] for line in ''.join(outputs).splitlines() if line.startswith('RESULT ')))
 assert native==ns['out'];reports[name]={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'results':native,'native_cpython_equal':True}
result={'scope':'12 actual parser executions: three exact sources × two actual uploads × CPython/native. No repairs, counterfactual edited input, whole-agent replay, hidden grading or score claim.','source_pins':'comparison/ocr-source-pins.json','actual_upload_hashes':{t:hashlib.sha256(s.encode()).hexdigest() for t,s in cases},'results':reports}
(P/'crosslist-parser-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
