# TRAIN-4/H4 stock boundaries — synthetic offline extension

The reviewed H4 composition passes fresh positive and threshold stock cases on both observed receipt-world shapes. This closes a specific weakness in the earlier all-short witnesses: a wrong item match can no longer hide behind an always-negative answer. It is bounded offline evidence, not a new live task result or a score estimate.

All cases here are **explicit synthetic overlays**, including those retaining the archived OCR text. The original archived worlds, previous review and agent sources remain unchanged. The copied upstream files are pinned in `input-pins.json`; `upstream/SHA256SUMS.json` is the original review seal (its complete build closure remains in the original package). This extension needs no encoder because it executes the exact previously reviewed readable and packed artifacts without changing or repacking them.

| Arm | Packed bytes | SHA256 |
|---|---:|---|
| Literal d6855r1 | 65,281 | `2b4de83bbba8e18e9b7eab46bd5fb4512a6cc373cacd49bf87ce7333b26bca85` |
| d6855 + exact d6928r1 H4 | 65,355 | `dcd8c371d7d214cff7f2e8e83cb467e9b41e4e3f21fd4292fc9cdf6c77455d4f` |

## Independent oracle and overlays

The intended SKU map and quantities were manually reconstructed from the actual receipts in the sealed prior review. The new host rechecks each mapped product's exact SKU, price and fulfillment type against its archived product record. It derives stock expectations directly from the actual policy: `max(on_hand - reserved, 0)`; absent SKU rows mean zero; incoming counts only when requested. Both retained instructions ask about today. Product, identity, policy, branch opening state and instruction bytes are unchanged.

t023 requests HSA50-AK10, W18-125-4AH, TERS18-25 and HSS-REDUCED, one each. t063 requests DHS680-5AH ×1, RMA235-AK30 ×12, CYL9-12 ×1 and EXPWOOD-190 ×1. The expected reference list is exactly upload, actual branch, those four product paths in receipt order, security and availability policies. Every final helper answer must match the complete message/outcome/reference object, not just the yes/no token. Product fields and citation content hashes are checked and recorded.

Each of three contexts has 14 inventory overlays:

- All four requested quantities exactly on hand, with no reservations.
- All four quantities exactly available after three reserved units are subtracted.
- Four independent one-short cases: only the selected line has `on_hand = quantity + 2`, `reserved = 3`; the other three remain sufficient.
- Four independent incoming-only cases: selected line has no on-hand stock, plus sufficient incoming quantities at day zero and day one. Neither incoming row counts for these requests. Incoming fields use the actual `quantity`/`arrival_in_days` schema.
- Four independent absent-row cases: only the selected intended SKU is removed from the existing branch inventory. Policy requires zero availability, without a fabricated missing-file response.

Unrelated existing inventory rows are set to zero and incoming lists cleared, so an incorrect match cannot benefit from accidental unrelated availability. All before/after response envelopes, including updated content hashes, are recorded. No catalogue products or tree entries are added or removed.

Contexts are t023 with archived OCR, t063 with archived OCR, and a transparent t063 exact-saw control that changes only `PT-SAW-AK-DHS680-5.` to `PT-SAW-MAK-DHS680-5AH`. The exact-saw context lets the parent reach the same stock logic without H4, separating matching reachability from stock correctness. No drill-bit correction is made.

## Results and reachability

42 cases × two arms × two source forms × CPython/native Monty = **336 executions**, including 168 native executions with a method-only ClassInstance. All four forms agree on complete RPC sequences, model requests, answers, overlays and logs within each arm/context/case. Parent and H4 have identical ECOM call sequences and router requests for every paired case.

| Context | Parent | H4 |
|---|---|---|
| t023 archived OCR, 14 stock overlays | Helper reaches; all expected answers and references | Same |
| t063 archived OCR, 14 stock overlays | Matching declines; fixed historical main reply is supplied | Helper reaches; all expected answers and references |
| t063 exact-saw OCR, 14 stock overlays | Helper reaches; all expected answers and references | Same |

Threshold positives are exactly `TRUE(1)` for t023 and `ja` for t063. Each single-line short, incoming-only or absent case is exactly `FALSE(2)` or `nein`, respectively. Thus the twelve-unit mower threshold is checked independently, and failure of any one intended line flips the answer while preserving exact citations.

The parent t063 archived-OCR fallback is asserted equal to the unchanged historical denial, including its actual references. That fixed reply is deliberately **not scored against the altered inventory**: no new main-model reasoning was performed. There are 280 cells that reach the deterministic helper and 56 parent fallback cells. This accounting distinguishes new matching reachability from inherited stock handling; it is not a model pass rate.

## Boundaries and unresolved gates

There are zero unmatched RPCs, derived tree responses, Write/Delete calls or live model/world calls. Exec is restricted to the exact archived `/bin/id` and `/bin/date` requests/responses. The strict archived host accepts extra Read arguments only at default-equivalent zero/false values. Native limits remain ten seconds per feed/turn and 1,000 suspensions; model replies are capped at the archived router plus one fixed historical main reply. No agent function is replaced or stubbed.

This extension does not establish complete fuzzy-match safety or resolve substitution-policy disagreements. It does not cover duplicate inventory rows, malformed inventory types, closed branches, explicit future/incoming requests, unavailable policy/upload reads, alternative identities, different task grammar or branch resolution ambiguity. Existing matching and identity gates remain exactly as in the reviewed composition. The target is these valid open-branch same-day requests, not a general availability engine certification. No full100 readiness, live outcome or aggregate-score improvement follows from the matrix.

## Reproduction

Use Python 3.14.3 with pydantic-monty 1.2.0:

```sh
python research/ecom1/2026-10-23-train4-h4-stock-boundaries/reproduce.py
```

The reproducer copies this directory, ignores bytecode caches, disables child bytecode generation and runs all 336 executions. It requires the regenerated `results.json` to be byte-identical. No external bytecode environment setting is required. `test_stock.py` can also run directly. The final seal covers inputs, scripts, full results and clean-reproduction receipt. No paid calls, Brain writes, source mutations or Git changes were made.
