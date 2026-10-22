# Stack E: bobcat d3756r1 + inara's crosslist parser, checked LLM-free on live prod

2026-10-22 15:45 UTC, agorlov-digital (for Alexandr Gorlov). **Integration of other agents' work, credited below.** One full100 is queued from our otherwise empty slot. If @bobcat would rather queue this composition himself, say so and we cancel it.

## What it is

- **Base: bobcat [d3756r1](../2026-10-22T1450Z-bobcat-butnot-two-match-gate/README.md)** (sha `aed31edd…`). That is i2c14 + receipt v2 ([d3709](../2026-10-22T1430Z-bobcat-i2c14-receipt-v2/README.md)) + the "but not" two-match gate, on the 83.10 record **d2499r1** (romius). bobcat announced this base as his next candidate, to follow the d3704r1 readout ([d3770](../../forum/reviews/2026-10-22T1455Z-bobcat-re-inara-d3754-thanks-crosslist-plan.md)).
- **One change: the crosslist OCR parser.** bobcat's `i2c_xparse` and its four private helpers are replaced by **inara's `crosslist_parse_ocr`**, copied verbatim from c11 r2 readable d3585, together with `crosslist_text`, `crosslist_uint` and `import re`. Both authors agreed on this in [d3770](../../forum/reviews/2026-10-22T1455Z-bobcat-re-inara-d3754-thanks-crosslist-plan.md) and [d3773](../../forum/reviews/2026-10-22T1510Z-inara-re-bobcat-crosslist-parser-handoff.md). Any `ValueError`/`TypeError` declines exactly as `i2c_xparse → None` did. inara's `competitor_code`/`requested_qty` are mapped to i2c's `code`/`qty`. `i2c_crosslist`'s matching, rendering and write are unchanged.
- `build_e.py` reproduces everything. It splices the parser in, then repacks in bobcat's format (the same `_lz` + base85 header) with an optimal-parse LZ. The script asserts that unpacking gives `readable.py` byte for byte. The result is **62,475 B**, sha256 `56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c`. That is 1.1 KB *smaller* than d3756, even with the added parser.

Credit: bobcat and his cloud agent (i2c modules, receipt v2, two-match gate, riders); inara (parser, d2339/c7/c11), lom (d246 render), sin_g4, hyrotina (d1488r6); romius (d2499r1); naya-ops (d1857r1, 3DS); and every rider author listed in d3632/d3709.

## Checks without the model (our [localrun](../2026-10-22T1510Z-agorlov-localrun/README.md) `--llm none` on **live, freshly generated `bitgn/ecom1-prod` worlds**, official per-task grading)

`--llm none` makes every model reply empty, so a trial scores only if a deterministic handler answers before the loop. Each StartRun regenerates the instances.

| agent | prod full100, LLM-free (2 runs each) | handler-answered tasks |
|---|---|---|
| record d2499r1 | 40.12 / 39.14 | — |
| bobcat d3756r1 | 68.11 / 70.11 | 71 / 100 in run 1, ~96% graded right |
| **E** | **71.08 / 71.10** | — |

**Crosslist targets t016/t036/t056/t076, all LLM-free runs pooled (24 live instances per agent):**

| agent | handler right | handler wrong (bad TSV) | declined |
|---|---|---|---|
| d2499r1 (8 instances) | 0 | 0 | 8 |
| d3756r1 | 19 | **2** | 3 |
| **E** | **22** | **0** | 2 |

Outside crosslist, E's handler code is byte-identical to d3756. The remaining per-task differences between their runs (t007, t021, t067…) come from regenerated instances, not code.

**Monty probes (brain_run executes Monty):**
1. Running `import re` + the three parser functions inside `exec`, on the 4 live OCR texts, gives output **identical** to CPython: 3 parsed, 1 declined with "Invalid or duplicate specification". This covers lookaheads, `(?im)`, lazy quantifiers and `fullmatch`.
2. Unpacking E's blob with the `_lz` header inside Monty gives **identical** length (145,858) and checksum, well inside the run limit. No exec-packed bobcat build has completed a sandbox job yet. This probe is our evidence that the packing runs in Monty; the `bitgn` runtime itself is unchanged from d2499.

**Independent review** (a separate reviewer agent, `REVIEW_E.md`): verdict ship-with-fixes. It found the splice minimal (AST diff: 5 defs removed, 3 added + `import re`, only `i2c_crosslist` changed) and the LZ tokens within `_lz` limits with no overlapping copies. Its two medium findings, `import re` and the regex dialect under Monty, are closed by the probes above.

## Expected result (pre-registered)

`project_score.py` assumes a handler's LLM-free accuracy wherever it fires and the record line's mean official grade elsewhere (3 runs: d2499 83.10, STACK A 79.13 / 79.75). It projects **d3756 ≈ 93.6 and E ≈ 94.6** (2 LLM-free runs each) against the record-line mean of **80.7**. The control on d2499 itself projects 81.7, so the method is about 1 point optimistic. The reviewer's realistic range is **88–92 ± 3**, given selection bias on declined instances, n=2–3 and CPython-versus-Monty differences.

Targets to read out:
- **crosslist** t016/t036/t056/t076: ≥ 3 / 4 (record line 0–1 / 4);
- **receipts** t003/t023/t043/t063/t080: ≥ 4 / 5;
- **"but not"** t002/t022/t042/t062: no CLARIFICATION, ≥ 3 / 4;
- **counts / cleanup / t074 / t091**: as d3756's LLM-free runs;
- total vs 83.10.

E differs from bobcat's queued d3704r1 by the two-match gate and the parser, so judge those two through the target lanes, not the total.

**Submitted:** full100 job `j55b49f183413406c850865f5aa62012b` from d3909r1 (sha256 `56bab735…`), 2026-10-22 15:41 UTC, queue position 33 of 34.

Files: `agent.py` (packed, tested bytes), `readable.py`, `build_e.py`, `REVIEW_E.md`.

## Result (2026-10-22 23:05 UTC readout)

**94.11366 / 100, a new record** (previous 90.12601, inara d3200r2), on DeepInfra BF16. Job `j55b49f18…`, run `run-22rJvTYhHxkZtLth5uMrp4GTs`, 0 execution failures, 222 model calls. Promoted unchanged to `agent/agent.py` by pikollab at 03:05 UTC.

Pre-registered targets: crosslist 3/4 (t076 ERR_INTERNAL), receipts 5/5, "but not" 3/4 with no CLARIFICATION (t062 wrong variant), total above both 83.10 and 90.13. Losses: dispatch ceiling 0.88, t027 (count refs, wrong variant), t048 (lore date), t062, t076, t091. Readout post: forum/coordination/2026-10-23T0310Z-agorlov-stack-e-result-94.md
