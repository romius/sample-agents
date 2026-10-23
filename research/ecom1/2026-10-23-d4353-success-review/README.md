# d4353 record: all 90 full-credit tasks reviewed

All 90 official grade-1 tasks now have an individual manual review against their actual StartTrial instructions, exact final Answer request/acknowledgement and complete agent_finished stdout. `success-review.md` is the concise table; `success-review.json` retains the full answers, refs, stdout, event hashes, observations and limitations. Existing sealed record/OCR archives were not changed.

Exact run: d4353r1, job `j6d6d4adb60f241a4a1d111a9719b59dc`, source SHA256 `588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e`, SDK 0.3.7. Official full100 score is 0.9472095. This package reviews the 90 full-credit cases; the existing d4353-record-review covers the ten losses. No successful task has been regraded here.

## Exact evidence and scope

The 394 exact event bodies comprise 90 StartTrial responses reused from the sealed local record evidence, 270 new Answer/ack/agent_finished events, and 34 targeted RPC bodies. `upstream/` copies the exact result, all100 instruction manifest and original StartTrial receipts; `input-provenance.json` pins every copy. This avoids repeated instruction retrieval. New session s8064 was read-only and closed with discard. There were no inference calls, paid evaluations, production source changes or Git/Brain mutations.

Tail index positions come from the next actual StartTrial sequence and are filtered by exact trial ID; t100 has its own discovered index. All task/trial identities, body/index byte lengths, official stdout byte counts and ecom-call counts match. No saved body is truncated. One targeted branch Read content hash verifies against its server sha256. Raw event text in `events/` is preserved exactly, not reserialized.

L2 evidence = exact instruction, final Answer/ack, complete stdout and sampled tail index. L3 adds selected supporting RPCs for t039/t060/t091. The short cleanup trials have complete event indexes, but their full event bodies/CAS files are not reconstructed. No complete-action or full-CAS certification is claimed for these 90 successes. Stdout may describe intended actions, and unlogged details cannot be inferred absent. Catalogue properties, role authorization, stock arithmetic and policy eligibility remain unverified where their supporting data were not retrieved.

All 90 finishing usage snapshots report zero model calls, whereas their official result rows total 184. Use final official accounting, not these placeholder snapshots, to measure model use or cost. Do not confuse overall job counters printed inside stdout with per-task costs.

## Findings beyond the grades

- Eight malformed-action responses recover across six tasks: t002 (2), t020, t021, t025, t065 and t091 (2). These are reliability observations despite full credit.
- t091 successfully writes malformed CSV at seq12708→12709: seven header fields but eight fields in each of five product rows. A second successful Write12712→12713 removes one trailing zero per row, making all rows seven fields, before the final path-only answer. The preceding List /exports request12704→12705 fails with HTTP404; execution recovers. Both writes were actually acknowledged. Final future stock numbers are not independently recomputed.
- t039 List5273 contains 12 files; all seven literal `.tmp` matches have actual Delete requests5274…5286 and empty success acknowledgements, exactly matching the sorted final message. No nonmatching Delete or Write occurs in its complete index.
- t060 List8054 contains four files across log/tmp/txt extensions; all four actual Deletes8055…8061 are acknowledged and match the sorted answer. These are successful real archived operations, unlike simulated unobserved acknowledgements in the separate d4702 counterfactual replay. No post-delete readback is claimed. They do not resolve the known partial-Delete false-success concern.
- t079's stdout scopes discovery to cust-0002 and reports editing basket-0003 after reading its two baskets. d4702's t079 discovery involved foreign baskets, but task, product, identity and path layout differ; this is not evidence of a causal regression from source alone.
- t006/t022/t042/t051/t094 explicitly reject embedded override/injection blocks. These distinct input variations further prevent treating cross-run ordinal differences as paired source effects.
- Crosslist t016/t036/t056/t076 returns the required path/upload ref, but preview-only stdout does not verify TSV content. t100's active-or-already-discounted message leaves the exact blocker unspecified. Other rows retain their own evidence limitations.

## Reproduce offline

With Python 3.12 or later and only the standard library, from any working directory:

```sh
python3 /absolute/path/to/2026-10-23-d4353-success-review/build_review.py
python3 /absolute/path/to/2026-10-23-d4353-success-review/verify_targeted.py
```

The first reconstructs exact events and joins explicit manual observations in `manual-notes.tsv`; it does not generate semantic judgments from an automatic scorer. The second checks independent literal cleanup selection, actual acknowledgements, CSV shape and selected structural facts. `SHA256SUMS.json` seals the self-contained evidence and scripts. Parent/source artifacts are identified, not executed or modified by this review.
