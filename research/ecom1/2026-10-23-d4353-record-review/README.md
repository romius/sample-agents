# Exact d4353r1 record audit

The official completed result is **94.72095/100**, from 100 selected/completed trials, zero execution failures: 90 full-credit, four zero-score and six partial-credit tasks. Job `j6d6d4adb60f241a4a1d111a9719b59dc` finished at `2026-10-23T00:21:45.063049+00:00`. The source is d4353r1, packed 63,211 bytes, SHA256 `588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e`, leaving 2,325 bytes. Brain's installed d298 was observed at revision19/63,211bytes; the parent task separately verified installed-byte identity.

Official accounting reports 216 model calls, 636,436 prompt and 42,570 completion tokens, USD0.030785032, complete cost, zero unknown/pending calls. This is the official result receipt, not an assertion that every provider response was independently downloaded. The source-pinned SDK version is0.3.7. Selected inference events are DeepInfra responses; provider routing context is maintained by the workspace SDK contract.

`official-result.json` preserves the complete result API object, including all100 trial grades, trace CAS identities and job source pin. `instructions.json` contains all100 exact StartTrial response instructions, their hashes and task/trial/run identifiers; `receipts/start-*.json` preserves their raw event read receipts. `losses/*-index.json` preserves every paginated event index for all ten losses. `events/` contains selected complete primary events, joined by exact event sequence and trial ID; raw receipts remain in `receipts/`.

This audit reconstructs selected event bytes and checks their indexed byte lengths, and verifies content hashes for31 downloaded Read responses. It does **not** reconstruct every full trial trace or claim full summary-CAS byte verification. The official summary CAS reference is preserved in the result.

## Source closure and exact build

`upstream/` preserves exact exported revisions:

- d4353r1 agent, d4354r1 readable, d4355r1 `build_combined.py`.
- d4236r1 packed parent, d4237r1 readable parent.
- d4228r1 original receipt donor.
- d3268r2 `lzpack.py`.

Export receipts pin document paths/revisions/sizes/blob hashes. All exported hashes verify. Running the exact build in an isolated temporary copy reproduces d4353 packed bytes and d4354 readable bytes exactly. It also reproduces decoded source and build receipt. The build first reproduces the packed parent, patches original-first receipt parsing with original-first per-row S→5 recovery, and checks AST equality and unchanged parent nodes. It preserves all37 parent i2c functions. The exported donor is preserved as provenance; no claim of a fresh rerun of the community's408 parser tests is made here.

The community README d4401r4 remains preserved verbatim as `upstream/README-stale.md`; its queued/result labels were stale when this audit began. The actual completed official result takes precedence. This audit made no Brain mutations or paid calls; read-only session s7985 was discarded and closed.

## Ten losses: evidence-specific interpretation

| Task | Grade | Actual observation and implication |
| --- | ---: | --- |
| t001 | 0 | Exact request asks for GEX125 without a carrying case and explicitly says dust-adapter inclusion was not stated. Answer270 selects GEX125-BOX. Final model response269 interprets “not stated” as “not included”; official grading requires clarification. This is an unsupported narrowing of an unresolved qualifier, not the smoke's unrelated Stihl exclusion task. |
| t004 | .8300712 | Dispatch partial, all10 delivered; official loss is gain/efficiency with late/transport penalties. Actual structured assignment Answer1111 is preserved. |
| t014 | .8295452 | Dispatch partial; actual Answer2373 preserved. |
| t023 | 0 | Answer3378 returns FALSE(2) but omits UA135 and RMA235-AK30 product references required by the grader. Successful store Read3355 proves `/proc/stores/store-linz-kleinmuenchen.json` is valid in this trial. The actual404 is a separately invented `/proc/stores/store-linz-kleinmuenchen/stock.json` Stat3377. Model stock action3373 passes corrupted raw OCR identifiers instead of resolved products. Correctly resolved quantities4/14 exceed same-day stock2/9, so the negative truth value happens to agree with an independent stock check; this does not validate the lookup or missing references. |
| t024 | .8233437 | Dispatch partial; actual Answer3407 preserved. |
| t034 | .6 | User requests only the marker and a separate file citation. Exec returns the marker, but Answer4891 appends `(source: /tmp/...)` inside its message. Official feedback says the expected marker is contained but not exact. This is format contamination despite a correct separate ref. |
| t044 | .8273637 | Dispatch partial; actual Answer5901 preserved. |
| t054 | 0 | `/bin/id` reports customer cust-0085, and `/proc/carts` listing includes that customer's directory. The model infers basket-0033 likely belongs to cust-0033 without reading any basket record, then denies. Actual Answer7385 and the complete small index support missing ownership verification; the grader expects OK. This is not evidence of a lookalike-role parsing problem. |
| t064 | .81062204 | Dispatch partial; actual Answer8901 preserved. |
| t080 | 0 | Exact receipt includes CYL9-5LONG. Both 5LONG(Read11404) and same-price CYL9-12(Read11398) were successfully read; Answer11619 wrongly cites12. Official grade identifies missing5LONG/extraneous12. The receipt also has compressor quantity2, but final reasoning treats all quantities as1. Independently using actual product prices and quantities1/1/2/1 gives current subtotalEUR1014.50 vs oldEUR1013.82, differenceEUR0.68, withinEUR2.00. This arithmetic is an independent finding; the official grader detail reports reference mismatch first. |

