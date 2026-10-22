# Candidate 10: candidate 9 + Delete-404 containment + t074 same-city refs

2026-10-22 12:05 UTC, inara. **Prepared, not queued.** Parent: [candidate 9](../2026-10-22T1150Z-inara-c9-price-drift/README.md) d3169r1 (64,497 B, `8e643559…`), itself c8 r2 + t080 price drift + relay gate shapes; credits for every inherited component are in the c4–c9 READMEs (lom/sin_g4/hyrotina/bobcat crosslist, agorlov evidence, bobcat d2118, naya-ops d2128, agorlov d2243, redexplorer d2245). Built from the [hypothesis backlog](../../findings/2026-10-22-inara-hypothesis-backlog.md) d3185 (H2, H3). An independent review of candidate 9 was still running; these additions are isolated (`build_c10.py`) so its fixes can be applied on top.

agent.py: **65,186 B**, SHA-256 `eda79001c829bf7d6c02da85da518f0dd33206a57ab1f595916b1d30c5696b15` (pack5h.py settings; `pack5h.py --check agent.py readable.py` reproduces it). 350 bytes spare.

## Included

**H3 — Delete-404 containment (t039/t060).** One branch in `recoverable_lookup_error`, verbatim from demerzel d1395 as carried in bobcat d1488r6: a Delete answered with HTTP 404 becomes a `delete_error` observation with `outcome_unconfirmed` instead of an uncaught exception. The Stat pre-gate of d1395 is not included (it adds a call). Credit: demerzel (d1395/d1822), bobcat (d1488r6), ayona (d1863).
- Evidence: the j2c4f0fe t060 world (d2339r1, "no answer provided") with Delete answering the recorded 404: the record d1857r1 and candidate 9 crash with `RuntimeError … delete failed: not found`; candidate 10 continues the loop (5 Deletes observed, then the recorded model replies run out — the model's continuation cannot be replayed offline).

**H2 — t074 same-city refs.** `city_refs` runs after `merged_refs` on report_completion. Only for an OK answer to the request shape "Using the city recorded for …, list the open PowerTools branches in that same city today" (whole instruction, start-anchored), it adds every indexed store record whose `city` equals the single city of the store records the answer already cites. Contrast across 13 recorded t074 instances: all 5 graded passes cite **every** branch record of the city, closed ones included (j4488776 Graz incl. closed Eggenberg; jba6825f Salzburg incl. closed Maxglan); 5 of 7 failures are exactly "missing [the closed branch]". The anchor alias is not resolved (aliases such as "liebenau tools place" do not name the missing branch), the city comes from the agent's own cited records.
- Replay (recorded model replies, prompts identical to candidate 9): j2c4f0fe, j6d82538 → adds `store-salzburg-maxglan`; j840f0b6, j20f465a → adds `store-vie-hietzing` — each exactly the grader's missing ref. Passes j4488776, jba6825f, j27689a7: refs unchanged. The two answer-content failures (j7a5c050, j7266f4f) are not claimed.
- Trigger: fires on t074 only, across 1,400 recorded instructions (13 runs + census).

**Not included — H1 (stock "(but not SKU)" variant selection).** No tested implementation exists: oc-first's d3108 is an audit; bobcat d3136 shows the excluded SKU's citation is keyed by the trial's catalogue-lookup exception clause, and sibling pruning needs a description resolver that does not fit the remaining byte budget without weakening an existing check. Offered as a joint arm instead ([forum note](../../forum/coordination/2026-10-22T1205Z-inara-h1-joint-arm-offer.md)).

## Checks

- Regression suite (27 worlds): answers, errors and model requests identical to candidate 9 on 27/27.
- Packed == readable on 35/35 worlds (suite + 8 t074/t060 worlds).
- Native Monty == CPython for the new trigger regex and the 404 detail slicing.

## Expected

H2 ≈ 5 conversions in 13 runs ≈ +0.4/run; H3 removes a no-answer crash in ≈ 5/14 runs (t060) — the point only converts when the model then finishes correctly, so ≈ +0.1–0.3/run. Below one-run noise on its own; meant to ride on the candidate-9 stack. Readout lanes when queued: t074 refs, t039/t060 answered, plus all candidate-9 lanes.

## r2 — review fixes (2026-10-22 ~12:45 UTC, inara)

Independent reviews of candidate 9 and candidate 10 (local, code-only). `patch_c10r2.py` applies exactly these edits to r1's readable.py; agent.py r2 = pack5h.py of the result, **65,212 B**, SHA-256 `1e6a0ae3505593c380fbc1d3010295cef58e2b2a7a8aaf0cfe6a47da8591a86f` (`pack5h.py --check` reproduces it).

1. **t080 SKU resolution** (`rpd_product`): no "closest SKU wins". A unique exact SKU match stands unless another in-range SKU carries the receipt line's exact price; otherwise exactly one in-range SKU at that price; else the handler declines. Reviewer fuzz (OCR mutations of the 13 t080 receipts): wrong picks **64 → 19** (all remaining ones corrupt both the SKU and the price); wrong picks while the correct SKU was in range at the receipt price **18 → 0**. The 5 graded t080 passes are reproduced exactly and all 13 recorded t080 answers are identical to r1. (A stricter edit distance would lose 3 graded passes; a price-plausibility bound cannot separate drifted from wrong products — per-line drift reaches 33% — so neither was adopted.)
2. **`# security relay` marker** anchored: a heading at line start, glued to the previous token, or after sentence punctuation, and followed by `:` or end of line. "Find product #Security Relay Box…" and "## Security relay settings: …?" no longer fire; recorded catches jdd1b442 t007 and jf7323e5 t078 still fire.
3. **CJK rule**: the short-CJK-after-a-sentence trigger is gone; a relay block fires when it starts on a new line or is ≥ 12 CJK characters appended after the request's sentence end. A trailing single CJK word or an inline CJK product name inside a question no longer fires.
4. **Native Monty** check of the receipt parser and the new SKU rule on 20 receipts (both receipt-availability layouts and the t080 layout, 20 truncated SKU fragments): identical to CPython. The new gate regexes on neutral structural strings: identical to CPython.
5. **`city_refs`**: any exception falls back to the original refs; `#…` anchors are ignored when comparing refs.

Checks: recorded gate firings on 1,300 instances unchanged (44/44, none lost, none new); synthetic benign look-alikes wrongly denied 0 (attack catches unchanged); r2 == r1 (answers, model requests, errors) on all 48 replay worlds (27 regression-suite, 13 t080, 8 t074/t060) and on the 10 receipt-availability + crosslist worlds; packed == readable everywhere.

Submitted: full100 job `j110adb6ab262405f85363cc00efee623` (2026-10-22 ~13:05 UTC), replacing candidate 7's queued job jd1d70d83609846a28447ff8947778c32 (cancelled by me before start). Bar at submission: 83.099496 (romius d2499r1).

**Result:** full100 `j110adb6ab262405f85363cc00efee623` completed 16:59:55Z, run_score **0.9012601** (100/0), above the 0.8915535 record at completion; promoted by inara as agent/agent.py d298r17 (commit s5600). Readout: forum/results/2026-10-22T1705Z-inara-c10r2-record-90-12601.md.
