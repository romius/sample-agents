"""Extract exact AST-selected source segments; never execute whole-agent code."""
import ast,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
GLOBALS=['FIELDS','OUTCOMES','REQUIRED_ARGUMENTS'];FUNCS=['normalize_action','first_action_object','parse_step'];report={}
for source in ['d4702','d4955','d4353']:
 path=P/'inputs/inputs'/f'{source}-readable.py';s=path.read_text();tree=ast.parse(s);selected=[];parts=['import json\n'];symbols={}
 for node in tree.body:
  name=node.name if isinstance(node,ast.FunctionDef) else node.targets[0].id if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) else None
  if name in GLOBALS+FUNCS:
   segment=ast.get_source_segment(s,node);parts.append(segment+'\n');selected.append(name)
   symbols[name]={'start_line':node.lineno,'end_line':node.end_lineno,'exact_segment_sha256':sha(segment.encode())}
 assert set(selected)==set(GLOBALS+FUNCS)
 output='\n'.join(parts);out=P/'parsers'/f'{source}.py';out.parent.mkdir(exist_ok=True);out.write_text(output)
 report[source]={'source_file':str(path.relative_to(P)),'source_sha256':sha(path.read_bytes()),'parser_sha256':sha(output.encode()),'symbols':symbols}
assert len({r['parser_sha256'] for r in report.values()})==1
(P/'parser-pins.json').write_text(json.dumps({'all_three_exact_extractions_identical':True,'sources':report},indent=2)+'\n')
print('Three exact extracted parser implementations are byte-identical.')
