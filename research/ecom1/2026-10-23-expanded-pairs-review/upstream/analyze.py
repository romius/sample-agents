"""Independent mechanical disposition metrics; semantic grounding is manual.

Usage: python analyze.py records.json fixtures.json oracles.json report.json
Never infer semantic correctness from an OUTCOME_NONE_CLARIFICATION label.
"""
import collections,json,pathlib,re,sys
def parse(record,oracle):
    out={'case':record['step']['case'],'arm':record['step']['arm'],'kind':oracle['expected']['kind'],'status':None}
    if 'error' in record:return dict(out,status='error',error=record['error'])
    choice=record['response'].get('choices',[{}])[0]
    content=choice.get('message',{}).get('content') or ''
    out['finish_reason']=choice.get('finish_reason')
    if choice.get('finish_reason')=='length':return dict(out,status='truncated',content=content)
    body=content.strip()
    if body.startswith('```') and body.endswith('```'):body='\n'.join(body.splitlines()[1:-1])
    try:action=json.loads(body)
    except (ValueError,TypeError):return dict(out,status='malformed',content=content)
    if not isinstance(action,dict) or not isinstance(action.get('tool'),str):return dict(out,status='malformed',content=content)
    out['action']=action
    if action['tool'] in {'read','catalog','search','find','tree','list','stat'}:return dict(out,status='deferred')
    if action['tool']!='report_completion':return dict(out,status='unexpected_action')
    if not isinstance(action.get('message'),str) or not isinstance(action.get('grounding_refs',[]),list):return dict(out,status='malformed')
    outcome=action.get('outcome');message=action['message'];refs=action.get('grounding_refs',[])
    if outcome not in {'OUTCOME_OK','OUTCOME_NONE_CLARIFICATION','OUTCOME_NONE_UNSUPPORTED','OUTCOME_DENIED_SECURITY','OUTCOME_ERR_INTERNAL'} or any(not isinstance(r,str) for r in refs):return dict(out,status='malformed')
    out.update(status='final',outcome=outcome,message=message,refs=refs)
    e=oracle['expected'];rows=oracle['source_records'];paths={r['sku']:r['_path'] for r in rows}
    known=set(re.findall(r'PT-[A-Z0-9-]+',message.upper()))
    out['excess_clarification']=e['kind']=='unique' and outcome=='OUTCOME_NONE_CLARIFICATION'
    out['false_definitive_ok']=e['kind']!='unique' and outcome=='OUTCOME_OK'
    # Decomposition added after first12 live outputs; primary false_ok unchanged.
    out['false_single_sku_ok']=out['false_definitive_ok'] and len(known)==1
    out['multiple_skus_ok']=out['false_definitive_ok'] and len(known)>1
    out['correct_unique_sku_ref']=e['kind']=='unique' and outcome=='OUTCOME_OK' and message.strip()==e['sku'] and paths[e['sku']] in refs
    out['wrong_unique_identity']=e['kind']=='unique' and outcome=='OUTCOME_OK' and known!={e['sku']}
    out['excluded_quoted_or_cited']=e['kind']=='clarify' and (e['excluded'] in known or paths[e['excluded']] in refs)
    out['out_of_family_catalog_refs']=[r for r in refs if r.startswith('/proc/catalog/') and r not in paths.values()]
    out['missing_eligible_refs']=([s for s in e['eligible'] if paths[s] not in refs] if e['kind']=='clarify' and outcome=='OUTCOME_NONE_CLARIFICATION' else [])
    return out
def analyze(records,frozen,oracles):
    plan={(p['case'],p['arm']):p for p in frozen['plan']};seen=set();rows=[];bycase={o['case']:o for o in oracles}
    for record in records:
        p=record['step'];key=p['case'],p['arm'];assert key not in seen and plan[key]==p;seen.add(key)
        rows.append(parse(record,bycase[p['case']]))
    assert seen==set(plan),'Missing planned calls, retain rather than silently dropping'
    summaries={}
    for arm in ['parent','treatment']:
        rr=[r for r in rows if r['arm']==arm];g={}
        for kind in ['clarify','unique','unknown','conflict']:
            sub=[r for r in rr if r['kind']==kind]
            g[kind]={'planned':len(sub),'statuses':dict(collections.Counter(r['status'] for r in sub)),'outcomes':dict(collections.Counter(r.get('outcome') for r in sub if r['status']=='final'))}
        summaries[arm]={'planned':len(rr),'groups':g,**{k:sum(bool(r.get(k)) for r in rr) for k in ['excess_clarification','false_definitive_ok','false_single_sku_ok','multiple_skus_ok','correct_unique_sku_ref','wrong_unique_identity','excluded_quoted_or_cited']},'out_of_family_ref_answers':sum(bool(r.get('out_of_family_catalog_refs')) for r in rr)}
    return {'arms':summaries,'rows':rows,'warning':'No semantic success aggregate. Read manual description audit; CLAR does not establish truthful descriptions or retained qualifiers.'}
if __name__=='__main__':
    records,frozen,oracles=[json.loads(pathlib.Path(x).read_text()) for x in sys.argv[1:4]]
    result=analyze(records,frozen,oracles);pathlib.Path(sys.argv[4]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['arms'],indent=2))
