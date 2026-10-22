"""Native method-only-host checks of exact isolated definitions, not whole-agent validation."""
import ast,hashlib,json,platform
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent
src=(P/'upstream/readable.py').read_text();tree=ast.parse(src)
names={'i2c_cleanup','i2c_guard_dirs','i2c_diam_of','crosslist_text','crosslist_uint','crosslist_parse_ocr'}
code='import re\n'+ '\n\n'.join(ast.get_source_segment(src,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names)+'\n'
limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
ocr=next(json.loads(l)['data']['response']['content'] for l in (P/'responses-t076.jsonl').read_text().splitlines() if json.loads(l)['seq']==10098)
request='Please clean out every temporary file under /tmp/review. Delete all files there and nothing else. Return only the deleted paths, one per line, sorted alphabetically.'
class Host:
    def __init__(self,fail):self.fail=fail;self.calls=[];self.results=[]
    def call(self,method,args):
        self.calls.append([method,args])
        if method=='List':return {'entries':[{'name':n,'path':'/tmp/review/'+n,'kind':'NODE_KIND_FILE'} for n in ['a.txt','b.txt']]}
        assert method=='Delete'
        if self.fail and args['path'].endswith('b.txt'):raise RuntimeError('BitGN HTTP 404: {"code":"not_found","message":"delete failed: not found"}')
        return {}
    def record(self,result):self.results.append(result);return {}
rows=[]
cases=[('cleanup_success',False,'bitgn.record(i2c_cleanup(request))',{}),('cleanup_partial',True,'bitgn.record(i2c_cleanup(request))',{}),
 ('negative_diameter',False,'bitgn.record(i2c_diam_of("outside 190mm listing"))',{}),
 ('original_ocr',False,'try:\n r=crosslist_parse_ocr(ocr)\nexcept ValueError as e:\n r={"error":str(e)}\nbitgn.record(r)',{'ocr':ocr}),
 ('single_prefix_removed',False,'bitgn.record(crosslist_parse_ocr(ocr))',{'ocr':ocr.replace('## scanline ##  Total requested units:','Total requested units:')})]
with m.Monty() as pool:
    for label,fail,body,extra in cases:
        h=Host(fail)
        with pool.checkout(limits=limits) as session:
            session.feed_run(code+body,inputs={'bitgn':m.ClassInstance(h,allowed_methods={'call','record'}),'request':request,**extra},print_callback=lambda *a:None)
        assert len(h.results)==1
        rows.append({'case':label,'calls':h.calls,'result':h.results[0]})
assert rows[0]['result']['message']=='/tmp/review/a.txt\n/tmp/review/b.txt'
assert rows[1]['result']['message']=='/tmp/review/a.txt' and rows[1]['result']['outcome']=='OUTCOME_OK'
assert rows[2]['result']==(None,190)
assert rows[3]['result']['error']=='OCR must identify one branch and both complete totals'
assert len(rows[4]['result']['lines'])==5
out={'python':platform.python_version(),'monty':'1.2.0','record_readable_sha256':hashlib.sha256(src.encode()).hexdigest(),'limits':limits,'scope':__doc__,'checks':rows,'real_sdk_calls':0,'model_calls':0}
(P/'native-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':'passed','checks':len(rows)}))
