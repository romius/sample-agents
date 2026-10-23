# Exact d4353 inference retry comparison — offline, unsubmitted

This experiment compares two inference boundaries on the exact current record source d4353r1, without combining the separate OCR repair. It establishes scripted execution mechanics, not a score gain, provider reliability improvement, or a recommended winner. Independent review is required before any proposed evaluation.

## Source and changes

The unchanged record is 63,211 bytes, SHA256 `588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e`. `parent-build/` contains exact d4355r1 builder, d4236r1 packed/d4237r1 readable predecessors, d4228r1 receipt donor and d3268r2 lazy packer. `verify_inputs.py` reconstructs the exact record packed, readable, decoded payload and build receipt. `SOURCE-PINS.json` preserves input identities. The receipt donor is lineage evidence; the exact builder carries the applied receipt logic.

| Variant | Packed bytes | Headroom below65,536 | SHA256 |
| --- | ---: | ---: | --- |
| SDK-only containment | 63,969 | 1,567 | `f57cd915d9ac27fea0dd54ef39cacc26858363c59a3c961a6a3db4a747655d18` |
| One guest retry owner | 64,304 | 1,232 | `d54f36a91a88c9b2925a68111ac4815aa6d09a3e920b4218ea38e5cec80c5dbc` |

`build.py` applies the same edits to the original readable source and exact decoded payload, verifies AST equality, reproduces original packed bytes, and uses the record's exact lazy packer. No unrelated trimming is performed. `dispatch`, `recoverable_lookup_error`, `crosslist_parse_ocr`, and `i2c_cleanup` remain byte-identical within each original representation. No missing-Exec404 recovery or OCR normalization is added. Current d4353 already excludes Exec from its generic readonly404 whitelist; older StackE descriptions of broad Exec404 recovery do not apply.

The SDK-only comparison catches exceptions around only the three direct router/main/forced inference assignments. The helper already has a fallback catch; recognized cancellation now propagates through helper, I2C dispatcher and its outer catch. Router errors now return an empty route list and continue into the general fallback: this is **new behavior** for d4353, whose router previously propagated errors. It is not evidence that selecting fewer policy documents preserves task quality. Main inference error terminates the main loop, suppresses a further forced inference, and reports internal error. Forced inference error is caught before parsing; a deliberately invalid sentinel response reaches the existing parse-error catch and then an accurate inference-failed internal answer. Parsing, dispatch and Answer side effects remain outside the new inference catch. A forced Answer RuntimeError after a recorded side effect therefore propagates and is not retried or answered again.

The guest variant starts from this containment source and replaces exactly four `bitgn.llm` call sites with one helper. The helper contains the only remaining `bitgn.llm` call and permits at most three identical invocations for recognized transient errors. It recognizes explicit timeout/connection exception prefixes and anchored HTTP502/503/504, including known unconfirmed-cost wrappers. HTTP400/429, other statuses, unknown errors, recognized cancellation, malformed object/array JSON, all array bodies, and JSON generation evidence (`id`, `choices`, `usage`) do not retry. Mixed transient→400/unknown/cancellation sequences stop at the second invocation. This is conservative tested string coverage, not a complete provider-error or cancellation parser. No backoff or global budget is introduced.

Cancellation recognition uses anchored forms with optional known exception/HTTP/JSON `error.message` envelopes. Negated wording and `cancellation_policy` are not mistaken for committed cancellation. The actual SDK cancellation formatter is not demonstrated by these receipts. The archived SDK guide states committed cancellation blocks later host calls regardless of guest catches; a permissive fake host does not demonstrate post-cancellation live requests or mutations.

## Evidence and controls

**318 exact whole-agent native executions passed:**53 cases ×3 versions ×2 forms (readable and packed). Public Monty1.2.0 method-only `ClassInstance` exposes task/call/answer/llm/usage without lazy attributes. Limits are10 seconds per feed/turn and1,000 suspensions. There are also28 classifier cases run in both CPython and native Monty, totaling56 isolated classifier evaluations. These are distinct counts, not benchmark trials.

Every inference site is reached through the unchanged whole agent: router, main, forced report, and optional stock-exclusion helper. Persistent and recovering503/timeout,400/429/unknown, explicit JSON cancellation and negated cancellation are covered at all four sites. Healthy router/main/helper/forced requests match parent bytes, and packed/readable histories, actions and answers match. Repeated guest requests retain identical model/messages/settings. A third-attempt504 success and transient→terminal transitions test the loop boundary. Write/Delete/mutating Exec errors after recorded side effects execute once; a completed Write followed by inference failure also remains a single mutation. Forced Answer side-effect error is not swallowed by the inference boundary.

