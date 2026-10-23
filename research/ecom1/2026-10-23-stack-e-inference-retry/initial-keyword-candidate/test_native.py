"""Offline exact whole-agent fault injection through public method-only Monty hosts."""
import ast
import copy
import hashlib
import json
import platform
from pathlib import Path
import pydantic_monty as monty

P=Path(__file__).resolve().parent
W=json.loads((P.parent/'2026-10-23-stack-e-ocr-replay/world.json').read_text())
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
        if stage in self.case.get('fail_stages',[]) and n<=self.case.get('failures',99):
            raise RuntimeError(self.case['error'])
        if stage=='router':return copy.deepcopy(W['router_response'])
        if stage=='main' and n<=self.case.get('malformed',0):return response('not JSON')
        if stage=='main' and n<=self.case.get('length',0):return response('{','length')
        if stage=='main' and self.case.get('write_first') and n==1:
            return response(json.dumps(dict(tool='write',path=W['export'],content='SCRIPTED local artifact')))
        if stage=='main' and self.case.get('write_first') and n>1 and self.case.get('after_write_error'):
            raise RuntimeError(self.case['after_write_error'])
        return response(json.dumps(DONE))

CASES=[dict(name='healthy'),dict(name='recoverable_503_on_second_guest_request',fail_stages=['main'],failures=1,error='HTTP 503 unavailable'),
    dict(name='persistent_503',fail_stages=['main','forced'],error='HTTP 503 unavailable'),
    dict(name='terminal_400_connection_word',fail_stages=['main','forced'],error='HTTP 400 connection parameter invalid'),
    dict(name='unknown_error',fail_stages=['main','forced'],error='database is locked'),
    dict(name='uncertain_timeout',fail_stages=['main','forced'],error='Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out'),
    dict(name='sdk429_exhausted',fail_stages=['main','forced'],error='OpenRouter HTTP 429: rate limited',sdk_attempts=5),
    dict(name='router400_falls_back_distinct_prompt',fail_stages=['router'],error='HTTP 400 invalid parameter'),
    dict(name='router_benign_cancel_option_name',fail_stages=['router'],error='HTTP 400 invalid cancellation_policy parameter'),
    dict(name='router_negated_cancel_false_positive',fail_stages=['router'],error='HTTP 503 request was not cancelled; upstream unavailable'),
    dict(name='main_cancel',fail_stages=['main','forced'],error='Cancelled by user'),
    dict(name='main_cancel_connection',fail_stages=['main','forced'],error='Cancelled: connection closed'),
    dict(name='main_cancel503',fail_stages=['main','forced'],error='HTTP 503 request cancelled'),
    dict(name='router_cancel',fail_stages=['router'],error='Cancelled by user'),
    dict(name='forced_cancel',malformed=3,fail_stages=['forced'],error='Cancelled by user'),
    dict(name='malformed_then_valid',malformed=1),dict(name='length_then_valid',length=2),
    dict(name='malformed_forced',malformed=3),dict(name='length_forced',length=3),
    dict(name='write_then_main_error',write_first=True,after_write_error='HTTP 503 unavailable'),
    dict(name='write_mutation_error_no_retry',write_first=True,mutation_error='BitGN HTTP 503: write result unconfirmed')]

def execute(pool,source,case):
    host=Host(case);output=[];error=None
    try:
        with pool.checkout(limits=LIMITS) as session:
            session.feed_run(source,inputs={'bitgn':monty.ClassInstance(host,allowed_methods={'task','call','answer','llm','usage'})},print_callback=lambda *a:output.append(str(a[-1])))
    except Exception as exc:error=str(exc)
    assert not host.unmatched,(case['name'],host.unmatched)
    return dict(case=case['name'],llm_stages=host.counts,guest_llm_calls=len(host.llms),
        simulated_provider_attempts=host.provider_attempts,request_hashes=[sha(canon(x)) for x in host.llms],
        rpc_calls=host.calls,mutations=host.mutations,answers=host.answers,raised=error,
        output=''.join(output),request_details=host.llms)

