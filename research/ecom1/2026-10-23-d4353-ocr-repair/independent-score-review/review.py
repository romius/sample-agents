"""Independent bounded source/oracle/native review; never rebuild reports in parent."""
import ast,base64,copy,hashlib,importlib.metadata,json,runpy
from pathlib import Path
import pydantic_monty as m
P=Path(__file__).resolve().parent.parent;R=P/'replay';OUT=P/'independent-score-review'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def unpack(raw):
 tree=ast.parse(raw);call=tree.body[-1].value
 assert isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='exec'
 value=ast.literal_eval(call.args[0].args[0]);t=base64.b85decode(value);out=bytearray();i=0
 while i<len(t):
  c=t[i];i+=1
  if c<128:assert i+c+1<=len(t);out.extend(t[i:i+c+1]);i+=c+1
  else:
   assert i+2<=len(t);distance=(t[i]<<8)|t[i+1];i+=2;length=c-124
   assert 0<distance<=len(out) and length<=distance
   out.extend(out[len(out)-distance:len(out)-distance+length])
 return ''.join(map(chr,out))
parent=(P/'parent-readable.py').read_text();new=(P/'readable.py').read_text();pa=ast.parse(parent);ca=ast.parse(new)
oldfn=next(n for n in pa.body if isinstance(n,ast.FunctionDef) and n.name=='crosslist_parse_ocr')
newfn=next(n for n in ca.body if isinstance(n,ast.FunctionDef) and n.name=='crosslist_parse_ocr')
added=newfn.body.pop(1);assert isinstance(added,ast.Assign) and ast.unparse(added.targets[0])=='text'
assert ast.dump(pa)==ast.dump(ca)
line=new.splitlines(keepends=True)[added.lineno-1];assert new.count(line)==1 and new.replace(line,'',1)==parent
assert sha((P/'parent.py').read_bytes())=='588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e'
assert sha((P/'agent.py').read_bytes())=='420e904a4cb502221f8609f99bd0f62370deda775abb41b5be9880042f0b7bf8'
for packed,payload,readable in [('parent.py','parent-decoded.py','parent-readable.py'),('agent.py','portable.py','readable.py')]:
 decoded=unpack((P/packed).read_text());assert decoded==(P/payload).read_text()
 assert ast.dump(ast.parse(decoded))==ast.dump(ast.parse((P/readable).read_text()))
packer=runpy.run_path(str(P/'lzpack.py'))
assert packer['pack']((P/'parent-decoded.py').read_text(),lazy=True).encode()==(P/'parent.py').read_bytes()
assert packer['pack']((P/'portable.py').read_text(),lazy=True).encode()==(P/'agent.py').read_bytes()
# Derive child trees independently from the actual complete source Tree.
events={e['seq']:e for n in ['initial-rpc-responses.jsonl','remaining-rpc-responses.jsonl'] for e in [json.loads(l) for l in (R/n).read_bytes().splitlines()]}
source=events[10110]['data']['response']['root'];w=load(R/'world.json');treechecks=[]
def depth(n):return max([1+depth(c) for c in n.get('children',[])]+[0])
for root in ['/proc/catalog','/proc/locations']:
 child=next(x for x in source['children'] if x['name']==root.rsplit('/',1)[1]);d=depth(child);assert d==2
 actual=w['derived_rpc'][canon(['Tree',{'root':root,'level':3}])]
 assert actual['root']==child
 old=w['derived_rpc'][canon(['Tree',{'root':root,'level':0}])];assert actual==old
 treechecks.append({'root':root,'maximum_depth':d,'requested_depth':3,'exact_archived_child':True})
# Independently reproduce original oracle files in isolation, then compare LF-only adaptation.
import tempfile,shutil,subprocess,sys,os
with tempfile.TemporaryDirectory(prefix='ocr-port-oracle-') as td:
 td=Path(td)
 for q in R.iterdir():
  if q.is_file():shutil.copyfile(q,td/q.name)
 subprocess.run([sys.executable,str(td/'prepare_archived.py')],check=True,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 for n in ['expected.tsv','fresh-expected.tsv']:
  before=(td/n).read_bytes();after=(R/n).read_bytes();assert before.endswith(b'\n') and not before.endswith(b'\n\n') and before[:-1]==after
 for n in ['manual-oracle.json','fresh-manual-oracle.json']:assert (td/n).read_bytes()==(R/n).read_bytes()
# Check author ledger independently without claiming all112 rerun here.
ledger=load(R/'replay-results.json');rows=ledger['results'];assert len(rows)==112
assert len({(r['version'],r['form'],r['engine'],r['case']) for r in rows})==112
for r in rows:
 fn=r['version']+('-readable.py' if r['form']=='readable' else '.py')
 assert sha((R/'upstream'/fn).read_bytes())==r['source_sha256'] and not r['unmatched_calls']
for version in ['parent','candidate']:
 for case in {r['case'] for r in rows}:
  group=[r for r in rows if r['version']==version and r['case']==case];assert len(group)==4
  for k in ['rpc_calls','writes','answers','scripted_llm_calls','router_request_sha256']:
   assert all(r[k]==group[0][k] for r in group)
# Use the exact reviewed host prefix but run only four meaningful native packed cases.
src=(R/'replay.py').read_text();prefix=src.split('\nrows=[]',1)[0];ns={'__file__':str(R/'replay.py')};exec(compile(prefix,str(R/'replay.py'),'exec'),ns)
checks=[]
with m.Monty() as pool:
 for version,case in [('parent','original'),('candidate','original'),('candidate','fresh_two_row_noisy'),('candidate','contradictory_noisy')]:
  ocr=next(x[1] for x in ns['CASES'] if x[0]==case);host=ns['Host'](ocr)
  with pool.checkout(limits=ns['LIMITS']) as session:
   session.feed_run((R/'upstream'/(version+'.py')).read_text(),inputs={'bitgn':m.ClassInstance(host,allowed_methods={'task','call','answer','llm','usage'})},print_callback=lambda *a:None)
  ref=next(r for r in rows if r['version']==version and r['case']==case and r['engine']=='monty' and r['form']=='packed')
  assert host.calls==ref['rpc_calls'] and host.writes==ref['writes'] and host.answers==ref['answers'] and len(host.llms)==ref['scripted_llm_calls'] and not host.unmatched
  checks.append({'version':version,'case':case,'full_history_matches':True,'write_count':len(host.writes),'outcome':host.answers[0]['outcome']})
report={'status':'passed bounded independent source/oracle/native review','python':sys.version.split()[0],'monty':importlib.metadata.version('pydantic-monty'),'one_assignment_only':True,'exact_parent_and_candidate_pack_reproduced':True,'decoded_payloads_equal_saved_and_AST_equal_readable':True,'tree_checks':treechecks,'positive_oracle_rendering_only_terminal_LF_removed':True,'manual_oracle_files_unchanged':True,'ledger112_identity_and_four_form_history_checks':True,'independent_native_packed_reruns':checks,'all112_rerun_here':False,'request_capture_limit':'ledger has full RPC histories and router request hash/count, not full LLM request bodies; frozen router response is not live inference evidence','model_calls':0,'production_changes':False,'source_sha256':{n:sha((P/n).read_bytes()) for n in ['agent.py','readable.py','parent.py','parent-readable.py','lzpack.py']}}
(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
