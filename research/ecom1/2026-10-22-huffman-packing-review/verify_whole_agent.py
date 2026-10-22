"""Run the pinned full inventory/recovery suite on Huffman-wrapped exact prepack."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'2026-10-22-inventory-integration'
sys.path.insert(0,str(PARENT))
import verify_integration as suite
for name in ['readable.py','prepack.py']:(HERE/name).write_bytes((PARENT/name).read_bytes())
suite.HERE=HERE
suite.SOURCES={name:(HERE/name).read_text() for name in ['readable.py','prepack.py','inventory-packed.py']}
suite.main()
