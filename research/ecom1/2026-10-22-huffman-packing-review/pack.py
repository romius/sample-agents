"""Canonical Huffman coding of the pinned LZ4 stream; pure Monty runtime.

Header: uint32 decoded token count, then256 uint8 code lengths. Canonical codes
are assigned by (length,symbol), MSB first, trailing bits padded with zeros.
The existing bobcat/romius LZ4 token format and decode loop remain unchanged.
"""
import base64,collections,heapq,runpy
from pathlib import Path
PARENT=Path(__file__).resolve().parent.parent/'2026-10-22-inventory-integration'
codec=runpy.run_path(str(PARENT/'lzpack_dp.py'))

HUFFMAN=''' b=base64.b85decode(s);count=b[0]*16777216+b[1]*65536+b[2]*256+b[3];table={};code=0;previous=0
 for length,symbol in sorted((v,k) for k,v in enumerate(b[4:260]) if v):
  code=code<<(length-previous);table[length,code]=symbol;code+=1;previous=length
 t=[];value=0;width=0
 for byte in b[260:]:
  for shift in range(7,-1,-1):
   value=value*2+((byte>>shift)&1);width+=1
   if (width,value) in table:
    t.append(table[width,value]);value=0;width=0
    if len(t)==count:break
  if len(t)==count:break
 o=[];i=0;n=len(t)'''
OLD_LINE=' t=base64.b85decode(s);o=[];i=0;n=len(t)'
assert codec['STUB'].count(OLD_LINE)==1
STUB=codec['STUB'].replace(OLD_LINE,HUFFMAN)

def lengths_for(data):
    counts=collections.Counter(data)
    heap=[(n,s,s) for s,n in counts.items()];heapq.heapify(heap)
    if len(heap)==1:return {heap[0][1]:1}
    while len(heap)>1:
        a=heapq.heappop(heap);b=heapq.heappop(heap)
        heapq.heappush(heap,(a[0]+b[0],min(a[1],b[1]),(a[2],b[2])))
    lengths={}
    def visit(node,depth):
        if isinstance(node,int):lengths[node]=depth
        else:visit(node[0],depth+1);visit(node[1],depth+1)
    if heap:visit(heap[0][2],0)
    return lengths

def canonical(lengths):
    codes={};code=0;previous=0
    for length,symbol in sorted((v,k) for k,v in lengths.items()):
        code<<=length-previous
        if length<1 or length>255 or code>=(1<<length):raise ValueError('invalid Huffman lengths')
        codes[symbol]=(code,length);code+=1;previous=length
    return codes

def huffman_encode(data):
    if len(data)>=2**32:raise ValueError('token length')
    lengths=lengths_for(data);codes=canonical(lengths)
    result=bytearray(len(data).to_bytes(4,'big')+bytes(lengths.get(s,0) for s in range(256)))
    value=0;width=0
    for symbol in data:
        code,length=codes[symbol];value=(value<<length)|code;width+=length
        while width>=8:
            width-=8;result.append((value>>width)&255)
        value&=(1<<width)-1
    if width:result.append(value<<(8-width))
    return bytes(result)

def huffman_decode(data):
    if len(data)<260:raise ValueError('truncated Huffman header')
    count=int.from_bytes(data[:4],'big')
    lengths={s:l for s,l in enumerate(data[4:260]) if l}
    codes=canonical(lengths);table={(length,code):symbol for symbol,(code,length) in codes.items()}
    if count and not table:raise ValueError('empty codebook')
    if count==0:
        if data[260:]:raise ValueError('unexpected empty stream payload')
        return b''
    out=bytearray();value=0;width=0
    for i,byte in enumerate(data[260:]):
        for shift in range(7,-1,-1):
            value=(value<<1)|((byte>>shift)&1);width+=1
            if (width,value) in table:
                out.append(table[width,value]);value=0;width=0
                if len(out)==count:
                    if byte&((1<<shift)-1) or i!=len(data)-261:raise ValueError('extra bits/bytes')
                    return bytes(out)
            elif width>=max(lengths.values()):raise ValueError('unknown Huffman code')
    raise ValueError('truncated Huffman data')

def pack(source):
    compile(source,'<Huffman LZ4 source>','exec')
    raw=source.encode('ascii');tokens=codec['encode'](raw);encoded=huffman_encode(tokens)
    assert huffman_decode(encoded)==tokens and codec['decode'](tokens)==raw
    return STUB%base64.b85encode(encoded).decode()
