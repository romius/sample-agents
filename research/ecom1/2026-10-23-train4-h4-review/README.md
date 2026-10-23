# Exact TRAIN-4 d6855r1 + H4 donor composition review

The exact H4 diff succeeds on the actual observed t063 receipt world when applied to TRAIN-4 d6855r1: the deterministic helper returns `nein` / `OUTCOME_OK` with the correct upload, branch, product and policy references. The t023 result remains the existing deterministic `FALSE(2)` answer. This is a bounded offline donor composition review. It is not a new baseline, full100 readiness decision, live-model comparison or measured score gain.

The distinction from bare d4353 is material. TRAIN-4 already has the whole-SKU one-deletion rule that resolves t063's nontruncated drill-bit corruption. It also has an all-price exact-SKU guard. H4 adds only the truncated-prefix one-deletion fallback to `FO`; no X10 Levenshtein rule, handoff, role handling, reporting rule or other behavior is added.

## Exact source and build closure

Read-only Brain session s8226 inspected the workspace AGENTS and build instructions, exported exact revisions and was discarded. Direct source exports match the matching files in the published composition archive:

| Input | Exact reference | SHA-256 |
|---|---|---|
| TRAIN-4 packed parent | d6855r1 | `2b4de83bbba8e18e9b7eab46bd5fb4512a6cc373cacd49bf87ce7333b26bca85` |
| Parent readable payload | d6856r1 | `9886cb40612a943d861d924a30e1d6709f6c191375a72735828408e3a50557f0` |
| Proposed H4 diff | d6928r1 | `fc18318b08b475a4a5fb7fa51860158235292774f43bfdac8d077d6b0a502688` |
| Original encoder | d4558r1 | `e8d3844011dce71a0a21251fdd7134925b3ba9ab2ba556b36ad795a749c43afc` |
| Composition source archive | d6866r1 | `212bbbafcaccd346af95e795f070153e2cca32b5705baa050ba4ce368026db53` |

`community/repro/` retains the archive's exact original rc7 parent, decoder stub, recipe, manifests and historical tests/results, including its disclosed original coordinator assertion failure. `build.py` checks every published manifest pin, reproduces the original rc7 base packing and the owner recipe result, then reproduces d6855r1 byte-for-byte. It applies exactly the one removed/added line in d6928r1, with exactly one source match. The only changed top-level AST node is `FO`. It uses the original encoder/stub, verifies decode roundtrip and the65,536-byte source limit. No estimated or substitute packing claim is used.

The H4 packed artifact is **65,355 bytes**, SHA256 `dcd8c371d7d214cff7f2e8e83cb467e9b41e4e3f21fd4292fc9cdf6c77455d4f`: +74bytes,181bytes remaining. Its exact readable payload is106,144bytes, SHA256 `97e3c6d1290f61d6f740a5b966f83391859617d12ea2f1993f629b1df33f77ad`. `formatted-readable.py` is a separate AST-rendered reading aid; it is not the packed payload.

## Whole-agent results

The two worlds are the sealed **observed d4702** t023/t063 worlds, with complete original trace evidence in the receipt-world archive. They are not inferred to match any TRAIN-4 live draw. Their copied Read objects, exact content hashes, request/response ledgers, policies and original model bodies are retained under `inputs/`. No upload or catalogue edits occur in the actual-world cases.

| Case | d6855 parent | d6855 + H4 |
|---|---|---|
| Actual t023 |4/4 resolver lines; deterministic `FALSE(2)` |4/4; identical answer/refs |
| Actual t063 |3/4; declines at saw; fixed historical denial supplied |4/4; deterministic `nein` with exact refs |
| Saw corruption without truncation marker |Declines |Declines |
| Two same-price H4 candidates |Declines |Declines |
| Exact normalized SKU at a different price |Declines |Declines |
| Corrected exact saw SKU |Deterministic `nein` |Identical |
| Harmless receipt note |Declines at original saw |Deterministic `nein` |
| Same-price substitution-only rival |Declines at original saw |Unique H4 deletion match; deterministic `nein` |

64 whole-agent executions cover two arms × readable/packed × CPython/native Monty × eight cases. Native runs use method-only ClassInstance and10-second feed/turn,1000-suspension limits. Every source/runtime form has identical calls, messages, answers and logs within each arm/case. Parent/H4 ECOM request sequences are identical in all cases; no Write/Delete or extra action Exec occurs. Only archived `/bin/id` and `/bin/date` Exec responses are used. Unmatched calls fail; no derived Tree responses or unknown-file defaults are supplied. The host caps supplied model replies at two, and accepts extra Read arguments only when their values are default-equivalent zero/false. These are explicit offline replay limits, not claims about live provider behavior.

