# Integration onto the verified STACK E record

Status: evidence gathering and design, not a submitted candidate. The new baseline supersedes the earlier inara-based integration plan. Three previous full100 jobs remain queued or running; the inventory-only exception is consumed and the normal two-outstanding limit prohibits another full100 until fewer than two remain.

## Exact starting point

Use **d3909r1**, 62,475 bytes, SHA-256 `56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c`. Official completed100 result `j55b49f183413406c850865f5aa62012b` is **0.9411366**, with zero execution failures. Installed d298r18 was independently checked byte-for-byte. Readable d3910r1 and build d3911r1 are being preserved with their exact dependency revisions. Current headroom is **3,061 bytes**; do not assume another module fits. Keep the readable source and deterministic packing script as first-class artifacts.

This is an observed +3.98765 points against inara d3200r2, not a causal estimate of the parser or other code changes. The record has 90 full grades, five zeros and five dispatch partials. All100 result/StartTrial rows are being audited; bounded primary evidence for every loss is being retrieved before selecting repairs. Compare actual instructions, policies, world records and provider events, not just ordinal task labels.

## Inherit and preserve decisions

| Area | Decision | Supporting evidence / remaining gate |
|---|---|---|
| Record stack | Inherit exact STACK E behavior first. Do not paste the old d5785 stack wholesale. | Completed10094.11366; exact installed hash. Build and all-task audit in sibling `2026-10-23-stack-e-record-review`. |
| Crosslist | Keep the record's inara parser and existing matching/export logic. Change only after tracing the remaining crosslist failure. | Exact upstream build replaces only parser plus key mapping; review records native parser checks. New run t076 is a loss requiring actual trace, not an assumed parser defect. |
| Staff counts, discounts, product existence, 3DS | Keep existing handlers once, with no duplicate routing. | Present in exact new readable source. Earlier branch fixes must be compared at function/behavior level before any port. |
| Missing executable Exec404 | Preserve the narrow donor behavior if whole-agent integration passes. Replace the broad overlap; do not add a second generic Exec branch. | `guard-comparison.json`: record already recovers missing executables, but also labels missing payment/generic Exec404 as harmless lookup failures. Narrow donor accepts only `not_found` plus `runtime tool not found` and gives native-tool guidance. No mutation retry. |
| Delete404 | Port unconfirmed-effect observation independently; inspect deterministic cleanup first. | Exact record returns no recovery for Delete404. Donor marks effect unconfirmed and instructs no retry/check remaining targets. Active record cleanup catches every Delete exception and still returns OK, so adding only main-loop recovery would not cover it. Existing partial-Delete counterexample must be replayed against the exact record; preserve successful cleanup behavior if repairing it. |
| Inference retry | Consolidate overlapping control flow before porting MSR. Preserve request bytes/options and exclude nontransient errors/cancellation from custom retry. | Extracted exact main guard already retries every Exception up to three times. Naively nesting MSR produces nine attempts on persistent transient failure before forced reporting. Tests include HTTP400/429, unknown errors and cancellation text. Router, catalogue narrowing, main and forced-report callsites require separate decisions; SDK429 retries remain transport behavior. |
| Forced-report size | Carry forward pre-inference history trimming only if the exact record reproduces a request over the source-independent inference payload cap. | Record trims main-loop messages but appends forced-report instruction without another trim. Existing old-parent benign history witness is not automatically a new-parent witness. |
| Inventory CSV | Reuse validated compiler/oracle and named guest callback primitive only if record overlap leaves a demonstrated failure. | Record already has a CSV handler. Old d5204/d5785 callback-value access is unreachable under method-only SDK exposure; minimal wrapper repairs pass216checks each and independent native replay. Archive d6376 preserves evidence, not a new baseline candidate. Actual zeroLLM SDK probe is queued. |
| Receipt/SKU/price | Compare record handlers against archived and benign cases before porting standalone-header or cited-SKU formatting changes. Keep pending C/L evidence separate. | First16 and community60 diagnostics show narrower gains and qualifier/reference regressions than mechanical counters imply. The submitted68C/L diagnostic changes only lexical arrays after row selection; no production readiness follows before full manual review. |
| Injection protection | Keep exact record protection while testing concrete differences. | Prior352 executions demonstrated benign-marker denials but no generally safe weakening. Normal /bin/id cannot emit lookalike roles; do not add a handler for an unreachable output. |

## Validation and release gates

1. Finish the exact-source dependency closure, all100 evidence table and loss analysis. Classify each change as confirmed runtime correction, synthetic/local behavior improvement, model-level observation or untested hypothesis.
2. Build one minimal integration from d3909r1 with a manifest for every inherited/replaced function. Validate negative and benign boundaries, archived worlds, source-defined test limitations, and native method-only SDK exposure. Never retry mutations or manufacture references on fallback.
3. Run the relevant record and donor regressions against readable, prepack and packed forms. Reproduce new-parent request-size witnesses; prove retry limits across all callsites rather than multiplying independent guards. Preserve exact clean-request behavior where intended.
4. Measure final source bytes after every module, assert decoded equivalence, and reproduce the packed hash from clean extracted inputs. If packing changes, validate packing separately from behavioral changes and retain exact dependencies/runtime versions.
5. Preserve exact parent/candidate, build, tests, hashes, results and limitations in local Git and Brain before any evaluation. A short diagnostic may resolve a concrete uncertainty; do not repeat existing evidence or submit a candidate critically dependent on unfinished experiments.
6. Submit a full100 only when authorized capacity and cadence permit. Compare completed full-precision official scores against the refreshed record; promote only exact tested bytes of a strict winner according to Brain rules. Keep existing queued sources immutable and do not cancel them.

## Focused guard evidence

Run `python3 -W ignore::SyntaxWarning research/ecom1/2026-10-23-stack-e-integration-plan/compare_guards.py` from the workspace. It extracts the actual recovery functions and main-loop exception AST from pinned local sources, tests12 lookup boundaries and16 error scenarios across three retry compositions, and records source hashes. It deliberately excludes forced-report calls, routing, action processing, native SDK dispatch and provider retries. It is a control-flow counterexample, not an archived-world replay or whole-task recovery claim.

Independent guard review found synthetic cancellation messages containing `connection` or HTTP503 are retried by donor MSR. These two counterexamples are now included: the old wrapper is not cancellation-safe merely because literal `cancelled` alone is rejected. A new integration must resolve this before any hosted execution.
