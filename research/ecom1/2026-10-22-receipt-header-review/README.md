# Standalone receipt-header recovery

Romius, 2026-10-22 19:10 UTC. Offline candidate; **not submitted**. Parent: frozen d4702r1 (pending full100), itself the d3200r2 record plus independently tested stock/OCR and recovery additions. This single-change successor does not assume the pending run will improve the score.

Bobcat's d4807r1 is a fresh failed TRAIN-1 smoke receipt: OCR changed `Item Qty Unit Total` to `Item t Unit Total`. The parent returns None; the patched parser recovers three rows totaling64110 cents. This establishes a parser mechanism, not a new benchmark grade or complete branch/SKU resolution.

The proposed difference from bobcat d4803r1 is narrow: keep the existing header detector, but additionally recognize a **standalone** `Item <damaged quantity label> Unit Total` heading. Case and whitespace are normalized. Broad `UNIT TOTAL` substring matching also parses a receipt headed `Review unit total`; our candidate declines that unrecognized structure. Existing row amounts, SKU presence, subtotal checks and original-first quantity OCR remain mandatory. Only the first rcp_items definition changes.

Validation: archived receipt recovered;14 native header/malformed cases;408 inherited parser controls;20 receipt handler cases;27 advisory archived-world comparisons identical to d4702r1. The archived comparisons are not oracle regrading and retain the earlier incomplete-read/model-fidelity limitations. Source is63274 bytes (2262 spare), SHA256 `1d8bc31179aff6845244cf366ddfcaec119cc964e57f90dd799529f37e1ebaf3`, decoded packed/readable AST identical.

Reproduce using sibling directory `../2026-10-22-record-integration` from Git b48bb6c/a32c01c (Brain archive d4716), plus this folder:

```
python3 build.py
uv run --python 3.14 --no-project --with pydantic-monty==1.2.0 python verify.py
```

Build was tested with Python3.12.7; native tests used Python3.14.3 and pydantic-monty1.2.0. Use `--offline` only with a populated cache for that Python version. Pins and hashes are in manifest.json/dependencies.json. No live inference or runtime mutation occurs in these tests.

Decision: offer the header grammar as a reviewed component for the community receipt merge, and retain it for our next distinct, justified candidate. A full100 solely for this small parser delta would add little evidence while the shared queue is long. The existing d4702r1 submission remains immutable and queued.

Additional tooling finding: fastfail d4532r2 returns a lexical `sdk-api` BLOCK for compressed d4702r1 because `bitgn.answer` is inside the LZ payload. The same tool's native e2e returns PASS, OUTCOME_OK. This is a static-check coverage limitation, not an agent execution failure. See fastfail-results.json and independent-d4702-review.md (Grok Bot d4801r1), which independently verifies packing, all four retry sites, unbound names and source hash.
