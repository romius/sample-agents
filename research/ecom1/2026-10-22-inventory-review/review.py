"""Independent CSV oracle and native donor workflow on two exact archived worlds.

Lists are reconstructed from recorded complete Trees; persistence and second scans
are simulated. No provider calls, live writes, or hidden grader recomputation.
"""
import copy,csv,datetime,hashlib,io,json
from pathlib import Path
import pydantic_monty as monty

HERE=Path(__file__).resolve().parent
donor=(HERE/'upstream/d4012r1').read_text()
assert hashlib.sha256(donor.encode()).hexdigest()=='6dfb12462ba0ef5261c7c61c46d07735fca67dec25552f3124c8b4831a8bf179'
engine_source=donor[donor.index('IX_POLICIES='):donor.index('IX_RESULT=')]
engine={};exec(engine_source,engine)

def fixture(label):
    events=sorted(sum([json.loads(p.read_text()) for p in HERE.glob(label+'-t091-part*.json')],[]),key=lambda e:e['seq'])
    reads={e['data']['response']['path']:e['data']['response'] for e in events if e['data']['method']=='Read'}
    instruction=next(e['data']['response']['instruction'] for e in events if e['data']['method']=='StartTrial')
    execs=[e['data']['response'] for e in events if e['data']['method']=='Exec']
    clock=next(r for r in execs if r['stdout'].startswith('2026-'))
    identity=next(r for r in execs if r['stdout'].startswith('user:'))
    roots=engine['ix_roots'](reads['/AGENTS.MD']['content'])
    listings={}
    def walk(node,parent=''):
        path=parent+'/'+node['name'] if node['name']!='/' else ''
        if node['kind']!='NODE_KIND_DIR':return
        entries=[]
        for child in node.get('children',[]):
            entries.append(dict(name=child['name'],path=path+'/'+child['name'],kind=child['kind']))
            walk(child,path)
        listings[path or '/']=dict(path=path or '/',entries=entries)
    for event in events:
        if event['data']['method']=='Tree':walk(event['data']['response']['root'])
    collections=[]
    for root in roots:
        paths={item['path'] for directory,response in listings.items() if directory==root or directory.startswith(root+'/')
               for item in response['entries'] if item['kind']=='NODE_KIND_FILE'}
        available={p for p in reads if p.startswith(root+'/')}
        assert paths==available,(label,'complete Tree/Read coverage',paths-available,available-paths)
        collections.append([dict(path=p,record=json.loads(reads[p]['content'])) for p in sorted(paths)])
    assert list(map(len,collections))==[101,17]
    writes=[e['data']['arguments'] for e in events if e['data']['method']=='Write']
    return dict(instruction=instruction,reads=reads,listings=listings,clock=clock,identity=identity,
                products=collections[0],stores=collections[1],recorded_writes=writes)

def expected_csv(world,request,branch):
    # Independent date and CSV libraries; no ix_day/ix_compile arithmetic reused.
    today=datetime.date.fromisoformat(world['clock']['stdout'][:10])
    store=next(p['record'] for p in world['stores'] if p['record']['name']==branch)
    inventory={r['sku']:r for r in store['inventory']}
    family=sorted(p['record']['sku'] for p in world['products'] if p['record']['family_id']==request['family'])
    out=io.StringIO();writer=csv.writer(out,lineterminator='\n');writer.writerow(['SKU']+request['dates'])
    for sku in family:
        row=inventory.get(sku);values=[]
        for date in request['dates']:
            offset=(datetime.date.fromisoformat(date)-today).days
            if row is None:value=0
            elif offset==0:value=max(row['on_hand']-row['reserved'],0)
            else:value=sum(x['quantity'] for x in row.get('incoming',[]) if x['arrival_in_days']==offset)
            values.append(value)
        writer.writerow([sku]+values)
    return out.getvalue()

