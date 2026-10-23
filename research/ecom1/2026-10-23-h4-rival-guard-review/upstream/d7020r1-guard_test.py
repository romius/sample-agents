import json,random,sys
sys.path.insert(0,'../s92')
from load import load
A=load('../s97/cand_dec.py');B=load('../s98/cand_h4_dec.py');G=load('cand_h4g2_dec.py')
assert A['_bad']==0 and B['_bad']==0 and G['_bad']==0,(A['_bad'],B['_bad'],G['_bad'])
ARMS=[('rc7(d6855)',A),('rc7+H4',B),('rc7+H4+guard',G)]
def setp(pr):
    for _,g in ARMS: g['X']['products']=pr
def run(f,c):
    out=[]
    for _,g in ARMS:
        r=g['FO'](f,c); out.append(r['sku'] if r else None)
    return out
res={'fixtures':[],'held':[],'receipts':None,'robust':{},'cross':{}}
# romius d7000 neutral fixtures (as stated) + truncated-longer variants where H4 is the only path
fx=[]
for cand in ['PT-DRL-MAXK-ABCDEF','PT-DRL-MAXK-ABCDEFGH']:
    base=[{'sku':cand,'price_cents':100}]
    fx.append((f'{cand} alone',base))
    for r,p in [('PT-DRL-MAK-ABCDEF',101),('PT-DRL-MAK-ABCDGF',100),('PT-DRL-MAK-ABCDGF',101)]:
        rr=r if cand.endswith('DEF') else r+'GH'
        fx.append((f'{cand} + rival {rr}@{p}',base+[{'sku':rr,'price_cents':p}]))
        fx.append((f'{cand} + rival {rr}@{p} (rev order)',[{'sku':rr,'price_cents':p}]+base))
for name,pr in fx:
    setp(pr); o=run('PT-DRL-MAK-ABCDEF.',100); res['fixtures'].append([name,o]); print('FX',name,o)
# real archived worlds
for t,up in (('t023','hrNh9v44_receipt_ocr.txt'),('t063','AztYLH6h_receipt_ocr.txt')):
    w=json.load(open(f'../s98/arch/{t}/world.json'));text=open(f'../s98/arch/{t}/{up}').read()
    pr=[]
    for p,f in w['files'].items():
        if p.startswith('/proc/catalog/'):
            j=json.loads(f['content']);pr.append({'sku':j['sku'],'price_cents':j['price_cents']})
    setp(pr); it=G['DM'](text)
    rows=[run(f,c) for q,c,f in it]; res['held'].append([t,rows]); print('HELD',t,rows)
# old receipts
d=json.load(open('../s89/receipts.json')); cat=json.load(open('../s89/t023_catalog.json'))
setp([{'sku':s,'price_cents':p} for path,s,p in cat]); same=n=0
for k,(o,r) in d.items():
    if not r: continue
    it=G['DM'](r) or []
    rows=[run(f,c) for q,c,f in it]; n+=1; same+=all(x[1]==x[2] for x in rows)
res['receipts']=f'{same}/{n} identical H4 vs H4+guard'; print(res['receipts'])
# robustness on t063 catalog
setp(pr); prods=pr; random.seed(11)
conf={'0':'O','1':'I','5':'S','8':'B','2':'Z','O':'0','I':'1','S':'5','B':'8'}
def corrupt(s,k):
    s=list(s)
    for _ in range(k):
        op=random.choice(['del','sub','ocr']);i=random.randrange(len(s))
        if op=='del' and len(s)>8: del s[i]
        elif op=='sub': s[i]=random.choice('ABCDEFGHJKMNPRTUVWXY0123456789')
        else: s[i]=conf.get(s[i],s[i])
    return ''.join(s)
for k in (0,1,2):
  for cut in ('.','-',''):
    r={a:{'right':0,'wrong':0,'none':0} for a,_ in ARMS}
    for p in prods:
        for _ in range(20):
            s=p['sku']; L=random.randrange(max(10,len(s)-6),len(s)+1) if cut=='' else random.randrange(max(10,len(s)-6),len(s))
            f=corrupt(s[:L],k)+cut
            for (a,_),x in zip(ARMS,run(f,p['price_cents'])):
                r[a]['none' if x is None else 'right' if x==p['sku'] else 'wrong']+=1
    res['robust'][f'k{k}{cut or "full"}']=r; print('ROB',k,repr(cut),r)
# cross price: fragment of p with price of a different q
random.seed(5); r={a:{'wrong':0,'n':0} for a,_ in ARMS}
for _ in range(20000):
    p,q=random.sample(prods,2); s=p['sku']; L=random.randrange(max(10,len(s)-6),len(s))
    f=corrupt(s[:L],random.choice([0,1]))+'.'
    for (a,_),x in zip(ARMS,run(f,q['price_cents'])):
        r[a]['n']+=1; r[a]['wrong']+= (x is not None and x!=p['sku'])
res['cross']=r; print('CROSS',r)
json.dump(res,open('guard_test2.json','w'),indent=1)
