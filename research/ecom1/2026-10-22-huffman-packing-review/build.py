import hashlib,json
from pathlib import Path
from pack import pack
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'2026-10-22-inventory-integration'
PROBE=HERE.parent/'2026-10-22-sku-evidence-review'
rows=[]
for label,source_path in [('inventory',PARENT/'prepack.py'),('sku-definition-only',PROBE/'size-only-prepack.py')]:
    source=source_path.read_text();packed=pack(source)
    (HERE/(label+'-packed.py')).write_text(packed)
    rows.append(dict(label=label,source=str(source_path.relative_to(HERE.parent)),prepack_sha256=hashlib.sha256(source.encode()).hexdigest(),
       packed_sha256=hashlib.sha256(packed.encode()).hexdigest(),bytes=len(packed.encode()),headroom=65536-len(packed.encode()),
       status='experimental packing; validation pending; not submitted'))
(HERE/'size-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
