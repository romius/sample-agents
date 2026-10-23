"""Verify pins, regenerate exact parser extraction, run syntax controls in isolation."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
for n,v in json.loads((P/'INPUT-PINS.json').read_text()).items():
 b=(P/n).read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256'],n
outputs=['parser-pins.json','parsers/d4702.py','parsers/d4955.py','parsers/d4353.py','test-results.json']
with tempfile.TemporaryDirectory(prefix='null-effort-adjudication-') as tmp:
 d=Path(tmp)/'package';shutil.copytree(P,d,ignore=shutil.ignore_patterns('__pycache__','independent','publication'))
 for script in ['extract_parsers.py','test_parsers.py']:subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(d/script)],check=True,capture_output=True)
 for n in outputs:assert (d/n).read_bytes()==(P/n).read_bytes(),n
report={'status':'PASS','input_pins':23,'exact_regenerated_files':{n:sha((P/n).read_bytes()) for n in outputs},'source_parser_controls':69,'strict_checks':69,'semantic_results':None,'independent_review':'pending','paid_calls':0}
(P/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
