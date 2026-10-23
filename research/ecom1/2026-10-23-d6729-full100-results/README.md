# d6729 full100 — partial capture in progress

Job `jc2949c1cd1b84139a2eac424ef598966`, run `run-22rM8NBxSKHyZan5Db8N6VWR4`, exact d6729r1. The first frozen snapshot has **73 completed tasks, zero execution failures, grades pending**; t074 is in progress. This is not a completed evaluation or a score claim. The next scheduled job refresh is 04:30 UTC. The parent agent owns current-record comparison and any promotion.

`receipts/snapshot-01.json` is one exact official result snapshot. Its original 69,143-byte JSON print exceeded the display window; the remaining bytes were recovered through `brain.output(3, offset=...)`, not through repeated calls to a changing live result. Raw response receipts preserve the reconstruction. The recovered original text SHA256 is `82aac67846f86b15fdc4c422d063b534b31d43947cdda838e604fb2b148dabef`.

## Completed-task evidence retained so far

`partial-review.json` contains all t001–t073 actual StartTrial instructions/hashes, final Answer arguments, full agent_finished stdout/hashes, authoritative snapshot usage and exact event references. Every task is joined using actual task/trial/run IDs. Every retained lifecycle event is reconstructed from explicit UTF-8 byte offsets and checked against the compact trace index's declared length, kind and trial identity. There are 511 retained lifecycle events: StartTrial request/response, Answer request/response, agent_finished, EndTrial request/response for each of the 73 tasks. No agent_error event was present in the traversed indexes.

The full index was traversed for each task to select lifecycle events; its total indexed bytes match the immutable sealed-trial trace size. Only the selected index entries and full lifecycle events are retained at this stage. The listed CAS digest identifies the official entire trial; **none of these selected lifecycle traces is claimed to reproduce that full CAS digest**. Full loss indexes and all loss-side model responses/RPC requests remain to be collected after grades become available. No successful task is independently certified business-correct merely from an Answer or outcome token. Printed usage snapshots and agent_finished usage are preserved verbatim; the official settled per-trial result is the accounting source.

The 27 remaining task slots are not captured by this snapshot. Matching task ordinals in another evaluation do not imply equal instructions, inputs or worlds, and no causal improvement is inferred.

## Exact submitted source

The local nine-file source/build closure is copied from the already reviewed OCR repair, without unrelated replay or archive contents. `source-pins.json` retains original local paths and exact hashes. `verify_source.py` rebuilds in a temporary directory and requires all nine files to remain byte-identical, including the exact d4353 parent repack and one-line OCR successor.

- Submitted source: d6729r1, 63,411 bytes, SHA256 `420e904a4cb502221f8609f99bd0f62370deda775abb41b5be9880042f0b7bf8`.
- Parent: d4353r1 / readable d4354r1; original packer d3268r2.
- The only source change is the previously reviewed ASCII hash-scanline prefix normalization before strict OCR total parsing. No submitted source or job was changed during capture.

Reproduce the current offline checkpoint with `python verify_lifecycle.py` and `python verify_source.py` from this folder. The first script intentionally requires the frozen 73-task snapshot; later capture will add an explicit final verifier rather than silently rewriting its historical meaning. Read-only Brain session s8290 remains open for the scheduled refresh. No paid calls, Brain writes, Git edits, cancellation or publication occurred. The prior TRAIN-4 stock extension remains sealed and unchanged.
