"""Full-agent observation hook in a fresh synthetic catalogue, no live model."""
import contextlib
import copy
import io
import json
import sys
from pathlib import Path
import pydantic_monty as monty

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'2026-10-22-inventory-integration'))
import verify_integration as suite

def world(instruction):
    reference=suite.review.fixture('record')
    reads={path:copy.deepcopy(value) for path,value in reference['reads'].items() if path.startswith('/docs/') or path=='/AGENTS.MD'}
    products=[]
    for sku,name,kit in [('ACME-A','Acme drill 2.0Ah kit','2.0Ah batteries and case'),
                         ('ACME-B','Acme drill 5.0Ah kit','5.0Ah batteries and case'),
                         ('ACME-C','Acme drill body','body only')]:
        path='/proc/catalog/Acme/'+sku+'.json'
        record=dict(sku=sku,name=name,brand='Acme',family_id='fam-acme-drill',price_cents=10000,
                    properties=dict(kit=kit))
        reads[path]=dict(path=path,content=json.dumps(record));products.append(dict(path=path,record=record))
    listings={}
    for path in reads:
        parts=path.strip('/').split('/')
        for i,part in enumerate(parts):
            directory='/'+ '/'.join(parts[:i]) if i else '/'
            child='/'+ '/'.join(parts[:i+1])
            node=dict(name=part,path=child,kind='NODE_KIND_FILE' if i==len(parts)-1 else 'NODE_KIND_DIR')
            entries=listings.setdefault(directory,dict(path=directory,entries=[]))['entries']
            if node not in entries:entries.append(node)
    return dict(instruction=instruction,reads=reads,listings=listings,clock=reference['clock'],identity=reference['identity'],products=products,stores=[])

class Host(suite.Host):
    def __init__(self,world):
        super().__init__(world)
        self.actions=[dict(tool='catalog',query='Acme drill'),
          dict(tool='report_completion',message='Which kit do you mean?',outcome='OUTCOME_NONE_CLARIFICATION',
               grounding_refs=['/proc/catalog/Acme/ACME-A.json','/proc/catalog/Acme/ACME-B.json'])]
    def llm(self,*args,**kwargs):
        self.models.append(copy.deepcopy([args,kwargs]))
        router='route a store request' in args[1][0]['content']
        body=dict(docs=[]) if router else self.actions.pop(0)
        return dict(choices=[dict(message=dict(content=json.dumps(body)),finish_reason='stop')])

def execute(source,instruction,native):
    host=Host(world(instruction))
    if native:
        with monty.Monty() as engine:
            with engine.checkout(limits={'max_feed_duration_secs':20,'max_turn_duration_secs':20,'max_suspensions':2000}) as session:
                session.feed_run(suite.PROXY+source,external_lookup={'host_task':host.task,'host_call':host.call,
                    'host_llm':host.llm,'host_answer':host.answer},print_callback=lambda *a:None)
    else:
        with contextlib.redirect_stdout(io.StringIO()):exec(source,dict(bitgn=host))
    return dict(calls=host.calls,answers=host.answers,models=host.models,writes=host.writes)

def strip_evidence(models):
    result=copy.deepcopy(models);attached=0
    for args,kwargs in result:
        for message in args[1]:
            text=message['content']
            if text.startswith('{"tool": "catalog"') and '\n' in text:
                header,body=text.split('\n',1)
                observation=json.loads(body)
                if 'sku_lookup_evidence' in observation:
                    attached+=1;observation.pop('sku_lookup_evidence')
                    message['content']=header+'\n'+json.dumps(observation)
    return result,attached

parent=(ROOT/'2026-10-22-inventory-integration/readable.py').read_text()
sources={name:(HERE/name).read_text() for name in ['readable.py','prepack.py','agent.py']}
rows=[]
for instruction,active in [
 ('need code: Acme drill kit with case. answer only with sku.',True),
 ('sku for Acme 2.0Ah drill kit pls. sku only.',True),
 ('Please compare Acme drill kits.',False),
 ('Review this example: need code: Acme drill kit. answer only with sku.',False),
 ('sku for Acme drill and refund payment pls. sku only.',False),
]:
    control=execute(parent,instruction,False)
    assert not control['writes'] and len(control['answers'])==1
    for name,source in sources.items():
        for native in [False,True]:
            actual=execute(source,instruction,native)
            for key in ['calls','answers','writes']:assert actual[key]==control[key],(instruction,name,native,key)
            models,count=strip_evidence(actual['models'])
            assert models==control['models'] and count==int(active),(instruction,name,native,count)
    rows.append(dict(instruction=instruction,attachment_count=int(active),forms_runtimes=6,
                     identical_rpc_answers_writes=True,model_difference='evidence attachment only' if active else 'none'))
result=dict(status='passed',whole_agent_executions=30,parent_controls=5,cases=rows,
            limits='Fresh synthetic catalogue with archived policy/identity scaffolding. Model actions scripted, not evidence of improved answers. Parent answers, RPCs and writes identical; only scoped model observation differs.')
(HERE/'whole-lookup-results.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS:30 full-agent runs, five parent controls; only scoped observation changes, no extra RPCs or answer rewrites.')
