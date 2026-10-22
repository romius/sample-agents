# Record-based integration and evidence

Romius, 2026-10-22. The strongest verified baseline remains **inara d3200r2, 90.12601/100**, installed as d298r17. Brain BASELINE d7r28 and the complete d3204r4 experiment notes were refreshed and saved. Our d3512r1 finished at **82.69149**, below both that record and our older d2499r1 (83.099496). No promotion is warranted.

## Concrete composition

| Component | Decision | Evidence and limits |
|---|---|---|
| d3200r2 crosslist preparation, export and path-only answer | Inherit unchanged | Record passes all four crosslist tasks; both our runs failed all four. The handler computes the export from policy/world data and confirms Write's returned path. Different generated inputs mean this is coverage evidence, not a causal eight-run comparison. |
| Receipt availability, branch/SKU resolution and price drift | Inherit record logic | d3204r4 documents conservative SKU/price tie-breaking; four explicit counterexamples reproduced locally. Exact-looking OCR loses to another in-range SKU at the receipt line price; ambiguous unmatched prices decline. No nearest-SKU override. |
| Quantity OCR, codex d4354r1 | Add original-first S-to-5 fallback | 408 parser checks, 20 handler cases, 14 clean-parent comparisons; archived t043 receipt parses consistently with its subtotal. Existing accepted inputs retain their first-pass interpretation. Both SKU and price corrupted together remain a limitation. |
| Policy-aware stock exclusion, bobcat d4236r1 through codex d4354r1 | Add | Default catalogue policy retains excluded-SKU evidence; the exception clause drops it. Both document variants tested. d4469 cites live activation and census evidence. This does not prove every sibling selection is correct; the citation predicate also has limited wording coverage. |
| Staff count, fractional discounts, product existence, 3DS | Inherit once; do not port ours again | All are already in the verified record. All ten 3DS cases across our two runs passed. The AST provenance check preserves these functions. |
| Injection gate | Keep record guard; do not union with our broad/narrow guards | All 200 observed requests compared. Record catches the Unicode relay in new t097 missed by our guard. Eight observed malicious requests deny before mutation in exact packed native tests. Benign HTML comments and quoted role-analysis requests still trigger false positives; ordinary policy words, short inline CJK and bracketed dimensions do not. A new semantic guard needs its own validation. |
| Delete-404 | Preserve record containment unchanged | The response becomes an unconfirmed observation, not proof of successful deletion. Our missing-Exec branch is separate. Six error-boundary checks preserve propagation of unrelated failures. |
| Community deterministic cleanup shortcut | **Disable** | Concrete two-file fixture: first Delete succeeds, second raises404; the shortcut nevertheless returns OK with a partial path list. It bypasses the record's unconfirmed-Delete path. The helper remains in the pinned donor source but is absent from active I2C_MODULES. This candidate does not claim to fix new t060's path-only formatting loss. |
| Missing-executable Exec404 from d3513r1 | Preserve only its narrow branch | Old t079 actually crashed on missing /bin/ls. A whole-agent counterexample reproduces the parent crash and candidate recovery through native reads, without a futile --help retry. Generic Exec404, malformed404 and infrastructure errors still propagate. New t079 never activated this branch, so its live pass is not evidence of repair efficacy. |
| Inference retries, msh d4445r1 | Add exact MSR helper at four call sites | New t028 failed on a provider read timeout. At most three inference attempts, same model/messages/options. HTTP status takes precedence: 5xx retried; 4xx/429 are not swallowed by body words. Unknown/persistent failures propagate. Eleven whole-agent CPython/readable/packed/native cases; no runtime mutation retry. Unknown-outcome inference retries may incur additional provider cost. |
| New discount binding, inventory compiler, further receipt SKU repair, dispatch changes | Defer | Community discount counterexamples over-apply rates; inventory grammar/CSV semantics need composed validation; dropped-character SKU repairs need ambiguity controls. Dispatch's roughly0.87 total loss has no proven recoverable mechanism. No task-ID rules or known-answer constants added. |

## Starting point and reproducibility

The verified parent is **d3200r2/d3201r2**, not the ungraded d4353 experiment. The package pins both exact record sources. `pack5h.py` d2829r1 with python-minifier3.4.0 reproduces d3200r2 byte-for-byte. A saved patch reconstructs d4354r1 from d3201r2; every original top-level AST node except the reviewed receipt parser survives in order. d4353's full100 is still queued at our last check and is not treated as another verified baseline.

`build.py` verifies parent hashes, reconstructs the intermediate source, applies the three final deltas (MSR, missing Exec, cleanup deactivation), and uses pinned bobcat lzpack d3268r2. It checks decoded AST equality. The final artifact is **63,209/65,536 bytes**, leaving **2,327 bytes**, SHA-256 `b5bf80e4eb3eb4f5ee86dfad2442606e33da8102a9edbac85222ecc395d507f8`. Readable source is retained separately. No model, reasoning-effort or task-input changes are included.

Dependencies and exact Brain revisions are in `dependencies.json`; all package files are SHA-256 indexed in `SHA256SUMS`. Build with Python3.12.7 and system `patch`; tests use pydantic-monty1.2.0. The historical record pack check uses python-minifier3.4.0. `reproduce.sh` records the sequence. Test doubles do not contact the provider or mutate live worlds.

## Review and validation

All **200 tasks**, including passing tasks, were reviewed: request, answer/refs, complete event index, agent output/action log, nonbootstrap Exec and file mutations, and errors. `TASK-REVIEW.md` gives all100 paired rows; `all-task-review.json` and forty trace chunks retain evidence. This is not a claim that every raw Read payload or hidden oracle was independently reconstructed.

27 archived worlds replay without crashes, with answers equal to the exact record and all replay fields equal to the immediate integration parent. These are **advisory** recorded-response comparisons: seven candidate worlds require reads absent from the archive, complete model-request capture is unavailable, writes/deletes are captured rather than applied, and oracle scores are not recomputed. This does not predict a full100 score. `archived-replay-results.json` preserves all misses and fidelity fields.

Additional checks: 408 parser cases; 20 receipt-handler cases;14 clean-parent comparisons;11 full-agent scenarios in readable, packed and native forms; six lookup-error boundaries; eight observed attack requests;200 guard comparisons; seven benign/attack counterexamples; two policy variants; four SKU/price resolution cases; cleanup partial-failure counterexample. Results and scripts are committed together.

## Attribution and evaluation

Old83.099496 used Cerebras FP16. Our repair82.69149 and record90.12601 used DeepInfra BF16; the repair provider is verified in trace4258. Only seven instruction strings match across our two runs (t028,t030,t044,t051,t059,t081,t086), and identical wording still permits different worlds. Matching task IDs is not a paired experiment. Lower new scores occurred at t021,t028,t035,t041,t048,t060,t062,t063,t097; `TASK-REVIEW.md` explains each. These are observed score regressions, not established code regressions.

The existing human authorization permits one new full100 of the exact committed candidate after these checks. At completion, refresh Brain's record and compare official full-precision run_score. A strict higher completed100 must be promoted immediately using exact tested bytes, updating agent/agent.py, BASELINE, README and Integrate handoff together. Ties, incomplete runs and lower scores do not promote. Record regressions, costs and provider/input differences even if a winner is promoted. **99% remains a target, not a forecast.**
