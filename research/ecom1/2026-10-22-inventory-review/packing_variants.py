from pathlib import Path
import ast,json,runpy,hashlib,time
p=Path(__file__).resolve().parent
base=p.parent/'2026-10-22-record-integration';template=(base/'pack5h.py').read_text();packer=runpy.run_path(str(p/'lzpack_longest.py'));source=(p/'packing-probe/readable.py').read_text();result={}
for name,locals_,globals_,hoist in [('no_rename',False,False,False),('locals_only',True,False,False),('all_no_hoist',True,True,False),('globals_only',False,True,False)]:
 s=template.replace('rename_locals=True','rename_locals='+str(locals_)).replace('rename_globals=True','rename_globals='+str(globals_)).replace('hoist_literals=True','hoist_literals='+str(hoist));ns={'__name__':'probe'};exec(s,ns)
 variant=ns['mini'](source);portable=variant.encode('ascii','backslashreplace').decode();assert ast.dump(ast.parse(portable))==ast.dump(ast.parse(variant));packed=packer['pack'](portable,lazy=True)
 (p/'packing-probe'/(name+'-prepack.py')).write_text(portable);(p/'packing-probe'/(name+'-agent.py')).write_text(packed)
 result[name]={'bytes':len(packed.encode()),'headroom':65536-len(packed.encode()),'sha256':hashlib.sha256(packed.encode()).hexdigest(),'locals':locals_,'globals':globals_,'hoist':hoist}
 print(name,result[name],flush=True)
(p/'packing-variants.json').write_text(json.dumps(result,indent=2)+'\n')
