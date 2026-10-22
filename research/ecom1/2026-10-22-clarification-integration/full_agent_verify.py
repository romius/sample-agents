"""Run pinned parent recovery regressions on the exact successor in native Monty."""
import os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-record-integration'
sys.path.insert(0,str(BASE))
os.chdir(BASE)
source=(BASE/'verify.py').read_text()
source=source.replace("packed=P.joinpath('agent.py').read_text();readable=P.joinpath('readable.py').read_text()", "packed=Path("+repr(str(HERE/'agent.py'))+").read_text();readable=Path("+repr(str(HERE/'readable.py'))+").read_text()")
source=source.replace("P.joinpath('verification.json')", "Path("+repr(str(HERE/'whole-agent-verification.json'))+")")
exec(compile(source,str(BASE/'verify.py'),'exec'),{})
