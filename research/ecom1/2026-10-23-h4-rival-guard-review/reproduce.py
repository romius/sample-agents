import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
outputs=['guard-packed.py','build-result.json','fixtures.json','results.json','forensic-k0-results.json']
with tempfile.TemporaryDirectory(prefix='h4-rival-guard-review-') as t:
 T=Path(t)/'review';shutil.copytree(P,T,ignore=shutil.ignore_patterns('__pycache__','clean-reproduction.json','SHA256SUMS.json'))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');runs=[]
 for script in ['build.py','review.py','forensic_k0.py']:
  r=subprocess.run([sys.executable,str(T/script)],cwd=t,env=env,capture_output=True,text=True,check=True);runs.append({'script':script,'exit_code':r.returncode})
 matches={n:sha(T/n)==sha(P/n) for n in outputs};assert all(matches.values())
 result={'scope':'Clean-copy exact offline reproduction; no live calls','python':sys.version,'monty_version':'1.2.0','runs':runs,'byte_exact_outputs':matches,'sha256':{n:sha(P/n) for n in outputs}}
 (P/'clean-reproduction.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
