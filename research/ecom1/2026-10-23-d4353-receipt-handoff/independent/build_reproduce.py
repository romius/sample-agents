"""Build only an isolated temporary copy; leave prototype sources/artifacts untouched."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;U=P.parent/'initial-prototype'
required=['build.py','handoff.py','lzpack.py','parent.py','parent-readable.py','parent-decoded.py']
outputs=['agent.py','readable.py','decoded.py','candidate.diff','build-result.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={n:sha(U/n) for n in required+outputs}
with tempfile.TemporaryDirectory(prefix='ecom1-receipt-independent-') as tmp:
 t=Path(tmp)
 for n in required:shutil.copy2(U/n,t/n)
 r=subprocess.run([sys.executable,str(t/'build.py')],cwd=t,text=True,capture_output=True,check=True)
 assert {n:sha(t/n) for n in outputs}=={n:pins[n] for n in outputs}
assert {n:sha(U/n) for n in pins}==pins
result={'isolated_build_byte_identical':True,'source_unchanged':True,'pins':pins,'python':sys.version.split()[0],'candidate_bytes':(U/'agent.py').stat().st_size,'headroom':65536-(U/'agent.py').stat().st_size}
(P/'build-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
