"""Read-only isolated evidence reconstruction; no model/runtime tests or network."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 pins=json.loads((P/'input-pins.json').read_text())
 for rel,pin in pins.items():
  b=(P/rel).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256'],rel
 if (P/'SHA256SUMS.json').exists():
  for rel,pin in json.loads((P/'SHA256SUMS.json').read_text()).items():
   b=(P/rel).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256'],rel
 expected={str(f.relative_to(P)):f.read_bytes() for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts and 'publication' not in f.parts and f.name not in ['SHA256SUMS.json','reproduction.json'] and f.suffix!='.zip'}
 logs=[]
 with tempfile.TemporaryDirectory(prefix='output-boundaries-') as td:
  dest=Path(td)/P.name;shutil.copytree(P,dest,ignore=shutil.ignore_patterns('__pycache__','publication','*.zip'))
  for name in ['reassemble_requests.py','analyze.py']:
   r=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(dest/name)],cwd=dest,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),text=True,capture_output=True)
   assert r.returncode==0,(name,r.stdout,r.stderr);logs.append({'script':name,'stdout':r.stdout,'exit_code':r.returncode})
  for rel,b in expected.items():assert (dest/rel).read_bytes()==b,rel
 report={'status':'PASS isolated exact evidence reproduction','python':sys.version,'input_pins':len(pins),'copied_files_compared':len(expected),'all_compared_bytes_equal':True,'scripts':logs,'agent_inference_tests_run':0,'model_calls':0,'Brain_calls':0,'source_changes':False}
 if '--write-report' in sys.argv:(P/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
 elif (P/'reproduction.json').exists():assert report==json.loads((P/'reproduction.json').read_text())
 print('PASS: exact31-event reassembly and165-response/25-boundary census reproduced; no inference/runtime tests.')
if __name__=='__main__':main()
