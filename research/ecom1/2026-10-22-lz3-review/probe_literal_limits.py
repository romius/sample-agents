"""Explore token allocation with pinned LZ3 encoder; save every exact probe/hash."""
import hashlib,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-inventory-integration'
TEMPLATE=(HERE/'lz3.py').read_text()
def codec(literal_limit):
    assert literal_limit in [16,32,48,64,96,128]
    code=TEMPLATE.replace('MAX_MATCH=130','MAX_MATCH='+str(258-literal_limit))
    code=code.replace('128',str(literal_limit)).replace('p+c-125','p+c-'+str(literal_limit-3))
    scope={'__name__':'token_probe'};exec(code,scope)
    return scope,code

def main():
    source=(BASE/'prepack.py').read_text();rows=[]
    for limit in [16,32,48,64,96,128]:
        start=time.monotonic();scope,code=codec(limit);packed=scope['pack'](source)
        (HERE/('literal-'+str(limit)+'-packed.py')).write_text(packed)
        rows.append(dict(literal_limit=limit,max_match=258-limit,bytes=len(packed.encode()),seconds=round(time.monotonic()-start,3),
           sha256=hashlib.sha256(packed.encode()).hexdigest()))
    (HERE/'literal-limit-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
