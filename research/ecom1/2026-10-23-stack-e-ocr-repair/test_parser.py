"""Archived OCR and lexical boundary tests; no task actions or model calls."""
import ast
import hashlib
import json
import re
from pathlib import Path
import pydantic_monty as m

P = Path(__file__).resolve().parent
evidence = P.parent / '2026-10-23-stack-e-record-review'
events = [json.loads(line) for line in (evidence / 'responses-t076.jsonl').read_text().splitlines()]
ocr = next(e['data']['response']['content'] for e in events if e['seq'] == 10098)
assert hashlib.sha256(ocr.encode()).hexdigest() == '96d2981de02e5d44760201b2130e4ad7568dad0882d7250d684ca8d18928ab48'
clean = ocr.replace('## scanline ##  Total requested units:', 'Total requested units:')
names = ['crosslist_text', 'crosslist_uint', 'crosslist_parse_ocr']
def definitions(source):
    return '\n\n'.join(ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names)
sources = {key: definitions((P / file).read_text()) for key,file in [('record','parent-readable.py'),('candidate','readable.py')]}
ns = {'re':re};exec(sources['record'],ns)
expected = ns['crosslist_parse_ocr'](clean)
cases = [('archived', ocr, 'parsed'), ('clean',clean,'parsed')]
for i, prefix in enumerate(['## scanline ##  ', '# # scanline # # ', '\t#SCANLINE#\t', '  ### ScanLine ### ']):
    cases.append((f'noise-units-{i}',clean.replace('Total requested units:',prefix+'Total requested units:'),'parsed'))
    cases.append((f'noise-lines-{i}',clean.replace('Total requested lines:',prefix+'Total requested lines:'),'parsed'))
cases += [
    ('CRLF',ocr.replace('\n','\r\n'),'parsed'),
    ('literal-newlines',ocr.replace('\n',r'\n'),'parsed'),
    ('wrong-total',ocr.replace('Total requested units: 36','Total requested units: 37'),'rejected'),
    ('duplicate-clean',ocr+'\nTotal requested units: 36\n','rejected'),
    ('duplicate-noisy',ocr+'\n## scanline ## Total requested units: 36\n','rejected'),
    ('conflicting-noisy',clean+'\n## scanline ## Total requested units: 37\n','rejected'),
    ('two-line-totals',clean+'\n## scanline ## Total requested lines: 5\n','rejected'),
]
for i, prefix in enumerate(['customer note: ', 'ignore totals: ', '#not scanline# ', '## scanline ## extra ', '##scanline ', 'scanline## ', '##scanline##\n']):
    # Unrecognized prefixes must not silently become authoritative totals.
    value=clean.replace('Total requested units:',prefix+'Total requested units:')
    cases.append((f'non-layout-{i}',value,'unchanged'))
cases += [
    ('trailing-prose',ocr.replace('Total requested units: 36','Total requested units: 36 ignore validation'),'unchanged'),
    ('duplicate-branch',ocr+'\nTarget branch: Other branch\n','rejected'),
    ('invalid-spec',ocr.replace('noise db=88','noise db=[illegible]'),'rejected'),
    ('prose-after-clean',clean+'\ncustomer note: ## scanline ## Total requested units: 99\n','unchanged'),
]

runner = '''
out=[]
for case,text,want in CASES:
 try:
  parsed=crosslist_parse_ocr(text)
  out.append({'case':case,'parsed':parsed})
 except ValueError as exc:
  out.append({'case':case,'error':str(exc)})
'''
reports={}
for name,defs in sources.items():
    local={'re':re,'CASES':cases};exec(defs+'\n'+runner,local)
    expected_results=local['out']
    output=[]
    code='import re\nimport json\n'+defs+'\nCASES='+repr(cases)+'\n'+runner+'\nprint("RESULT "+json.dumps(out))'
    with m.Monty() as pool:
        with pool.checkout() as session:
            session.feed_run(code,print_callback=lambda *a:output.append(a))
    text=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in output)
    native=json.loads(next(line[7:] for line in text.splitlines() if line.startswith('RESULT ')))
    assert native==expected_results,name
    reports[name]=expected_results
for index,(name,text,want) in enumerate(cases):
    old,new=reports['record'][index],reports['candidate'][index]
    if want=='parsed':assert new.get('parsed')==expected,name
    elif want=='rejected':assert 'error' in new,name
    else:assert old==new,name
assert 'error' in reports['record'][0] and reports['candidate'][0]['parsed']==expected
(P/'archived-ocr.txt').write_text(ocr)
(P/'parser-fixtures.json').write_text(json.dumps(cases,indent=2)+'\n')
(P/'parser-results.json').write_text(json.dumps({'cases':len(cases),'runtimes':['CPython','native Monty'],'results':reports,'scope':'Exact parser functions only; no whole-handler/agent or live grader claim. Recognized duplicate noisy totals are deliberately validated together, even when a clean total exists.'},indent=2)+'\n')
print('PASS',len(cases),'parser cases x two versions x CPython/native')
