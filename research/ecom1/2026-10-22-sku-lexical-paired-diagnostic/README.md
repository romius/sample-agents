# Prepared C/L lexical-label diagnostic

**Local preparation only. Nothing has been submitted or published. No real model calls are made by building or verifying these files.** The root agent decides whether to proceed after meaningful review.

This prepares 17 complete runtime-captured fixture pairs × two counterbalanced repeats = **68 logical next-action requests**. C is the exact d5785r1 source-level SDK request. L deletes only the two lexical arrays from the same already-selected sibling rows. All other messages, settings, facts, original match scores/order, counts, truncation flags and shared guidance remain constant. The diagnostic never executes model-requested tools or interacts with an ECOM world. Its carrier Answer says the task was not attempted; the carrier grade is irrelevant.

The actual source being studied is d5785r1, readable d5789r1. It is preserved externally and not edited. The frozen runtime captures include full bootstrap, actual catalogue indexing, actual bounded observation generation, the scripted first catalogue action and the resulting next-action request. They are synthetic worlds with archived policy/identity scaffolding; scripted routing/first actions are not claims about what a live model will choose.

See `PREREGISTRATION.md` for the fixed manual semantic rubric and interpretation limits. No outcome-only semantic scorer exists here. `manual-review-sheet.json` is a blank 68-row assessment template, not a result.

## Input freeze and artifacts

`DEPENDENCIES.json` pins reviewed source inputs, copied request files, the capture report and independent review. `inputs/` is a byte-for-byte frozen snapshot; the Tree-depth and AGENTS catalogue-root corrections were independently reviewed before this snapshot was frozen. The final build reads those copies rather than mutable captures. A changed frozen input or pinned build source causes failure.

`fixtures.json` embeds every complete C/L request with canonical request hashes. `call-plan.json` fixes all 68 ordinals/cases/arms/repeats. `runner.py` adapts the original diagnostic runner: the exact request loop is retained, but raw-response and usage stdout dumps are replaced with bounded metadata after community d6210 demonstrated a 65,536-byte stdout overflow. `readable.py` and Huffman/LZ-packed `agent.py` are generated artifacts. The inherited Huffman, dynamic-programming LZ encoder and longest-match codec are all pinned as transitive dependencies. `manifest.json` records exact source sizes/hashes, SDK settings, request sizes, scope and restrictions.

The runner records each planned request ordinal, bounded case/arm/hash/status metadata, response ID (first 32 characters), finish reason (first 16), and error preview (first 32). It never prints raw responses, reasoning, message contents, or usage objects. Full responses/errors and usage must be harvested from immutable inference trace events and reconciled against the fixed plan. It adds no custom retry; SDK provider retries can increase transport attempts beyond 68 logical calls. Cancellation exceptions are rethrown immediately. It does not parse, repair, score, execute or otherwise act on model output. Only `bitgn.llm` and one terminal `bitgn.answer` are used; `bitgn.usage` is never fetched or printed.

## Checks and reproduction

Use an existing Python environment with `pydantic-monty==1.2.0`, and run from any directory:

```sh
python research/ecom1/2026-10-22-sku-lexical-paired-diagnostic/build.py
python research/ecom1/2026-10-22-sku-lexical-paired-diagnostic/verify.py
```

The local cached environment used for this research is `/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python`. No package download is needed. Build validates the exact captured SDK call, reversible C/L removal, U4's shared policy glossary and F2's real 32-indexed/16-eligible/10-shown exposure. Both compact and default JSON request serializations must fit 64 KiB; packed source must fit 65,536 bytes. These are byte limits, not token or dollar estimates.

Verification uses 40 fake-host executions: readable/packed × CPython/native Monty × success, third-call error, all-call errors, malformed/raw response shapes, cancellation on calls 1/34/68, huge responses with maximal Unicode ID/finish metadata, oversized Unicode errors, and cancellation hidden beyond a long error preview. Every requested input is checked against the independently reconstructed fixed order and canonical hash. Native checks use 10-second feed/turn limits and 1,000 suspensions. The host exposes no ECOM action hook. The fake host checks bounded metadata against complete raw inputs, including malformed objects and hypothetical tool actions that must never execute. It verifies total UTF-8 stdout stays below 65,536 bytes, including adversarial Unicode escaping. Raw response contents never enter stdout; the eventual readout must obtain them from immutable inference traces. Cancellation tests prove runner stopping/rethrow behavior under a simulated exception; they do not emulate platform transport cancellation.

## Limits

U4's glossary appears in the actual shared policy observation; F2's N15 is truncated and O15 lies outside the matched-family attachment, so neither hidden supporting SKU is an expected next-action answer. Every attachment has `pool_complete=false`. Evidence for a property is distinct from evidence for global uniqueness or a required final disposition. L retains original lexical rankings and shared token-coverage guidance, and is shorter than C; this is not a test of all lexical information or an isolated semantic-label effect. No result establishes benchmark improvement, full100 readiness, or permission for an automatic follow-on run.
