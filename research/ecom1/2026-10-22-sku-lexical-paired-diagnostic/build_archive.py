"""Seal reviewed offline evidence, reproduce from extraction, never dispatch.

ZIP_DEFLATED level 9 is deterministic within the recorded Python/zlib runtime.
Names are workspace-root relative; timestamps, permissions and ordering are fixed.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zipfile
import zlib

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
WORKSPACE = HERE.parents[2]
RUNTIME = RESEARCH / "2026-10-22-sku-lexical-runtime-prompts"
MONITOR = RESEARCH / "2026-10-22-monitor-2233"
OUTPUT_NAMES = {"evidence-bundle.zip", "archive-manifest.json", "archive-verification.json", "SHA256SUMS"}
REPRODUCED = ("agent.py", "readable.py", "fixtures.json", "call-plan.json", "manual-review-sheet.json", "manifest.json")
REVIEWED = {
    "agent.py": "dc5e1951f404dca549fe97a6fd38de36419ece9ecd0c3aa07d4f6369998bda3e",
    "readable.py": "52c33ff84e7f1dfb59a83d5c80af787688518530640262b34a15f02fa3cf79e7",
    "fixtures.json": "c2dd7b4f5917d6118351becaa7d9aeee7cd2c7d510cb1c5eb5076bb202b57571",
    "call-plan.json": "89550772dc28c05a1f73d06d5c09d325e7c78de5fb7e89fd5d2c7c1490ff97a5",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_file(path):
    return json.loads(path.read_text())


def excluded(path):
    parts = path.relative_to(WORKSPACE).parts
    return ("__pycache__" in parts or path.name in OUTPUT_NAMES
            or path.suffix in (".pyc", ".zip")
            or any(word in part.lower() for part in parts
                   for word in ("publication", "submission", "post-publication")))


def collect():
    files, pins = {}, {}

    def add(path, expected=None):
        assert not path.is_symlink(), ("symlink", str(path))
        path = path.resolve()
        name = path.relative_to(WORKSPACE).as_posix()
        assert not excluded(path), ("excluded dependency", name)
        data = path.read_bytes()
        if expected is not None:
            assert sha(data) == expected, ("pin mismatch", name)
            pins[name] = expected
        files[name] = data

    # Directories are deliberately narrow; unrelated research is not packaged.
    for folder in (HERE, RUNTIME, MONITOR):
        for path in sorted(folder.rglob("*")):
            if path.is_file() and not excluded(path):
                add(path)
    review = HERE / "independent-review.md"
    assert review.is_file() and "no remaining blocking finding" in review.read_text()
    for name, expected in REVIEWED.items():
        add(HERE / name, expected)
    dependency = json_file(HERE / "DEPENDENCIES.json")
    for relative, expected in dependency["frozen_files"].items():
        add(HERE / relative, expected)
    for item in dependency["upstream_provenance"].values():
        add(RESEARCH / item["source"], item["sha256"])
    for relative, expected in dependency["build_sources"].items():
        add(RESEARCH / relative, expected)
    verifier = dependency["original_verifier"]
    add(RESEARCH / verifier["path"], verifier["sha256"])
    for relative, expected in json_file(RUNTIME / "DEPENDENCIES.json").items():
        # ../../proto is resolved against research/ecom1, then normalized to a
        # workspace-relative ZIP name. No traversal member enters the archive.
        add(RESEARCH / relative, expected)
    original = (RESEARCH / verifier["path"]).parent
    prior = json_file(original / "manifest.json")
    add(original / "manifest.json")
    for name, key in (("agent.py", "packed_sha256"), ("readable.py", "readable_sha256"), ("fixtures.json", "fixtures_sha256")):
        add(original / name, prior[key])
    assert "proto/bitgn/vm/ecom/ecom.proto" in files
    return dict(sorted(files.items())), dict(sorted(pins.items()))


def write_zip(path, files):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in files.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def without_timing(report):
    for row in report["executions"]:
        row.pop("seconds", None)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "evidence-bundle.zip")
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.suffix == ".zip", "output must end in .zip"
    files, pins = collect()
    source_snapshot = {name: sha(data) for name, data in files.items()}
    expected = {name: sha((HERE / name).read_bytes()) for name in REPRODUCED}
    runtime_hash = sha((RUNTIME / "results.json").read_bytes())
    with tempfile.TemporaryDirectory(prefix="sku-lexical-bundle-") as temporary:
        temporary = Path(temporary)
        first, second = temporary / "first.zip", temporary / "second.zip"
        write_zip(first, files)
        write_zip(second, files)
        assert first.read_bytes() == second.read_bytes(), "nondeterministic ZIP"
        extracted = temporary / "extracted"
        with zipfile.ZipFile(first) as archive:
            assert archive.namelist() == list(files)
            for name in archive.namelist():
                assert not name.startswith("/") and ".." not in Path(name).parts
            archive.extractall(extracted)
        for name, expected_hash in source_snapshot.items():
            assert sha((extracted / name).read_bytes()) == expected_hash
        diag = extracted / HERE.relative_to(WORKSPACE)
        runtime = extracted / RUNTIME.relative_to(WORKSPACE)
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for command in ("build.py", "verify.py"):
            run = subprocess.run([sys.executable, str(diag / command)], cwd=extracted,
                                 env=environment, capture_output=True, text=True, timeout=180)
            assert run.returncode == 0, (command, run.stdout[-3000:], run.stderr[-3000:])
        for name, expected_hash in expected.items():
            assert sha((diag / name).read_bytes()) == expected_hash, ("rebuild differed", name)
        actual_report = json_file(diag / "verification.json")
        assert without_timing(actual_report) == without_timing(json_file(HERE / "verification.json"))
        assert sha((runtime / "results.json").read_bytes()) == runtime_hash
        # Rebuild the ZIP with the extracted builder in collection-only mode:
        # restore verification timing bytes so every preserved input is exact.
        verification_name = (HERE / "verification.json").relative_to(WORKSPACE).as_posix()
        (diag / "verification.json").write_bytes(files[verification_name])
        import runpy
        extracted_module = runpy.run_path(str(diag / "build_archive.py"))
        extracted_files, extracted_pins = extracted_module["collect"]()
        assert files == extracted_files and pins == extracted_pins
        third = temporary / "extracted-rebuild.zip"
        extracted_module["write_zip"](third, extracted_files)
        assert first.read_bytes() == third.read_bytes(), "extracted ZIP rebuild differed"
        for name, expected_hash in source_snapshot.items():
            assert sha((WORKSPACE / name).read_bytes()) == expected_hash, ("source changed during sealing", name)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(first.read_bytes())
    archive_manifest = dict(format="workspace-root-relative ZIP_DEFLATED level 9; sorted names; 1980-01-01; regular files 0644",
                            files={name: dict(bytes=len(data), sha256=sha(data)) for name, data in files.items()},
                            pinned_dependencies=pins)
    report = dict(status="passed offline; no dispatch", archive_name=output.name,
                  files=len(files), uncompressed_bytes=sum(map(len, files.values())),
                  archive_bytes=output.stat().st_size, archive_sha256=sha(output.read_bytes()),
                  python=platform.python_version(), zlib_build=zlib.ZLIB_VERSION, zlib_runtime=zlib.ZLIB_RUNTIME_VERSION,
                  compression="ZIP_DEFLATED level 9; byte reproducibility within pinned runtime", pydantic_monty=importlib.metadata.version("pydantic-monty"),
                  deterministic_two_writes=True, extracted_builder_byte_identical=True,
                  isolated_build_and_verify=True, verification_executions=40,
                  verification_equal_excluding_timing=True, exact_rebuilt_sha256=expected,
                  runtime_results_preserved_sha256=runtime_hash,
                  runtime_capture_regenerated=False, original_files_unchanged=True,
                  safe_workspace_relative_paths=True, no_model_calls=True, no_ecom_actions=True,
                  excluded=["__pycache__", "*.pyc", "*.zip", "publication/submission/post-publication names", "SHA256SUMS", "archive-manifest.json", "archive-verification.json"])
    for name, data in (("archive-manifest.json", archive_manifest), ("archive-verification.json", report)):
        (HERE / name).write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
