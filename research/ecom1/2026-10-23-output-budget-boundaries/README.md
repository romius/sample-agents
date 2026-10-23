# Output-budget boundaries in archived d4702/d4955 losses

The 165 complete model responses archived for the two runs' 34 loss/partial trials contain **25 null-content or length-finished responses**: 18 null final contents with `finish_reason=stop`, and seven `length` responses (five also null). All 25 are exact **main-loop** requests, not router or forced-report calls. No matching response caused a mutation dispatch. This is a loss-selected population, not an all100 prevalence or causal score analysis.

The useful new boundary is not HTTP retry behavior. Three consecutive invalid final responses can exhaust the local invalid-action allowance before 30 steps, while the forced-report path has a different truncation check from the main loop. The exact d4353 control flow shares these output-handling boundaries. A small new offline control comparing main and forced handling of the same length-finished response is justified; no patch or model rerun is prepared here.

## Exact evidence scope

| Source | Job | Archived loss responses | Selected responses |
|---|---|---:|---:|
| d4702r1 | jfdd875bba6ba4773a549e8703764efa9 | 65 across 17 trials | 9 null/stop |
| d4955r1 | j37e3df7ac8564c0899c81a706e0aea9a | 100 across 17 trials | 9 null/stop + 7 length |

Every response is linked to its exact request, full call/response ID, source, trial, settings, bytes/hash, indexed offset, next inference, and next actual RPC in `decision-table.json`; the concise 25-row view is `decision-table.md`. Selected responses are all HTTP 200/DeepInfra, medium reasoning, temperature 0, max_tokens 2048. No provider failure or transport retry is inferred from an empty final field. Actual raw usage is retained without imputing unavailable accounting.

The original archives already held every indexed model response and every RPC request in the 34 loss trials, plus selected request/world bodies. We copied those exact sealed artifacts. Read-only Brain session s8272 retrieved 31 missing request bodies: the relevant anomalous calls and immediate following calls needed for feedback/phase comparison. Ninety-five bounded chunks reconstruct all 31 exactly; every range, byte count, event/call/trial identity and indexed offset is verified. The session was discarded without changes. This retrieval performed no inference, submission, cancellation, or other paid work.

All original index pages are complete, with contiguous trace offsets summing to each official trial's trace bytes. For the six affected trials, every indexed RPC request body is present: no Write, Delete, or state-changing Exec appears. Lifecycle Answer is reported separately. These are selected exact event bodies plus complete indexes, **not** a new full-trial CAS reconstruction. No synthetic request substitutes for missing evidence.

Exact packed sources are retained: d4353 `588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e`; d4702 `b5bf80e4eb3eb4f5ee86dfad2442606e33da8102a9edbac85222ecc395d507f8`; d4955 `2f145f03558a944c30398ec59aabb92ea7d891e05889b1a8f348d07d11cbfb20`. Input pins include their exact readable counterparts. Task IDs refer only to their named run; no cross-run world equivalence or causal grade attribution is assumed.

## Six observed control-flow sequences

| Run/task | Observed boundary | Next observed behavior |
|---|---|---|
| d4702 t016 | Null/stop at main steps 4,5,6; 70/105/105 completion tokens | Exact forced request2647 follows the third invalid reply. Response2648 proposes a Read, not report_completion. It is not dispatched. Answer2649 is internal error claiming a 30-step limit despite only six main calls. |
| d4702 t043 | Null/stop at main steps 2,3 | Main step4 recovers with List6362. Invalid counter resets. Later report is still a main call, not forced. This demonstrates recovery before the three-consecutive threshold. |
| d4702 t074 | Null/stop at step1; a valid stores action at2; null/stop at3,4,5 | Valid step2 resets the invalid allowance. Forced request11143 follows step5. Response11144 proposes Search, which is not dispatched; Answer11145 again incorrectly describes a 30-step limit. |
| d4955 t043 | One null/stop at main step4 | Main step5 List5392 executes. A later non-JSON `<NO>` is separately repaired; final report5649 is main step9, not a forced call. |
| d4955 t056 | Null/stop at2,3; valid stores at4; null/stop at5,6,7 | Forced request6989 follows the second streak. Response6990 reports clarification because further catalogue lookup is needed; Answer6991 is sent. No report file is written. This is an honest incompleteness report, not a completed deliverable. |
| d4955 t076 | Null/stop at3,7,8; length at13,18,19,25,27,28,29 | Intervening valid actions reset the counter. The final three length replies trigger forced request9571 after29 main calls. Response9572 says no TSV was created but selects OK. The previously completed completion-integrity review owns that reporting defect; this audit adds its budget/feedback history, not a duplicate repair. |

The null/stop cases consume 70–710 reported completion tokens, well below the requested 2048 allocation. Their raw reasoning often discusses a next action, while the final `content` is null and no native tool_calls are present. The agent deliberately parses final content only. This does not justify executing reasoning text, retrying HTTP 200 as a transport failure, or claiming that a larger completion allocation fixes these cases.

