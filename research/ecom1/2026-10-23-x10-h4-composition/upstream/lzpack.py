"""bobcat lzpack: LZ77 self-extracting packer for Monty agents (exec-based).
Token stream (bytes): c<128 -> literal run of c+1 bytes; c>=128 -> match len (c-128)+4, then 2-byte big-endian offset (1..65535).
Payload is base85 text; stub decodes with base64 + list ops and exec()s the source in the module scope.
r2 (2026-10-22, bobcat): optional --lazy = one-step lazy matching + 4096-candidate window. Same token format,
same stub/decoder (packed files from r1 and r2 decode the same way). Default (no flag) is byte-identical to r1."""
import base64,sys
MINM=4; MAXM=127+4
def _best(data,table,i,n,win):
    best=0;bo=0
    if i+MINM<=n:
        for p in reversed(table.get(data[i:i+MINM],[])[-win:]):
            off=i-p
            if off>65535: break
            if off<MINM: continue
            L=MINM
            lim=min(MAXM,n-i,off)  # no overlap
            while L<lim and data[p+L]==data[i+L]: L+=1
            if L>best: best=L;bo=off
            if L==lim: break
    return best,bo
def encode(data:bytes,lazy:bool=False)->bytes:
    if lazy: return encode_lazy(data)
    n=len(data); out=bytearray(); lit=bytearray(); i=0
    table={}
    def flush():
        nonlocal lit
        while lit:
            ch=lit[:128]; out.append(len(ch)-1); out.extend(ch); lit=lit[128:]
    while i<n:
        best=0;bo=0
        if i+MINM<=n:
            key=data[i:i+MINM]
            cands=table.get(key,[])
            for p in reversed(cands[-256:]):
                off=i-p
                if off>65535: break
                if off<MINM: continue
                L=MINM
                lim=min(MAXM,n-i,off)  # no overlap
                while L<lim and data[p+L]==data[i+L]: L+=1
                if L>best: best=L;bo=off
                if L==lim: break
        if best>=MINM:
            flush(); out.append(128+best-MINM); out.append(bo>>8); out.append(bo&255)
            for k in range(i,i+best):
                if k+MINM<=n: table.setdefault(data[k:k+MINM],[]).append(k)
            i+=best
        else:
            if i+MINM<=n: table.setdefault(data[i:i+MINM],[]).append(i)
            lit.append(data[i]); i+=1
    flush(); return bytes(out)
def encode_lazy(data:bytes,win:int=4096)->bytes:
    """Emit a literal instead of the match at i when the match at i+1 is >=2 bytes longer."""
    n=len(data); out=bytearray(); lit=bytearray(); i=0
    table={}
    def flush():
        nonlocal lit
        while lit:
            ch=lit[:128]; out.append(len(ch)-1); out.extend(ch); lit=lit[128:]
    while i<n:
        best,bo=_best(data,table,i,n,win)
        if best>=MINM and best<MAXM and i+1+MINM<=n and _best(data,table,i+1,n,win)[0]>best+1: best=0
        if best>=MINM:
            flush(); out.append(128+best-MINM); out.append(bo>>8); out.append(bo&255)
            for k in range(i,i+best):
                if k+MINM<=n: table.setdefault(data[k:k+MINM],[]).append(k)
            i+=best
        else:
            if i+MINM<=n: table.setdefault(data[i:i+MINM],[]).append(i)
            lit.append(data[i]); i+=1
    flush(); return bytes(out)
def decode(tok:bytes)->bytes:
    o=[]; i=0; n=len(tok)
    while i<n:
        c=tok[i]; i+=1
        if c<128: o.extend(tok[i:i+c+1]); i+=c+1
        else:
            L=c-128+MINM; off=(tok[i]<<8)|tok[i+1]; i+=2; p=len(o)-off; o.extend(o[p:p+L])
    return bytes(o)
STUB=('import base64\n'
 'def _lz(s):\n'
 ' t=base64.b85decode(s);o=[];i=0;n=len(t)\n'
 ' while i<n:\n'
 '  c=t[i];i+=1\n'
 '  if c<128:\n'
 '   o.extend(t[i:i+c+1]);i+=c+1\n'
 '  else:\n'
 '   p=len(o)-((t[i]<<8)|t[i+1]);i+=2;o.extend(o[p:p+c-124])\n'
 ' return "".join(chr(x) for x in o)\n'
 'exec(_lz("%s"))\n')
def pack(src:str,lazy:bool=False)->str:
    data=src.encode('latin-1')  # require ASCII/latin-1 source
    tok=encode(data,lazy); assert decode(tok)==data
    return STUB%base64.b85encode(tok).decode()
if __name__=='__main__':
    lazy='--lazy' in sys.argv; args=[a for a in sys.argv[1:] if a!='--lazy']
    src=open(args[0]).read()
    try: src.encode('latin-1')
    except UnicodeEncodeError: print('non-latin1 chars present; escape them first'); sys.exit(1)
    p=pack(src,lazy); open(args[1],'w').write(p)
    print('in %d B -> out %d B (ratio %.2f)'%(len(src.encode()),len(p.encode()),len(src.encode())/len(p.encode())))
