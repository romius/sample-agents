"""Offline exact whole-agent fault injection through public method-only Monty hosts."""
import ast
import copy
import hashlib
import json
import platform
from pathlib import Path
import pydantic_monty as monty

P=Path(__file__).resolve().parent
W=json.loads((P/'fixture/world.json').read_text())
LIMITS=dict(max_feed_duration_secs=10,max_turn_duration_secs=10,max_suspensions=1000)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(x.encode()).hexdigest()
def response(content,finish='stop'):
    return {'choices':[{'finish_reason':finish,'message':{'content':content}}]}
DONE=dict(tool='report_completion',message='SCRIPTED terminal response',outcome='OUTCOME_NONE_UNSUPPORTED',grounding_refs=[])

class Host:
    def __init__(self,case):
        self.case=case;self.calls=[];self.llms=[];self.answers=[];self.mutations=[];self.unmatched=[];self.counts={};self.provider_attempts=0
    def task(self):return copy.deepcopy(W['task'])
    def usage(self):return {'offline':True,'model_calls':0}
    def answer(self,message,*,outcome,refs):
        self.answers.append(dict(message=message,outcome=outcome,refs=refs));return {}
    def call(self,method,args):
        self.calls.append([method,copy.deepcopy(args)])
        if method in ('Write','Delete') or method=='Exec' and args['path'] not in ('/bin/date','/bin/id'):
            self.mutations.append([method,copy.deepcopy(args)])
            if self.case.get('mutation_error'):raise RuntimeError(self.case['mutation_error'])
            return {}
        key=canon([method,args])
        for table in ('rpc','derived_rpc'):
            if key in W[table]:return copy.deepcopy(W[table][key])
        self.unmatched.append([method,copy.deepcopy(args)])
        raise RuntimeError('UNMATCHED OFFLINE RPC '+key)
    def llm(self,*args,**kwargs):
        messages=args[1]
        stage='router' if kwargs.get('max_completion_tokens')==1024 else 'forced' if messages[-1]['content'].startswith('Stop working now.') else 'main'
        self.counts[stage]=self.counts.get(stage,0)+1
        n=self.counts[stage]
        self.llms.append(dict(stage=stage,args=copy.deepcopy(args),kwargs=copy.deepcopy(kwargs)))
        # Explicit fake SDK policy demonstration only, not SDK implementation.
        self.provider_attempts+=self.case.get('sdk_attempts',1) if stage in self.case.get('fail_stages',[]) else 1
        if stage=='main' and n<=len(self.case.get('errors',[])):
            raise RuntimeError(self.case['errors'][n-1])
        if stage in self.case.get('fail_stages',[]) and n<=self.case.get('failures',99):
            raise RuntimeError(self.case['error'])
        if stage=='router':return copy.deepcopy(W['router_response'])
        if stage=='main' and n<=self.case.get('null_content',0):return copy.deepcopy(self.case['null_response'])
        if stage=='forced' and self.case.get('forced_response'):return copy.deepcopy(self.case['forced_response'])
        if stage=='main' and n<=self.case.get('malformed',0):return response('not JSON')
        if stage=='main' and n<=self.case.get('length',0):return response('{','length')
        if stage=='main' and self.case.get('write_first') and n==1:
            return response(json.dumps(self.case.get('first_action',dict(tool='write',path=W['export'],content='SCRIPTED local artifact'))))
        if stage=='main' and self.case.get('write_first') and n>1 and self.case.get('after_write_error'):
            raise RuntimeError(self.case['after_write_error'])
        return response(json.dumps(DONE))

def execute(pool,source,case,host_class=Host):
    host=host_class(case);output=[];error=None
    try:
        with pool.checkout(limits=LIMITS) as session:
            session.feed_run(source,inputs={'bitgn':monty.ClassInstance(host,allowed_methods={'task','call','answer','llm','usage'})},print_callback=lambda *a:output.append(str(a[-1])))
    except Exception as exc:error=str(exc)
    assert not host.unmatched,(case['name'],host.unmatched)
    return dict(case=case['name'],llm_stages=host.counts,guest_llm_calls=len(host.llms),
        simulated_provider_attempts=host.provider_attempts,request_hashes=[sha(canon(x)) for x in host.llms],
        rpc_calls=host.calls,mutations=host.mutations,answers=host.answers,raised=error,
        output=''.join(output),request_details=host.llms)

