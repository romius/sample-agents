"""Copy frozen diagnostic inputs without modifying the author package."""
import hashlib,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;S=P.parent/'2026-10-23-null-final-effort-diagnostic'
pins={}
for n in ['PLAN.md','frozen.json','call-plan.json','manifest.json','SHA256SUMS.json']+[f'inputs/{s}-{form}.py' for s in ['d4702','d4955','d4353'] for form in ['agent','readable']]+[f'inputs/{f}-{kind}.json' for f in ['A016','A074','B056','B076'] for kind in ['request-event','trigger-event','previous-boundary']]:
 b=(S/n).read_bytes();out=P/'inputs'/n;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
 pins[str(out.relative_to(P))]={'original_workspace_path':str((S/n).relative_to(P.parent.parent.parent)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
(P/'INPUT-PINS.json').write_text(json.dumps(pins,indent=2)+'\n');print('Pinned',len(pins),'inputs.')
