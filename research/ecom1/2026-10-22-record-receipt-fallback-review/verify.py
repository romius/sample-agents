"""Check current community t043 question against our existing pinned evidence."""
import hashlib,json
from pathlib import Path
import pydantic_monty as m
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-record-integration'
NEW=HERE.parent/'2026-10-22-inventory-integration'
events=json.loads((HERE/'record-t043-events.json').read_text())
by_seq={e['seq']:e for e in events}
r=by_seq[5955]['data']['response'];text=r['content']
assert hashlib.sha256(text.encode()).hexdigest()==r['sha256']=='fb1a7aaac8872d800a48e08045ac82bc3fe97f3c96049cdc05e632f2096cff98'
previous=json.loads((BASE/'archived_receipt.json').read_text())
assert previous['job']=='j110adb6ab262405f85363cc00efee623' and previous['event']==5955
assert previous['response']==r
instruction=by_seq[5935]['data']['response']['instruction']
identity=by_seq[5943]['data']['response']['stdout']
old=(BASE/'record_readable.py').read_text().split('\nmessages = [')[0]
new=(NEW/'readable.py').read_text().split('\nIX_RESULT=')[0]
expected=[[1,26990,'PT-DRL-BOS-GSR55-5AH'],[5,23990,'PT-WASH-BO5-UA135-CAR'],[2,38990,'PT-MOW-STI-RMA235-AK30'],[12,24990,'PT-SAW-MAK-DHS680-BLADE']]
results={}
for name,source in [('record',old),('queued_inventory',new)]:
    ns={};exec(source,ns)
    actual=json.loads(json.dumps(ns['rcp_items'](text)))
    eligibility=ns['rcp_request'](instruction,identity)
    output=[]
    with m.Monty() as engine:
        with engine.checkout() as session:
            session.feed_run(source+'\nprint(json.dumps([rcp_items(text),rcp_request(instruction,identity)]))',
                inputs=dict(text=text,instruction=instruction,identity=identity),print_callback=lambda *a:output.append(a))
    printed=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in output)
    assert json.loads(printed)==[actual,eligibility]
    assert eligibility
    assert actual==(None if name=='record' else expected)
    results[name]=dict(parser=actual,employee_request_eligible=eligibility,cpython_native_equal=True)
assert sum(q*p for q,p,s in expected)==524800
methods=[e['data'].get('method') for e in events]
read_paths=[e['data']['response']['path'] for e in events if e['data'].get('method')=='Read']
assert not any(p.startswith('/proc/') for p in read_paths)
policy=by_seq[5951]['data']['response']['content']
assert 'Availability checks are read-only unless the user asks for an export file.' in policy
results.update(exact_existing_fixture=True,receipt_sha256=r['sha256'],subtotal_cents=524800,
    source_job='j110adb6ab262405f85363cc00efee623',source_event=5955,identity=identity,instruction=instruction,
    existing_test_path='../2026-10-22-record-integration/test_combined.py',read_paths_in_failed_trace=read_paths,
    conclusion='Queued original-first S-for-5 recovery already fixes the exact parser blocker. Do not duplicate an employee handler: record eligibility already accepts this runtime employee and exact feasibility wording.',
    limits='This does not prove a successful full availability answer. Failed trace contains no catalogue/store Reads; unavailable values cannot be supplied from another generated world. Native parser result is not a hidden-grade recomputation. Employee feasibility is read-only under observed availability policy, not checkout authorization.')
(HERE/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS:exact archived receipt equals prior fixture;record rejects and queued parser recovers four rows/subtotal;both employee gates already accept;native parity. Full-world outcome unproven.')
