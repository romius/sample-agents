"""Run from any directory after clean extraction; Python3 + pydantic-monty1.2.0."""
import hashlib,json,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parent
for script in ['build.py','replay/prepare_archived.py','replay/prepare_port.py','test_parser.py','test_independent_controls.py','replay/replay.py']:
 subprocess.run([sys.executable,str(p/script)],check=True,cwd=p)
print('PASS exact parent rebuild, candidate build, 300 parser checks, 112 whole-agent replays')
