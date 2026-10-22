import hashlib,json,sys
from pathlib import Path
from lz3 import pack
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'2026-10-22-inventory-integration'
PROBE=HERE.parent/'2026-10-22-sku-evidence-review'
rows=[]
for label,folder in [('inventory',PARENT),('sku-definition-only',PROBE)]:
    name='prepack.py' if label=='inventory' else 'size-only-prepack.py'
    source=(folder/name).read_text();packed=pack(source)
    (HERE/(label+'-packed.py')).write_text(packed)
    rows.append(dict(label=label,prepack_sha256=hashlib.sha256(source.encode()).hexdigest(),
      packed_sha256=hashlib.sha256(packed.encode()).hexdigest(),bytes=len(packed.encode()),headroom=65536-len(packed.encode()),
      status='experimental packing; whole-agent/native validation pending; not submitted'))
(HERE/'size-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
