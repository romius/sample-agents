import ast,base64,hashlib,json,runpy
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 for f,pin in json.loads((P/'input-pins.json').read_text()).items():
  b=(P/'inputs'/f).read_bytes();assert sha(b)==pin['sha256'] and len(b)==pin['bytes']
 source=(P/'upstream/d7019r1-cand_h4g2_dec.py').read_text();assert sha(source.encode())=='fc443326b4cebed7473990c923f4231d6bb92a88aae57cacc988a0044c1ebc48'
 stub=(P/'inputs/stub.txt').read_text();lz=runpy.run_path(str(P/'inputs/lzopt.py'))['lz']
 def pack(s):return (stub+'exec(_lz("'+base64.b85encode(lz(s.encode('ascii'))).decode()+'"))\n').encode()
 for read,packed in [('parent-readable.py','parent.py'),('h4-readable.py','h4.py')]:assert pack((P/'inputs'/read).read_text())==(P/'inputs'/packed).read_bytes()
 old=ast.parse((P/'inputs/h4-readable.py').read_text());new=ast.parse(source);assert len(old.body)==len(new.body)
 changed=[(getattr(a,'name',None),getattr(b,'name',None)) for a,b in zip(old.body,new.body) if ast.dump(a)!=ast.dump(b)];assert changed==[('FO','FO')]
 raw=pack(source);capture=[];exec(raw.decode(),{'exec':capture.append});assert capture==[source]
 (P/'guard-packed.py').write_bytes(raw)
 d={'scope':'Exact original d4558r1 encoder and TRAIN stub; all-path guard artifact unchanged','parent_and_H4_exact_repack':True,'only_changed_function_vs_H4':changed,'decoded_sha256':sha(source.encode()),'packed_bytes':len(raw),'packed_sha256':sha(raw),'limit_bytes':65536,'headroom':65536-len(raw),'under_limit':len(raw)<=65536,'decode_roundtrip':True}
 (P/'build-result.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
if __name__=='__main__':main()
