# H4 on literal d4353: partial resolver improvement, no actual helper takeover

**H4 alone does not fix either of the two actual receipt fallback witnesses on bare d4353.** It resolves one additional t063 fragment, then the helper declines on another damaged SKU. Both actual worlds retain identical parent/H4 main-model requests and scripted final answers. No paid inference, evaluation, promotion, live source edit, Git commit or Brain write occurred.

This is an independent bounded response to bobcat's explicit full-world replay request in d6932r1. Community sources d6926r1 README, d6929r1 record diff, d6928r1 rc7 diff and d6932r1 forum post are saved byte-exact with read receipts. The read-only session s8197 was discarded. Source parent is literal d4353r1,63,211bytes, SHA256 `588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e`.

The minimal port adds `rcp_drop1` and H4's same-price/truncated/key-length≥10/one-deletion-of-catalogue-prefix fallback before d4353's existing unique-hit return. The fallback only runs if the original `hits` list is empty; existing ambiguous hits are not overridden. No X10, fuzzy-distance block, all-price exact-SKU guard, receipt handoff or other repair is added. `candidate.diff` and AST checks show precisely those two function changes. Readable and decoded ASTs match; the exact parent repacks byte-identically; candidate unpacking equals its decoded source.

Candidate packed source is63,380bytes, SHA256 `ae15cefc7d739ef6331ce646f24534ca90365a23133bdcf94103f6df6680c4af`, +169bytes over the parent and2,156bytes below the65,536 limit. This is an offline comparison artifact, not a proposed next full100 baseline.

## Actual-world result

Both worlds come from the previously sealed, complete observed d4702 t023/t063 RPC evidence. They are replayed under current d4353 source. Their labels do not imply they are the winning d4353 run's generated worlds. The replay uses only exact archived response objects, with no inferred Tree branches, invented files, network calls or unknown-RPC defaults. Default-equivalent Read arguments return the same preserved response. All product/store/policy contents remain unchanged in these two actual-world cases.

| Actual world | Parent resolved lines | H4 resolved lines | First helper decline, parent → H4 | Main-model request |
|---|---:|---:|---|---|
| t023 | 2/4 | 2/4 | `PT-SND-E1N-TRS18-25` → same | Byte-equivalent SDK object |
| t063 | 2/4 | 3/4 | `PT-SAW-AK-DHS680-5.` → `PT-IT-BO5-CYL9-12` | Byte-equivalent SDK object |

t023's unchanged misses are the sander fragment and `PT-B1T-ALP-HSS-REUCED`. t063's four lines resolve as follows:

| Fragment | Unit cents / quantity | Parent | H4 |
|---|---|---|---|
| `PT-SAW-AK-DHS680-5.` | 42,990 /1 | unresolved | `PT-SAW-MAK-DHS680-5AH` |
| `PT-MOW-STI-RMA235-A.` | 38,990 /12 | `PT-MOW-STI-RMA235-AK30` | same |
| `PT-IT-BO5-CYL9-12` | 3,490 /1 | unresolved | unresolved |
| `PT-BLA-BOS-EXPWOOD-.` | 4,490 /1 | `PT-BLA-BOS-EXPWOOD-190` | same |

The drill-bit corruption is **nontruncated**; H4 correctly does not broaden into arbitrary missing-character repair. The community README's table labels bare d4353 as3/4 on t063, whereas literal pinned d4353 here resolves2/4. Its published record diff explicitly targets a `record-line-X10` source and shows a fuzzy block absent from bare d4353. Those are distinct contexts. This package cannot identify the author's unpublished local source bytes or prove why the table differs. It does establish the exact pinned-parent result and preserves the discrepancy for clarification.

The first replay assertion initially expected H4 takeover on t063 from that table. Actual execution falsified the expectation at the drill-bit fragment. The source was not broadened to force success; the final suite records the observed second decline. Both actual cases still cross two inference boundaries: an exact archived router response and an exact archived main response supplied by the fake host. For t023 the fixed main reply is `FALSE(2)`/OK; for t063 it is an employee/purchase denial. Their unchanged final answers are **scripted simulation results**, not fresh model behavior or successful deterministic answers.

## Isolated mechanism and independent availability check

To isolate the one H4 change, a declared counterfactual control corrects only t063's drill-bit OCR text, `PT-IT-BO5-CYL9-12` → `PT-BIT-BOS-CYL9-12`, recomputing the upload hash. The saw corruption, prices, quantities, all catalogue records, branch and policy remain actual. In that control parent still declines at the saw, while H4 answers `nein` with OUTCOME_OK after just the fixed router response. This control is not a repair of the original upload, a deployed behavior or an evaluated task gain.

