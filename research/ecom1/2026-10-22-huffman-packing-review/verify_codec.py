"""Independent prefix-tree decoding and optimal small-alphabet costs, native decode."""
import ast,base64,collections,hashlib,itertools,json,random,time
from pathlib import Path
import pydantic_monty as m
import pack
HERE=Path(__file__).resolve().parent

def tree_decode(data):
    assert len(data)>=260
    count=sum(data[i]*(256**(3-i)) for i in range(4))
    if not count:return b''
    ordered=sorted((n,c) for c,n in enumerate(data[4:260]) if n)
    root={};number=0;previous=0
    for width,symbol in ordered:
        number*=2**(width-previous);assert number<2**width
        digits=bin(number)[2:].zfill(width);node=root
        for digit in digits:
            assert 'symbol' not in node
            node=node.setdefault(digit,{})
        assert not node;node['symbol']=symbol;number+=1;previous=width
    decoded=[];node=root
    for byte in data[260:]:
        for digit in bin(byte)[2:].zfill(8):
            assert digit in node
            node=node[digit]
            if 'symbol' in node:
                decoded.append(node['symbol']);node=root
                if len(decoded)==count:return bytes(decoded)
    raise AssertionError('incomplete stream')

rng=random.Random(20261022)
vectors=[b'',bytes(range(256)),bytes(range(255,-1,-1))*10]
vectors += [bytes([i])*n for i in range(256) for n in [1,9]]
vectors += [rng.randbytes(n) for n in [1,2,7,8,9,31,32,33,127,128,129,1024,4096,65535]]
vectors += [bytes(rng.randrange(k) for _ in range(n)) for k in [2,3,7,16,64] for n in [3,16,129,1500]]
for data in vectors:
    encoded=pack.huffman_encode(data)
    assert tree_decode(encoded)==pack.huffman_decode(encoded)==data
    assert pack.huffman_encode(data)==encoded
# Independent finite prefix-length cost minimization for every small frequency triple.
optimal=0
for counts in itertools.product(range(1,5),repeat=3):
    data=b''.join(bytes([i])*count for i,count in enumerate(counts))
    lengths=pack.lengths_for(data);cost=sum(counts[i]*lengths[i] for i in range(3))
    minimum=min(sum(c*l for c,l in zip(counts,lengths)) for lengths in itertools.product(range(1,4),repeat=3)
                if sum(2**(3-l) for l in lengths)<=8)
    assert cost==minimum;optimal+=1
malformed=[b'',bytes(259),bytes([0,0,0,1])+bytes(256),pack.huffman_encode(b'abc')[:-1],pack.huffman_encode(b'abc')+b'\x00']
oversubscribed=bytearray(260);oversubscribed[3]=1;oversubscribed[4:7]=b'\x01\x01\x01';malformed.append(bytes(oversubscribed)+b'\x00')
for data in malformed:
    try:pack.huffman_decode(data)
    except ValueError:pass
    else:raise AssertionError('malformed accepted')
artifacts=[]
for label in ['inventory','sku-definition-only']:
    source=(HERE/(label+'-packed.py')).read_text()
    payload=ast.parse(source).body[-1].value.args[0].args[0].value
    tokens=tree_decode(base64.b85decode(payload))
    decoded=pack.codec['decode'](tokens)
    expected=(HERE.parent/('2026-10-22-inventory-integration/prepack.py' if label=='inventory' else '2026-10-22-sku-evidence-review/size-only-prepack.py')).read_bytes()
    assert decoded==expected
    out=[];program=source[:source.index('exec(_lz(')]+'\nprint(_lz(payload))'
    started=time.monotonic()
    with m.Monty() as engine:
        with engine.checkout() as session:session.feed_run(program,inputs={'payload':payload},print_callback=lambda *a:out.append(a))
    elapsed=time.monotonic()-started
    text=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in out)
    assert text==expected.decode()+'\n'
    artifacts.append(dict(label=label,bytes=len(source.encode()),source_sha256=hashlib.sha256(source.encode()).hexdigest(),
           token_bytes=len(tokens),native_decode_seconds=round(elapsed,4),exact_native_decode=True))
result=dict(status='passed',roundtrip_vectors=len(vectors),optimal_cost_oracles=optimal,malformed_streams_rejected=len(malformed),artifacts=artifacts,
  limits='No paid run. Native decoder consumes only build-validated self-contained payload. Timings are local single observations, not runtime latency guarantees. Header overhead can enlarge small inputs. New outer Huffman format with unchanged inner LZ4.')
(HERE/'codec-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
