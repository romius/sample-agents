# Offline lexical-label ablation review

23 October 2026. Prepared by score-opportunities; semantic fixture oracles passed independent review, with the explicit U4 shared-glossary condition; see independent-review.md. No model calls, ECOM RPCs, Brain edits, production edits, or benchmark submissions.

Question: does displaying derived lexical `found/absent` labels encourage constraint substitution beyond the primary product evidence? This package constructs an isolated comparison; it does not answer that behavioral question.

- **C**: actual current SKU evidence observation, from the real parent `world_tool`, original-request scope and integrated helper.
- **L**: deep-copy C **after** bounded sibling selection, removing only `lexical_query_tokens_found` and `lexical_query_tokens_absent` from its sibling rows.

Raw records, properties, original matches/order/scores, request description, advice, row order, counts, and completeness/truncation metadata remain identical. Reinserting the original two fields reconstructs C exactly. No computed semantic labels enter either observation.

## Files and reproduction

Run from the repository root:

```sh
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline python research/ecom1/2026-10-22-sku-lexical-ablation-review/verify.py
```

Only Python standard-library dependencies are needed. Source hashes are enforced by `PINNED` in [verify.py](verify.py), and recorded with relative paths in [DEPENDENCIES.json](DEPENDENCIES.json). The exact scope/helper function ASTs must match the integrated source. The helper's two original-request metadata fields are added by the existing integration's documented transformation; the check reproduces that transformation for comparison.

- [fixtures.py](fixtures.py) and [fixtures.json](fixtures.json): 17 neutral synthetic fixtures across the plan's 16 groups; U2 has separate null/empty variants. Each oracle lists the requested constraint relation, actual SKU/field/value, and a reviewable explanation.
- [observations.json](observations.json): exact C/L observations, sizes, and canonical-JSON hashes for each fixture.
- [isolation-details.json](isolation-details.json): 34 ordering permutations, 44 budget checks, early-strip counterexamples, and scope fallbacks.
- [results.json](results.json): concise check counts, input/output hashes, runtime version, and limitations.

The script checks the existence and typed value of 38 cited source facts. It deliberately **does not** automatically certify the semantic relation labels or grade arbitrary answer text. The parent team should independently review those judgments before constructing any model diagnostic. In U4, the glossary is explicit fixture context, not a fabricated product field; a later model request must supply it identically to both arms. **The current offline observations do not supply this glossary to a model.** U4's supported-synonym judgment is conditional on that future context. The fixture records the exact shared context requirement. The oracle describes what supplied facts support, not a requirement to answer uniquely when the observation hides relevant facts.

## What passed, and the useful counterexample

All C/L construction and evidence-preservation checks pass. Negative qualifiers, exact-SKU/property conflicts, absent/null/empty/false distinctions, positive properties, and multiple families remain unchanged in the source evidence after label removal. Unsupported scope falls back unchanged. Oversized original observations are preserved rather than silently truncated. Non-ASCII input is checked using the helper's existing JSON byte accounting.

For the 32-record truncation fixture, C and correct L retain **10 siblings** at 9,500 bytes. Deliberately removing labels **before** row selection admits **12 siblings**, changing evidence coverage. The script records **56** budgets where that incorrect ablation admits additional rows. Thus deleting the assignments from the helper is not an isolated representation test; the proposed L must strip fields after selection.

Pool-order permutations change C in 28 of 34 checks because lexical ties affect original matching/family ordering. Every paired C/L comparison still preserves identical evidence. Do not require cross-permutation invariance from the existing retriever or mistake ordering changes for an effect of removing labels. F2 explicitly demonstrates that a supporting record in the full synthetic fixture can be absent from the observation; neither arm may infer global absence from that omission.

## Limits and next step

These checks run exact definition prefixes in CPython with a prebuilt synthetic `WORLD`; they do not validate index construction, native Monty behavior, full-agent histories, policy routing, or model reasoning. There is no automatic semantic-answer scorer and no full100-readiness claim. No paid test should follow automatically.

Independent source-linked oracle and C/L isolation review is complete. Next freeze the precise selected comparison and semantic assessment rubric before considering a separately chosen bounded diagnostic. The completed earlier diagnostic and its frozen scorer/results remain untouched.

The independent review identified F3's inherited grinder kind/category as inconsistent with its printed-card property. The fixture now uses `kind-printed-card` and `cat-printed-materials`, agreeing with `product_type="printed card"`; no schema-precedence rule is implied. See [REVIEW-NOTES.md](REVIEW-NOTES.md). Any later C/L screen must construct complete, identical runtime-format requests except for the two stripped fields, including the same actual policy/glossary context in both arms. Observation equality alone is not sufficient request parity.

The final N1/N2 review also removed a semantic ambiguity: both fixtures now name P-BAT-A the neutral **Nera G1 grinder unit**, not a body/body-only product. N1's explicit `batteries_included=false` is its sole negative-constraint support. N2 removes exactly that property, with all product names, other records, request, and query unchanged. Assertions enforce this one-property difference; no artificial convention about the meaning of “body” is required.
