"""Independent format/oracle/native checks for experimental minimum-match3 packing."""
import ast,base64,hashlib,itertools,json,random
from pathlib import Path
import pydantic_monty as m
import lz3
HERE=Path(__file__).resolve().parent

def independent_decode(tokens):
    out=[];cursor=0;refs=[]
    while cursor<len(tokens):
        tag=tokens[cursor];cursor+=1
        if tag<128:
            assert cursor+tag+1<=len(tokens)
            out.extend(tokens[cursor:cursor+tag+1]);cursor+=tag+1
        else:
            assert cursor+2<=len(tokens)
            count=tag-125;distance=256*tokens[cursor]+tokens[cursor+1];cursor+=2
            assert 3<=count<=130 and count<=distance<=min(65535,len(out))
            begin=len(out)-distance
            for j in range(count):out.append(out[begin+j])
            refs.append((count,distance))
    return bytes(out),refs

def oracle(data):
    n=len(data);best=[0]*(n+1)
    for i in range(n-1,-1,-1):
        possibilities=[k+1+best[i+k] for k in range(1,min(128,n-i)+1)]
        for j in range(max(0,i-65535),i):
            for k in range(3,min(130,n-i,i-j)+1):
                if data[j:j+k]==data[i:i+k]:possibilities.append(3+best[i+k])
        best[i]=min(possibilities)
    return best[0]

randomizer=random.Random(20261022)
cases=[bytes(x) for n in range(12) for x in itertools.product(range(2),repeat=n)]
cases += [bytes(randomizer.randrange(5) for _ in range(randomizer.randrange(1,45))) for _ in range(160)]
for data in cases:
    encoded=lz3.encode(data);actual,refs=independent_decode(encoded)
    assert actual==lz3.decode(encoded)==data
    assert len(encoded)==oracle(data)
vectors=[bytes(range(256)),b'',b'abcabc',b'abcdABCDEFGHIJabcdabcdABCDEFGHIJ']
for n in [1,2,3,4,127,128,129,130,131,255,256,1024,2048]:
    vectors += [randomizer.randbytes(n),(b'abcde'*((n+4)//5))[:n],bytes([0])*n]
boundary=b'abcdefg'+randomizer.randbytes(65528)+b'abcdefg'
vectors.append(boundary);reference_counts=0;longest=0;three=0
for data in vectors:
    encoded=lz3.encode(data);actual,refs=independent_decode(encoded)
    assert actual==lz3.decode(encoded)==data
    reference_counts+=len(refs);longest=max([longest]+[o for n,o in refs]);three+=sum(n==3 for n,o in refs)
assert longest==65535
for invalid in [b'\x00',b'\x80',b'\x80\x00',b'\x80\x00\x03',b'\x02abc\x80\x00\x02']:
    try:lz3.decode(invalid)
    except ValueError:pass
    else:raise AssertionError(invalid)
artifacts=[]
for name in ['inventory','sku-definition-only']:
    packed=(HERE/(name+'-packed.py')).read_text();payload=ast.parse(packed).body[-1].value.args[0].args[0].value
    raw,refs=independent_decode(base64.b85decode(payload))
    three+=sum(n==3 for n,o in refs)
    source=(HERE.parent/('2026-10-22-inventory-integration/prepack.py' if name=='inventory' else '2026-10-22-sku-evidence-review/size-only-prepack.py')).read_bytes()
    assert raw==source
    decoder=packed[:packed.index('exec(_lz(')]+'\nprint(_lz(payload))'
    output=[]
    with m.Monty() as engine:
        with engine.checkout() as session:session.feed_run(decoder,inputs={'payload':payload},print_callback=lambda *a:output.append(a))
    text=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in output)
    assert text==source.decode()+'\n'
    artifacts.append(dict(name=name,bytes=len(packed.encode()),sha256=hashlib.sha256(packed.encode()).hexdigest(),exact_native_decode=True))
assert three>0
result=dict(status='passed',oracle_inputs=len(cases),roundtrip_vectors=len(vectors),checked_references=reference_counts,
            length3_references=three,maximum_distance=longest,malformed_streams_rejected=5,artifacts=artifacts,
            limits='Build-time window-bounded shortest-byte parse. New decoder format; do not use LZ4 runtime on LZ3 streams. Runtime stub trusts build-validated payload. No model/evaluation claim.')
(HERE/'codec-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
