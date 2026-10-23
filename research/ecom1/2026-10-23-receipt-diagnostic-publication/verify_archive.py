"""Extract exact closure and rerun its four reproduction/review entry points."""
from pathlib import Path
import hashlib, json, os, subprocess, sys, tarfile, tempfile
P = Path(__file__).resolve().parent
meta = json.loads((P/'publication/archive.json').read_text())
archive = P/'publication/diagnostic.tar.xz'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == meta['sha256']
scripts = ['diagnostic-plan/reproduce.py', 'diagnostic-runner/reproduce.py',
           'diagnostic-review/review_plan.py', 'diagnostic-review/review_runner.py']
with tempfile.TemporaryDirectory(prefix='receipt-diagnostic-closure-') as td:
    root = Path(td)
    with tarfile.open(archive) as tar:
        assert sorted(tar.getnames()) == sorted(meta['files'])
        tar.extractall(root, filter='data')
    def check():
        for name,pin in meta['files'].items():
            data = (root/name).read_bytes()
            assert len(data) == pin['bytes'] and hashlib.sha256(data).hexdigest() == pin['sha256'], name
    check(); reports = []
    for script in scripts:
        result = subprocess.run([sys.executable, str(root/'research/ecom1/2026-10-23-d4353-receipt-handoff'/script)],
            cwd=root, env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}, capture_output=True, text=True)
        assert result.returncode == 0, (script,result.stdout,result.stderr)
        reports.append({'script':script,'stdout':result.stdout})
    check()
report = {'status':'PASS','archive_sha256':meta['sha256'],'files_byte_identical':len(meta['files']),
          'scripts':reports,'live_model_calls':0}
(P/'publication/verification.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k != 'scripts'}))
