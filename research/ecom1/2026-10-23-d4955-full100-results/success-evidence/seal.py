"""Hash this evidence closure; no timestamps or environment-derived metadata."""
import hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
files={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json' and '__pycache__' not in p.parts and 'publication' not in p.parts}
if '--check' in sys.argv:
 assert files==json.loads((P/'SHA256SUMS.json').read_text());print(f'Verified {len(files)} sealed files')
else:(P/'SHA256SUMS.json').write_text(json.dumps(files,indent=2)+'\n');print(f'Sealed {len(files)} files')