def main():
    rows=[]
    with monty.Monty() as pool:
        for version in ('parent','candidate'):
            for form in ('readable','packed'):
                filename=('parent-readable.py' if form=='readable' else 'parent.py') if version=='parent' else ('readable.py' if form=='readable' else 'agent.py')
                source=(P/filename).read_text()
                for case in CASES:
                    row=execute(pool,source,case);row.update(version=version,form=form,source_sha256=sha(source));rows.append(row)
    def row(version,name):return next(x for x in rows if x['version']==version and x['form']=='readable' and x['case']==name)
    for version in ('parent','candidate'):
        for case in CASES:
            group=[r for r in rows if r['version']==version and r['case']==case['name']]
            for key in ('llm_stages','guest_llm_calls','request_hashes','rpc_calls','mutations','answers'):
                assert group[0][key]==group[1][key],(version,case['name'],key)
            assert bool(group[0]['raised'])==bool(group[1]['raised'])
    for name in ('persistent_503','terminal_400_connection_word','unknown_error','uncertain_timeout','sdk429_exhausted'):
        assert row('parent',name)['llm_stages']==dict(router=1,main=3,forced=1)
        assert row('candidate',name)['llm_stages']==dict(router=1,main=1)
        assert row('candidate',name)['answers'][0]['outcome']=='OUTCOME_ERR_INTERNAL'
    for name in ('main_cancel','main_cancel_connection','main_cancel503'):
        assert row('candidate',name)['llm_stages']==dict(router=1,main=1)
        assert row('candidate',name)['raised'] and not row('candidate',name)['answers']
    assert row('candidate','router_cancel')['llm_stages']==dict(router=1)
    assert row('candidate','router_cancel')['raised'] and not row('candidate','router_cancel')['answers']
    assert row('candidate','forced_cancel')['llm_stages']==dict(router=1,main=3,forced=1)
    assert row('candidate','forced_cancel')['raised'] and not row('candidate','forced_cancel')['answers']
    for name in ('healthy','malformed_then_valid','length_then_valid','malformed_forced','length_forced','router400_falls_back_distinct_prompt','router_benign_cancel_option_name'):
        for key in ('llm_stages','request_hashes','rpc_calls','mutations','answers'):
            assert row('parent',name)[key]==row('candidate',name)[key],(name,key)
    assert row('parent','recoverable_503_on_second_guest_request')['answers'][0]['outcome']=='OUTCOME_NONE_UNSUPPORTED'
    assert row('candidate','recoverable_503_on_second_guest_request')['answers'][0]['outcome']=='OUTCOME_ERR_INTERNAL'
    assert row('candidate','router_negated_cancel_false_positive')['raised']
    assert not row('parent','router_negated_cancel_false_positive')['raised']
    for version in ('parent','candidate'):
        for name in ('write_then_main_error','write_mutation_error_no_retry'):
            assert len(row(version,name)['mutations'])==1
        assert row(version,'write_mutation_error_no_retry')['raised']
    # Exact nested helper/dispatch catches exercised in native Monty. This is an
    # isolated transitive-control-flow probe, distinct from the whole-agent rows.
    helpers=[]
    for version in ('parent','candidate'):
        source=(P/('parent-readable.py' if version=='parent' else 'readable.py')).read_text()
        tree=ast.parse(source)
        names={'inference_cancelled','i2c_llm_narrow','i2c_dispatch'}
        code='import json\nimport re\n'+'\n'.join(ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names)
        outer=next(n for n in tree.body if isinstance(n,ast.If) and any(isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='i2c_dispatch' for c in ast.walk(n)))
        code+='\nINSTRUCTION="SKU only mystery model"\nI2C_MODULES=[["helper",helper_probe]]\nanswered=False\n'+ast.get_source_segment(source,outer)
        code=code.replace('I2C_MODULES=[["helper",helper_probe]]','def helper_probe(ins):\n return i2c_llm_narrow(ins,[])\nI2C_MODULES=[["helper",helper_probe]]')
        for error in ['Cancelled: connection closed','HTTP 400 invalid cancellation_policy parameter','HTTP 503 unavailable']:
            host=Host(dict(name='isolated_helper',fail_stages=['main'],error=error));raised=None
            with monty.Monty() as pool:
                try:
                    with pool.checkout(limits=LIMITS) as session:
                        session.feed_run(code,inputs={'bitgn':monty.ClassInstance(host,allowed_methods={'llm','answer'})},print_callback=lambda *a:None)
                except Exception as exc:raised=str(exc)
            assert len(host.llms)==1 and not host.answers
            assert bool(raised)==(version=='candidate' and error.startswith('Cancelled'))
            helpers.append(dict(version=version,error=error,raised=raised,guest_llm_calls=1))
    # Keep request bodies separate to keep the compact report reviewable.
    requests={f"{r['version']}/{r['form']}/{r['case']}":r.pop('request_details') for r in rows}
    (P/'fake-requests.json').write_text(json.dumps(requests,indent=2)+'\n')
    report=dict(status='offline native controls passed',python=platform.python_version(),monty='1.2.0',limits=LIMITS,
        exact_whole_agent_executions=len(rows),scenarios=len(CASES),isolated_helper_controls=helpers,
        no_paid_calls=True,no_live_sdk=True,mutation_retry_added=False,
        sdk429_attempts_are_declared_fake_policy_simulation=True,
        important_counterexamples=['503 that succeeds on a second guest invocation loses recovery',
                                  'negated cancellation wording triggers conservative cancellation detector'],results=rows)
    (P/'test-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','exact_whole_agent_executions','scenarios','important_counterexamples')}))

if __name__=='__main__':main()
