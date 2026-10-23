# d4702: all 83 full-credit tasks, answer and execution-summary audit

All 83 official grade-1 tasks have been manually reviewed against their exact StartTrial instruction, final Answer request and acknowledgement, and complete agent_finished stdout. See `success-review.md` for the concise table and `success-review.json` for exact messages, refs, stdout, per-event paths/hashes and uncertainty. Official grades remain unchanged. This closes the missing successful-task final-log coverage; it is not a complete independent audit of every action or business fact.

The source is d4702r1, SHA256 `b5bf80e4eb3eb4f5ee86dfad2442606e33da8102a9edbac85222ecc395d507f8`, job `jfdd875bba6ba4773a549e8703764efa9`. The sibling `result.json` and `instructions-all100.json` are exact input dependencies pinned in `event-manifest.json`. This audit does not compare same-ordinal tasks across runs as paired worlds.

## Evidence and limits

Session s8029 was read-only and finished with discard. `receipts/` retains returned Brain responses, including exact bounded trace-event text. Tail positions were derived from the next actual StartTrial sequence, filtered by the returned trial ID; every tail has an Answer request, acknowledgement and agent_finished. t100 used its own discovered index. Every task and trial identity, body byte length, index body length, official output byte count and ecom-call count was checked. No body was truncated. `events/` contains the exact event text bytes, not reserialized event objects.

There are 271 unique complete events: 249 core events (three per success), plus 22 supporting RPC events for t079 and t091. Seven Read content hashes verify against the server's sha256 fields. Tail indexes are intentionally incomplete event indexes; these 83 complete trial CAS files were not reassembled. The official CAS descriptors are retained as provenance, not mislabeled as independently verified full-trace hashes. Full provider requests/responses were not harvested here.

L2 evidence means instruction + Answer/ack + full stdout with sampled tail index. L3 additionally includes targeted RPC bodies for t079/t091. Stdout can contain intended model actions, refusals and handler summaries; it is not universal proof each logged step executed. No absence of a logged action is treated as proof no mutation occurred. Numeric results, SKU resolution and policy eligibility remain unverified wherever their supporting records were not fetched. The manual notes are explicit judgments, not an automated semantic scorer.

All 83 agent_finished usage objects show zero model calls while the official successful-task result rows total 179 calls. These finishing snapshots are not the final accounting authority. Use official result usage, never infer zero spend from agent_finished.

## Concrete findings retained despite grade 1

- t007, t027, t054, t079, t090 and t091 recover eight malformed-action responses in total. Final credit does not erase those reliability/cost signals.
- t045's model report contains `/proc/stock/...`; the actual final refs remove that placeholder. This is a filtered proposal, not a fabricated citation delivered to the user.
- t091 executes `/bin/sql`, which returns exitCode 1 and a SQL connection/cluster-down error, not Exec404. It later Reads the store JSON and receives a successful CSV Write acknowledgement. The requested header and three written family rows are preserved. The final answer includes a leading space before the export path, despite the path-only instruction. Future inventory columns have not been independently recomputed.
- t079's authoritative identity is customer cust-0001. It successfully Reads basket-0075 owned by cust-0146 and basket-0074 owned by cust-0145 during discovery, then Reads its own two active baskets and writes the newer basket-0001. The targeted check confirms original fields/line preserved and exactly one requested saw line appended, with acknowledgement. No foreign data appears in the final answer or targeted Write. The unnecessary foreign-record access deserves investigation; this package does not assert external disclosure or settle whether ownership-discovery Reads themselves violate the policy.
- t036/t056/t076 return the requested export paths with upload refs, but stdout only says CROSSLIST_PREVIEW prepared. Those summaries alone do not certify TSV contents. t100 gives a disjunctive active-or-discounted blocker; its precise blocker is not established by this final log.
- t061 contains literal escaped unicode separators in its clarification text. This is a presentation observation, not a wrong-product finding.

## Reproduce without network or inference

From any working directory, with the parent result and instruction files in place:

```sh
python3 /absolute/path/to/success-evidence/build_review.py
python3 /absolute/path/to/success-evidence/verify_targeted.py
```

Both scripts use only the Python standard library. The first reconstructs raw event files and the table/JSON by joining explicit `manual-notes.tsv` observations to exact evidence. It does not infer those judgments from keywords. The second verifies bounded, individually inspected witnesses and structural properties. `SHA256SUMS.json` seals this subfolder; generated evidence and original receipts are included. No production source, Brain document, benchmark job, or Git state was modified.
