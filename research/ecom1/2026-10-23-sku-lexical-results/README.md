# Offline validator for the 68-call lexical diagnostic

Prepared while job `j8359aedb3a54484e876f62f0bba9221a` is queued. This directory contains **no real 68-call results**. It does not modify the frozen diagnostic package, contact Brain, dispatch inference, execute model actions, or assign semantic pass scores.

The target is source `d6280r1`, SDK 0.3.7, SHA-256 `dc5e1951f404dca549fe97a6fd38de36419ece9ecd0c3aa07d4f6369998bda3e`. Frozen request/plan hashes are enforced. `validate_trace.py` adapts the actual archived 16-call `verify_capture.py` schema, retaining exact request/provider/identity/cost checks while removing that earlier verifier's assumptions about final action type and outcome. The original verifier is rerun unchanged in an isolated temporary copy during tests.

## Run offline tests

From the workspace root:

```sh
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python research/ecom1/2026-10-23-sku-lexical-results/test_validator.py
```

The current 30 checks cover archived16 evidence and explicitly synthetic68 metadata; prompt/token/provider/source/job/trial mismatches; missing requests, responses, entire calls, stdout and retry events; immutable hash mismatch; truncated NDJSON/pagination; interleaved and duplicate calls; unpriced retries/errors; generation-evidence rejection; cancellation with all 68 retained cells; length-truncated and malformed model text; and cost mismatch. Synthetic replies are copied from archived16 solely to exercise the schema. They are not predictions or observations for the 68-call experiment. `test-results.json` records these checks, not research outcomes.

## Audit future harvested evidence

Preserve the full immutable trial NDJSON and the final single-trial summary. The summary schema follows the archived16 `summary.json` and additionally requires `job_id` from the immutable job receipt, exactly equal to the target job above. Do not insert that identity based only on a filename. Its `source` object must contain the submitted document, revision, SHA and SDK version; its trial must include the exact sealed trace blob hash/byte count and durable usage. Join provenance only from actual receipts. Truncated paginated output or a trace index is not a substitute for raw events.

```sh
python3 research/ecom1/2026-10-23-sku-lexical-results/validate_trace.py \
  --trace /absolute/path/to/trial-trace.ndjson \
  --summary /absolute/path/to/summary.json \
  --output /absolute/path/to/trace-audit.json
```

The validator emits a compact summary, and writes all 68 planned cells with full final response/error events, event hashes/sequence references, full call identities, separate attempt records, exact raw content and pending manual-review status. Truncated response-ID prefixes are only checked against the full response event; they never identify or deduplicate a call. Original NDJSON must be retained for all retry/error event bodies and immutable byte-level evidence.

A `reconciled` status means structural trace reconciliation only. It does **not** mean semantically correct, task complete, fully priced, or suitable for promotion. Billing has its own `cost_complete` flag. Every protocol deviation remains in `problems` and all rows remain visible. No favorable-repeat selection or semantic auto-pass scorer exists. Apply the frozen manual rubric separately to visible evidence.

## Request normalization and retries

Only the known SDK completion-token alias is normalized: source-level `max_completion_tokens` becomes wire `max_tokens`. No content, whitespace, instructions, ranking, history, reasoning, temperature or other settings are changed. Wire `stream=false` and the exact DeepInfra BF16 provider object are required. The SDK guide documents the two token parameter aliases; the archived SDK 0.3.7 provider-control source and request event provide separate wire evidence. `normalization-evidence.json` links these pinned artifacts. The archived16 requests already use `max_tokens`, so their reproduction alone does not prove the alias. An unexpected future wire representation is flagged for review rather than silently accepted.

A retry must preserve the full call ID and request, increment the attempt, follow an HTTP 429 without generation ID, choices or usage, and have an intervening observed `llm_retry` event. The bound is five attempts and at most 60 seconds of recorded retry delay. The validator does not infer retry events, recover missing events, add experimental repeats, retry failures or launch replacement jobs.

## Missing evidence and accounting

Absent events remain missing/unknown. Only explicit cancellation status or the frozen runner's valid cancellation metadata can support `unattempted_after_cancellation` after the last request marker. Otherwise absent later cells are `missing_or_unattempted_unknown`, with an incomplete-execution finding. A request marker without its full terminal event is incomplete even on cancellation. A missing entire call causes count/request mismatches; positional candidate mapping never certifies it. Full trace hash, byte count and seal checks detect truncated captures even if the visible prefix looks consistent.

Full provider error events are linked by call/attempt; SDK exception wrappers are not reconstructed from a 32-character preview. An HTTP success with malformed or length-truncated content remains available for manual review. A non-200 rejection body and an `llm_error` are preserved as different event kinds. Unknown event schemas fail closed and require a reviewed adapter.

Costs use decimal arithmetic. Every observed attempt must have explicit valid cost and token evidence to establish complete attempt accounting, and totals must agree with the settled trial summary and any single-trial job aggregates. A 429 without usage remains unpriced, even if the aggregate summary declares settlement and its reported total equals known successful costs. Additional durable per-attempt billing evidence would require a reviewed adapter; this validator never imputes zero. The carrier grade is ignored, and only StartTrial/Answer/EndTrial lifecycle RPCs are permitted. None of these checks establishes a model or full100 score improvement.