| Main inference scenario after successful router | Exact record | SDK-only | Guest owner |
| --- | --- | --- | --- |
| One503 then valid response |1call, propagates error |1call, internal answer |2calls, scripted completion |
| Persistent503 or observed-form timeout |1call, propagates |1call, internal answer |3calls, internal answer |
|400/429/unknown |1call, propagates |1call, internal answer |1call, internal answer |
| Recognized cancellation |1call, propagates |1call, propagates |1call, propagates |
| HTTP200 null content×3, forced non-report |3correction calls+forced, internal answer |same |same |

The fixture uses archived t076 from job `j55b49f183413406c850865f5aa62012b`, not d4353's own task world. All135 RPC responses and126 Read files are included and reverified against their archived event index and content hashes. Four derived Trees select exact children of the archived complete `/proc` Tree: level0 and level3 for catalogue/locations. Their actual subtree depth is2, so level3 introduces no additional descendants. No product or inventory field is invented. The inherited noisy OCR makes deterministic handling decline and reach the general loop.

The optional helper requires a **declared synthetic stock-exclusion request and catalogue/availability policy overlay** (`helper-overlay.json`), actual archived catalogue/stores, a scripted empty router selection, and `{}` helper response. This is d4353's reachable `stock_butnot` path. No function replacement occurs. The synthetic unavailable model and excluded ID are intentional reachability devices, not observed user input. A successful `{}` means the helper returns to existing general fallback, not correct extraction or successful stock resolution. Its fallback catch already existed in the record; router fallback did not.

`evidence/new-failure-t003/t045/t056/t059.json` are four actual provider-control timeout observations of **the same** `TimeoutError: The read operation timed out` suffix, with each agent error confirming the full unconfirmed-cost wrapper. They are from other source/world trials and support error-string classification only, not retry success or paid recovery for d4353.

`evidence/d4702-t016-events.ndjson` is the complete archived180,075-byte trace, SHA256 `69939661aa608af4b130ded9fcb0962b4cb619668bfdb9b7fd51b353e0ec07ab`. Exact response bodies at2642/2644/2646 have HTTP200, finish_reason stop, null final content, and action-like reasoning. Forced response2648 is a Read action, not a report. Those actual response bytes are **overlaid onto a different archived world and scripted prompts**; this is not an actual d4702 request/world replay. All versions make three distinct correction requests then one forced request, report internal error, and leave mutations empty. The guest wrapper performs no transport retry. Parent/candidate parity shows inherited handling is unchanged, not future provider behavior. The misleading inherited30-step-limit wording remains for this non-transport case and other malformed/length exhaustion; fixing it is outside this experiment.

## SDK accounting and limits

The pinned SDK0.3.7 guide permits at most five internal attempts and60 seconds waiting for qualifying429 rejections without generation evidence; timeout and other errors are not automatically retried. Exhausted429 receives one guest invocation. A scripted internally recovered429 returns successfully without any guest retry. **All physical-attempt counts here are declared fake SDK-policy simulations**, not executed SDK HTTP retries or observed budgets. The mixed429→503 control retains the possible15 physical attempts per three guest invocations (plus a separate successful router request), not a global trial/cost quota. Router/helper exhaustion can continue into a different main prompt. Main exhaustion does not start the forced request. Timeout/connection cost is unknown; another call can incur additional cost even when the first lacks an observed final result.

## Offline reproduction

Install pinned Monty1.2.0 in Python3.14.3, then run `python reproduce.py` from this directory. It copies the package to a temporary directory, rebuilds the exact parent and both candidates, revalidates archived input lineage, runs the classifier and whole-agent suites, and requires15 regenerated outputs to be byte-identical. No network, Brain, inference service or production mutation is used. `requests.json` retains complete scripted inference requests; `test-results.json` retains outcomes, action records and simulated counts. Runtime public ClassInstance source is preserved under `runtime/`.

All artifacts are offline and unsubmitted. No automatic preference, actual task-score gain or wholesale baseline recommendation follows from these mechanics. Live provider format coverage, reliability, cost and quality consequences remain unmeasured. Independent review is pending.
