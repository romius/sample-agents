# Completed C/L diagnostic: self-contained evidence and reproduction

This package joins the unchanged frozen preregistration, 17 fixture requests, 68-call plan and exact d6280r1 source with the completed job's raw CAS-verified traces, transport receipts, unchanged v2 validator/tests, and primary/independent manual reviews. The explicit `actual-members.json` member list is authoritative. The original diagnostic and validator archives and their seals are unchanged; their source members are incorporated byte-for-byte, with their archived manifests and seals preserved. Generated ZIPs, publication receipts and subsequent retry-study folders are excluded.

Job `j8359aedb3a54484e876f62f0bba9221a` used SDK0.3.7 and source SHA256 `dc5e1951f404dca549fe97a6fd38de36419ece9ecd0c3aa07d4f6369998bda3e`. All68 planned requests and complete responses reconcile, with68 provider attempts, zero retries, all DeepInfra, cost $0.012366758 complete. There are149 immutable trace events. Both trial/run CAS byte hashes are verified from220 bounded chunks in144 read batches; the summary blob is identified by the receipt but its raw CAS bytes were not separately downloaded. The carrier grade is irrelevant.

The frozen host-capture provenance is historical evidence, not present-day full-agent readiness. The experiment executes direct next-action LLM requests. It does not test STACK E deterministic early-answer paths or establish effects on the full100 score. Label deletion also changes request length, while scores/order/query/guidance remain present. Deferred catalogue requests were not executed. No model inference is made by packaging or reproduction.

## Reproduce from an extracted workspace

Use Python3.14.3, pydantic-monty1.2.0, zlib build/runtime1.2.12. Python/native wheel are pinned external runtime dependencies, not bundled binaries. With those dependencies cached:

```sh
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python /path/to/extracted/research/ecom1/2026-10-23-sku-lexical-results/publication/reproduce_actual_results.py --output /tmp/actual-results-reproduction.json
```

The script checks every member hash and original seal, rebuilds the exact diagnostic source from frozen inputs, runs40 fake-host diagnostic checks and50 unchanged v2 validator tests, reconstructs149 actual trace events, reconciles all68 actual request/response/cost records, and regenerates raw review inputs. It verifies all34 primary C/L pair joins, all68 independent/primary full-response joins and the12 retained classification/label difference rows. Verification timing is compared after removing only `seconds`, then restored to the original archived bytes. All other included files must remain byte-identical. It rebuilds the deterministic ZIP twice and from a further isolated extraction.

The primary transcription script reproduces already-authored judgments and verifies their exact response joins; it is not a semantic scorer. Independent manual judgments are preserved separately. Automated reconstruction cannot prove a human interpretation correct. Any differences between reviewers remain visible in their separate files and comparison notes; packaging does not overwrite or adjudicate them.

To rebuild only the archive, run `build_actual_archive.py --output /tmp/actual-results-evidence.zip` with the same pinned Python/zlib runtime. ZIP members use explicit sorted paths, fixed1980 timestamps and0644 permissions. Determinism is claimed for the pinned runtime, not for arbitrary zlib versions. The archive carries its own explicit member manifest; the manifest cannot hash itself. Final ZIP SHA256 and clean-extraction report are separately published metadata, excluded from the ZIP to avoid self-reference.

## Frozen review outcome and differences

Both reviewers and the final root reconciliation recommend **not integrating lexical-label deletion** on this evidence. F2 yields deferred catalogue requests, while F3 yields contradicted flat-head final selections; no task-success or overall semantic score is inferred. `actual-results/RECONCILIATION.md` supplies the final interpretation. Historical primary text that says independent review is pending remains unchanged; the later reconciliation supersedes that status.

`independent-primary-comparison.json` and its unchanged reproduction script retain12 row-level differences: E3 exact-ID conflict flag (four rows), F3 L unsupported-positive breadth (two), F4 positive-control applicability (four), and F2 L action-label spelling (two). N3 literal quotation-policy concerns remain separate from selecting/citing an excluded product. Both original68-row sheets remain intact. Exact model contents and response hashes support direct inspection; the package does not force consensus or convert these flags into scores.
