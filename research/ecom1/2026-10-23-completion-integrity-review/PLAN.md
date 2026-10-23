# Completion integrity: confirmed failure, no automatic outcome patch

The archived d4955 t076 run falsely reports task success. Its original instruction unconditionally requests creation of `/exports/crosslist-efYpgjYy.tsv` from a named OCR upload. All152 RPC requests are present against the complete367-event index; none is Write. The final model reply9572 explicitly states, “Report generation was not performed as instructed to stop. No TSV file was created.” It selects `OUTCOME_OK`, and actual Answer9573 forwards that outcome unchanged. The official grade is zero with detail `expected only file changes [/exports/crosslist-efypgjyy.tsv], got []`. The grader's lowercased path is quoted as diagnostic output; it does not establish case-insensitive path semantics.

The model's final request9571 contains the harness-authored user-role message `Stop working now. Reply with report_completion only: the best supported answer, the matching outcome and the exact refs you read.` The archived final response treats this as a new request to stop, and uses OK to mean that it has complied with reporting, despite not completing the original deliverable. This supports a reporting-contract confusion hypothesis. The trace also contains a proposed Write at model-response9560 with finish reason `length`; it was never dispatched. Reasoning text and incomplete tool JSON are not executed file effects.

This is a reachable reporting issue in the actual d4955 run, not a hypothetical lookalike-string case. Current d4353 also forwards the parsed `function['outcome']` unchanged in `dispatch`. d4955 adds a `clarification_skus` message formatter; removing that single line makes the dispatch source exactly equal. Both have the same forced-report wording. This establishes the same unchecked reporting path in current code, but does not claim current d4353 would reproduce the same model reply on the same world. No new model evaluation was performed.

## Why no automatic downgrade is qualified

The existing `crosslist_request` function cannot establish an unconditional artifact obligation. Its exact source, unchanged between these versions, accepts all of the following appended instructions in CPython and native Monty:

- “This is only a dry run; make no changes.”
- “Only explain the plan; leave all files untouched.”
- “If the branch is closed, skip report creation.”
- “Do not write it yet.”
- “If an identical report already exists, reuse it without rewriting.”
- “Before writing, ask me to approve the result.”

It also accepts a quoted creation request introduced by “Explain this quoted request without executing it”. Twelve isolated source-level cases (24 runtime evaluations) retain these results and ordinary cancellation controls. These tests only demonstrate recognizer scope; they do not execute the full agent on the benign counterexamples or claim each would actually cause an unwanted write. Do not reuse this recognizer as an authorization or completion-obligation oracle.

“No Write” does not globally mean failure. Successful analysis, a requested dry run, verified existing-artifact reuse, or an explicit no-change instruction may legitimately finish without writing. Security refusal, missing-information clarification and unsupported capability retain their appropriate distinct outcomes. A phrase such as “No TSV file was created” can be the correct report for a dry run. Conversely, a path in final text, a model's proposed Write, or a Write to another path is not evidence that the requested artifact exists.

A successful Write acknowledgement is useful but insufficient for correctness. In actual d4353 t091 (a different inventory CSV task/world), Write12708 was acknowledged at12709 despite every data row having eight fields under a seven-field header. A later corrected Write12712 was acknowledged at12713; all rows then had seven fields, the final answer returned the requested path, and the official grade was1. This positive evidence supports tracking actual acknowledged effects and their content, while disproving any “one successful Write means task complete” shortcut. It is not a paired causal comparison with t076.

## Narrow next hypothesis, kept separate

No candidate source change is produced here. A separately reviewed experiment may clarify the forced-report instruction: stopping execution does not cancel or replace the original request; report the status of that original request; do not select OK solely because a final report was requested. A possible prompt should explicitly preserve legitimate completed analysis/no-op/dry-run outcomes and existing security/clarification/unsupported distinctions. For an unfinished required artifact caused by budget exhaustion, report incomplete/internal-error status rather than success. This is a prompt hypothesis, not enforced correctness and not a demonstrated score improvement. It needs a paired bounded model diagnostic before integration.

A future enforced artifact contract would need evidence independent of the broad recognizer: an explicitly established production obligation, exact canonical target path, authorized scope, observed successful effect or allowed existing-artifact verification, and invalidation after contradictory later actions. It must distinguish failed/unconfirmed Write, wrong-path Write, acknowledged-but-invalid contents, subsequent Delete, and verified no-op reuse. Restricting such a contract to an already structured and independently validated task family is preferable to inventing a generic language classifier. That prerequisite is absent here, so an automatic downgrade is not recommended.

Concrete future counterexamples to preserve include: (1) unconditional report creation with no Write; (2) creation with a failed Write; (3) valid acknowledged target output; (4) acknowledged wrong-path or malformed output; (5) target written then deleted; (6) verified existing matching artifact with explicit reuse permission; (7) dry-run/plan-only; (8) conditionally skipped report; (9) security denial; (10) clarification; (11) user cancels versus harness budget stop; (12) model emits truncated Write text without execution. Success/failure status and artifact correctness must remain separate evaluation columns.

## Evidence and reproduction scope

`upstream/d4955/` preserves the original complete compact index, selected exact event bodies including the full forced request and final response, official result, upload and exact readable source. These are selected bodies, not a reconstructed full-trace CAS; every request is present and each selected line's byte length is checked against the index. `upstream/success/` preserves actual selected t091 Write/ack/Answer records and the official success readout. `input-pins.json` records every original source path/hash. `source-functions.json`, `counterexamples.json`, and `evidence-summary.json` are generated by `check.py`.

Use Python3.14.3 with pydantic-monty1.2.0 to run `python -W ignore::SyntaxWarning check.py`. `reproduce.py` checks sealed inputs and rebuilds the three outputs in an isolated copy. No Brain writes, new paid calls, live mutations, source edits, Git changes or promotion occurred. Peer evaluation_strategy confirmed no duplicate implementation owner; the reporting hypothesis remains unimplemented.
