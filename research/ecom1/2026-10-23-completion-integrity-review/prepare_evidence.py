import ast,json,hashlib,shutil,collections
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parent
sources={'d4955':R/'2026-10-23-d4955-full100-results','d4353':R/'2026-10-23-d4353-record-review','success':R/'2026-10-23-d4353-success-review'}
copylist=[(sources['d4955']/n,'d4955/'+n) for n in ['index-t076.json','t076-events.ndjson','result.json','t076-uploaded-ocr.txt']]
copylist += [(sources['d4955']/'sources/2026-10-22-clarification-integration/readable.py','d4955/readable.py'),(sources['d4353']/'upstream/readable.py','d4353/readable.py'),(sources['success']/'success-review.json','success/success-review.json')]
copylist += [(f,'success/events/'+f.name) for f in sorted((sources['success']/'events').glob('t091*'))]
pins={}
for src,name in copylist:
 dst=P/'upstream'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);pins[name]={'source':str(src),'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}
(P/'input-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
