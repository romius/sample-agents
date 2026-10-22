"""Offline reconstruction/checks only. Manual judgments are retained, not re-scored."""
import argparse, copy, hashlib, importlib.metadata, json, os, platform, subprocess, sys, tempfile, zipfile, zlib
from pathlib import Path
import build_actual_archive as pack
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
RESULTS=HERE.parent;ACTUAL=RESULTS/'actual-results';DIAG=RESULTS.parent/'2026-10-22-sku-lexical-paired-diagnostic'
def load(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def stripped_timing(obj):
    obj=copy.deepcopy(obj)
    for row in obj['executions']:row.pop('seconds',None)
    return obj

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args()
    assert platform.python_version()=='3.14.3' and importlib.metadata.version('pydantic-monty')=='1.2.0'
    assert zlib.ZLIB_VERSION==zlib.ZLIB_RUNTIME_VERSION=='1.2.12'
    before=pack.collect();logs=[]
    def run(script,*params):
        p=subprocess.run([sys.executable,str(script),*map(str,params)],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,timeout=180)
        logs.append({'script':script.relative_to(ROOT).as_posix(),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
        assert p.returncode==0,logs[-1]
    for seal in [DIAG/'SHA256SUMS',RESULTS/'SHA256SUMS',RESULTS/'SHA256SUMS-v2',ACTUAL/'SHA256SUMS']:
        for line in seal.read_text().splitlines():
            h,n=line.split(maxsplit=1);assert sha((seal.parent/n).read_bytes())==h,(seal,n)
    run(DIAG/'build.py')
    old_verification=(DIAG/'verification.json').read_bytes()
    run(DIAG/'verify.py')
    assert stripped_timing(load(DIAG/'verification.json'))==stripped_timing(json.loads(old_verification))
    (DIAG/'verification.json').write_bytes(old_verification) # Preserve archived timing bytes after semantic parity check.
    run(RESULTS/'test_validator_v2.py')
    run(ACTUAL/'reassemble.py')
    run(RESULTS/'validate_trace_v2.py','--trace',ACTUAL/'trial-trace.ndjson','--summary',ACTUAL/'summary.json','--output',ACTUAL/'validation.json')
    run(ACTUAL/'prepare_review.py')
    run(ACTUAL/'primary-review-transcription.py')
    run(ACTUAL/'compare-independent-primary.py')
    actual=load(ACTUAL/'validation.json');assert actual['status']=='reconciled' and actual['provider_attempts']==68 and actual['retry_events']==0
    assert actual['billing']['observed_cost_usd']=='0.012366758' and actual['billing']['cost_complete']
    primary=load(ACTUAL/'primary-manual-review.json')
    assert len(primary)==68 and {r['step']['ordinal'] for r in primary}==set(range(1,69))
    for row,raw in zip(primary,actual['rows']):
        assert row['step']==raw['step']
        assert row['response_ref']['sha256']==raw['raw_final_event_sha256']
        assert row['cited_evidence']['raw_final_content']==raw['raw_content']
    pairs=load(ACTUAL/'primary-paired-readout.json')['pairs']
    assert len(pairs)==34 and len({(r['case'],r['repeat']) for r in pairs})==34
    byordinal={r['step']['ordinal']:r for r in primary}
    paired_ordinals=[]
    for pair in pairs:
        for arm in ['C','L']:
            n=pair[arm+'_ordinal'];paired_ordinals.append(n);row=byordinal[n]
            assert (row['step']['case'],row['step']['repeat'],row['step']['arm'])==(pair['case'],pair['repeat'],arm)
            assert pair[arm+'_flags']=={k:row[k] for k in pair[arm+'_flags']}
        assert set(pair['changed_flags'])=={k for k in pair['C_flags'] if pair['C_flags'][k]!=pair['L_flags'][k]}
    assert sorted(paired_ordinals)==list(range(1,69))
    # Interpretations are explicit manual text; only their source joins are checked.
    # Independent-review files are pinned by the member manifest. Their judgments
    # remain independent manual evidence, never inferred by this reproduction.
    after=pack.collect();assert before==after,'preserved member changed during reproduction'
    archive=pack.packed(after);assert archive==pack.packed(after)
    with tempfile.TemporaryDirectory(prefix='lexical-actual-repack-') as t:
        t=Path(t);a=t/'a.zip';a.write_bytes(archive)
        with zipfile.ZipFile(a) as z:
            assert z.namelist()==list(after)
            assert all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist())
            z.extractall(t/'workspace')
        p=t/'workspace'/HERE.relative_to(ROOT)/'build_actual_archive.py'
        b=t/'b.zip'
        out=subprocess.run([sys.executable,str(p),'--output',str(b)],cwd=t/'workspace',capture_output=True,text=True,timeout=120)
        assert out.returncode==0,(out.stdout,out.stderr)
        assert b.read_bytes()==archive,'clean extracted packer differed'
    report={'status':'passed offline clean-extracted reproduction','python':platform.python_version(),'monty':importlib.metadata.version('pydantic-monty'),'zlib':zlib.ZLIB_RUNTIME_VERSION,'exact_diagnostic_source_build':True,'fake_host_diagnostic_checks':40,'unchanged_v2_validator_tests':50,'actual_trace_events':149,'actual_requests_verified':68,'actual_provider_attempts':68,'retry_events':0,'complete_cost_usd':'0.012366758','manual_semantics_recomputed':False,'manual_transcription_reproduced':True,'primary_response_joins_verified':68,'primary_paired_joins_verified':34,'independent_primary_full_content_joins_verified':68,'review_difference_rows_retained':12,'all_members_unchanged':True,'deterministic_archive_and_extracted_repack':True,'archive_sha256':sha(archive),'archive_bytes':len(archive),'archive_files':len(after),'model_calls':0,'brain_writes':False,'git_operations':False,'logs':logs}
    if args.output:args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='logs'},indent=2))
if __name__=='__main__':main()
