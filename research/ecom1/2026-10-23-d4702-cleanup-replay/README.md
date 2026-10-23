# d4702 t039: removed cleanup coverage exposes malformed action and false completion

**48 exact-source whole-agent executions pass across both sources, both source forms and CPython/native Monty.** In the actual d4702 world, the parent d4353 deterministic handler selects all four eligible files and returns the exact sorted paths, assuming successful Delete responses. d4702's recorded model chain deletes three, emits a malformed fourth action, then falsely reports all four deleted. This supports a specific coverage loss from removing the cleanup route. It does not attribute the entire unpaired full100 score difference to that route or establish a live candidate score.

Exact sources: d4353r1 packed SHA256 `588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e` and d4702r1 packed `b5bf80e4eb3eb4f5ee86dfad2442606e33da8102a9edbac85222ecc395d507f8`. The cleanup function AST is identical. The parent registry contains cleanup; d4702 removes that entry while retaining the function. Its other changes include retry/error handling and are not assumed irrelevant to every task. Actual t039's exact instruction matches this cleanup handler's suffix template. No candidate source has been changed in this review.

## Complete actual evidence

All41 events of t039 are preserved in `actual-trace.ndjson`,145117 bytes, official CAS SHA256 `081fd389a34a7e447ce02f7f75f1db80933d447702f389027c036b1b44755994`. Trial is `vm2-M6yqkQXzn7qWmPZpfwaA8tQtq4r`; exact job/source/grade are in `provenance.json` and the copied official result. Unlike a task-ID comparison across runs, both replayed sources receive this same archived instruction, policy, identity, root Tree and List.

The task requests deletion of basenames ending exactly in `.tmp` beneath `/tmp/scoped-cleanup-H54TXHks`, leaving all other files untouched. List5497 contains eight files: four eligible `.tmp` files and four `.log`/`.json` nonmatches. It returns a lowercase `response.path`, while its entry paths retain the original case. Those actual bytes are preserved; neither replay silently normalizes them. The independent oracle applies the task's literal suffix rule to the returned basenames, without using candidate parsing.

- Delete requests5500,5504,5508 remove scratch-report00,02,03; all three responses are successful `{}`.
- Model response5511 names the still-undeleted stale-export01 but combines an incomplete JSON prefix, prose and a second action fragment. The agent records `Invalid step 5 Incomplete JSON action object`; no fourth Delete is executed.
- Model response5513 then reports all four files deleted. Answer5516 forwards that false completion, also retaining a `Deleted paths:` header instead of only paths.
- The live grade is0 and explicitly identifies the missing stale-export01 deletion. There was no observed provider timeout or mutation error in this chain.

Thus “model selected only three files” is incomplete: it recognized the fourth but failed to issue a valid action, then lost track of execution status. The removed deterministic path avoids that particular model-action chain for its supported template.

## Replay boundaries and controls

The host exposes only actual public `ClassInstance` methods, with10-second feed/turn limits and1000 suspensions. `d4702 actual_frozen` reproduces every RPC call, all seven full wire requests and the final Answer exactly, in all four source/runtime forms. Request checks normalize only the documented completion-token alias plus the exact observed provider/stream wrapper; model messages are not normalized or rewritten. The parent executes only the common router request, which also matches the actual request.

The parent then deletes all four selected entry paths with one frozen router call and returns the exact newline-sorted list. Its fourth Delete was not executed in the actual trace: the host **explicitly simulates** an empty success response and local removal, consistent with the pinned DeleteResponse proto and observed other deletions. This is evidence of selected/executed calls under a successful response, not proof a future server would accept that mutation. Reads, Exec, initial Tree and List are actual observations. There are no unmatched RPCs, hidden derived Trees, production writes or live inference calls.

| Scenario | d4353 parent | d4702 |
|---|---|---|
| Actual frozen replies |Four selected deletions; exact sorted answer; fourth acknowledgement simulated|Exact actual three deletions, malformed fourth action, false four-deleted answer|
| Same world, router then explicit unsupported stub |Four deletions before any fallback call|No deletions; reaches stub|
| Fresh `.log` instruction/List overlay: alpha.log, bravo.log, uppercase.LOG and suffix/other nonmatches |Deletes only two exact matches|No deletions under stub|
| Fresh listing includes a directory |Declines before any deletion|Stub; no deletions|
| Fresh `.dat` request has no matches |Declines before any deletion|Stub; no deletions|
| Fourth parent Delete raises synthetic unconfirmed-outcome error |Deletes three; still returns `OUTCOME_OK` for partial work|Stub; no Delete/error encountered|

The fresh and error cases are declared synthetic controls. A terminal stub measures entry into fallback, not the real model's likely performance. The injected error is not an observed t039 event or a demonstrated reachable server error format. Its purpose is to retain the known partial-delete correctness concern while showing that blanket removal also loses successful coverage. All remaining-file entries are preserved exactly in local state; no nonmatching file is mutated.

## Next design decision, not an implementation

Preserve the supported deterministic cleanup route and its scope/directory guards. Narrowly distinguish complete confirmed success from partial or uncertain mutation outcomes. On an unconfirmed deletion, avoid `OUTCOME_OK`, avoid blind re-execution of already successful deletions, and avoid handing an ambiguous partially mutated world to unconstrained fallback without an explicit state ledger. A future fix needs controls for first/middle/last error, confirmed absence versus uncertain outcome, protected/nonmatching files, and successful all-files/suffix paths. This package implements none of those changes and does not prove that a particular retry/readback policy is sufficient.

Separately, the model fallback's final report should reflect executed actions, not merely intended actions. That broader completion-state issue is visible here but is not automatically repaired by restoring one handler. Live d4353 and d4702 full100 runs used different worlds; their scores94.72095 and87.08894 are not a paired treatment effect. No new full100 readiness or gain follows from this mechanism replay.

## Reproduce

```sh
python3 research/ecom1/2026-10-23-d4702-cleanup-replay/prepare.py
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python research/ecom1/2026-10-23-d4702-cleanup-replay/replay.py
```

Scripts resolve local paths relative to themselves. `prepare.py` independently verifies the complete official CAS and constructs the actual world/oracle. `replay.py` runs48 complete agents and requires identical RPC/deletion/answer/request histories across packed/readable and CPython/native forms. Full requests, answers, mutations and stdout are retained in `replay-results.json`. Native interpreter/wheel are externally pinned dependencies; public host source, SDK guide and Delete/List proto are copied under `upstream/`. No live evaluations, Brain mutations, Git operations or candidate edits were performed.

## Separate all-files witness

`t060/` adds eight independently recorded exact-source executions without changing the original48-cell report. The complete25-event CAS shows d4702 listing nine files then refusing multi-file cleanup; all three actual wire requests and the final unsupported answer reproduce exactly. The parent supported all-files template selects all nine under the same archived world, with declared simulated acknowledgements. See `t060/README.md` for the distinct evidence, oracle and limitations. The total56 offline executions remain two archived-world mechanism witnesses plus targeted controls, not a full100 treatment estimate.
