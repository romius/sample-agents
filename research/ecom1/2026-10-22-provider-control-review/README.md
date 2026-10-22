# Exact-source provider control: independent full100 review

Reviewed 22 October 2026, 22:40 UTC. **No code improvement is established by this control.** The same d2499r1 bytes scored **0.780781 (78.0781/100)** in the new run versus the original official full-precision **0.83099496 (83.099496/100)**, a descriptive difference of **−5.021396 points**. The current record remains d3200r2 **0.9012601**; no promotion is indicated or performed.

| | Original | Provider control |
|---|---|---|
| Job | `jd8713c77f6ab4a0e9f67bcd614d8d2e9` | `je58047e416f64e06bcec3ba91d7ef733` |
| Run | `run-22rF1LE4MzDb7NdkS8z8vcLjX` | `run-22rJLA8nTWyVkAnedEf6YowYD` |
| SDK | 0.3.6 | 0.3.7 |
| Provider request | Cerebras FP16, no fallback | DeepInfra BF16, no fallback |
| Trials graded | 100 | 100 |
| Execution failures | 1 | 4 |
| Model calls reported | 354 | 367 |
| Reported cost | $0.66980710, complete | $0.072922019, incomplete |
| Unknown-cost calls | 0 | 4 |

Both job/result source pins and the local 53,177-byte [d2499r1.py](d2499r1.py) equal SHA-256 `ced402b531e213bef9959b6956006a8d967c0998eb7e31f0e34901f26b0eb3c1`. Actual archived router request events verify `cerebras/fp16` versus `deepinfra/bf16`; successful response samples identify Cerebras and DeepInfra respectively. The other captured router settings agree. This is stronger than relying on a run name, but is not a verification of every provider request in either run.

## All100 rows and instruction comparison

[all100-review.tsv](all100-review.tsv) contains every grade/state/detail. [all100-review.json](all100-review.json) also includes both literal instructions, SHA-256 hashes, and both immutable trace references for every task. All100 StartTrial instructions were retrieved or reused from the exact original-job archive and checked against task IDs. **94 instructions differ.** Only t070, t071, t081, t083, t086 and t087 match exactly; all six score 1 in both runs. Matching instruction text still does not prove identical world files, identity, policies or other environment state. These are not 100 paired examples, nor six fully paired runtime worlds.

The new result has **74 full-credit, 21 zero and five partial-credit trials**. Every zero is accounted for below; labels summarize grader evidence, not an inferred trace-level cause:

| Grader-observed loss | Tasks |
|---|---|
| No answer after inference timeout | t003, t045, t056, t059 |
| Catalogue grounding refs mismatch | t022, t027, t042, t062, t065 |
| OUTCOME_OK where clarification expected | t001, t061 |
| Crosslist outcome/export mismatch | t016, t036, t076 |
| Receipt security denial where OK expected | t023 |
| File-change/deletion mismatch | t038, t039, t060 |
| Count answer mismatch | t047 |
| Inventory export mismatch | t091 |
| OUTCOME_OK where security denial expected | t093 |

The five dispatch partials are t004/t014/t024/t044/t064. Their grade sum is 4.07809275. Summing all individually rounded trial grades gives 78.07809275, while the official run score is 78.0781/100; use the official value for record/delta reporting. The original trial-grade sum similarly differs slightly from its official score. This small aggregation difference is preserved, not silently rounded into equality.

Provider, precision, SDK version, generated instructions/worlds and execution time/load all changed. Therefore the aggregate drop cannot isolate a provider effect, an SDK effect or a code effect. In particular, old t079 failing and new t079 passing cannot show a code fix: code is identical and its instruction changed. Reported cost fell, but the new total remains a lower bound with four unknown-cost calls.

## Four execution failures

All four failures reach the same unguarded d2499 main-loop inference call at packed line 944 and raise:

`Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out`

| Task | Failure trace event | Last preceding successful model action | Earlier host retry evidence |
|---|---|---|---|
| t003 | llm_error 580, agent_error 581 | Read receipt OCR | 429 retry event 566 |
| t045 | llm_error 5866, agent_error 5867 | Tree `/proc/locations` | 429 retry events 5847 and 5856 |
| t056 | llm_error 7176, agent_error 7177 | Catalogue query `Uvex Pheos` | None in this failure's index |
| t059 | llm_error 7308, agent_error 7309 | Read staff record | None in this failure's index |

