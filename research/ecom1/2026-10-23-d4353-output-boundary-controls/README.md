# d4353 main versus forced output boundaries — offline source controls

The phase asymmetry is reachable and partly protective. Exact d4353 rejects every `length` response in its main loop before parsing, but the forced branch parses a response regardless of finish reason and dispatches **only** `report_completion`. A complete, truthful report can remain usable despite `length`. A uniform action-acceptance rule is therefore not supported by these controls.

**76 native whole-agent executions pass:** 19 payloads × main/forced × exact readable/packed source. This is a source-control experiment with fake inference and in-memory RPC effects, not a candidate repair, provider test, task-score result or evidence that a forced `length` response occurred in a live run. The sealed upstream audit found all 25 selected null/length responses in the main loop; it is copied as provenance and remains unchanged.

## Exact sources and reproduction

The parent is verified record **d4353r1**, packed 63,211 bytes, SHA256 `588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e`; readable 153,653 bytes, SHA256 `f898132a754187b0052a637e1ca4caaccdd3ac46f72df80bc11d2b37b3737d0b`. The exact original builder, donor, packer and parent inputs are local in `parent-build/`. `verify_inputs.py` rebuilds packed/readable/decoded bytes and verifies every copied input plus all 135 archived RPC response receipts, 126 Read files and four explicitly derived Tree results. No parent source line changes.

Use Python 3.14.3 with pydantic-monty 1.2.0:

```sh
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python research/ecom1/2026-10-23-d4353-output-boundary-controls/reproduce.py
```

The interpreter path is this workspace's installed runtime; another installation with the pinned versions is supported. `verify_runtime.py` checks the installed public ClassInstance source against the saved exact bytes. The harness uses `ClassInstance(host, allowed_methods={...})` with default `lazy_attrs=None`; an independent negative control verifies that extracting `bitgn.call` as a value fails. Limits are 10 seconds per feed/turn and 1000 suspensions. No network, Brain, actual inference or ECOM mutations occur. `prepare.py` documents original copying only; it is **not** needed by isolated reproduction. Inputs are all local, with no writable external-folder assumptions. `reproduce.py` runs in a temporary standalone copy and compares eight generated outputs byte-for-byte.

## Fixture and injection boundaries

The main fixture is the previously archived **d3909 t076 crosslist world** from the retry comparison, not d4955 t076 and not a claim about d4353's paid task-ID draw. It contains the actual instruction for `/uploads/5qt53BQ6_competitor_purchase_request_ocr.txt` and `/exports/crosslist-JgSownP1.tsv`, archived policy/catalogue RPC responses and the fixed archived router response. Running exact d4353 against this declared simulated host makes its deterministic helper decline into the main loop. Unmatched RPCs fail the test; the only additional RPC results are explicitly fake mutation acknowledgements.

Read-only arithmetic cases explicitly replace the instruction with “what is 1 + 1?” and use a scripted empty-doc router result. Their report `2` with OUTCOME_OK is independently true and requires no mutation. This is a benign synthetic compatibility control, not a replayed live task. The other complete report explicitly says that no export was written and more catalogue work is needed; it makes no false completion claim.

For main injection, the first main response is the test payload; if the loop continues, a separate scripted non-success recovery report follows. For forced injection, three preceding main responses—null/stop, partial JSON/length, and non-JSON/stop—reach the shared three-consecutive-invalid threshold, then the forced response is injected. Every request/response is preserved in `requests.json` / `responses.json`. Exact readable/packed request, RPC, stdout, answer and in-memory-effect parity is asserted. Main and forced inference settings are both max_completion_tokens=2048, medium reasoning, temperature=0; the fake host does not validate provider routing, wire limits or accounting.

## Observations and policy tradeoffs

`decision-table.md` gives all 19 paired payloads; `results.json` retains all 76 executions and their calls/answers/effects. `policy-matrix.json` compares hypothetical **acceptance decisions on these fixed payloads only**; no alternate policy is integrated or executed.

- Complete plain and fenced reports with `stop` are accepted at both boundaries. Complete plain and fenced reports with `length` are rejected at main, requiring one more scripted main response, but accepted at forced. The arithmetic controls show that forced acceptance can preserve a true, benign result. Blanket rejection of forced `length` would lose these reports; no actual alternative model recovery is implied.
- Partial JSON and null content are not dispatched. At main they consume one invalid step and then accept the separately scripted recovery report. At forced they produce the existing generic OUTCOME_ERR_INTERNAL answer. Three mixed invalid main responses reach forced after only three main calls; the inherited “30-step limit” wording is inaccurate here. That reporting issue was already established separately and is not a new repair in this package.
- A complete report followed by a truncated second report is accepted at forced: `first_action_object` returns the first balanced object and ignores the tail. This is a concrete syntactic ambiguity witness; the scripted first arithmetic answer is still true. We do not infer that a real truncated tail retracts the first report or that accepting it changes a grade. Main rejects the same `length` payload.
- A normal-stop Read is dispatched in main, while a length Read is rejected. Forced Read is ignored for both finish reasons. The same phase restriction holds for Write, Delete and the scripted stateful `/bin/discount` Exec: main/stop dispatches exactly once; main/length and every forced version dispatch zero times. All effects exist only in the fake host's dictionary/list. This establishes source dispatch behavior, not real service authorization, command semantics, idempotence or successful artifact creation.

A uniform “accept any parseable action” rule would permit the main length mutations suppressed today and, if it also removed the phase filter, permit forced nonreport actions. These are clear regressions to the current conservative boundary. Keeping the forced report-only filter is necessary regardless of any shared parser implementation.

A shared **plain whole-text JSON report exception** would accept complete main length reports and reject trailing partial second objects, but it would also reject fenced reports already supported by the source; the additional fenced cases demonstrate that benign compatibility regression. A carefully normalized whole-response grammar could preserve fences, but was not designed or validated here. Even such a grammar would establish syntax, not truth, evidence sufficiency, successful mutation or correct outcome. The earlier completion-integrity audit remains separate.

**Recommendation:** retain phase-specific dispatch and do not promote a shared acceptance-policy repair based on these controls. The asymmetry alone is not a defect. If future evidence warrants a report-only acceptance change, require explicit compatibility rules for fences/wrappers, trailing-content handling and semantic completion reporting; preserve the main mutation-length guard and forced nonreport prohibition. There is no observed forced-length incident or demonstrated live/aggregate gain in this package.

## Files and limits

`INPUT-PINS.json` pins 25 original inputs. `verify_inputs.py`, `verify_runtime.py`, `test_boundaries.py`, `compare_policies.py` and `reproduce.py` reproduce the evidence. Public runtime source is saved under `runtime/`. `SHA256SUMS.json` seals this author package; independent review, if added later, remains outside that seal. Fake successful mutation acknowledgements deliberately avoid testing real command failures or retry semantics. No prior inference-retry suite or paid diagnostic was repeated.