Router replies are fixed exact historical response bodies, not fresh model inference. When a deterministic helper declines, the fake host supplies that world's fixed historical final reply; these denial outputs are simulation controls, not new model outcomes. On actual t063 the H4 helper completes after the router and never consumes a main-model reply. Its correctness is assessed from actual inventory/policy, not by counting an OK outcome.

## Independent answer reconstruction

The human mapping is fixed separately from `FO`'s results. Product prices, quantities, unique inventory rows, receipt addresses, branch opening state, policy, content hashes and final references are asserted by `analyze.py`.

- t023: open PowerTools Linz Hafen, Industriezeile76. Requested HSA50-AK10, W18-125-4AH, TERS18-25 and HSS-REDUCED, one each; all have zero same-day availability (the hedge trimmer's3 on hand are all reserved). Prices total70,460cents, matching704.60 in the receipt. Later incoming stock does not count today. The exact required negative token is `FALSE(2)`.
- t063: open PowerTools Vienna Favoriten, Favoritenstrasse221. Requested DHS680-5AH ×1, RMA235-AK30 ×12, CYL9-12 ×1 and EXPWOOD-190 ×1; availability is0,7,0,0. Prices/quantities total518,850cents, matching5,188.50. All four lines are short. The exact required negative token is `nein`.

Both original tasks ask read-only availability, not purchase execution. Exact archived `/bin/id` evidence is retained in `analysis.json`: t023 is `emp-0037` with RoleEmployee, RoleStoreManager, RoleOrderViewer and RoleDiscountManager; t063 is `emp-0076` with RoleEmployee, RoleCustomerService and RoleRefundManager. Their Exec request/response event IDs and full raw stdout are preserved, alongside the actual `/bin/date` output. Both have the exact RoleEmployee token. The policy does not prohibit their read-only branch-stock checks. The helper performs no mutation. Receipt staff labels are not treated as authentication. The manual intended-product reconstruction is explicitly separate from the resolver's ability to infer the corrupted strings.

## Acceptance policy and limits

Unlike the bare d4353 port, rc7 checks **all** normalized exact-SKU matches before price-filtered fallback. If an exact SKU exists at another price, or there are duplicate exact normalized SKUs, both parent and H4 decline. Independent module controls verify this in both catalogue orders. The previously demonstrated bare-parent exact-other-price acceptance is therefore not transferred to this context.

rc7 recognizes exact/prefix/suffix/one-deletion relationships; it does not use X10's arbitrary substitution distance. A same-length substitution-only rival is not an eligible match and does not veto a unique H4 deletion match. A control containing only that rival still declines. This is a stated acceptance policy, not proof that all real OCR corruption follows deletion-only noise. Two eligible H4 hits and existing prefix ambiguity decline. Invalid price types, wrong price, short fragments, two deleted characters and nontruncated examples are also retained. Twenty module cases per arm (two actual receipt parses plus18 controls) execute in CPython/native for80 evaluations, preserving the actual pre-bootstrap module and functions.

Synthetic catalogue rivals replace an existing unrelated record, leaving its old descriptive metadata deliberately inconsistent. Those before/after envelopes are explicitly recorded as collision tests, not claimed as realistic observed products. Actual cases do not use them. This suite does not reproduce or certify the community12,120-probe claim and does not establish exhaustive fuzzy-match safety. The proposed composition should still receive an independent exact-artifact review and any owner-required regression checks before a future evaluation decision. No paid jobs, shared source mutations, Git writes, Brain commits or promotions occurred.

## Reproduction

Use Python3.14.3 with pydantic-monty1.2.0:

```
python research/ecom1/2026-10-23-train4-h4-review/reproduce.py
```

The runner copies the package to a temporary directory, excludes caches, disables child bytecode generation, rebuilds and reruns64 whole-agent plus80 module evaluations, then requires all eight generated outputs to remain byte-identical. `build.py`, `replay.py` and `analyze.py` can also be run separately. `source-export.json`/`archive-export.json` and the direct export bytes preserve immutable Brain pins; `input-pins.json` links the observed worlds. The source archive's older tests/results are historical provenance, not relabeled as this review's fresh results.