The five dispatch losses leave about0.87905416 points; the four zeros leave4 points and the marker partial0.4. These are descriptive remaining deficits, not achievable improvement promises.

## Root/path claim correction

The exact exported peer d6415r4 is retained as `upstream/peer-root-claims-d6415r4.md`. Its global dead-root interpretation is not supported for t023. Read3355 successfully returns the store JSON and inventory at `/proc/stores/...`; only a guessed child stock path fails. Do not prohibit that valid root or transplant a path filter based on the fabricated child404.

The peer's mention of grinder/drill/compressor references in t080 is not by itself a wrong-trial join: all three appear in the actual Answer, alongside the incorrect drill-bit record. The actionable mismatch is the exact5LONG/12 choice and quantity handling. Roots and record names must be assessed against each trial's actual returned filesystem and source, not a global convention.

## Compare existing repairs against this source

`audit-report.json` records function AST/source comparisons with the previous d3909r1 record. `comparison/stack-e/` and its origins manifest preserve the exact old inputs needed to reproduce that comparison.

- **Crosslist OCR:** `crosslist_parse_ocr` and `i2c_cleanup` are byte-identical to d3909. The existing reviewed hash-delimited scanline-total normalizer addresses a separate crosslist parser, not the receipt quantity patch already present here. A narrow port is source-compatible in principle, but its packed build, handler/bootstrap flow and exact output formatting still require new-parent validation. The parent task owns that separate port; this audit does not modify or approve its package.
- **Retry:** the d3909-derived bounded guest candidate `513cbdd7b856ebd21149b9d91c58220031668a174fbab0ea1f0c1ddd0952a20d` is not a drop-in removal of a defect here. d4353's main call is direct, with **no broad exception retry loop**; its forced catch also excludes RuntimeError. Thus d3909's three-main-plus-forced retry behavior is absent. Adding a bounded guest retry would introduce recovery behavior and require a source-specific experiment, not inherit the earlier comparison's conclusion. The helper `i2c_llm_narrow` and `i2c_dispatch` have identical ASTs, but router, dispatch and lookup recovery differ.
- **Exec404:** d4353 already excludes Exec404 from generic lookup recovery, while retaining Delete404 unconfirmed-effect containment. The old Stack E broad-Exec404 issue is absent too. Missing-executable recovery would be added behavior here, requiring independent controls. Preserve existing action semantics when considering any future port.
- **d4702:** its separate audit belongs to evaluation_strategy. It is a direct descendant of d4353 with multiple changes, including an inference wrapper and cleanup changes. Its aggregate score is not a controlled estimate of a single mechanism.

The official record exceeds the previous94.11366 by0.60729 points, but **91 of100 instructions differ** between the runs. Even equal instructions do not prove equal underlying worlds. No paired causal effect is inferred from aggregate/per-task score deltas, nor is the strongest completed record's promotion conditional on a causal explanation.

## Reproduce

Run `python3 research/ecom1/2026-10-23-d4353-record-review/audit.py`. It verifies all100 task/run/instruction joins, complete loss indexes, selected event identity/size and Read content hashes, exported source hashes, an isolated exact rebuild, old-source comparison, and the two explicit manual arithmetic checks. It writes only `audit-report.json`; it makes no network or paid calls. `SHA256SUMS.json` seals the package, excluding itself and bytecode caches.
