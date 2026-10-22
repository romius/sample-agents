"""Header grammar controls, exact native parsing, and advisory archived-world regression."""
import ast,contextlib,hashlib,io,json,sys
from pathlib import Path
import pydantic_monty as m
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'2026-10-22-record-integration'
sys.path.insert(0,str(BASE))
import test_combined as rc,replay,run_suite
parent=(BASE/'agent.py').read_text();packed=(HERE/'agent.py').read_text()
def namespace(source):
    code=rc.decoded_source(source);ns={}
    exec(code[:code.index('\nmessages = [')],ns)
    ns.update(DM=ns['rcp_items'],FP=ns['receipt_availability'],FU=ns['receipt_price_drift'])
    return ns
rc.namespace=namespace
old=namespace(parent);new=namespace(packed)
archive=(HERE/'archived-ocr.txt').read_text()
expected=[(1,19990,'PT-GRD-MET-W18-I25-FLAT'),(1,28990,'PT-HDG-STI-HSA50-AK20'),(17,890,'PT-SAFE-UVEX-PHEO5-CLEAR')]
assert old['DM'](archive) is None
assert new['DM'](archive)==expected
assert sum(q*u for q,u,s in expected)==64110
cases=[]
for header in ['Item t Unit Total','Item Qty Unit Total','  ITEM  Q7Y\tUnit Total  ','Item | Unit Total','Item quantity Unit Total']:
    text=archive.replace('Item t Unit Total',header)
    assert new['DM'](text)==expected
    cases.append((header,text,expected))
for header in ['Review unit total','The item t unit total matters','"Item t Unit Total"','Item t Unit Total appendix','Unit Total','Item price unit total is explained here']:
    text=archive.replace('Item t Unit Total',header)
    assert new['DM'](text) is None,header
    cases.append((header,text,None))
for name,text in [('bad subtotal',archive.replace('641.10','640.10')),
                  ('missing SKU',archive.replace('SKU PT-HDG-STI-HSA50-AK20','')),
                  ('bad row amount',archive.replace('1 289.90 289.90','1 289.90 280.00'))]:
    assert new['DM'](text) is None,name
    cases.append((name,text,None))
# Show why the community's substring relaxation is broader than this proposal.
original=(BASE/'readable.py').read_text()
wide=original.replace('"ITEM QTY UNIT TOTAL" in " ".join(up.split())','"UNIT TOTAL" in " ".join(up.split())')
assert namespace(wide)['DM'](cases[5][1])==expected

receipt_archive=json.loads((BASE/'archived_receipt.json').read_text())['response']['content']
parser=rc.parser_checks((BASE/'receipt_parent.py').read_text(),packed,receipt_archive)
handlers=[rc.handler_checks(parent,packed,g) for g in ['handlers-0','handlers-1','handlers-2','handlers-3','drift']]
# Test the decoded exact artifact in native Monty with all header/invalid controls.
code=rc.decoded_source(packed);prefix=code[:code.index('\nmessages = [')]
native_code=prefix+'\nprint("RESULT "+json.dumps([rcp_items(text) for text in '+repr([t for _,t,_ in cases])+']))'
out=[]
with m.Monty() as pool:
    with pool.checkout() as session:session.feed_run(native_code,print_callback=lambda *a:out.append(a))
text=''.join(str(a[1]) if len(a)>1 else str(a[0]) for a in out)
native=json.loads(next(line[7:] for line in text.splitlines() if line.startswith('RESULT ')))
assert native==json.loads(json.dumps([e for _,_,e in cases]))
worlds=[]
for w in sorted((BASE/'worlds').glob('*.json')):
    a=run_suite.run_world(replay,str(BASE/'agent.py'),str(w))
    b=run_suite.run_world(replay,str(HERE/'agent.py'),str(w))
    assert a==b,w.name
    worlds.append(b)
report=dict(source_sha256=hashlib.sha256(packed.encode()).hexdigest(),
 header_cases=[dict(name=n,expected=e,native_equal=True) for n,t,e in cases],
 broad_substring_counterexample='Review unit total followed by otherwise balanced rows is accepted by broad relaxation but declined by standalone-header grammar.',
 archived_receipt_fixed=True,archived_receipt_sum_cents=64110,parser=parser,handlers=handlers,
 archived_worlds=worlds,scope='Parser mechanism and mock handler controls;27 advisory archived-world replay fields unchanged. No live grade or fresh model behavior inferred.')
(HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: archived receipt recovered;14 native header/malformed controls;408 inherited parser controls;20handler cases;27 advisory world comparisons unchanged.')
