"""Size-only lower-bound probe; no routing hook and explicitly NOT an evaluation candidate."""
import ast,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-record-integration'
PARENT=HERE.parent/'2026-10-22-inventory-integration'
sys.path.insert(0,str(PARENT))
from lzpack_dp import pack
source=(PARENT/'readable.py').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=='aef93a8c2b25feeb097e70a063d5ffff6c15f52622a3e4e058859901b0a921e1'
helper=(HERE/'bounded_lookup_evidence.py').read_text()
marker='IX_RESULT=ix_run('
assert source.count(marker)==1
probe=source.replace(marker,helper+'\n'+marker)
ns={'__name__':'packing'};exec((BASE/'pack5h.py').read_text().replace('hoist_literals=True','hoist_literals=False'),ns)
prepack=ns['mini'](probe).encode('ascii','backslashreplace').decode()
packed=pack(prepack)
result=dict(kind='size-only probe without routing hook; NOT an evaluation candidate',parent='d5204r1',parent_bytes=65292,
    parent_headroom=244,definition_only_packed_bytes=len(packed.encode()),extra_bytes=len(packed.encode())-65292,
    remaining_to_cap=65536-len(packed.encode()),probe_sha256=hashlib.sha256(packed.encode()).hexdigest(),
    readable_sha256=hashlib.sha256(probe.encode()).hexdigest(),prepack_sha256=hashlib.sha256(prepack.encode()).hexdigest(),
    source_size_limit=65536,can_ship=False,reason='No intent/routing integration, no model outcome evidence; definition alone measured before adding any runtime hook.')
(HERE/'size-only-readable.py').write_text(probe)
(HERE/'size-only-prepack.py').write_text(prepack)
(HERE/'size-only-packed.py').write_text(packed)
(HERE/'size-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
