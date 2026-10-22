# FROZEN is embedded by build.py. No ECOM-world reads or mutations are issued.
print('SKU_DIAGNOSTIC_BEGIN '+json.dumps({'calls':len(FROZEN['plan']),'purpose':'paired next-action diagnostic, not task score'}))
for step in FROZEN['plan']:
    fixture=FROZEN['fixtures'][step['case_index']]
    request=fixture['arms'][step['arm']]
    parameters={k:v for k,v in request.items() if k not in ['model','messages']}
    print('SKU_DIAGNOSTIC_REQUEST '+json.dumps(step))
    try:
        response=bitgn.llm(request['model'],request['messages'],**parameters)
        result={'step':step,'response':response}
    except Exception as error:
        if 'cancel' in str(error).lower():
            raise
        result={'step':step,'error':str(error)}
    print('SKU_DIAGNOSTIC_RESULT '+json.dumps(result))
print('SKU_DIAGNOSTIC_END '+json.dumps(bitgn.usage()))
bitgn.answer('Paired SKU diagnostic completed; carrier task was not attempted. See diagnostic trace; grade is not research evidence.',outcome='OUTCOME_NONE_UNSUPPORTED',refs=[])
