"""Build and reproduce the offline validator evidence archive without live calls."""
import argparse
import hashlib
import json
import os
import platform
import runpy
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORKSPACE = HERE.parents[2]
ENVIRONMENT = dict(python='3.14.3', zlib_build='1.2.12', zlib_runtime='1.2.12')
LOCAL = [
    'validate_trace.py', 'test_validator.py', 'test-results.json', 'README.md',
    'DEPENDENCIES.json', 'normalization-evidence.json', 'VALIDATION.md', 'SHA256SUMS',
    'validate_trace_v2.py', 'test_validator_v2.py', 'test-results-v2.json', 'README-v2.md',
    'DEPENDENCIES-v2.json', 'retry-schema-evidence-v2.json', 'VALIDATION-v2.json',
    'SHA256SUMS-v2', 'independent-review.md', 'ARCHIVE-DEPENDENCIES.json',
    'BUNDLE.md', 'build_archive.py',
]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(path.read_text())

def collect():
    files, pins = {}, {}
    def add(path, digest=None):
        assert not path.is_symlink(), path
        path = path.resolve()
        name = path.relative_to(WORKSPACE).as_posix()
        assert not name.startswith('/') and '..' not in Path(name).parts
        data = path.read_bytes()
        if digest is not None:
            assert sha(data) == digest, ('dependency mismatch', name)
            pins[name] = digest
        files[name] = data
    for name in LOCAL:
        add(HERE / name)
    for seal in ('SHA256SUMS', 'SHA256SUMS-v2'):
        for line in (HERE / seal).read_text().splitlines():
            digest, name = line.split(maxsplit=1)
            assert name in LOCAL and sha((HERE / name).read_bytes()) == digest, (seal, name)
    for dependency_file in ('DEPENDENCIES.json', 'DEPENDENCIES-v2.json', 'ARCHIVE-DEPENDENCIES.json'):
        for name, digest in load(HERE / dependency_file).items():
            add(ROOT / name, digest)
    assert len(load(HERE / 'DEPENDENCIES-v2.json')) == 64
    return dict(sorted(files.items())), dict(sorted(pins.items()))

def write_zip(path, files):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in files.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE / 'validator-evidence.zip')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.suffix == '.zip'
    environment = dict(python=platform.python_version(), zlib_build=zlib.ZLIB_VERSION, zlib_runtime=zlib.ZLIB_RUNTIME_VERSION)
    assert environment == ENVIRONMENT, ('pinned runtime required', environment)
    files, pins = collect()
    hashes = {name: sha(data) for name, data in files.items()}
    with tempfile.TemporaryDirectory(prefix='sku-validator-bundle-') as temporary:
        temporary = Path(temporary)
        a, b = temporary / 'a.zip', temporary / 'b.zip'
        write_zip(a, files)
        write_zip(b, files)
        assert a.read_bytes() == b.read_bytes()
        extracted = temporary / 'workspace'
        with zipfile.ZipFile(a) as archive:
            assert archive.namelist() == list(files)
            assert all(not n.startswith('/') and '..' not in Path(n).parts for n in archive.namelist())
            archive.extractall(extracted)
        assert all(sha((extracted / name).read_bytes()) == digest for name, digest in hashes.items())
        local = extracted / HERE.relative_to(WORKSPACE)
        run = subprocess.run([sys.executable, str(local / 'test_validator_v2.py')], cwd=extracted,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                             text=True, capture_output=True, timeout=120)
        assert run.returncode == 0, (run.stdout[-3000:], run.stderr[-3000:])
        assert (local / 'test-results-v2.json').read_bytes() == (HERE / 'test-results-v2.json').read_bytes()
        tests = load(local / 'test-results-v2.json')
        assert tests['total_tests'] == 50 and tests['original_verifier_reused_unchanged']
        assert all(sha((extracted / name).read_bytes()) == digest for name, digest in hashes.items())
        namespace = runpy.run_path(str(local / 'build_archive.py'))
        rebuilt, rebuilt_pins = namespace['collect']()
        assert rebuilt == files and rebuilt_pins == pins
        c = temporary / 'c.zip'
        namespace['write_zip'](c, rebuilt)
        assert c.read_bytes() == a.read_bytes()
        assert all(sha((WORKSPACE / name).read_bytes()) == digest for name, digest in hashes.items())
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(a.read_bytes())
    manifest = dict(format='workspace-relative sorted ZIP_DEFLATED level9, 1980-01-01 timestamp, 0644 permissions',
                    environment=environment,
                    members={name: dict(bytes=len(data), sha256=sha(data)) for name, data in files.items()},
                    pinned_dependencies=pins)
    important = {name: digest for name, digest in hashes.items()
                 if name.endswith(('/agent.py', '/fixtures.json', '/call-plan.json', '/SHA256SUMS', '/SHA256SUMS-v2',
                                   '/independent-review.md', '/validate_trace_v2.py'))}
    metadata = dict(status='passed isolated offline archive reproduction', files=len(files),
                    archive_bytes=output.stat().st_size, archive_sha256=sha(output.read_bytes()),
                    uncompressed_bytes=sum(map(len, files.values())), environment=environment,
                    dependency_pins=len(pins), v2_dependency_pins=64, extra_review_evidence_pins=4,
                    exact_source_fixture_plan_seal_review_hashes=important,
                    tests=50, test_report_byte_identical=True, archived16_verifier_reproduced=True,
                    deterministic_double_write=True, extracted_builder_identical=True,
                    original_members_unchanged=True, both_seals_verified=True,
                    real68_results=False, model_calls=0, brain_writes=False, git_operations=False,
                    test_stdout=run.stdout)
    (HERE / 'archive-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (HERE / 'BUNDLE.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps({key: metadata[key] for key in ('status', 'files', 'archive_bytes', 'archive_sha256', 'tests')}, indent=2))

if __name__ == '__main__':
    main()
