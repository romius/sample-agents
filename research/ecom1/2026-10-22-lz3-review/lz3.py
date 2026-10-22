"""Experimental LZ3 format: match lengths3..130; independent of old LZ4 decoder.

Extends romius minimum-byte parser / bobcat LZ format. Literal tokens remain
0..127 with1..128 bytes; reference tokens128..255 now mean3..130 bytes plus
unsigned16-bit distance. Nonoverlap remains required. Do not decode with LZ4.
"""
import base64
MIN_MATCH=3
MAX_MATCH=130
STUB=('import base64\n'
 'def _lz(s):\n'
 ' t=base64.b85decode(s);o=[];i=0;n=len(t)\n'
 ' while i<n:\n'
 '  c=t[i];i+=1\n'
 '  if c<128:\n'
 '   o.extend(t[i:i+c+1]);i+=c+1\n'
 '  else:\n'
 '   p=len(o)-((t[i]<<8)|t[i+1]);i+=2;o.extend(o[p:p+c-125])\n'
 ' return "".join(chr(x) for x in o)\n'
 'exec(_lz("%s"))\n')

def encode(data,window=4096):
    n=len(data);table={};matches=[]
    for i in range(n):
        best=0;offset=0
        if i+MIN_MATCH<=n:
            key=data[i:i+MIN_MATCH]
            for previous in reversed(table.get(key,[])[-window:]):
                distance=i-previous
                if distance>65535:break
                if distance<MIN_MATCH:continue
                length=MIN_MATCH;limit=min(MAX_MATCH,n-i,distance)
                while length<limit and data[previous+length]==data[i+length]:length+=1
                if length>best:best=length;offset=distance
                if length==min(MAX_MATCH,n-i):break
            table.setdefault(key,[]).append(i)
        matches.append((best,offset))
    cost=[0]*(n+1);choice=[None]*n
    for i in range(n-1,-1,-1):
        best=n*2+1;selected=None
        for length in range(1,min(128,n-i)+1):
            total=1+length+cost[i+length]
            if total<=best:best=total;selected=(length,0)
        match,offset=matches[i]
        for length in range(MIN_MATCH,match+1):
            total=3+cost[i+length]
            if total<=best:best=total;selected=(length,offset)
        cost[i]=best;choice[i]=selected
    out=bytearray();i=0
    while i<n:
        length,offset=choice[i]
        if offset:out.extend([128+length-MIN_MATCH,offset>>8,offset&255])
        else:out.append(length-1);out.extend(data[i:i+length])
        i+=length
    assert len(out)==cost[0]
    return bytes(out)

def decode(data):
    output=bytearray();i=0
    while i<len(data):
        control=data[i];i+=1
        if control<128:
            length=control+1
            if i+length>len(data):raise ValueError('truncated literal')
            output.extend(data[i:i+length]);i+=length
        else:
            if i+2>len(data):raise ValueError('truncated reference')
            length=control-128+MIN_MATCH;distance=int.from_bytes(data[i:i+2],'big');i+=2
            if not length<=distance<=len(output):raise ValueError('invalid nonoverlapping reference')
            start=len(output)-distance;output.extend(output[start:start+length])
    return bytes(output)

def pack(source):
    compile(source,'<LZ3 source>','exec')
    raw=source.encode('ascii');encoded=encode(raw)
    assert decode(encoded)==raw
    return STUB%base64.b85encode(encoded).decode()
