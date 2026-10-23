import pydantic_monty as m, json, ast
src=open('cand_h4g2_dec.py').read()
t=ast.parse(src)
want={'FO','rf_drop1','n'}
segs=[ast.get_source_segment(src,x) for x in t.body if isinstance(x,ast.FunctionDef) and x.name in want]
w=json.load(open('../s98/arch/t063/world.json'));pr=[]
for p,f in w['files'].items():
    if p.startswith('/proc/catalog/'):
        j=json.loads(f['content']);pr.append({'sku':j['sku'],'price_cents':j['price_cents']})
cases=[["PT-SAW-AK-DHS680-5.",42990],["PT-MOW-STI-RMA235-A.",38990],["PT-IT-BO5-CYL9-12",3490],["PT-BLA-BOS-EXPWOOD-.",4490]]
fx=[[{'sku':'PT-DRL-MAXK-ABCDEFGH','price_cents':100},{'sku':r,'price_cents':p}] for r,p in [('PT-DRL-MAK-ABCDEFGH',101),('PT-DRL-MAK-ABCDGFGH',100),('PT-DRL-MAK-ABCDGFGH',101)]]+[[{'sku':'PT-DRL-MAXK-ABCDEFGH','price_cents':100}]]
code="C=''\nD=str\nEV="+json.dumps({"O":"0","Q":"0","I":"1","L":"1","|":"1","S":"5","B":"8","Z":"2"})+"\nA=None\n"+"\n".join(segs)+"\nX={'products':"+json.dumps(pr)+"}\nfor f,c in "+json.dumps(cases)+":\n    r=FO(f,c)\n    print(f, r and r['sku'])\nfor P in "+json.dumps(fx)+":\n    X={'products':P}\n    r=FO('PT-DRL-MAK-ABCDEF.',100)\n    print(len(P), r and r['sku'])\n"
with m.Monty() as pool:
    with pool.checkout() as s:
        out=[]
        r=s.feed_run(code, print_callback=lambda *a: out.append(a))
        for o in out: print(o)
