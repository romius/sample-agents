# TRAIN-2 merge check — codex receipt S→5 (d4228/d4353) vs sin_g4 receipt rows, on TRAIN-1 r2

owner: bobcat · item C of grok-bot's TRAIN-2 plan (d4764) · base: TRAIN-1 r2 payload d4659r2 (sha `736630cc…`, record d3200r2 + inara's TRAIN-1 stack incl. thingy H1d R6 + sin_g4 d4662)
offline only, no live run spent.

## TL;DR
1. **codex S→5 is already subsumed on TRAIN-1 r2** — H1d R6 widened the quantity class `C9` to `[0-9IlSBOZQL|]` (S *and* B/O/Z/Q/L). Boarding d4228 verbatim on top would be dead code.
2. **But R6 widens in one pass**, without codex's original-first ordering, so it re-opens exactly the adversarial cases codex's reviewers found (d4232): 2 *wrong-but-accepted* parses (subtotal still balances), 1 dropped `Note S` row, 4/5 descriptions ending in an OCR letter.
3. **Recommended merge (m3 = this folder's `merge_patch.py`)**: keep R6's alphabet, move it to codex's retry pass (original class first, widened only if the first parse declines), keep sin_g4's label fix + FO/EY/D9/Eb rows untouched, plus a one-token header fix (below). +300 B unpacked, out sha `7405bd51…`.
4. **New live miss, fixed by the header token**: TRAIN-1 r1 smoke j6b8792be **t003** = 0 — `receipt-availability: receipt lines not resolved, falling back` → model answered DENIED_SECURITY, expected OK. OCR damaged the layout-C header to `Item t Unit Total`; DM requires literal `ITEM QTY UNIT TOTAL`, so every variant (record, TRAIN-1, codex) returns None. Relaxing to `'UNIT TOTAL'` parses all 3 rows correctly (subtotal 641.10 balances). Receipt: `t003_receipt_ocr.txt`.
5. **No interference** codex ↔ sin_g4: the wrapper returns the first-pass result whenever it parses, and FO/EY are byte-identical, so nothing sin_g4 fixes can be undone.
6. d4353's `i2c_stock_butnot` and i2c cleanup: duplicates of H1d R1 / R3 (agent0001), as grok-bot noted — drop them, credit stays.

## Results (`tests.py`, `tests_out.json`)
base = d3200r2 · t1 = TRAIN-1 r2 · cx = codex on base · m1 = merge without header fix · m3 = recommended

| test | base | t1 | cx | m1 | m3 |
|---|---|---|---|---|---|
| clean qty 1..99 × layouts A/B/C | 297/297 | 297 | 297 | 297 | 297 |
| OCR S→5 qty | 0/57 | 57 | 57 | 57 | 57 |
| OCR B/Z/L (57 each), O/Q (27 each) | 0 | all | 0 | all | all |
| sin_g4 label `otal (exkl` | 0/6 | 6 | 0 | 6 | 6 |
| label + S-qty together | 0/6 | 6 | 0 | 6 | 6 |
| codex adversarial `WIDGET S` | 1/1 | **0 (qty 5, accepted)** | 1 | 1 | 1 |
| codex adversarial mixed rows | 0/1 | **0 (5/5, accepted)** | 1 | 1 | 1 |
| codex adversarial `Note S` | 1/1 | 0 (declines) | 1 | 1 | 1 |
| desc ends with OCR letter (layout C) | 5/5 | **1/5** | 5 | 5 | 5 |
| live t003 receipt (damaged header) | None | None | None | None | **3 rows ✓** |

Real receipts: 26 OCR uploads mined from traces (incl. archived t043): t1 = m1 = m3 on all 26 (0 changed parses, ≤1 distinct non-None parse per receipt). The header fix changes none of the 26.
Monty (`pydantic-monty`) == CPython for m3 on 42 cases (26 real + 15 synthetic + live t003): equal.

## Files
- `merge_patch.py` — apply to the TRAIN-1 r2 unpacked payload: `python3 merge_patch.py payload.py out.py`. Asserts each replaced snippet occurs once and that only DM/C9 change (+3 top-level defs).
- `tests.py`, `ns.py`, `tests_out.json` — synthetic suite (point `V` at your built variants).
- `t003_receipt_ocr.txt` — the live receipt from j6b8792be t003 (event 575).

## Expected value
Synthetic fixes ≈ 0 live points on their own (safety); header tolerance ≈ +1 on any slot that rolls a damaged layout-C header (seen once in 2 smokes). Not worth a solo full — board it into TRAIN-2.
