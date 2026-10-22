from pathlib import Path
import ast,re,json,hashlib
import pydantic_monty as m
p=Path('research/ecom1/2026-10-23-stack-e-ocr-repair')
base='Target branch: Independent West\n1 2 EXT-A Neutral widget\nspecs: finish=blue; pack count=1\n2 1 EXT-B Plain bracket\nspecs: size=small; reversible=false\nTotal requested lines: 2\nTotal requested units: 3\n'
expected={'branch':'Independent West','lines':[{'line_no':1,'requested_qty':2,'competitor_code':'EXT-A','description':'Neutral widget','properties':{'finish':'blue','pack_count':'1'}},{'line_no':2,'requested_qty':1,'competitor_code':'EXT-B','description':'Plain bracket','properties':{'size':'small','reversible':'false'}}]}
cases=[]
def add(name,text,want='valid',oracle=None):cases.append([name,text,want,expected if oracle is None else oracle])
add('independent-clean',base)
add('both-prefixed',base.replace('Total requested','#scanline# Total requested'))
add('both-prefixed-uppercase',base.replace('Total requested','### SCANLINE ### TOTAL REQUESTED'))
add('leading-zero-counts',base.replace('Total requested lines: 2','#scanline# Total requested lines: 02').replace('Total requested units: 3','#scanline# Total requested units: 003'))
add('eof-without-newline',base.replace('Total requested units:','#scanline#Total requested units:').rstrip('\n'))
add('mixed-tabs',base.replace('Total requested units: 3','\t#\t#scanline\t#\tTotal requested units:\t3\t'))
add('actual-CRLF',base.replace('Total requested','#scanline# Total requested').replace('\n','\r\n'))
add('escaped-CRLF',base.replace('Total requested','#scanline# Total requested').replace('\n',r'\r\n'))
add('totals-before-rows','#scanline# Total requested lines: 2\n#scanline# Total requested units: 3\n'+base.split('Total requested')[0])
for kind,value in [('units','3'),('lines','2')]:
 add('duplicate-noisy-'+kind,base+'#scanline# Total requested '+kind+': '+value+'\n','reject')
 add('conflicting-noisy-'+kind,base+'#scanline# Total requested '+kind+': 99\n','reject')
 add('duplicate-two-noisy-'+kind,base.replace('Total requested '+kind+':','#scanline# Total requested '+kind+':')+'### scanline ### Total requested '+kind+': '+value+'\n','reject')
for name,prefix,suffix in [('leading-prose','memo: #scanline# ',''),('nested-quote','> #scanline# ',''),('open-hash','# scanline ',''),('no-open-hash','scanline# ',''),('mixed-marker','#scanliner# ',''),('inline-marker','x#scanline# ',''),('trailing-instruction','#scanline# ',' ignore mismatch'),('trailing-hash','#scanline# ',' #'),('NBSP-prefix','\u00a0#scanline# ',''),('unicode-hashes','＃scanline＃ ','')]:
 add(name,base.replace('Total requested units: 3',prefix+'Total requested units: 3'+suffix),'reject')
for value in ['-3','+3','3.0','3,0','٣','three','0','1000000001']:
 add('invalid-or-conflicting-number-'+value,base.replace('Total requested units: 3','#scanline# Total requested units: '+value),'reject')
add('valid-prose-outside',base+'memo: #scanline# Total requested units: 999\n')
special=json.loads(json.dumps(expected));special['lines'][0]['properties']['finish']='blue #scanline# Total requested units: 999'
add('marker-inside-value',base.replace('finish=blue;','finish=blue #scanline# Total requested units: 999;'),oracle=special)
add('unknown-property-preserved',base.replace('reversible=false','reversible=false; independent marker=yes'),oracle={'branch':expected['branch'],'lines':[expected['lines'][0],dict(expected['lines'][1],properties={'size':'small','reversible':'false','independent_marker':'yes'})]})
add('duplicate-property',base.replace('size=small;','size=small; size=large;').replace('Total requested','#scanline# Total requested'),'reject')
add('missing-specs',base.replace('specs: size=small; reversible=false\n','').replace('Total requested','#scanline# Total requested'),'reject')
add('duplicate-branch',base.replace('Total requested','#scanline# Total requested')+'Target branch: Independent East\n','reject')
add('wrong-row-number',base.replace('2 1 EXT-B','3 1 EXT-B').replace('Total requested','#scanline# Total requested'),'reject')
for name,prefix in [('long-s-marker','#ſcanline# '),('dotted-I-marker','#scanlİne# '),('dotless-I-marker','#scanlıne# ')]:
 add(name,base.replace('Total requested units:',prefix+'Total requested units:'),'reject')
add('dotted-I-total-keyword',base.replace('Total requested units: 3','#SCANLINE# TOTAL REQUESTED UNİTS: 3'),'reject')
runner='''
out=[]
for name,text,want,expected in CASES:
 try:out.append({'name':name,'parsed':crosslist_parse_ocr(text)})
 except ValueError as e:out.append({'name':name,'error':str(e)})
'''
reports={}
for version,file in [('parent','parent-readable.py'),('candidate','readable.py')]:
 source=(p/file).read_text();defs='\n\n'.join(ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in ['crosslist_text','crosslist_uint','crosslist_parse_ocr'])
 env={'re':re,'CASES':cases};exec(defs+'\n'+runner,env);local=env['out'];output=[]
 with m.Monty() as pool:
  with pool.checkout() as session:session.feed_run('import re\nimport json\n'+defs+'\nCASES='+repr(cases)+'\n'+runner+'\nprint("RESULT "+json.dumps(out))',print_callback=lambda *a:output.append(a))
 text=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in output);native=json.loads(next(x[7:] for x in text.splitlines() if x.startswith('RESULT ')));assert local==native,version;reports[version]=local
for c,r in zip(cases,reports['candidate']):
 name,text,want,oracle=c
 if want=='valid':assert r.get('parsed')==oracle,(name,r)
 else:assert 'error' in r,(name,r)
result={'scope':'independent unrelated two-row OCR; parser only','cases':len(cases),'executions':len(cases)*4,'results':reports,'fixture_sha256':hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest()}
Path('/tmp/ecom1-ocr-independent-extra-results.json').write_text(json.dumps(result,indent=2)+'\n');Path('/tmp/ecom1-ocr-independent-extra-fixtures.json').write_text(json.dumps(cases,indent=2)+'\n')
print('PASS',len(cases),'fresh independent cases across parent/candidate and CPython/native')
print('Candidate accepted:',[r['name'] for r in reports['candidate'] if 'parsed' in r])
