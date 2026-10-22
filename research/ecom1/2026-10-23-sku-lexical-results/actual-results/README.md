# Completed 68-call diagnostic: structural readout

Job `j8359aedb3a54484e876f62f0bba9221a`, run `run-22rKCszzuEoyDjuakc6fpA1Tf`, completed at 2026-10-22 23:14:49 UTC. Exact source is d6280r1, SDK 0.3.7, SHA-256 `dc5e1951f404dca549fe97a6fd38de36419ece9ecd0c3aa07d4f6369998bda3e`. The frozen plan contains all 17 fixtures × C/L × two counterbalanced repeats.

Unchanged independently reviewed `../validate_trace_v2.py` returns **reconciled**, no structural deviations. All 68 planned calls have exact verified requests and complete final responses. There are 68 distinct transport attempts, zero retry events, and 68 explicitly observed DeepInfra providers. All finish reasons are `stop`; no length stops or missing responses were found. This is not a semantic success tally.

Every response has usage evidence. Costs sum to **$0.012366758**, with 224,504 prompt tokens and 23,883 completion tokens (248,387 total), matching the settled job and trial accounting. Stdout is 23,496 bytes. The diagnostic carrier's zero grade is intentionally irrelevant; no full100 score claim follows.

All 149 immutable events were harvested through a read-only Brain session (`s7712`, discarded afterward). An initial 100-item printed index exceeded the 24,000-byte Brain output limit and was discarded. Complete 50/50/49 index pages were used instead. A total of 220 bounded chunks in 144 read batches preserves every event's exact text and offset. `reassemble.py` verifies chunk continuity, indexed offsets, event identity, complete scope lengths, and both official CAS hashes:

| Trace | Bytes | SHA-256 |
| --- | ---: | --- |
| Trial | 1,297,613 | `6b5c7026c7d3def4d6a5d60e954f2881d098cd4a52b1df4282b662dc7661f980` |
| Run | 20,030 | `639cc9bb7b38c42fe71ddb31944b662005046aa9cd8f28a1c551b4268c8c94ea` |

`receipts/result.json` preserves the complete tool receipt. The validator summary adds `job_id` from that same receipt's `job.id`, after checking run/source identity; it is not inferred from a filename. The summary blob ID is recorded but its raw CAS bytes were not independently downloaded. Trial and run trace bytes were independently reconstructed and verified exactly.

Reproduce offline from the workspace root:

```sh
python3 research/ecom1/2026-10-23-sku-lexical-results/actual-results/reassemble.py
python3 research/ecom1/2026-10-23-sku-lexical-results/validate_trace_v2.py --trace research/ecom1/2026-10-23-sku-lexical-results/actual-results/trial-trace.ndjson --summary research/ecom1/2026-10-23-sku-lexical-results/actual-results/summary.json --output research/ecom1/2026-10-23-sku-lexical-results/actual-results/validation.json
python3 research/ecom1/2026-10-23-sku-lexical-results/actual-results/prepare_review.py
```

`manual-review-inputs.md` and `.json` expose all 68 complete answers for human/agent assessment under the frozen preregistration. Their event IDs and full response IDs link directly to the trace. No semantic auto-pass scorer was used. False OK, unsupported positive, qualifier loss, contradicted option, controls and deferred/malformed output require separate visible-evidence review. In particular, hidden F2 tail facts must not be treated as known model evidence, and a supported option does not necessarily establish uniqueness.

The C/L intervention deletes two sibling lexical diagnostic arrays. It retains match scores/order, query text and shared decision rules; it also changes request length. Results cannot isolate semantic labels from attention or length effects. These observations do not establish a score improvement or justify baseline promotion. The frozen offline archive and original v1/v2 seals remain unchanged; actual results live in this separately added directory.
