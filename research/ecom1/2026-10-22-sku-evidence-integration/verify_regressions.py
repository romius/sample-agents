"""Frozen whole-agent inventory/recovery regressions on the new exact forms."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'2026-10-22-inventory-integration'
sys.path.insert(0,str(PARENT))
import verify_integration as suite
suite.HERE=HERE
suite.SOURCES={name:(HERE/name).read_text() for name in ['readable.py','prepack.py','agent.py']}
suite.main()
