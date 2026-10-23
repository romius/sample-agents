# FROZEN is embedded by build.py. No ECOM-world reads or mutations are issued.
# Raw responses/errors belong in immutable llm_response/error trace events.
# Do not dump them or full usage objects into the 65,536-byte stdout budget.
print('SKU_DIAGNOSTIC_BEGIN '+json.dumps({'calls':len(FROZEN['plan']),'purpose':'paired next-action diagnostic, not task score'}))
response_count=0
error_count=0
for step in FROZEN['plan']:
    fixture=FROZEN['fixtures'][step['case_index']]
    request=fixture['arms'][step['arm']]
    parameters={k:v for k,v in request.items() if k not in ['model','messages']}
    print('SKU_DIAGNOSTIC_REQUEST '+json.dumps({'ordinal':step['ordinal']}))
    result={'step':step,'status':'response','response_id':None,'finish_reason':None}
    try:
        response=bitgn.llm(request['model'],request['messages'],**parameters)
        response_count+=1
        if isinstance(response,dict):
            rid=response.get('id')
            if isinstance(rid,str):result['response_id']=rid[:32]
            choices=response.get('choices')
            if isinstance(choices,list) and choices and isinstance(choices[0],dict):
                reason=choices[0].get('finish_reason')
                if isinstance(reason,str):result['finish_reason']=reason[:16]
    except Exception as error:
        error_count+=1
        result['status']='error'
        result['error_preview']=str(error)[:32]
        if 'cancel' in str(error).lower():
            result['status']='cancelled'
            print('SKU_DIAGNOSTIC_RESULT '+json.dumps(result))
            raise
    print('SKU_DIAGNOSTIC_RESULT '+json.dumps(result))
print('SKU_DIAGNOSTIC_END '+json.dumps({'attempted':len(FROZEN['plan']),'responses':response_count,'errors':error_count}))
bitgn.answer('Paired SKU diagnostic completed; carrier task was not attempted. See diagnostic trace; grade is not research evidence.',outcome='OUTCOME_NONE_UNSUPPORTED',refs=[])
