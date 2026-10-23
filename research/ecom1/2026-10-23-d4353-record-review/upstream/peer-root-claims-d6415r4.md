# Reference citations are the leak every stack shares

2026-10-23 02:33 UTC, grafragovdeepseek. I scanned every completed 100-trial job still in the queue window and counted the trials whose grade is a **reference** failure (`invalid references` or `refs for family ... mismatch`) rather than a wrong outcome or a wrong number.

| stack | score | ref-failed trials | which |
|---|---|---|---|
| d3909 (the record) | 0.9411 | **3** | t027, t062, t091 |
| d2499 | 0.7808 | **5** | t022, t027, t042, t062, t065 |
| d3848 | 0.7872 | **6** | t002, t007, t022, t025, t042, t062 |
| d3843 | 0.7707 | **4** | t002, t007, t047, t061 |

Every stack loses between three and six trials to **what it cited**, not to what it answered. On a 100-trial run that is 3-6 points, and no stack is exempt - the record included.

## What recurs

- **t062 fails in all four.** A but-not stock check whose expected product is `PT-WASH-KAR-K4-PIPE`; every stack cites a sibling. The clearest case of "answer plausible, citation wrong".
- **t027 fails in three of four** - the catalogue count. On stacks without a handler it fails as a ref mismatch because the answer cites nothing.
- **t022/t042** (the but-not pair) fail in three - the auto-added sibling ref problem my guard finding diagnosed.
- **t002** fails in two with `missing [...]` - the "but not" gate cites the wrong side.

## What follows

1. **Check references before believing a stack is done.** A trial can be right in substance and score 0; read by outcome alone, all four stacks look better than they are.
2. **`tools/rootmap.dead_refs()`** catches the dead-root class (`/proc/products`, `/proc/stores`, `/proc/returns`) in one call - that is t091's cause.
3. **t062 needs the right SKU, not more SKUs.** My first draft of this section said "cite the family, not one sibling" - that is wrong, and the grade detail says why: `missing [/proc/catalog/Karcher/PT-WASH-KAR-K4-PIPE.json], extra [/proc/catalog/Karcher/PT-WASH-KAR-K4-CAR.json]`. The grader compares sets and **penalises extras as well as omissions**, so citing the whole family would add three more extra refs and still fail. The fix is to resolve the phrase to `PIPE`, not to cite wider. The phrase itself - "karcher k4 outside the home car reel listings" - is the hard part, and mapping "car" to a SKU is what produced CAR in the first place.

   The honest statement is: **t062 is a resolution problem, not a citation-width problem**, and the only cheap defence is to refuse or ask when a phrase does not name a SKU cleanly - a refusal costs less than a wrong single cite.

## The audit is now a call, and it found a second dead root in t091

`trialpeek.dead_roots(job, trials=...)` walks the Answer of each trial and reports the ones that cite a dead root; `refs_of(job, trial)` returns a trial's references. Run on the record job (`j55b49f18341`, trial t091) it returns:

```
refs_of(job, "t091") ->
  ['/exports/inventory-family-eqMvAeV3.csv',
   '/proc/stores/store-linz-hafen.json',            <- dead: real root is /proc/locations
   '/proc/products/cat-garden-outdoor/kind-pressure-washers/PT-WASH-KAR-K4-CAR.json']  <- dead: real root is /proc/catalog
```

So t091 cites **two** dead roots, not one: the store reference too. The export itself is fine; both supporting citations point at roots that do not exist.

## The record moved again at 00:27Z, and two of its four zeros are the same class

New record: **94.72095** - codex `d4353r1`, job `j6d6d4adb60f24`, promoted by inara at 00:27Z, +0.607 over STACK E (a margin the promoter itself notes is inside the ~4-point same-source spread). I ran the audit on its losses within minutes:

| trial | score | what the audit says |
|---|---|---|
| t023 | 0 | cites **`/proc/stores/store-linz-kleinmuenchen.json`** - a dead root; the live store path is `/proc/locations/...` |
| t080 | 0 | cites the right roots but the **wrong products**: `/proc/catalog/Bosch Professional/PT-GRD-BOS-GWS1400-CASE.json`, `…-GSR55-5AH.json`, `/proc/catalog/Einhell/PT-CMP-EIN-TEAC270-50S.json`, where the grader wants `…/PT-BIT-BOS-CYL9-5…` |
| t001 | 0 | expected `OUTCOME_NONE_CLARIFICATION`, answered `OUTCOME_OK` - a clarification miss |
| t054 | 0 | expected `OUTCOME_OK`, answered `OUTCOME_DENIED_SECURITY` - an over-refusal |

So the class repeats across records: **one dead-root reference (t023) and one wrong-SKU reference (t080) of four zeros**. `trialpeek.dead_roots(job, trials=["t023","t080"])` returns exactly `[('t023', 1, '/proc/stores/store-linz-kleinmuenchen.json')]`.

The dead-root fix is the same one-liner as before - cite `/proc/locations`, never `/proc/stores`. t080 needs the product resolved rather than the first three matches cited; in the same trial patch it cited three plausible products and the grader wanted the one the question named.

This is the second record in a row whose zeros include the dead-root class. The finding is not about one stack.
