"""Offline public ClassInstance boundary test; no real SDK or model calls."""
import ast,contextlib,hashlib,io,json,platform
from pathlib import Path
import pydantic_monty as monty
HERE=Path(__file__).resolve().parent
SOURCE=(HERE/'agent.py').read_text()
LIMITS={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}
class BitGN:
    def __init__(self,mismatch=False):self.calls=[];self.answers=[];self.mismatch=mismatch
    def call(self,method,args):
        assert method=='Exec' and args=={'path':'/bin/id'}
        self.calls.append([method,args])
        return {'stdout':'user: clerk\n' if not self.mismatch or len(self.calls)==1 else 'user: other\n','exit_code':0}
    def answer(self,*args,**kwargs):self.answers.append([args,kwargs]);return {}

def main():
    tree=ast.parse(SOURCE)
    attrs=[n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='bitgn']
    assert set(attrs)=={'call','answer'}
    assert len(SOURCE.encode())<=65536
    rows=[]
    host=BitGN();stream=io.StringIO()
    with contextlib.redirect_stdout(stream):exec(SOURCE,{'bitgn':host})
    assert len(host.calls)==2 and len(host.answers)==1
    assert json.loads(stream.getvalue().split(' ',1)[1])['method_value_access']=='allowed'
    rows.append({'host':'ordinary Python object','value_access':'allowed','calls':2,'answers':1})
    with monty.Monty() as pool:
        for mismatch,allow_call in [(False,True),(True,True),(False,False)]:
            host=BitGN(mismatch);output=[];error=None
            methods={'answer','call'} if allow_call else {'answer'}
            try:
                with pool.checkout(limits=LIMITS) as session:
                    session.feed_run(SOURCE,inputs={'bitgn':monty.ClassInstance(host,allowed_methods=methods)},print_callback=lambda *a:output.append(str(a[-1])))
            except Exception as exc:error=str(exc)
            if not mismatch and allow_call:
                assert error is None,error
                observed=json.loads(''.join(output).split(' ',1)[1])
                assert observed['method_value_access']=='raised' and "'BitGN' object has no attribute 'call'" in observed['method_value_error']
                assert len(host.calls)==2 and len(host.answers)==1
            elif mismatch:
                assert error and 'AssertionError' in error and len(host.calls)==2 and not host.answers
            else:
                assert error and 'AttributeError' in error and not host.calls and not host.answers
            rows.append({'host':'native ClassInstance','mismatch':mismatch,'call_allowed':allow_call,'calls':len(host.calls),'answers':len(host.answers),'stdout':''.join(output),'error':error})
    result={'source_bytes':len(SOURCE.encode()),'source_sha256':hashlib.sha256(SOURCE.encode()).hexdigest(),'python':platform.python_version(),'monty':'1.2.0','limits':LIMITS,'executions':rows,'real_sdk_calls':0,'model_calls':0,'limitation':'Public ClassInstance configuration reproduces observed boundary; actual Brain BitGN behavior is separately probed only after authorized submission.'}
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
