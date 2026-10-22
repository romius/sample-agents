# Completed paired SKU diagnostic: promising outcome change, incomplete semantics

Captured and reviewed 2026-10-22 after the 22:03 UTC monitor. Job `j787116277efa48ac998df5c6c563f55c`, diagnostic d5622r1, run `run-22rJfyxokZEh2HnAgGFgsCWeE`, completed 21:47:22 UTC. This is the existing short diagnostic, not another submission and not an ECOM1 score experiment.

All 16 planned logical calls completed in 16 provider attempts: HTTP 200, finish reason stop, no errors, retries, truncation, deferred actions or malformed final JSON. Settled cost is **$0.004214326**, complete with no unknown or pending calls; 88,318 prompt and 5,568 completion tokens. Parent eight calls cost $0.001829032; treatment eight cost $0.002385294 (about 30.4% more in this small diagnostic). The carrier grade is intentionally irrelevant.

## Evidence integrity

`verify_capture.py` verifies the complete sealed trace, all 16 actual requests against the pre-dispatch frozen fixtures and SHA-256 plan, provider pinning, every captured response against the runner records, call order, single attempts, and total cost against the settled result. Every pair differs only by the predeclared observation field. Actual provider is DeepInfra BF16, no fallbacks, model GPT-OSS-120B. No generated action was executed; only StartTrial, Answer and EndTrial RPCs occur.

The exact 39-event trial trace is 473,901 bytes, SHA-256 `908a01e24361bda0f4c8c704d4fb795e8b73154bae8feccb1ead0b5e0ece97c2`. All raw event files, the concatenated sealed trace, records, verified calls, summary and trace index are preserved. `community-acceptance-readout.json` retains the independent codex-sol-61 result d5979r1/d5968r1/d5969r1. Its preregistered scorer d5820r1 was already pinned locally before outputs; `frozen-scorer-report.json` is its unchanged result.

## What changed and what did not

| Criterion | Parent | Treatment | Interpretation |
| --- | ---: | ---: | --- |
| Wrong unique OK on ambiguous questions | 2/4 | 0/4 | Both standard-head answers change from wrong FLAT selection to clarification. |
| Correct SKU and reference on unique controls | 4/4 | 4/4 | No observed unique-control loss or excess clarification. |
| Explicit actual SKU names in case-ambiguity raw messages | 0/2 | 2/2 | Already provided by our d4955 final formatter; not two additional production fixes. |
| Standard-head clarifications preserving qualifier uncertainty | 0/2 | 0/2 | Treatment changes disposition but still fails the original semantic criterion. |

Treatment call 3 describes BODY as a **standard grinder body**, unsupported by the actual card. Treatment call 12 lists the known flat-head variant among options and drops the requested standard-head uncertainty. Neither establishes a faithful resolution of the qualifier. Parent calls 4 and 11 falsely return FLAT as a unique OK. Parent calls 1 and 10 already clarify battery capacity and cite both appropriate kits; our existing d4955 formatter supplies their missing SKU strings.

The independent frozen scorer reports four narrow criterion pairs improved and none regressed, including the two raw-message SKU omissions. Its standard-head branch tests clarification disposition only. Do not describe its treatment 8/8 as eight semantically correct decisions, four new production fixes, or 100% task accuracy. Keep the frozen metric unchanged and the manual semantic review separate.

Only four questions, two underlying catalogue contexts and two repeats were tested. Two controls were derived coherently from one archived world. These are development mechanism checks, not fresh multi-family holdouts. We verified matched inputs and identical inference settings; provider nondeterminism and the tiny sample remain. The prompt/call costs do not estimate full-agent cost. This diagnostic does not exercise repeated-observation history pressure, world mutations, complete end-to-end task grades or the forced-report repair.

## Integration decision

Retain the narrow evidence attachment as a research candidate, with the separate history-pressure repair d5785r1 if revisited. Do not submit unrepaired d5620r1 or infer full100 readiness from this result. Before another evaluation, explicitly test negative and conflicting qualifiers, missing attributes and fresh product families; demonstrate that the observation helps preserve unresolved constraints without inventing properties. Avoid adding another SKU-display handler because d4955 already covers that case.

Record d3200r2 remains the strongest verified baseline, official 0.9012601 (90.12601/100). At the 22:03 monitor all three authorized full100s d4702/d4955/d5204 remained queued. The inventory-only third-slot exception is consumed; normal two-outstanding limit applies and no new full100 was submitted. Existing jobs were not cancelled or modified. Next regular refresh is approximately 22:33 UTC.

## Reproduce without inference

Run `python3 verify_capture.py` from this directory. Run the frozen scorer with `python3 ../../2026-10-22-monitor-2133/upstream/acceptance.py records.json ../fixtures.json frozen-scorer-report.json`. See the independent semantic review and formatter replay script/results alongside this file. No test needs new model calls.
