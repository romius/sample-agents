"""Minimum-token-cost parse over bounded LZ77 matches; unchanged bobcat runtime stub.

The build-time search uses the corrected longest-match finder from our pinned
d3268r3 review. Dynamic programming selects literal runs (1..128 bytes) and
non-overlapping references (4..131 bytes). Optimality is relative to the matches
found in the bounded candidate window, not every possible compression format.
"""
import base64,runpy
from pathlib import Path

UPSTREAM=Path(__file__).resolve().parent.parent/'2026-10-22-inventory-review/lzpack_longest.py'
codec=runpy.run_path(str(UPSTREAM))
STUB=codec['STUB']
decode=codec['decode']

def encode(data,window=4096):
    n=len(data);table={};matches=[]
    for i in range(n):
        matches.append(codec['_best'](data,table,i,n,window))
        if i+4<=n:table.setdefault(data[i:i+4],[]).append(i)
    cost=[0]*(n+1);choice=[None]*n
    for i in range(n-1,-1,-1):
        best=n*2+1;selected=None
        for length in range(1,min(128,n-i)+1):
            total=1+length+cost[i+length]
            if total<=best:best=total;selected=(length,0)
        match,offset=matches[i]
        for length in range(4,match+1):
            total=3+cost[i+length]
            if total<=best:best=total;selected=(length,offset)
        cost[i]=best;choice[i]=selected
    out=bytearray();i=0
    while i<n:
        length,offset=choice[i]
        if offset:
            out.extend([128+length-4,offset>>8,offset&255])
        else:
            out.append(length-1);out.extend(data[i:i+length])
        i+=length
    assert len(out)==cost[0]
    return bytes(out)

def pack(source):
    compile(source,'<source>','exec')
    data=source.encode('ascii');tokens=encode(data)
    assert decode(tokens)==data
    return STUB%base64.b85encode(tokens).decode()
