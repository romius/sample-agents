# Missing-executable Exec404 recovery on exact d4353 — offline candidate

This separate candidate adds narrowly classified recovery for an unavailable executable. The archived failure is reachable: an earlier agent actually issued `/bin/ls -R /proc/baskets`, received a structured runtime-tool-not-found404, and failed without answering. Exact current d4353 reproduces that failure in the archived same-world offline replay. The candidate instead exposes a tool-availability observation and permits subsequent native actions. This is evidence of reachable control-flow repair, not actual task completion, future model behavior or a measured score gain. No OCR or inference-retry candidate is combined here. No paid call, submission, promotion or publication was performed.

## Source and scope

Parent d4353r1 is63,211 bytes, SHA256 `588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e`. Candidate `agent.py` is63,564 bytes, SHA256 `d44e7055e533cc3b9028ff4fb0294ccf4b60065ae8b2b87864cb0ffdc49d3495`, with1,972 bytes below the65,536 limit. `readable.py` SHA256 is `8cb9485e0d4c4febd80e885a7c41bd2d89ace93e4f24176d9105e0d6a367f48a`.

The exact d4355r1 parent builder, d4236r1/d4237r1 predecessors, d4228r1 donor and d3268r2 lazy packer are preserved in `parent-build/`. The parent packed/readable/decoded representations rebuild exactly. The candidate applies identical changes to readable and decoded source, verifies AST equality, and uses the exact parent packer. Only two existing functions change:

- `recoverable_lookup_error`: after inherited one-prefix normalization, an Exec error must have the exact `BitGN HTTP 404: ` envelope, valid JSON object, `code == "not_found"`, and a string message starting `runtime tool not found:`. Everything else retains the original path through the function.
- `observation`: a returned `unavailable_tool` marker suppresses the additional `--help` Exec against the known missing executable. The original failed Exec is never automatically retried by this change.

`recovery_donor.py` preserves the previously shared mechanism. The donor's broad `startswith("runtime tool not found")` accepts a fresh lexical collision, `runtime tool not foundry inventory missing`; this candidate requires the colon delimiter and an actual string type. Both donor and exact parent already strip one leading `RuntimeError: `, so the saved error representation is not a donor reachability gap. No filename, task ID, customer, SKU or expected answer is hard-coded into production behavior.

The parent Delete404 containment branch is byte-identical, including its unconfirmed-effect guidance. Generic readonly404 recovery, non4044xx handling, dispatch, inference and deterministic task handlers are unchanged. Non4044xx Exec can still trigger the parent's help behavior and broad “nothing changed” wording; this experiment does not endorse or repair those inherited semantics. Existing `/bin/sql` exitCode1 is a returned process result and never enters this exception classifier; its observation/help suppression through the parent's reporting-bin list remains unchanged.

## Actual witness and error boundary

The witness comes from old2 job `jd8713c77f6ab4a0e9f67bcd614d8d2e9`, t079, trial `vm2-M6xEUVY5beJJgp3UfkqdSuq1zaJ`, instruction “Add 1 of bare makita dhs680 lxt saw body to my newest active basket.” Original request10608 is Exec `/bin/ls`, args `[-R, /proc/baskets]`, empty stdin. RPC error10609 contains:

```
RuntimeError: BitGN HTTP 404: {"code":"not_found","message":"runtime tool not found: not found"}
```

The final line of agent_error10610 is the same string with one additional leading `RuntimeError: `. Official result records failed/no-answer, score0. Its four calls cost0.0067499USD with complete recorded cost; these are historical witness costs, not costs incurred by the offline tests. The event's generic `outcome_unconfirmed: true` is preserved. The recovery classification relies on the specific structured missing-runtime-tool category; it does not treat every404 or generic unconfirmed action as safe absence. Backend dispatcher implementation was not inspected.

`test_boundaries.py` demonstrates that native method-only `ClassInstance` preserves the host exception argument exactly in guest `str(exc)`, then adds an exception-type prefix to the uncaught terminal line. Feeding the **saved RPC error string once** reproduces the archived two-prefix terminal line. Feeding only the raw HTTP suffix yields one prefix; adding another wrapper to the saved string yields three. The primary replay therefore uses the saved string once, without extra wrapping. A separate raw-HTTP case also passes normalization. This reconstructs the observed boundary representation; it does not infer the SDK's internal formatter implementation.

The complete274-event trace was retrieved read-only through byte ranges and reassembled to370,247 bytes. SHA256 `1bcbf63ed2febf0911a728234f9862c9c221ea7bb324fc4a3906ec7d1e63c356` matches the official sealed CAS receipt in `evidence/official-t079.json`. Every indexed byte length, event sequence, kind and trial ID is checked. All125 Read files are verified against actual content hashes. Raw harvest chunks, index, source audit and official receipt are retained. Read-only Brain session s8051 ended with discard.

## Replay and counterexamples

**168 exact whole-agent executions passed:**21 cases ×parent/candidate ×readable/packed ×CPython/native;84 are native. Public Monty1.2.0 method-only hosts use10-second feed/turn limits and1,000 suspensions. No agent function is replaced. The archived router and three actual model response bodies drive the initial catalogue lookup, malformed-step correction and failed Exec. The same current parent/candidate requests match through this point. Current-source prompts are not asserted equal to the historical old2 prompts; actual response bodies are replayed without model calls.

RPC responses come from the same archived t079 world. Current d4353 requests positive-depth subtrees where the older source requested the complete `/proc` Tree. `prepare.py` derives exact child subtrees only where their observed depth fits level3; no labels, product fields or descendants are invented. Default-equivalent Read options may reuse the exact complete archived file response, with explicit false/zero guards. Every other unmatched host call fails the replay.

For the actual error, parent fails with the exact archived terminal error line. Candidate emits `unavailable_tool`, invokes no automatic help/repeat Exec, then follows a **scripted** native Tree of `/` and terminal internal-error answer that explicitly says the basket was not updated. This continuation tests the available control flow and absence of duplicate Exec; it is not evidence that a live model chooses Tree, performs the requested edit or earns a passing grade. There is no fabricated successful basket mutation or automatic task-pass count.

Fresh whole-agent cases cover another missing binary, generic404, invoice/payment record404, malformed/array JSON, wrong code, non-string message, the prefix collision, non404500/400/403, healthy Exec, SQL exitCode1, Delete404/malformed404/500, and invoice/payment errors after a scripted side effect. Each target operation occurs once. Only the missing-executable cases add recovery; all other cases match parent calls, request bodies, help invocations, answers and side-effect records. Inherited recoverable4xx may issue a distinct help Exec, which is counted separately rather than called a replay of the original operation.

Additional isolated checks execute21 classifier/observation cases in parent/candidate under CPython/native, totaling84 evaluations. They include the no-colon and double-added-wrapper exclusions plus readonly404 parity. Three native representation probes and SQL observation parity are separate checks, not additional benchmark trials. `requests.json` and `whole-results.json` preserve full scripted requests and outcomes.

## Reproduce and review

With Python3.14.3 and `pydantic-monty==1.2.0`, run `python reproduce.py`. It checks pinned inputs, copies the folder into a temporary directory, rebuilds exact parent and candidate, reassembles the sealed trace, reruns boundary/whole-agent controls, and requires13 generated outputs to match byte for byte. `build.py` also works under Python3.12.7. No network or inference service is used during reproduction.

Independent review is pending. The candidate is not combined with the ready OCR or retry packages, and no source or artifact in those sealed packages was edited. Generalization to other provider/runtime error formats and actual model continuation remain unmeasured.