class ReplayHost:
    def __init__(self,world,fault=''):
        self.world=world;self.fault=fault;self.calls=[];self.files={};self.writes=[];self.read_counts={}
    def call(self,method,args):
        self.calls.append([method,copy.deepcopy(args)])
        path=args.get('path')
        if method=='Exec':return copy.deepcopy(self.world['identity' if path=='/bin/id' else 'clock'])
        if method=='List':
            response=copy.deepcopy(self.world['listings'][path])
            if self.fault=='truncated-list':response['truncated']=True
            return response
        if method=='Read':
            self.read_counts[path]=self.read_counts.get(path,0)+1
            if path in self.files:
                return {'path':path,'content':self.files[path]+('wrong' if self.fault=='readback-mismatch' else '')}
            response=copy.deepcopy(self.world['reads'][path])
            if self.fault=='second-scan-drift' and path.endswith('.json') and self.read_counts[path]==2:response['content']+=' '
            return response
        if method=='Stat':
            if self.fault=='existing-destination':return {'path':path,'kind':'NODE_KIND_FILE'}
            raise RuntimeError('BitGN HTTP 404: {"code":"not_found"}')
        if method=='Write':
            self.writes.append(copy.deepcopy(args));self.files[path]=args['content']
            if self.fault=='lost-write-ack':raise RuntimeError('connection lost after persistence')
            return {'path':path}
        raise AssertionError((method,args))

def execute(world,native=False,fault=''):
    host=ReplayHost(world,fault)
    if native:
        source=engine_source+'\nresult=ix_run(instruction,host_call)\nprint("RESULT "+json.dumps(result))'
        output=[]
        with monty.Monty() as pool:
            with pool.checkout(limits={'max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000}) as session:
                session.feed_run(source,inputs={'instruction':world['instruction']},external_lookup={'host_call':host.call},print_callback=lambda *a:output.append(a))
        text=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in output)
        result=json.loads(next(line[7:] for line in text.splitlines() if line.startswith('RESULT ')))
    else:result=engine['ix_run'](world['instruction'],host.call)
    return result,host

def legacy_width(body):
    # Exact algorithm in thingy d4485r1 R4 (qE), with readable local names.
    lines=body.split('\n');width=lines[0].count(',')+1;out=[]
    for line in lines:
        fields=line.split(',')
        while len(fields)>width and fields[-1]=='0':fields.pop()
        out.append(','.join(fields))
    return '\n'.join(out)

def main():
    results={}
    for label in ['own','record']:
        world=fixture(label);request=engine['ix_request'](world['instruction'])
        bound=engine['ix_bound_request'](request,world['stores'])
        expected=expected_csv(world,request,bound['branch'])
        compiled=engine['ix_compile'](bound,world['clock']['stdout'][:10],world['products'],world['stores'])
        assert compiled['body']==expected
        written=world['recorded_writes'][-1]['content']
        assert legacy_width(written)==expected
        parsed=list(csv.reader(io.StringIO(written)))
        assert all(len(row)==len(parsed[0])+1 and row[-1]=='0' for row in parsed[1:])
        replay,host=execute(world);native,nativehost=execute(world,True)
        assert replay==native and host.calls==nativehost.calls and host.writes==nativehost.writes
        assert replay['terminal'] and replay['outcome']=='OUTCOME_OK'
        assert len(host.writes)==1 and host.writes[0]['content']==expected
        failures={}
        for fault in ['truncated-list','second-scan-drift','existing-destination','lost-write-ack','readback-mismatch']:
            result,fault_host=execute(world,True,fault)
            post=fault in ['lost-write-ack','readback-mismatch']
            assert len(fault_host.writes)==int(post)
            assert result['terminal']==post
            if post:assert result['outcome']=='OUTCOME_ERR_INTERNAL'
            failures[fault]={'result':result,'write_attempts':len(fault_host.writes)}
        (HERE/(label+'-expected.csv')).write_text(expected)
        results[label]={'products':101,'stores':17,'tree_read_coverage_complete':True,'instruction':world['instruction'],
            'expected_csv':expected,'recorded_csv':written,'only_extra_zero_columns':True,
            'native_workflow':replay,'simulated_calls':len(host.calls),'fault_checks':failures}
    quoted='SKU,quantity\n"ACME, drill",0\n'
    assert legacy_width(quoted)!=quoted
    assert list(csv.reader(io.StringIO(quoted)))==[['SKU','quantity'],['ACME, drill','0']]
    results['quoted_csv_counterexample']={'before':quoted,'after':legacy_width(quoted),'valid_before':True}
    results['limits']='Exact recorded source bytes; reconstructed List responses and simulated persistence/stability. No live score, regenerated model trace or hidden regrade. Full-agent integration not tested here.'
    (HERE/'review-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('PASS: both complete archived worlds match independent oracle; native donor success plus10 failure boundaries; quoted CSV counterexample reproduced')
    print({k:v['simulated_calls'] for k,v in results.items() if k in ['own','record']})

if __name__=='__main__':main()
