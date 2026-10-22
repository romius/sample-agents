# Offline validator evidence bundle

This bundle preserves the original validator and seven-file seal alongside the separately sealed v2 correction, final independent review, all 64 v2 dependencies, and four additional archived request events cited in the review. Paths are relative to the workspace root. No publication records, generated archives, bytecode, or external runtime binaries are included.

Use `validate_trace_v2.py` for future complete target-trace audits. V1 remains historical evidence. Structural reconciliation, billing completeness, and manual semantic judgment are separate. There are no actual results from the target 68-call diagnostic in this bundle. Archived retry request subsets support transport-ID and accounting observations; they are not a complete immutable retry trace. Whole-chain positive controls are explicitly synthetic.

Rebuild from the extracted workspace root with Python 3.14.3 linked against zlib 1.2.12:

```sh
python3 research/ecom1/2026-10-23-sku-lexical-results/build_archive.py
```

Only Python's standard library is required. The builder requires the pinned Python and zlib versions, checks both seals and all dependency hashes, writes sorted ZIP_DEFLATED level 9 members with fixed timestamps and permissions, and runs the 50-test v2 suite once in a clean temporary extraction. That suite also reproduces the original archived16 verifier. Its output must match the sealed test report byte-for-byte. The extracted builder must produce the identical archive. Original workspace inputs are verified unchanged afterward.

The sibling generated `archive-manifest.json` lists each member's bytes and SHA-256. Generated `BUNDLE.json` records archive size/hash, runtime, reproduction checks and important source/fixture/plan hashes. Both are outside the ZIP to avoid recursive self-hashes, as is the ZIP itself. Reproducibility is promised under the pinned runtime, not across zlib versions. These packaging additions do not alter either validator seal. No model calls, world actions, Brain writes or Git operations are performed.
