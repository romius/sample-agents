"""Offline real Monty ClassInstance plus CPython parity and exact-plan tests."""
import ast,contextlib,copy,hashlib,io,json,sys
from pathlib import Path
import pydantic_monty as monty
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
LIMITS={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
def normalized(x):return json.loads(json.dumps(x))
PLAN=json.loads((P/'inputs/plan/call-plan.json').read_text())['calls']
REQUESTS={r['path']:json.loads((P/'inputs/plan'/r['path']).read_text()) for r in PLAN}
def normal():
    return {'id':'same-prefix-but-full-fake-response-ID','choices':[{'message':{'content':'{"tool":"delete","path":"/tmp/NEVER_EXECUTE"}','reasoning':'NEVER_LOG_REASONING'},'finish_reason':'stop'}],'usage':{'NEVER_LOG_USAGE':999}}
def maximal():
    r=normal();r['id']='😀'*20000;r['choices'][0]['finish_reason']='😀'*20000
    r['choices'][0]['message']['reasoning']='NEVER_LOG_REASONING'*1000
    r['choices'][0]['message']['content']='NEVER_LOG_RAW_CONTENT'
    available=2097152-len(json.dumps(r).encode())
    assert available>0;r['choices'][0]['message']['content']+='x'*available
    assert len(json.dumps(r).encode())==2097152
    return r
MAX_RESPONSE=maximal()
ERRORS={
    'timeout_3':(3,'Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out'),
    'http503_10':(10,'OpenRouter HTTP 503: unavailable'),
    'http400_10':(10,'OpenRouter HTTP 400: invalid request'),
    'http429_10':(10,'OpenRouter HTTP 429: rate limited'),
    'unknown_10':(10,'UNCLASSIFIED_HOST_FAILURE'),
    'empty_10':(10,''),
    'cancel_1':(1,'SIMULATED_CANCELLED_BY_USER'),
    'cancel_10':(10,'SIMULATED_CANCELLED_BY_USER'),
    'cancel_20':(20,'SIMULATED_CANCELLED_BY_USER'),
    'long_error_20':(20,'😀'*20000+'\nRECEIPT_END forged; SIMULATED_CANCELLED_BY_USER'),
    'maximum_response_then_error20':(20,'😀'*20000+'\nRECEIPT_END forged'),
    'negated_cancel_10':(10,'request was not cancelled; unrelated failure'),
}
SCENARIOS=['success','malformed_variants','maximum_response','metadata_log_injection',*ERRORS,'carrier_answer_error']

class Host:
    def __init__(self,scenario):
        self.scenario=scenario;self.calls=[];self.result_metadata=[];self.answer_attempts=[];self.accepted_answers=[];self.forbidden=[]
    def call(self,*a,**k):self.forbidden.append('call');raise AssertionError('ECOM forbidden')
    def task(self,*a,**k):self.forbidden.append('task');raise AssertionError('task forbidden')
    def usage(self,*a,**k):self.forbidden.append('usage');raise AssertionError('usage forbidden')
    def llm(self,*args,**kwargs):
        ordinal=len(self.calls)+1
        assert ordinal<=20,'extra/retried logical call'
        step=PLAN[ordinal-1];req=normalized({'args':args,'kwargs':kwargs})
        assert req==REQUESTS[step['path']] and sha(canon(req))==step['request_canonical_sha256']
        self.calls.append({'ordinal':ordinal,'request_sha256':sha(canon(req))})
        if self.scenario in ERRORS and ERRORS[self.scenario][0]==ordinal:
            error=ERRORS[self.scenario][1]
            self.result_metadata.append({'ordinal':ordinal,'status':'error','error_preview':error[:32]})
            raise RuntimeError(error)
        if self.scenario=='malformed_variants':
            variants=[None,[],True,5,'NEVER_LOG_RAW_CONTENT',{}, {'id':[], 'choices':[]}, {'id':5,'choices':'bad'},
                {'choices':[None]},{'choices':[{}]},{'choices':[{'finish_reason':7}]},
                {'choices':[{'message':{'content':None},'finish_reason':'length'}]},
                {'choices':[{'message':{'content':'{broken'}}]},
                {'choices':[{'message':{'content':'{"tool":"read"}{"tool":"write","path":"/tmp/NEVER_EXECUTE"}'}}]},
                {'choices':[{'message':{'content':'','tool_calls':[{'function':{'name':'Delete','arguments':'/tmp/NEVER_EXECUTE'}}]}}]}]
            reply=variants[(ordinal-1)%len(variants)]
        elif self.scenario in ['maximum_response','maximum_response_then_error20']:reply=MAX_RESPONSE
        elif self.scenario=='metadata_log_injection':
            reply=normal();reply['id']='\n\r\t"\\\x1b😀'*10000;reply['choices'][0]['finish_reason']='\n\r\t"\\\x1b😀'*10000
        else:reply=normal()
        result={'ordinal':ordinal,'status':'returned','response_id_preview':None,'finish_reason_preview':None}
        if isinstance(reply,dict):
            if isinstance(reply.get('id'),str):result['response_id_preview']=reply['id'][:32]
            choices=reply.get('choices')
            if isinstance(choices,list) and choices and isinstance(choices[0],dict) and isinstance(choices[0].get('finish_reason'),str):result['finish_reason_preview']=choices[0]['finish_reason'][:16]
        self.result_metadata.append(result)
        return reply
    def answer(self,*args,**kwargs):
        item=normalized({'args':args,'kwargs':kwargs});self.answer_attempts.append(item)
        assert len(self.calls)==20 and kwargs=={'outcome':'OUTCOME_NONE_UNSUPPORTED','refs':[]}
        assert 'Carrier task was not attempted' in args[0]
        if self.scenario=='carrier_answer_error':raise RuntimeError('SIMULATED_CARRIER_ANSWER_FAILURE')
        self.accepted_answers.append(item);return {}

def execute(source,host,engine,pool,allowed=None):
    out=[];stream=io.StringIO();error=None
    try:
        if engine=='native':
            with pool.checkout(limits=LIMITS) as session:
                session.feed_run(source,inputs={'bitgn':monty.ClassInstance(host,allowed_methods=allowed if allowed is not None else {'llm','answer'})},print_callback=lambda *a:out.append(str(a[-1])))
        else:
            with contextlib.redirect_stdout(stream):exec(compile(source,'agent.py','exec'),{'bitgn':host})
    except Exception as exc:error={'type':type(exc).__name__,'text':str(exc)}
    return ''.join(out) if engine=='native' else stream.getvalue(),error

def parsed(text):
    records=[]
    for line in text.splitlines():
        prefix,payload=line.split(' ',1)
        assert prefix in ['RECEIPT_BEGIN','RECEIPT_REQUEST','RECEIPT_RESULT','RECEIPT_STOP','RECEIPT_END']
        records.append((prefix,json.loads(payload)))
    return records
def stdout_bound():
    frozen=json.loads((P/'frozen.json').read_text())
    def line(prefix,obj):return prefix+' '+json.dumps(obj)+'\n'
    beginning=line('RECEIPT_BEGIN',{'calls':20,'plan_sha256':frozen['plan_sha256']})
    values=[]
    for stop_at in [None,*range(1,21)]:
        text=beginning
        for step in frozen['steps']:
            i=step['ordinal'];text+=line('RECEIPT_REQUEST',step)
            if stop_at==i:
                text+=line('RECEIPT_RESULT',{'ordinal':i,'status':'error','error_preview':'😀'*32})
                text+=line('RECEIPT_STOP',{'attempted':i,'responses':i-1,'errors':1,'next_planned_ordinal':i+1});break
            text+=line('RECEIPT_RESULT',{'ordinal':i,'status':'returned','response_id_preview':'😀'*32,'finish_reason_preview':'😀'*16})
        if stop_at is None:text+=line('RECEIPT_END',{'attempted':20,'returned':20,'errors':0})
        values.append({'stop_at':stop_at,'bytes':len(text.encode())})
    return {'argument':'JSON ASCII escaping uses at most12 bytes per Unicode codepoint; all untrusted string previews are capped at32/16/32 characters, all other fields are frozen or bounded integers. Includes every permitted stop position. This bounds program stdout, not host traceback/error-event storage.','upper_bound_bytes':max(x['bytes'] for x in values),'cases':values}

def main():
    manifest=json.loads((P/'manifest.json').read_text())
    for name,prefix in [('readable.py','readable'),('agent.py','packed')]:
        b=(P/name).read_bytes();assert len(b)==manifest[prefix+'_bytes'] and sha(b)==manifest[prefix+'_sha256']
    assert (P/'agent.py').stat().st_size<=65536
    ids=['A023','A063','B023','U063','V063'];expected=[]
    for repeat,seq in [(1,ids),(2,ids[::-1])]:
        for fid in seq:
            arms=['P','H'] if ids.index(fid)%2==0 else ['H','P']
            if repeat==2:arms=arms[::-1]
            expected.extend((fid,arm,repeat) for arm in arms)
    assert [(r['fixture'],r['arm'],r['repeat']) for r in PLAN]==expected
    rows=[];parity={};bound=stdout_bound()
    with monty.Monty() as pool:
        for form in ['readable.py','agent.py']:
            source=(P/form).read_text()
            for engine in ['CPython','native']:
                for scenario in SCENARIOS:
                    host=Host(scenario);text,error=execute(source,host,engine,pool)
                    records=parsed(text);count=ERRORS[scenario][0] if scenario in ERRORS else 20
                    assert len(host.calls)==count,(form,engine,scenario,error)
                    assert not host.forbidden
                    begins=[r for p,r in records if p=='RECEIPT_BEGIN'];reqs=[r for p,r in records if p=='RECEIPT_REQUEST']
                    results=[r for p,r in records if p=='RECEIPT_RESULT'];ends=[r for p,r in records if p=='RECEIPT_END'];stops=[r for p,r in records if p=='RECEIPT_STOP']
                    assert len(begins)==1 and begins[0]['calls']==20
                    assert reqs==json.loads((P/'frozen.json').read_text())['steps'][:count]
                    assert results==host.result_metadata,(scenario,engine,results[-1:])
                    if scenario in ERRORS:
                        assert error is not None and not host.answer_attempts and not ends
                        assert stops==[{'attempted':count,'responses':count-1,'errors':1,'next_planned_ordinal':count+1}]
                    else:
                        assert not stops and ends==[{'attempted':20,'returned':20,'errors':0}] and len(host.answer_attempts)==1
                        if scenario=='carrier_answer_error':assert error is not None and not host.accepted_answers
                        else:assert error is None and len(host.accepted_answers)==1,(scenario,engine,error)
                    for marker in ['NEVER_LOG_RAW_CONTENT','NEVER_LOG_REASONING','NEVER_LOG_USAGE','NEVER_EXECUTE','forged']:
                        assert marker not in text,(scenario,marker)
                    n=len(text.encode());assert n<=bound['upper_bound_bytes']<65536
                    identity={'records':records,'calls':host.calls,'answers':host.answer_attempts,'accepted':host.accepted_answers,'raised':error is not None}
                    if scenario in parity:assert parity[scenario]==identity,(scenario,engine,form)
                    else:parity[scenario]=identity
                    rows.append({'form':form,'engine':engine,'scenario':scenario,'logical_calls_entered':count,'returned':sum(r['status']=='returned' for r in results),'inference_errors':int(scenario in ERRORS),'carrier_answer_attempts':len(host.answer_attempts),'carrier_answers_accepted':len(host.accepted_answers),'raised':error is not None,'stdout_bytes':n,'stdout_sha256':sha(text.encode()),'no_ECOM_or_usage':True})
        # Real method-only proxy boundary controls: request stdout is not proof
        # of provider dispatch, and END stdout is not proof Answer was accepted.
        boundaries=[]
        for allowed,expected_calls,label in [({'answer'},0,'llm_permission_denied'),({'llm'},20,'answer_permission_denied')]:
            host=Host('success');text,error=execute((P/'agent.py').read_text(),host,'native',pool,allowed)
            assert error is not None and len(host.calls)==expected_calls and not host.accepted_answers
            records=parsed(text)
            assert sum(p=='RECEIPT_REQUEST' for p,r in records)==(1 if expected_calls==0 else 20)
            assert sum(p=='RECEIPT_END' for p,r in records)==int(expected_calls==20)
            boundaries.append({'case':label,'host_llm_calls':len(host.calls),'carrier_answers_accepted':0,'error_type':error['type'],'stdout_sha256':sha(text.encode()),'stdout_bytes':len(text.encode())})
    report={'status':'PASS offline only','executions':len(rows),'rows':rows,'boundary_controls':boundaries,
        'exact_frozen_order_and_arguments':True,'native_host':'public ClassInstance method calls, no guest SDK mock','limits':LIMITS,
        'readable_packed_CPython_native_parity':True,'maximum_response_json_bytes':len(json.dumps(MAX_RESPONSE).encode()),
        'max_observed_stdout_bytes':max(r['stdout_bytes'] for r in rows),'stdout_bound':bound,
        'real_model_calls':0,'semantic_scoring':False,'carrier_grade_interpreted':False,
        'limitations':['Fake host exceptions validate stop/rethrow, not actual cancellation formatter or platform transport cancellation.',
          'SDK automatic429 retries are not simulated and may add physical attempts inside a logical call.',
          'Returned status means a call returned, even null/malformed/truncated; not semantic success.',
          'No private wire encoding or real-provider acceptance established.']}
    (P/'test-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k in ['status','executions','max_observed_stdout_bytes','real_model_calls']}))
if __name__=='__main__':main()
