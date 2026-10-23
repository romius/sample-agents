# Handover: final run known; detailed audit unfinished

Human requested ending this research round and handing off to a cheaper-model session. Harvesting stopped after the already in-flight batch. This file supersedes the running-status introduction in the historical README; that README and its 73-task checkpoint remain sealed unchanged.

## Official result

Job `jc2949c1cd1b84139a2eac424ef598966`, run `run-22rM8NBxSKHyZan5Db8N6VWR4`, d6729r1: **93.13638/100**, 100 completed, zero execution failures. 217 model calls, $0.029435706 complete accounting, 659,382 tokens. This is below the unchanged 94.72095 record. Root owns status/publication and confirmed no promotion.

`result.json` preserves the complete official final result. It came from a single recorded result call at session s8290 seq43; `receipts/final-result-pages.json` preserves its original 91,665-byte text and exact recovery receipts. Six zeros: t001, t025, t042, t047, t048, t091. Five dispatch partials: t004, t014, t024, t044, t064. `loss-list.json` preserves every exact grade detail and sealed trial CAS reference. No matching ordinal is assumed to imply a matching world or causal regression.

## Captured and verified

- t001–t091 complete selected lifecycle events: StartTrial request/response, final Answer request/response, complete agent_finished stdout, EndTrial request/response. There are 637 exact events, joined to the official task/trial/run IDs. `captured91-review.json` contains every captured actual instruction, final grade, answer and full stdout; raw bounded receipts remain authoritative.
- `receipts/lifecycle-*.json` contains t001–t073; `final-receipts/lifecycle-*.json` contains t074–t091. Every selected event has contiguous byte-offset reconstruction and declared-length checks against its trace index. Complete indexes were traversed but only selected lifecycle index entries were retained. This is **not** a full trace CAS reconstruction.
- The exact nine-file submitted-source/build closure is under `sources/`, with origin paths and hashes in `source-pins.json`. Temporary-directory rebuild reproduces all files byte-identically; source 63,411 bytes, SHA256 `420e904a4cb502221f8609f99bd0f62370deda775abb41b5be9880042f0b7bf8`.
- The original 73-task partial checkpoint remains unchanged. `verify_handover.py` verifies that seal as well as the complete final result and all 91 captured lifecycle records. `verify_source.py` reproduces the source; `verify_lifecycle.py` reproduces the historical 73-task checkpoint.

## Exact next steps

1. Start a **new read-only Brain session** and read workspace instructions. Session s8290 was successfully discarded at seq57, 04:31:35.560345 UTC; it is closed. Do not reuse its next_seq58. No pending operation or draft publication exists.
2. Capture lifecycle evidence for **t092–t100** using the saved source template in any lifecycle receipt, with the same exact job ID. Add new receipts; do not rewrite historical ones. Preserve StartTrial instruction, Answer and full stdout, and verify actual trial/run IDs from `result.json`.
3. Collect **complete indexes for all 11 graded losses** listed above. No loss-index or primary-body harvest was begun. Retain every loss RPC request and full model response/error/retry, relevant primary Read responses and actual model requests needed to explain the final action. Follow `2026-10-23-d4955-full100-results/reassemble.py` and its receipts: bounded UTF-8 chunks, exact offsets/lengths, no silent truncation. Claim full-trial CAS only when every indexed event has been reconstructed in order and the entire digest/size matches the official sealed reference.
4. Finish an all-100 review only after every task is present. Compare exact instructions and observed worlds before interpreting score changes. Analyze inherited problems, actual narrow OCR normalization activation and unmatched inputs separately. Lifecycle log `CROSSLIST_PREVIEW prepared` or a path-only Answer does not alone prove a Write occurred, was correct or required the repair.

No paid calls, job mutation/cancellation, Brain writes, publication or Git changes were made here. The supplied TRAIN-4 stock extension remains sealed unchanged. A separate initial independent review of the proposed effort diagnostic is in `2026-10-23-null-effort-review`; its semantic-contract additions are owned by evaluation_strategy and remain separate from this OCR audit.