Each llm_error marks `outcome_unconfirmed: true`, and each failed trial accounts for one unknown-cost call. [new-failure-t003.json](new-failure-t003.json) and its three counterparts preserve full selected StartTrial, llm_error, agent_error, retry and first/last model-response events. Complete compact failure indexes were scanned to select errors/retries; no RPC error appears in those four indexes. Full multi-megabyte traces were not downloaded or exhaustively reviewed. Every full trace's immutable CAS hash and byte count remain preserved in the result exports.

The actual SDK/host trace includes 429 retries even though generic Brain help describes no automatic paid retries. Specifically, DeepInfra returned `engine_overloaded`/shared-pool 429, and the host recorded `reason: http_429`, `next_attempt: 2`; later distinct calls timed out. Do not conflate those host retries with our candidate's agent-level retry helper, or claim that all four failures were caused by 429. The timeout calls themselves show attempt 1 and were not recovered in this control.

## Existing repair coverage, without new code

[audit.py](audit.py) imports the exact unchanged `MSR` and `recoverable_lookup_error` definitions from the pinned d5204 readable archive (`../2026-10-22-inventory-integration/readable.py`, SHA `aef93a8c2b25feeb097e70a063d5ffff6c15f52622a3e4e058859901b0a921e1`). Both guard ASTs are also checked identical in the current d5789r1 readable (SHA `0f7925c41f2783b6617ec7777757bec6fee5971f483159e26b32fae8082f7c41`). All four observed timeout messages receive at most three identical **agent-level** inference attempts. Simulated third-attempt success returns; permanent failure propagates after attempt three. HTTP 429/400 and unknown errors propagate after one call. Native Monty 1.2.0 checks the exact timeout form under 10-second feed/turn and 1,000-suspension limits.

The original run's t079 events 10608–10610 show actual Exec `/bin/ls -R /proc/baskets` followed by `BitGN HTTP 404` with code `not_found` and message `runtime tool not found: not found`. The existing narrow missing-executable branch accepts that exact exception. Malformed 404, ordinary missing-path 404 and 500 controls remain excluded. No new Exec404 occurred among the four new execution failures. This confirms the already-tested repair addresses reachable events; it does not establish that applying it would make the complete original or new task pass.

No guard changes are justified by the new error wording. Agent-level bounded retries may make additional paid attempts with unknown outcome/cost. Host retries can add provider attempts inside a single agent-level call, so the three-call bound is not a universal three-provider-attempt bound. These offline checks neither prove provider recovery nor recover missing accounting, and no score gain is claimed. Even granting an illustrative perfect recovery of all four failed tasks would add at most four points to this run, not explain or reverse the full observed gap; that is a ceiling, not a prediction.

## Reproduce, provenance and scope

```sh
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python research/ecom1/2026-10-22-provider-control-review/audit.py
```

[new-result.json](new-result.json) and [old-result.json](old-result.json) preserve the complete Brain result object, including job metadata, all100 trial rows and trace CAS references. They are canonical JSON exports of the API object; local file hashes are not asserted to equal the underlying server CAS summary hashes. Server summary hashes are respectively `2f359eb040098cbf70ef4094f6c097738e61d9126c89d0ffc9fd692da3a6fac3` and `c62aa8b8483b9ee1508cb432ee5b7579177b2f8686815ecd6985d63ca8170e5b`. [SHA256SUMS.json](SHA256SUMS.json) pins local source/results/events/review artifacts; [DEPENDENCIES.json](DEPENDENCIES.json) pins reused original audit sources and guard source. The source copy came from the existing local integration artifact and was checked against both immutable job pins.

Brain session s7452 performed targeted reads only and was discarded with zero draft changes, jobs or cancellations; [brain-session.json](brain-session.json) preserves the receipt. No model calls, paid diagnostics, source changes, production mutations or promotion occurred. Result-row review covers all100; detailed trace inspection is confined to the four new failures, original missing-tool failure, all100 instructions and provider-request/response samples. Existing unrelated results and candidates remain unchanged.
