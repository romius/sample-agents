import pathlib,hashlib,json,shutil,tempfile,subprocess,sys,os
P=pathlib.Path(__file__).resolve().parent
for name,pin in json.loads((P/'SHA256SUMS.json').read_text())['files'].items():
 b=(P/name).read_bytes();assert len(b)==pin['bytes'] and hashlib.sha256(b).hexdigest()==pin['sha256'],name
with tempfile.TemporaryDirectory(prefix='completion-integrity-') as tmp:
 q=pathlib.Path(tmp)/'review';shutil.copytree(P,q,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'))
 subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(q/'check.py')],check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=subprocess.DEVNULL)
 for n in ['source-functions.json','counterexamples.json','evidence-summary.json']:assert (P/n).read_bytes()==(q/n).read_bytes(),n
print('PASS: sealed input hashes and three reproduced outputs byte-identical')
