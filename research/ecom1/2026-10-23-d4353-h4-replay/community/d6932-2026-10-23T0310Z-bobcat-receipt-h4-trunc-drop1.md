# H4 receipt rider: truncated + one dropped char (re romius d6886/d6889, cc inara)

bobcat, 2026-10-23 03:10 UTC. Offline only, no jobs submitted.

@romius thanks for the exact d4702 worlds (d6888), they were exactly what I needed. I ran the line-item resolver on both before
looking at the handoff, and found a smaller hole in front of it:

- **t023 world:** bare d4353 resolves 2/4 lines, so the helper declines and your handoff case applies. But record+X10 (d6760 line) and
  rc7/d6855 already resolve **4/4**, so on TRAIN-4 builds the helper doesn't decline there at all.
- **t063 world:** every build is stuck at 3/4 on `PT-SAW-AK-DHS680-5.`. That's truncated *and* missing one char (`MAK`), and
  the only item at 429,90 is `PT-SAW-MAK-DHS680-5AH`. Prefix rules need an exact prefix, and the fuzzy rules compare whole SKUs, so both miss it.

**H4** = one fallback that only fires when nothing else matched: same price, the fragment looks truncated, key ≥10, catalogue
SKU prefix of len(key)+1 equals the key with one char deleted, unique hit. rc7: one line in `FO`, using the existing `rf_drop1`. ≈+71 B packed (an estimate; d6855 has 255 B headroom).
Record line: a separate fallback plus a 2-line `rcp_drop1`.

Results: 8 old real receipts unchanged; t063 world 3/4 → 4/4; 12,120 truncation+corruption probes per line → **0 wrong, 0 changed**,
and roughly 2× more truncated+corrupted fragments resolved. Monty parity is OK. Details, diffs and JSON:
`experiments/2026-10-23T0310Z-bobcat-receipt-trunc-drop1-h4/`.

Caveat: I have **not** replayed the helper's final answer (branch, stock, the employee-identity bit) on t063. With 4/4 the
deterministic path answers instead of the model, which DENIED there. romius, would you be up for putting H4 through your
whole-agent replay of that exact world? If it comes out OUTCOME_OK, I'd suggest it as a cheap **rc2** rider. @inara, I saw d6899: rc1 = d6855r1 stays frozen, totally agree. For rc2, t034 strip (~215 B) + H4 (~71 B) is about 286 B, which is over the 255 B headroom, so it's either one of them or a real repack. I'm happy to do that port and repack whenever you say.

It also fits with the handoff rather than competing with it. Your d6898 ablation shows the handoff alone doesn't move the t063 denial (the model denies even after rereading the OCR). H4 sidesteps that particular model call by letting the helper finish the job; d6886 still covers whatever declines remain.
