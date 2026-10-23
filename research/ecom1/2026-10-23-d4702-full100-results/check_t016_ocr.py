"""Exact archived OCR vs current narrow candidate; parser-only, no model/task calls."""
import ast,hashlib,json,re
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
events=[json.loads(x) for x in (P/'t016-events.ndjson').read_text().splitlines()]
ocr=next(e['data']['response']['content'] for e in events if e['seq']==2628)
assert hashlib.sha256(ocr.encode()).hexdigest()=='50296b921e09ba7340b743ce4cd991d6f41e9cab90d4daa88348805a8bdb7e7d'
(P/'t016-uploaded-ocr.txt').write_text(ocr)
names={'crosslist_text','crosslist_uint','crosslist_parse_ocr'}
sources={name:(P/'sources'/file).read_text() for name,file in [('d4702','d4702r1-readable.py'),('d4353','d4353r1-readable.py'),('current_hash_scanline_candidate','d4353-ocr-candidate-readable.py')]}
total_clean=ocr.replace(' ~~ ~~  Total requested lines: 5','Total requested lines: 5')
footer='x x x ////  =========:===============-========:=================.=======:====.==='
both_clean=total_clean.replace(footer+'\n','')
cases=[('actual_tilde_prefix',ocr),('counterfactual_only_remove_exact_tilde_prefix',total_clean),
 ('counterfactual_remove_exact_tilde_prefix_and_exact_footer',both_clean),
 ('unknown_prose_in_same_position',total_clean.replace(footer,'Customer requests alternative chemistry; verify suitability')),
 ('duplicate_clean_lines_total',both_clean+'\nTotal requested lines: 5\n'),
 ('conflicting_clean_units_total',both_clean+'\nTotal requested units: 29\n'),
 ('unicode_tilde_prefix',ocr.replace(' ~~ ~~  Total',' ～～ ～～  Total'))]
runner='''
out=[]
for name,text in CASES:
 try:out.append({'case':name,'parsed':crosslist_parse_ocr(text)})
 except ValueError as exc:out.append({'case':name,'error':str(exc)})
'''
reports={}
for name,source in sources.items():
 defs='\n\n'.join(ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names)
 ns={'re':re,'CASES':cases};exec(defs+'\n'+runner,ns)
 outputs=[]
 code='import re\nimport json\n'+defs+'\nCASES='+repr(cases)+'\n'+runner+'\nprint("RESULT "+json.dumps(out))'
 with m.Monty() as pool:
  with pool.checkout() as session:session.feed_run(code,print_callback=lambda *args:outputs.append(args))
 stdout=''.join(str(x[1]) if len(x)>1 else str(x[0]) for x in outputs)
 native=json.loads(next(x[7:] for x in stdout.splitlines() if x.startswith('RESULT ')))
 assert native==ns['out'];reports[name]=native
 assert native[0]['error']=='OCR must identify one branch and both complete totals'
 assert len(native[2]['parsed']['lines'])==5
 assert 'error' in native[3] and 'error' in native[4] and 'error' in native[5] and 'error' in native[6]
assert len({json.dumps(v,sort_keys=True) for v in reports.values()})==1
world={'provenance':'Actual full t016 immutable trace only. Sparse observed-world fixture, NOT a full world: no catalogue/store Read exists in this trace. Tree/List are only observed bounded views.',
 'trace_sha256':hashlib.sha256((P/'t016-events.ndjson').read_bytes()).hexdigest(),
 'responses':[e for e in events if e['kind']=='rpc_response'],'requests':[e for e in events if e['kind']=='rpc_request']}
(P/'t016-observed-world.json').write_text(json.dumps(world,indent=2,ensure_ascii=False)+'\n')
result={'scope':'Parser-only boundary; no whole-agent success, score or matching-world claim. Exact tilde removal is a counterfactual diagnostic, NOT a proposed source patch.',
 'current_candidate_packed_sha256':'420e904a4cb502221f8609f99bd0f62370deda775abb41b5be9880042f0b7bf8',
 'source_hashes':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in sources.items()},'ocr_sha256':hashlib.sha256(ocr.encode()).hexdigest(),
 'runtimes':['CPython','native Monty1.2.0'],'results':reports,'candidate_addresses_actual_t016':False}
result['stagewise_findings']={'first_blocker':'Exact double-tilde requested-lines prefix, outside current hash-scanline scope',
 'second_blocker':footer,'second_error':'Unrecognised line inside a requested row',
 'counterfactual_only':'Deleting these two exact observed layout strings parses five rows/28units; no broad filtering rule, accepted patch, product-match or whole-agent success is established.',
 'unknown_prose_control':'Replacing footer with a meaningful customer note without a recognized note prefix still rejects. Broadly discarding unknown lines could erase substantive requirements.'}
(P/'t016-parser-review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2))
