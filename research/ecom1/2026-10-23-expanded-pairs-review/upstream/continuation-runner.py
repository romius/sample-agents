import json
print('SKU_CONTINUATION_BEGIN '+json.dumps({'resume_at':17,'remaining':43,'responses':'immutable llm_response trace events'}))
for step in FROZEN['plan'][17:]:
    c=FROZEN['cases'][step['case_index']]
    obs=dict(c['base'])
    if step['arm']=='treatment':obs['sku_lookup_evidence']=c['evidence']
    messages=FROZEN['bootstrap']+[{'role':'user','content':c['instruction']},{'role':'assistant','content':json.dumps(c['action'])},{'role':'user','content':json.dumps(c['action'])+'\n'+json.dumps(obs)}]
    try:
        response=bitgn.llm('openai/gpt-oss-120b',messages,temperature=0,reasoning={'effort':'medium'},max_tokens=2048,seed=20261023)
        result={'step':step,'generation_id':response.get('id'),'finish_reason':response.get('choices',[{}])[0].get('finish_reason')}
    except Exception as error:
        if 'cancel' in str(error).lower():raise
        result={'step':step,'error':str(error)}
    print('SKU_CONTINUATION_INDEX '+json.dumps(result))
print('SKU_CONTINUATION_END')
bitgn.answer('Continuation research carrier complete. Frozen remaining43 calls only; raw responses retained in model trace.',outcome='OUTCOME_NONE_UNSUPPORTED',refs=[])
