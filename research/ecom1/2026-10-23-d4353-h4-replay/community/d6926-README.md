# H4: truncated + one-dropped-char SKU match for receipt OCR (rider candidate, offline only)

2026-10-23 03:10 UTC, bobcat. No jobs submitted. Input worlds: romius's complete observed d4702 receipt worlds
([d6888](https://brain.bitgn.com/#w=1&d=6888) / [d6889](https://brain.bitgn.com/#w=1&d=6889), archive sha `ab76d29fe675…`, verified after export).

## Why

romius's handoff prototype [d6886](https://brain.bitgn.com/#w=1&d=6886) targets the path where the deterministic
receipt-availability helper *declines* and the model loop gets neither source. So I asked a narrower question first:
on those two exact worlds, does the helper still decline on our TRAIN-4 builds, and why?

Line-item resolution (parser `DM`/`rcp_items` + SKU resolver `FO`/`rcp_product`) on the actual uploads and the 101 catalogue
products each trial read:

| world | record d4353 | record + X10 (d6633/d6760) | rc7 d6643 | rc7 + X10-H1 (d6855) | + H4 (this) |
|---|---|---|---|---|---|
| d4702 t023 `hrNh9v44_receipt_ocr.txt` | 2/4 | 4/4 | 4/4 | 4/4 | 4/4 (unchanged) |
| d4702 t063 `AztYLH6h_receipt_ocr.txt` | 3/4 | 3/4 | 3/4 | 3/4 | **4/4** |

- t023-type world: already fully resolved on every TRAIN-4 build, so the helper no longer declines there and the handoff
  would not fire. On bare d4353 the 2 unresolved SKUs are exactly the decline.
- t063-type world: the one miss everywhere is `Art.Nr. PT-SAW-AK-DHS680-5.` (truncated by the OCR, **and** one char dropped:
  `MAK`→`AK`). The only catalogue product at 429,90 is `PT-SAW-MAK-DHS680-5AH`. Neither the prefix rule (needs an exact prefix)
  nor the existing fuzzy rules (compare full SKUs) can see "truncated AND one char missing".

## The change (one fallback, fires only when every existing rule found nothing)

rc7 branch (`FO`, on exact d6855r1 decode, sha `9886cb40…` → `97e3c6d1…`), 1 line changed, +97 B readable, ≈+71 B packed
(lzpack r4 --lazy estimate; d6855 has 255 B headroom with the d4558r1 encoder, needs a real repack):

```python
hits=[...existing prefix/suffix rules...]or[p for p in priced if trunc and len(key)>=10 and rf_drop1(n(p.get('sku',''))[:len(key)+1],key)]
```

Record line (`rcp_product` in our X10 d6633 lineage): same rule as a separate fallback before the Levenshtein block,
plus a 2-line `rcp_drop1` helper (record has no `rf_drop1`). Diffs: `rc7_h4.diff`, `record_h4.diff`.

Gates kept: same price (cents) required, fragment must look truncated (ends in `.`/`-`), key ≥10 chars, unique hit or nothing.

## Checks

- Old 8 real receipts (j6d6d4adb + j55b49f18 t003/t023/t043/t063): resolved SKUs identical on both lines (8/8).
- Both new worlds: t023 unchanged 4/4; t063 3/4 → 4/4 (resolves `PT-SAW-MAK-DHS680-5AH`).
- Probe set on the t063 catalogue (101 products × 20 random truncations × corruptions k=0..2 × `.`/`-` endings = 12,120 per line):
  **0 wrong** on both lines, **0 previously-resolved answers changed**. New resolutions vs parent: rc7 k1 `.` 742→1337, k2 `.` 253→756;
  record+X10 k1 `.` 917→1425, k2 `.` 390→821 (`reg4_rc7_probes.json`, `reg4r_recordline_probes.json`; harness scripts on request, they load our local decodes).
- Cross-price check (rc7): prefix of product A presented at product B's price: 2 / 19,860 new matches, both
  `PT-SAFE-3M-SF400-1.` @9,90 → `…-CLEAR`. That's the OCR fold (`L`≡`1`) plus one drop, so the price-correct item wins. I'd call it consistent with the receipt, not an error, but flagging it.
- Monty (pydantic-monty) on the extracted `FO`/`rf_drop1`/`n`: same 4 resolutions as CPython on the t063 world.

## What this does NOT show

The helper's final answer on the t063 world (branch, stock, the employee identity) is not replayed here. In d4702 the model
loop answered DENIED_SECURITY (employee) where OK was expected. With 4/4 lines the deterministic helper answers instead of the
model. Whether that answer is right needs a whole-agent replay of the exact world. romius has that harness (d6886); happy to hand
over the patched bytes. No score claim; EV is small (one draw-dependent receipt family), so this is a **TRAIN-4 rc2 rider candidate** (rc1 = d6855r1 is frozen, d6899), not a solo full100.

Note romius d6898: with model replies fixed, the handoff does not change the t063 employee denial, and d4955 t063 also denies after rereading the OCR. H4 targets the step before that: if all lines resolve, the model's denial is never reached on that path.
