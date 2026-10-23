"""Narrow OCR layout repair on exact verified d4353r1; no other behavior changes."""
import ast, hashlib, json
from pathlib import Path
import lzpack
P=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def normalized(s):return ast.dump(ast.parse(s),include_attributes=False)
def decode(s):
 ns={};exec(s[:s.index('exec(_lz(')],ns)
 return ns['_lz'](s.split('exec(_lz("',1)[1].split('"))',1)[0])
parent=(P/'parent-readable.py').read_text();packed_parent=(P/'parent.py').read_bytes()
assert sha(packed_parent)=='588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
assert sha(parent.encode())=='f898132a754187b0052a637e1ca4caaccdd3ac46f72df80bc11d2b37b3737d0b'
assert sha((P/'lzpack.py').read_bytes())=='d93f463bd68d03438854f283ef7c478d72a8de236e71eba27a6bb10a7d50e02a'
decoded_parent=decode(packed_parent.decode())
assert lzpack.pack(decoded_parent,lazy=True).encode()==packed_parent
(P/'parent-decoded.py').write_text(decoded_parent)
assert normalized(decode(packed_parent.decode()))==normalized(parent)
pattern = '(?m)^[ \\t]*#[# \\t]*[sS][cC][aA][nN][lL][iI][nN][eE][ \\t]*#[# \\t]*(?=[tT][oO][tT][aA][lL] [rR][eE][qQ][uU][eE][sS][tT][eE][dD] (?:[lL][iI][nN][eE][sS]|[uU][nN][iI][tT][sS]):[ \\t]*[0-9]+[ \\t]*$)'
old='def crosslist_parse_ocr(text):\n    text = crosslist_text(text)\n'
new=old+'    text = re.sub('+repr(pattern)+", '', text)\n"
assert parent.count(old)==1
source=parent.replace(old,new,1)
assert source.replace(new,old,1)==parent
assert decoded_parent.count(old)==1
portable_source=decoded_parent.replace(old,new,1)
assert portable_source.replace(new,old,1)==decoded_parent
assert normalized(portable_source)==normalized(source)
packed=lzpack.pack(portable_source,lazy=True)
assert normalized(decode(packed))==normalized(source)
assert len(packed.encode())<=65536
for name,data in [('readable.py',source),('portable.py',portable_source),('agent.py',packed)]:
 (P/name).write_text(data)
manifest={'parent':'d4353r1','parent_readable':'d4354r1','packer':'d3268r2','change':'One ASCII scanline-prefix normalization assignment before strict OCR total parsing. All other source unchanged.','parent_rebuilt_exact':True,'candidate_decoded_ast_equal':True,'headroom_bytes':65536-len(packed.encode()),'evaluation':'none','files':{name:{'bytes':(P/name).stat().st_size,'sha256':sha((P/name).read_bytes())} for name in ['parent.py','parent-readable.py','parent-decoded.py','lzpack.py','build.py','readable.py','portable.py','agent.py']}}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest))
