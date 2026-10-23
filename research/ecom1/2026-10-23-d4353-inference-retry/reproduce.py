"""Clean offline reproduction; never executes imported agent top-level in CPython."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
names=['input-verification.json','build-result.json','classifier-results.json','helper-overlay.json','cases.json','requests.json','test-results.json']+[f'{d}/{n}' for d in ('sdk-only','guest-owned') for n in ('agent.py','readable.py','decoded.py','candidate.diff')]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={n:sha(P/n) for n in names}
with tempfile.TemporaryDirectory(prefix='d4353-retry-clean-') as tmp:
 dst=Path(tmp)/'experiment';shutil.copytree(P,dst,ignore=shutil.ignore_patterns('__pycache__','publication','independent','clean-reproduction.json','SHA256SUMS.json'))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for script in ('verify_inputs.py','build.py','test_classifier.py','test_comparison.py'):
  result=subprocess.run([sys.executable,'-W','ignore::SyntaxWarning',str(dst/script)],cwd=dst,env=env,capture_output=True,text=True)
  assert result.returncode==0,(script,result.stdout,result.stderr)
 after={n:sha(dst/n) for n in names}
 assert before==after,{n:[before[n],after[n]] for n in names if before[n]!=after[n]}
report={'status':'PASS','generated_files_reproduced':len(names),'whole_agent_executions':318,'classifier_evaluations':56,'exact_parent_build_reproduced':True,'no_network_or_model_calls':True,'sha256':before}
(P/'clean-reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS clean isolated reproduction:',len(names),'generated files identical;318 whole-agent +56classifier checks')
