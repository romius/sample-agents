import ast,base64,hashlib,json,runpy
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 receipt=json.loads((P/'community/source-export.json').read_text())['data']['files']
 for n,pin in receipt.items():
  b=(P/'community'/('export-'+n)).read_bytes();assert len(b)==pin['size'] and sha(b)==pin['blob']
 manifest=json.loads((P/'community/d6865.txt').read_text())
 for name,pin in manifest.items():
  b=(P/'community/repro'/name).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256'],name
 for a,b in [('export-parent','candidate.py'),('export-readable','readable.py'),('export-encoder','lzopt.py')]:assert (P/'community'/a).read_bytes()==(P/'community/repro'/b).read_bytes()
 source=(P/'community/export-readable').read_text();parent=(P/'community/export-parent').read_bytes();stub=(P/'community/repro/parent_stub.txt').read_text();lz=runpy.run_path(str(P/'community/export-encoder'))['lz']
 def pack(s):return (stub+'exec(_lz("'+base64.b85encode(lz(s.encode('ascii'))).decode()+'"))\n').encode()
 original=(P/'community/repro/parent_decoded.py').read_text()
 assert pack(original)==(P/'community/repro/parent.py').read_bytes()
 recipe=json.loads((P/'community/repro/rc7_edits.json').read_text())
 apply=runpy.run_path(str(P/'community/repro/apply_recipe.py'))['apply']
 assert apply(original,recipe)==source
 assert pack(source)==parent
 changes=(P/'community/export-h4diff').read_text().splitlines();old=[x[1:] for x in changes if x.startswith('-') and not x.startswith('---')];new=[x[1:] for x in changes if x.startswith('+') and not x.startswith('+++')];assert len(old)==len(new)==1 and source.count(old[0])==1
 candidate=source.replace(old[0],new[0],1);before=ast.parse(source).body;after=ast.parse(candidate).body;assert len(before)==len(after)
 changed=[]
 for a,b in zip(before,after):
  if ast.dump(a)!=ast.dump(b):assert isinstance(a,ast.FunctionDef) and a.name==b.name=='FO';changed.append(a.name)
 assert changed==['FO'];packed=pack(candidate);assert len(packed)<=65536
 for raw,decoded in [(parent,source),(packed,candidate)]:
  capture=[];exec(raw.decode(),{'exec':capture.append});assert capture==[decoded]
 files={'parent.py':parent,'parent-readable.py':source.encode(),'agent.py':packed,'readable.py':candidate.encode(),'formatted-readable.py':(ast.unparse(ast.parse(candidate))+'\n').encode()}
 for n,b in files.items():(P/n).write_bytes(b)
 report={'parent':'d6855r1','readable':'d6856r1','H4_diff':'d6928r1','encoder':'d4558r1','source_archive':'d6866r1','parent_exact_repack':True,'rc7_base_repack_and_owner_recipe_exact':True,'changed_function_only':'FO','files':{n:{'bytes':len(b),'sha256':sha(b)} for n,b in files.items()},'headroom':65536-len(packed)}
 (P/'build-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
