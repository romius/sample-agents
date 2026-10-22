from pathlib import Path
import hashlib,json,runpy,time
HERE=Path(__file__).resolve().parent
fixed=runpy.run_path(str(HERE/'lzpack_longest.py'));old=runpy.run_path(str(HERE/'upstream/lzpack_r3'))
data=b'abcdABCDEFGHIJabcdabcdABCDEFGHIJ';i=18;table={b'abcd':[0,14]}
assert old['_best'](data,table,i,len(data),4096)[0]==4 and fixed['_best'](data,table,i,len(data),4096)[0]==14
result={}
for name in ['ast_only','record_minifier']:
 source=(HERE/'packing-probe'/(name+'-prepack.py')).read_text();start=time.monotonic();packed=fixed['pack'](source,lazy=True)
 (HERE/'packing-probe'/(name+'-longest-agent.py')).write_text(packed)
 result[name]={'bytes':len(packed.encode()),'headroom':65536-len(packed.encode()),'sha256':hashlib.sha256(packed.encode()).hexdigest(),'seconds':round(time.monotonic()-start,3)}
 print(name,result[name],flush=True)
result['matching_counterexample']={'old_length':4,'new_length':14,'data':data.decode(),'offset':i}
(HERE/'longest-packing-results.json').write_text(json.dumps(result,indent=2)+'\n')
