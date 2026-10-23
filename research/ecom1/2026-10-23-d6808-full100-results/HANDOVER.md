# d6808 audit handover — unfinished

Stopped at the user's requested handover. No further harvesting, paid evaluation, source/job mutations, publication or Git edits by this audit agent. Read-only sessions s8291 and s8320 are closed/discarded; no pending operations.

Exact job `jb4798f05fa4941f88eacf20a40f42800`, run `run-22rMCgCkjqbqgNM5LjihcmGWL`, source d6808r1 SHA256 `d44e7055e533cc3b9028ff4fb0294ccf4b60065ae8b2b87864cb0ffdc49d3495`, SDK0.3.7. Root owns latest-record comparison and any promotion; no score exists in the captured running snapshots.

## Last snapshot

04:30 UTC: running,66 completed sealed tasks,0 failed, t067 running. Official partial usage165 model calls/$0.026269878,0 unknown-cost or pending calls at capture. This is partial run accounting, not final cost or a success count. `batch-0430/result.json` preserves the official result; three raw receipts recover one fixed63075-byte output using offsets0/24000/44000. `verify_snapshot.py` checks that reconstruction, including removal of server truncation annotation and print-added LF. No repeated result query was used. t022–t066 evidence was deliberately not harvested after stop instruction.

## Completed evidence

`INITIAL-SEAL.json` SHA256 `efa2d0c983470fb3ed6ed9517669baa094f6d20682bab67bfff3917f531ba02f` pins343 files. Keep all members unchanged. t001–t021 each retain exact StartTrial request/response, Answer request/ack, complete agent_finished stdout and EndTrial request/ack:147 events. All21 have explicit manual reviews. Three full traces t007/t012/t020 match official CAS; source-closure preserves99 exact prepared local files. Nine generated evidence artifacts reproduce byte-exact in an isolated copy. See INITIAL-BATCH.md and completed-initial-review.md for scope and anomalies.

Material findings: t007 has2 length-truncated responses and6 concatenated-action responses, with final count2 consistent with retrieved price/standard-cassette facts (small qualifier not independently resolved). t012 claims verified owner mismatch without any basket Read; refusal and unsupported ownership fact are distinct. t020 recovers from bare-date format output. t002 has2 invalid steps and an automatically included explicitly excluded125-product ref; full trace/grade not yet examined. None of the three full traces demonstrates Exec404 recovery. Agent_finished usage fields are zero placeholders; official completed-trial usage has58 calls for the first21.

## Resume

1. Start a new read-only Brain session and read workspace instructions. Check final job status/result at a deliberate interval. Notify root immediately on completion; root compares against latest verified record.
2. Preserve a fresh exact official snapshot with all slices if output truncates. Only capture sealed tasks. Resume final-log harvesting at t022 using trial IDs and trace offsets from the official snapshot. Use NEW subdirectories; initial reassemble.py glob patterns must not acquire later index/receipt files.
3. For every completed task, preserve instruction, Answer/ack, complete stdout and final lifecycle identity; inspect successes as well as losses. Once grades available, harvest every loss's full indexes/chunks, exact model responses/RPC requests and preferably complete CAS. Reuse initial scripts/protocol but maintain new immutable filenames. Target t002 for stronger evidence if its anomaly remains material.
4. Verify byte lengths/offset continuity/event identities/sealed hashes. Distinguish final-log evidence from full-world action certification. Review actual instructions before cross-run comparisons; same task IDs alone do not pair worlds.
5. Finish all100 review, final accounting and deterministic self-contained archive only after evidence is complete. This handover is not an all100 audit completion or score-improvement claim.

Lifecycle note: first session's discard initially hit automatic approval review; an empty status proof (zero changes/undo steps) resolved it and the subsequent discard succeeded. Both rejection and successful lifecycle receipts remain in the initial seal. No authorization or pending shared changes remain unresolved.