All seven length responses consume 2048 reported completion tokens. Response9518 contains repeated Read JSON; response9560 contains a partial Write for the requested TSV. The main length guard discards both before parsing/dispatch, correctly avoiding execution of a truncated reply. The five other length responses have null final content. No forced-report response in this selected evidence ends with length.

## Requests, feedback, and context pressure

All 25 immediate next requests differ from their predecessor. Exact hashes disprove an identical-prompt replay claim. Null/stop repair appends an empty assistant message and `No action executed. Fix your JSON: Return one JSON action object`; ordinary length repair appends only a user instruction requesting one short JSON action. At the third consecutive invalid response, the old request receives only the forced-report instruction. All immediate pairs here are append-only; no RPC occurs between the selected response and next inference.

The same main/forced allocation stays at 2048 and medium reasoning. The feedback does not distinguish a null final channel from malformed JSON, supply a new plan, or increase the output allocation. The allowance counts **consecutive** invalid outputs: a parsed action resets it, including read-only searches that may make little progress. This explains the multiple recoveries and long t076 sequence without asserting that all additional iterations were useful.

`context-pressure.json` preserves an exact longer-interval comparison: t076 request9539 (step20,44 messages,55,222 bytes under the source's `json.dumps(messages)` metric) to9559 (step25,50 messages,46,935 bytes). Four old messages were removed: the original OCR Read/action pair and catalogue Tree/action pair. Ten later messages were appended, including a fresh read of the same OCR. The nine-message bootstrap prefix remains. Therefore trimming occurred, but permanent receipt loss is not established; the re-read supplies the receipt again. This is a source message-history threshold, not a provider context-window error or a private wire-size measurement. The exact trimming instant between these endpoints was not separately retrieved.

Some response usage reports reasoning-token subcounts inconsistent with completion totals. Raw receipts are preserved; we do not derive a precise remaining-final-token budget from those subcounts or treat it as a measured causal explanation.

## Exact d4353 comparison and bounded next control

The main-loop-through-forced-report tails of d4353, d4702 and d4955 are byte-identical after replacing only the own sources' `MSR(` call spelling with `bitgn.llm(`. The wrapper is a transport-exception recovery change; it does not handle successful null/length replies. Source ranges/functions and hashes are saved in `source-comparison.json`.

The common source has these boundaries:

1. Router: 1024/low and explicit length decline. No selected anomalous router response is observed here.
2. Main: 2048/medium, explicit length guard before parsing, shared invalid counter for length and parse errors, break at three consecutive failures, reset on a parsed action; maximum30 main iterations. Empty content becomes an empty string.
3. Forced: one additional 2048/medium call, **no finish_reason length guard**, then parse final content and dispatch only if the parsed tool is report_completion. Other actions are ignored. The generic fallback message always says30-step limit, including earlier invalid-output breaks.
4. History is trimmed before main calls by deleting two messages after bootstrap while its JSON exceeds56,000 bytes. The forced call appends its instruction without repeating this trim. No over-limit forced request is observed in the selected cases.

**Recommended new offline control, not executed here:** on an exact-source native fake host, reach the three-invalid-output break and feed the same fully specified response to (a) a main boundary and (b) the forced boundary. Include a valid report_completion JSON prefix with finish_reason=length, a partial/non-JSON report with length, null/stop, a valid non-report action, and an ordinary stop-finished report. Assert exact calls, Answer dispatch, absence of Write/Delete/other proposed actions, and truthful termination reason separately. This isolates the missing forced length guard and early-stop reporting boundary without re-running existing inference retry classifiers or introducing a speculative provider retry. A length-finished parseable report can currently reach the forced dispatch by static control flow; it was **not** observed as a paid forced response in this census.

A second small history-boundary control is only warranted if a future proposal changes trimming: mix single-message length feedback with two-message invalid-JSON feedback around56,000 bytes, verify which exact source observations survive, and check the forced append separately. Do not propose cache-wide evidence injection, larger budgets, or an automatic failure downgrade from this loss-selected evidence alone.

The earlier completion-integrity review and its benign no-Write/dry-run controls are copied under `prior-completion-review/` for scope separation. No candidate, source mutation, inferred grade fix, live evaluation, or repeated diagnostic was produced. The recommended control remains future work requiring its own bounded implementation/review.

## Reproduction

Run `python3 research/ecom1/2026-10-23-output-budget-boundaries/reproduce.py`. It verifies copied input pins, recreates supplementary events and all census/phase/feedback/source-comparison outputs in an isolated temporary copy, and compares exact generated bytes. It does not execute agent inference tests or contact Brain. Original archives and sources remain unchanged. `prepare.py` records initial collection from workspace archives; the packaged reproduction uses the already pinned copies and does not need those external originals.
