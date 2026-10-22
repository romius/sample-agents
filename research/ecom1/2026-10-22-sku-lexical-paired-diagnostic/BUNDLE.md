# Reproducible offline evidence archive

Run from the workspace root with Python 3.14.3 and pydantic-monty 1.2.0:

```sh
python research/ecom1/2026-10-22-sku-lexical-paired-diagnostic/build_archive.py
```

This creates `evidence-bundle.zip` plus the adjacent `archive-manifest.json` (every member's SHA-256 and size) and `archive-verification.json` (archive SHA-256, size and validation). These three generated outputs and `SHA256SUMS` are excluded from the ZIP to avoid self-reference. Existing reviewed sources and captures remain unchanged.

The ZIP contains the final runtime-capture directory, this prepared diagnostic directory including all frozen inputs and independent review, the six monitor-2233 evidence files, and the exact source/build/capture dependency closure at workspace-relative paths. It also preserves the original diagnostic verifier with its direct inputs for provenance; that prior runner is not the current prepared runner. The protocol contract is stored at `proto/bitgn/vm/ecom/ecom.proto`. No archive member contains `..`, an absolute path or a symlink. Python caches and files named for publication, submission or post-publication are excluded. The separate provider-control archive is outside this bundle; its monitor summary is evidence only.

Members are sorted, timestamps fixed to 1980-01-01, mode fixed to regular 0644, and compression set to `ZIP_DEFLATED` level 9. Python and build/runtime zlib versions are recorded in the verification report; byte reproducibility is claimed within that pinned runtime, not across zlib versions. Two writes must be byte-identical. An isolated extraction runs the diagnostic build and all 40 fake-host verifier executions, checks exact source/readable/fixtures/plan/review-sheet/manifest hashes and compares verifier results excluding timing. It then restores the preserved verifier timing bytes in that temporary extraction, loads the extracted archive builder, and requires the extracted archive rebuild to be byte-identical. All original source members are rehashed before publishing the archive file.

Runtime capture is **not regenerated during sealing**: its saved timing values are nondeterministic, and its reviewed results and request bytes must remain frozen. The capture code and complete dependencies are available for a separate fresh reproduction. No model calls, ECOM actions, Brain edits, job submissions or benchmark evaluations occur in archive validation. Preparation and packaging establish reproducibility only, without a model or score claim. The independent review covers the diagnostic; the archive builder's separate validation is recorded in its generated report.
