# Independent whole-agent replay of the narrow OCR repair

**112 executions pass** for the final candidate SHA256 `229b630545bcb5414593bd96a8fb92ae5283c31e717120a1069f4b4e6f062468` (62,662 bytes), readable SHA256 `928b1928524b863618fd2a526952229bce3f00cdc325251f5c3034a9239c8ea6`. Exact parent is the verified d3909r1 STACK E record, SHA256 `56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c`. Neither source was modified by this review. The candidate remains unsubmitted; no live score improvement is established here.

The matrix is 14 OCR cases × parent/candidate × readable/packed × CPython/native Monty. Native execution uses Python3.14.3, pydantic-monty1.2.0, 10-second feed/turn limits and1,000 suspensions, with **method-only ClassInstance** exposure of task/call/answer/llm/usage. These are complete source executions, not extracted parser calls. Requests, answers and writes agree across all four source/runtime combinations for every version/case. There are zero unmatched RPCs and zero actual inference or ECOM SDK calls.

## Authoritative archived inputs and explicit simulation

Inputs come from t076 of winning full100 job `j55b49f183413406c850865f5aa62012b`, trial `vm2-M6yYmGWfpg1xh2ziPkmn2MQ3HJs`, immutable trace `dcd9333354fb1c5c72b39dc2e6c24dc5ffacbb2d70004ec9c384f26540b118fc`. All **135 RPC response events (259,432 bytes)** were downloaded, not synthesized. Each raw event byte count matches its trace index. Each Read content hash matches its server hash; all request/response methods and sequence joins are checked. There are126 distinct archived Read files.

The actual failing run fetched Tree(`/proc`, level0), followed by all101 catalogue files and17 store files. The candidate now asks for Tree(`/proc/catalog`, level0) and Tree(`/proc/locations`, level0), which were not actual requests in that trace. The host derives those two responses by selecting the exact corresponding child subtrees from the archived level0 Tree, retaining every field/descendant and adding no entries. Every leaf is covered by an actual Read. `world-provenance.json` records the derivations, exact source event, leaf paths and all original RPC locators. The bootstrap Tree(`/`, level2) is replayed exactly; it does not expose additional descendants. Completeness is evidence about this archived response, not a new live-server promise.

The first `llm` call receives the actual archived routing response selecting `/docs/purchase-request-crosslist.md`. When deterministic processing declines, subsequent `llm` receives an explicit fixed unsupported-terminal stub. This keeps the experiment confined to the handler's decision; it does not predict how a real model would recover. Both versions receive the same response rules. Router request hashes are retained. The script makes no wire-request identity or model-quality claim.

Successful report writes receive a **declared simulated acknowledgement containing the exact requested destination**; the failing archived trial never wrote a report. No other world mutation is allowed. There is no invented catalogue/store record or silently substituted RPC. The method-only host is an important startup check but cannot prove equivalence to every private SDK behavior. Existing report write/readback/error handling is unchanged and not fault-tested by this package.

## Independent oracle and outcomes

`manual-oracle.json` transcribes the five actual OCR rows independently of candidate parsing or rendering: quantities9,8,6,4,9 (36total), five exact descriptions and every requested property. `prepare.py` compares those values with actual catalogue records and derives same-day stock from the actual Graz Center inventory. The TSV columns/reasons follow the saved policy. In particular, row2 requests flow410 while its named product has420, so its match is property_mismatch with blank SKU/name and zero availability/fulfillment. Other rows fulfill8,2,0,0 with shortfalls1,4,4,9. Expected TSV SHA256 is `0bb89033e80c45603f6c9775c0f235b88a0196a3312844fa549d57fde3a3fc8d`.

| Case group | Parent | Final candidate |
| --- | --- | --- |
| Actual five-row OCR with hash-delimited scanline total | Declines, no Write | Exactly one Write matching independent TSV, path-only OK with exact upload/policy refs |
| Same five rows with plain totals | Exact TSV success | Identical success |
| Plain total plus duplicate or conflicting noisy total | Ignores noisy total and writes | Declines before Write |
| Duplicate plain total, wrong unit sum, misleading prose prefix | Declines | Declines |
| Fresh two-row Bosch body/kit request with plain totals | Exact independently derived TSV | Identical success |
| Same fresh request with noisy total | Declines | Exact independent TSV |
| Dotted-I, dotless-i and long-s marker spellings | Declines | Declines in both runtimes |
| Fresh sander/hedge requests whose matched products lack branch inventory rows, clean/noisy | Declines | Declines |

Successful whole-agent paths perform129 RPCs and one frozen router call; declining paths use8 or128 RPCs depending on whether parsing or later inventory evidence caused the decline, then the explicit unsupported stub. The results retain exact call logs, derived-tree requests, stdout, source/input hashes and output bodies.

The initial fresh sander/hedge fixture was intended as a positive clean control, but revealed that `i2c_same_day` returns None for absent branch inventory rows. Both exact sources therefore decline. This is recorded as a pre-existing coverage boundary rather than silently changing the oracle or claiming the OCR patch fixes it. Its stored TSV is a hypothetical absent-as-zero calculation, not a demonstrated accepted grading oracle. A different fresh positive fixture uses actual present inventory rows, both with zero available stock, to distinguish zero quantity from a missing row.

`initial-review/` preserves the original bea10fc candidate and its56 ASCII-case executions. A separate reviewer found Unicode regex case-folding differences, so that candidate was superseded by the explicit ASCII-case-pair version tested here. The initial result is not universal parity evidence. Final tests expressly cover three relevant non-ASCII negative controls; they do not establish equivalence for all Unicode input.

## Reproduction and limits

Run `python3 prepare.py`, then:

```sh
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python replay.py
```

Run from this directory or give absolute script paths. `prepare.py` reconstructs source maps/provenance and both positive TSV oracles; frozen absent-inventory fixtures are retained as inputs. Candidate build/parser tests and independent parser review live separately in `../2026-10-23-stack-e-ocr-repair/`. This package tests the complete archived handler path and targeted fresh counterexamples; it does not validate unrelated task families, live grading, mutation fault recovery, or inference behavior after fallback. No production changes, Brain mutations, submissions, cancellations or Git edits were made. Read-only Brain session s7706 was discarded.

## Complete release bundle

`package_bundle.py` archives all three sibling record-audit, repair and replay folders at their original workspace-relative paths. It includes the exact d3909 parent/parser-donor/build closure, initial and final candidate history, complete archived RPC source events, derivation ledger, independent 44-case controls and final independent review. `BUNDLE-SHA256SUMS.json` pins every included file except itself. TAR metadata is normalized; gzip OS byte9 is set to255 with flags0 so Python3.12 and3.14 emit identical archives. The native interpreter/wheel must be supplied using the pinned dependencies; the public host source is preserved for identity verification.

A clean extracted bundle reproduced the record and candidate byte-for-byte, then all300 parser evaluations and112 whole-agent executions, leaving all116 provisional bundle files unchanged. The final bundle additionally contains this verification record and finalized reviewer text. Run the entire reproduction from any directory with:

```sh
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python /path/to/extracted/research/ecom1/2026-10-23-stack-e-ocr-replay/reproduce_bundle.py
```

See `clean-extract-verification.json` for the tested source pins. The cache must already contain Python3.14.3 and Monty1.2.0 for offline execution.
