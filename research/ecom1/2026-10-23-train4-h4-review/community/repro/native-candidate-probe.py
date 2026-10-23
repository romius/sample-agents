import json
class SDK:
    def task(self):
        raise RuntimeError('LOAD_STOP')
    def call(self,*a,**k):
        return {}
    def usage(self):
        return {}
ns={'bitgn':SDK(),'print':lambda *a,**k:None}
try:
    exec(brain.read('d6855'),ns)
except RuntimeError as error:
    assert str(error)=='LOAD_STOP',str(error)
rows=[]
for case in json.loads(brain.read('d6860')):
    if case['fn']=='FC':
        try:
            actual={'status':'parsed','value':ns['FC'](case['text'])}
        except ValueError as error:
            actual={'status':'declined','error':str(error)}
    else:
        actual=ns['DM'](case['text'])
    normalized=json.loads(json.dumps(actual))
    assert normalized==case['expected_candidate'],(case['name'],normalized)
    rows.append({'name':case['name'],'fn':case['fn'],'status':'PASS','result':normalized})
print(json.dumps({'source':'d6855 draft exact packed rc7 two-owner recipe','scope':'actual pre-loop module initialization and 7 component calls, not complete native agent loop','rows':rows}))
