import json
from ns import namespace
V=['base','t1','cx','m1','m3']
NS={v:namespace(v+'.py') for v in V}
def receipt(layout,qty="5",unit="10.00",total="50.00",subtotal="50.00",sku="PT-REVIEW-HAMMER",label="Subtotal"):
    head="Review City Center\n"
    if layout=="A": row=qty+" Review Hammer "+total+"\nArt.Nr "+sku+"\nEinzelpreis EUR "+unit
    elif layout=="B": row="[1] "+qty+" Review Hammer "+unit+" "+total+"\nClerk No: "+sku
    else: row="Item Qty Unit Total\nReview Hammer "+qty+" "+unit+" "+total+"\nSKU "+sku
    return head+row+"\n"+label+" "+subtotal
res={}
def tally(name,fn):
    r={}
    for v in V:
        ok=0;tot=0;bad=[]
        for case,exp in fn():
            tot+=1;got=NS[v]['DM'](case)
            if got==exp: ok+=1
            else: bad.append((case[-60:],got))
        r[v]=f"{ok}/{tot}"
        if bad and len(bad)<=3: r[v]+=' bad:'+repr(bad)[:300]
    res[name]=r
EVM={'O':'0','Q':'0','I':'1','L':'1','|':'1','S':'5','B':'8','Z':'2'}
def clean():
    for L in 'ABC':
        for q in range(1,100):
            a=str(q*10)+'.00'; yield receipt(L,str(q),total=a,subtotal=a),[(q,1000,'PT-REVIEW-HAMMER')]
def ocr(letter,digit):
    def g():
        for L in 'ABC':
            for q in range(1,100):
                t=str(q)
                if digit not in t: continue
                a=str(q*10)+'.00'; yield receipt(L,t.replace(digit,letter),total=a,subtotal=a),[(q,1000,'PT-REVIEW-HAMMER')]
    return g
tally('clean 1..99 x3 layouts',clean)
for l,d in [('S','5'),('B','8'),('Z','2'),('O','0'),('Q','0'),('L','1')]: tally(f'OCR {l}-for-{d}',ocr(l,d))
def labelfix():
    for L in 'AC':
        for q in [1,3,7]:
            a=str(q*10)+'.00'; yield receipt(L,str(q),total=a,subtotal=a,label='otal (exkl. MwSt)'),[(q,1000,'PT-REVIEW-HAMMER')]
tally('sin_g4 label "otal (exkl" (A,C)',labelfix)
def both():
    for L in 'AC':
        for q in [5,15,25]:
            a=str(q*10)+'.00'; yield receipt(L,str(q).replace('5','S'),total=a,subtotal=a,label='otal (exkl. MwSt)'),[(q,1000,'PT-REVIEW-HAMMER')]
tally('label fix + S-qty together',both)
amb="ITEM QTY UNIT TOTAL\nWIDGET S 10.00 50.00 2 25.00 50.00\nSKU PT-ABCD-1234\nSubtotal 50.00"
tally('codex adversarial: "WIDGET S" description',lambda:[(amb,[(2,2500,'PT-ABCD-1234')])])
mixed=amb.replace("Subtotal 50.00","Gadget S 1.00 5.00\nSKU PT-WXYZ-5678\nSubtotal 55.00")
tally('codex adversarial: mixed rows',lambda:[(mixed,[(2,2500,'PT-ABCD-1234'),(5,100,'PT-WXYZ-5678')])])
note="ITEM QTY UNIT TOTAL\nReview Hammer 1 10.00 10.00\nSKU PT-REVIEW-HAMMER\nNote S 1.00 5.00\nSubtotal 10.00"
tally('codex adversarial: "Note S" line',lambda:[(note,[(1,1000,'PT-REVIEW-HAMMER')])])
# extra adversarial with R6 letters in descriptions
def descletters():
    for w in ['BOSCH B','MAKITA Z','KIT O','DRILL L','SET Q']:
        t=f"ITEM QTY UNIT TOTAL\n{w} 10.00 20.00 2 10.00 20.00\nSKU PT-ABCD-1234\nSubtotal 20.00"
        yield t,[(2,1000,'PT-ABCD-1234')]
tally('desc ends with OCR letter + prices (layout C)',descletters)
arch=json.load(open('../src/archived_t043.txt'))
print(type(arch), list(arch)[:5] if isinstance(arch,dict) else '')
json.dump(res,open('tests_out.json','w'),indent=1)
for k,r in res.items(): print(k, r)