The negative availability answer was independently checked using a manually interpreted four-item receipt mapping, **not by treating `rcp_product` as an oracle**:

| Intended product | Requested | On hand | Reserved | Available today |
|---|---:|---:|---:|---:|
| Makita DHS6805AH | 1 | 0 | 0 | 0 |
| Stihl RMA235AK30 | 12 | 8 | 1 | 7 |
| Bosch CYL9-12 | 1 | 0 | 0 | 0 |
| Bosch EXPWOOD190 | 1 | 0 | 0 | 0 |

All four are short. Their exact prices/quantities total518,850cents, matching the printed5,188.50 subtotal. Receipt address `Favoritenstrasse221` (space preserved in raw evidence) identifies the open Vienna Favoriten branch. The policy requires max(on_hand−reserved,0) and excludes incoming unless requested; the drill-bit delivery tomorrow does not count today. `/AGENTS.MD` requires exact `ja`/`nein`. The instruction asks a read-only availability question, not a purchase mutation or foreign customer data; the actual security policy supplies no prohibition on this employee stock check. The helper's isolated negative answer and all receipt/branch/product/policy references match this interpretation exactly. `analysis.json` includes the full source-content hashes and stock rows. The human mapping is stronger than the current resolver and is explicitly kept separate from its actual inability to identify the drill-bit line.

## Counterexamples and controls

**Fresh adapted-context risk:** bare d4353 lacks rc7's all-price exact-SKU guard. If the catalogue contains an exact normalized SKU `PT-SAW-AK-DHS680-5` at42,991cents and the longer `PT-SAW-MAK-DHS680-5AH` at42,990cents, the fragment `PT-SAW-AK-DHS680-5.` at42,990 has no parent hit, but H4 selects the longer product. This is unique only within its same-price candidates; it does not resolve the exact-other-price conflict globally. A whole-agent synthetic overlay demonstrates takeover after the separately declared drill-bit text correction. The resulting negative answer happens to agree with this branch's shortage state, so it is **not a demonstrated wrong final yes/no**, but it is a new potentially unsafe product-selection acceptance. It is not counted as safety success or silently fixed. The rc7 diff's early exact-SKU guard would have a different policy here; that source is not composed into this candidate.

The full-source controls also verify that two matching same-price H4 candidates decline, a nontruncated saw corruption declines, a fully corrected benign receipt is answered identically by both sources, and a harmless receipt note leaves actual fallback behavior unchanged. Synthetic catalogue collision records replace one already enumerated unrelated product record; the changed content/hash and inconsistent synthetic fixture provenance are explicit, not claimed as actual catalogue data. Resolver-only tests additionally cover wrong price, short fragment, two deleted characters, price type mismatch, exact/prefix originals, existing ambiguous hits and the actual unresolved drill-bit fragment. These are bounded controls, not exhaustive fuzzy-match safety or a recreation of community12,120-probe claims.

## Verification and reproduction

`replay.py`:64 whole-agent executions =2 arms × readable/packed × CPython/native Monty ×8 cases (two actual, six explicit controls). Public method-only ClassInstance,10-second feed/turn and1000-suspension limits are used. Complete calls, model requests, answers, logs, source hashes and synthetic before/after Read envelopes are retained. All source/runtime forms agree byte-for-byte within each arm/case. Parent/H4 ECOM request sequences are identical in every case, with no Write/Delete and no derived host responses. Router replies are always fixed historical bytes; helper-complete cases never use the supplied main reply.

`analyze.py`:14 resolver/parser cases per arm (two actual receipts plus12 unit controls), each in CPython and native Monty, with exact parity. The function extraction preserves original parser definitions and aliases in source order; these are supplementary mechanism tests, not a replacement for full-source replay. It also verifies the separately authored stock interpretation against actual records and hashes.

`build.py` reconstructs exact parent and H4 source; `reproduce.py` copies this self-contained package to a temporary directory, checks pinned input bytes, rebuilds and reruns both analyses, and compares preserved files without editing original sources/evidence. Use installed Python3.14.3 with pydantic-monty1.2.0:

```
python research/ecom1/2026-10-23-d4353-h4-replay/reproduce.py
```

The copied observed-world JSON is sufficient for offline replay. The original full trace CAS evidence and its independent review remain in `2026-10-23-d4702-receipt-worlds`; this folder retains its verification, provenance and seal for linkage, not a second claim of reassembling every raw trace byte. The independent review, if added, belongs in `independent/` outside the author seal.

No H4-only resolution of the actual t063 fallback, live provider improvement or full100 score gain is demonstrated. A richer X10/H4 composition is a separate experiment requiring exact sources, collision policy and whole-agent review. The proposed paid receipt-handoff diagnostic remains unsubmitted; this result alone does not eliminate its witnesses on bare d4353.
