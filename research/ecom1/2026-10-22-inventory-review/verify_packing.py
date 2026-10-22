"""Check the encoder's early-stop correction without changing the runtime decoder."""
import ast,base64,hashlib,json,random,runpy
from pathlib import Path
import pydantic_monty as monty
HERE=Path(__file__).resolve().parent
old=runpy.run_path(str(HERE/'upstream/lzpack_r3'))
new=runpy.run_path(str(HERE/'lzpack_longest.py'))
assert new['STUB']==old['STUB']
assert ast.dump(ast.parse(new['STUB']%'AAAA'))==ast.dump(ast.parse(old['STUB']%'AAAA'))
data=b'abcdABCDEFGHIJabcdabcdABCDEFGHIJ'
assert old['_best'](data,{b'abcd':[0,14]},18,len(data),4096)==(4,4)
assert new['_best'](data,{b'abcd':[0,14]},18,len(data),4096)==(14,18)
rng=random.Random(7119)
samples=[b'',b'a',bytes(range(256)),b'a'*2000,data,b'abcd'*600]
for _ in range(60):
    pieces=[bytes(rng.randrange(256) for _ in range(rng.randrange(1,90))) for _ in range(5)]
    samples.append(b''.join(rng.choice(pieces) for _ in range(rng.randrange(1,90))))
for sample in samples:
    for lazy in [False,True]:
        token=new['encode'](sample,lazy)
        assert new['decode'](token)==old['decode'](token)==sample
results={'counterexample':{'old_match':4,'longest_match':14},'roundtrip_samples':len(samples),'modes':2,'stub_unchanged':True,'sources':{}}
for name,folder in [('d4955','2026-10-22-clarification-integration'),('d4702','2026-10-22-record-integration')]:
    original=(HERE.parent/folder/'agent.py').read_text()
    scope={};exec(original[:original.index('exec(_lz(')],scope)
    payload=ast.parse(original).body[-1].value.args[0].args[0].value
    decoded=scope['_lz'](payload)
    packed=new['pack'](decoded,lazy=True)
    new_payload=ast.parse(packed).body[-1].value.args[0].args[0].value
    assert old['decode'](base64.b85decode(new_payload)).decode('ascii')==decoded
    assert ast.dump(ast.parse(decoded))==ast.dump(ast.parse((HERE.parent/folder/'readable.py').read_text()))
    prefix=packed[:packed.index('exec(_lz(')]
    with monty.Monty() as pool:
        with pool.checkout() as session:
            session.feed_run(prefix+'\nassert _lz(payload)==expected\n',inputs={'payload':new_payload,'expected':decoded})
    (HERE/'packing-probe'/(name+'-same-source-agent.py')).write_text(packed)
    results['sources'][name]={'old_bytes':len(original.encode()),'new_bytes':len(packed.encode()),
        'saved_bytes':len(original.encode())-len(packed.encode()),'sha256':hashlib.sha256(packed.encode()).hexdigest(),
        'native_decoded_bytes_equal':True,'readable_ast_equal':True}
results['limits']='Encoder-only component, no submission or replacement of pending sources. Native exact decoder bytes checked; full-agent control flow does not change. Longest-match correction need not minimize globally packed size for every input.'
(HERE/'packing-verification.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
