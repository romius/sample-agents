import ast,hashlib,json,shutil,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent;W=ROOT.parent/'2026-10-23-d4702-receipt-worlds'
sys.path.insert(0,str(P/'upstream'));from lzpack import pack
sha=lambda b:hashlib.sha256(b).hexdigest()
for arm in ['context_only','provenance_only']:
 for form in ['readable','decoded']:
  s=(P/'upstream'/(form+'.py')).read_text()
  if arm=='context_only':
   old='  for function, result in provenance:\n    note_policy_read(function, result)';assert s.count(old)==1;s=s.replace(old,'  for function, result in provenance:\n    pass')
  else:
   old='  return messages + additions';assert s.count(old)==1;s=s.replace(old,'  return messages')
  (P/'upstream'/f'{arm}-{form}.py').write_text(s)
 decoded=(P/'upstream'/f'{arm}-decoded.py').read_text();readable=(P/'upstream'/f'{arm}-readable.py').read_text()
 assert ast.dump(ast.parse(decoded))==ast.dump(ast.parse(readable));(P/'upstream'/f'{arm}.py').write_text(pack(decoded,lazy=True))
files={str(f.relative_to(P)):{'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted((P/'upstream').rglob('*')) if f.is_file()}
(P/'source-pins.json').write_text(json.dumps(files,indent=2)+'\n')
print('prepared',len(files),'inputs/derived arm sources')
