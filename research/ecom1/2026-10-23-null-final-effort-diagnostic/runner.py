# FROZEN contains only the reviewed request objects and exact ordinal plan.
# No ECOM actions, response parsing, semantic scoring, retries or usage calls.
print('NULL_FINAL_BEGIN '+json.dumps({'calls':20,'plan_sha256':FROZEN['plan_sha256']}))
responses=0
for step in FROZEN['steps']:
    request=FROZEN['requests'][step['fixture']+'-'+step['arm']]
    print('NULL_FINAL_REQUEST '+json.dumps(step))
    try:
        response=bitgn.llm(request['args'][0],request['args'][1],**request['kwargs'])
    except Exception as error:
        # No undocumented cancellation-string guess: every exception stops.
        # Raw errors and transport attempts must be recovered from the trace.
        print('NULL_FINAL_RESULT '+json.dumps({'ordinal':step['ordinal'],'status':'error','error_preview':str(error)[:32]}))
        print('NULL_FINAL_STOP '+json.dumps({'attempted':step['ordinal'],'responses':responses,'errors':1,'next_planned_ordinal':step['ordinal']+1}))
        raise
    responses+=1
    result={'ordinal':step['ordinal'],'status':'returned','response_id_preview':None,'finish_reason_preview':None}
    if isinstance(response,dict):
        response_id=response.get('id')
        if isinstance(response_id,str):result['response_id_preview']=response_id[:32]
        choices=response.get('choices')
        if isinstance(choices,list) and choices and isinstance(choices[0],dict):
            finish_reason=choices[0].get('finish_reason')
            if isinstance(finish_reason,str):result['finish_reason_preview']=finish_reason[:16]
    print('NULL_FINAL_RESULT '+json.dumps(result))
print('NULL_FINAL_END '+json.dumps({'attempted':20,'returned':responses,'errors':0}))
bitgn.answer('Null-final effort diagnostic finished. Carrier task was not attempted; its grade is not research evidence.',outcome='OUTCOME_NONE_UNSUPPORTED',refs=[])
