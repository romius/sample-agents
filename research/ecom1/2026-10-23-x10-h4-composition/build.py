"""Four isolated offline arms; preserve H4 early-before-fuzzy proposal unchanged."""
import ast,difflib,hashlib,json,runpy
from pathlib import Path
P=Path(__file__).resolve().parent;U=P/'upstream'
sha=lambda b:hashlib.sha256(b).hexdigest()
for name,pin in json.loads((P/'dependency-pins.json').read_text()).items():
 b=(P/name).read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256']
parent=(U/'parent-decoded.py').read_text();x10=(U/'d6633r1-decoded.py').read_text()
assert sha((U/'parent.py').read_bytes())=='588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
assert sha((U/'d6633r1.py').read_bytes())=='e58220a01be07757cfd722329ccdaf8d55758af4b9a7d75b86c5a63799504d2d'
assert sha(x10.encode())=='2c27fc301ce24bbb81803fa20ac105bdae7dabb990bbff5e90aef1e76932fd99'
def decoded(raw):
 capture=[];exec(raw,{'exec':capture.append});assert len(capture)==1;return capture[0]
assert decoded((U/'parent.py').read_text())==parent and decoded((U/'d6633r1.py').read_text())==x10
pack=runpy.run_path(str(U/'lzpack.py'))['pack'];assert pack(parent,lazy=True).encode()==(U/'parent.py').read_bytes()
helper='def rcp_drop1(a, b):\n  return len(a) == len(b) + 1 and any(a[:i] + a[i + 1:] == b for i in range(len(a)))\n\n\n'
fallback='  if not hits and cut and len(key) >= 10:\n    hits = [p for p in WORLD["products"] if p.get("price_cents") == cents and rcp_drop1(ocr_key(p.get("sku", ""))[:len(key) + 1], key)]\n'
def compose(s,has_fuzzy):
 anchor='def rcp_product(fragment, cents):\n';assert s.count(anchor)==1;s=s.replace(anchor,helper+anchor,1)
 start=s.index(anchor);end=s.index('\ndef rcp_store(',start) if not has_fuzzy else s.index('\ndef rcp_dist(',start)
 part=s[start:end];marker='  if not hits and len(key) >= 10:\n' if has_fuzzy else '  return hits[0] if len(hits) == 1 else None'
 assert part.count(marker)==1;s=s[:start]+part.replace(marker,fallback+marker,1)+s[end:]
 before=ast.parse(s.replace(helper,'',1));after=ast.parse(s) # explicit occurrence proof below
 return s
sources={'d4353':parent,'d4353_H4':compose(parent,False),'X10':x10,'X10_H4':compose(x10,True)}
def occurrence_map(s):
 out={};count={}
 for n in ast.parse(s).body:
  key=n.name if isinstance(n,(ast.FunctionDef,ast.ClassDef)) else '$statement'
  i=count.get(key,0);count[key]=i+1;out[f'{key}#{i}']=ast.dump(n,include_attributes=False)
 return out
def delta(a,b):
 a,b=occurrence_map(a),occurrence_map(b)
 return {'changed':[k for k in a.keys()&b.keys() if a[k]!=b[k]],'added':sorted(b.keys()-a.keys()),'removed':sorted(a.keys()-b.keys())}
dx=delta(parent,x10);dx['changed'].sort();assert dx=={'changed':['rcp_items#0','rcp_product#0'],'added':['rcp_dist#0'],'removed':[]}
report={'status':'offline composition; H4 guard bypass deliberately preserved','original_X10_delta':dx,'arms':{},'H4_branch_order':'exact/price-prefix hits, then same-price drop1 truncated prefix, then X10 fuzzy with global-rival guard only when hits remains empty'}
for name,s in sources.items():
 dest=P/'arms'/name;dest.mkdir(parents=True,exist_ok=True);(dest/'readable.py').write_text(s)
 b=(U/('parent.py' if name=='d4353' else 'd6633r1.py')).read_bytes() if name in ['d4353','X10'] else pack(s,lazy=True).encode()
 assert decoded(b.decode())==s and len(b)<=65536;(dest/'agent.py').write_bytes(b)
 item={'readable_sha256':sha(s.encode()),'packed_sha256':sha(b),'packed_bytes':len(b),'headroom':65536-len(b)}
 if name.endswith('_H4'):
  base=parent if name=='d4353_H4' else x10;d=delta(base,s);assert d=={'changed':['rcp_product#0'],'added':['rcp_drop1#0'],'removed':[]};item['delta_from_uncomposed_arm']=d
  (dest/'change.diff').write_text(''.join(difflib.unified_diff(base.splitlines(True),s.splitlines(True),fromfile=name.removesuffix('_H4'),tofile=name)))
 report['arms'][name]=item
(P/'build-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
