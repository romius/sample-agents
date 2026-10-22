# Independent review of C/L lexical ablation fixtures

23 October 2026, integration-plan subagent. **Final offline review passed after the author corrected F3 and neutralized the N1/N2 product name.** No paid calls, Brain mutations, completed diagnostic-result edits, or production changes. C means the actual bounded attachment including lexical labels; L is that exact completed observation with only the two lexical label fields removed after budget selection.

## Final verdict

C/L isolation is correctly implemented. The initial 17 fixtures across 16 semantic groups preserve supplied primary product fields and distinctions between explicit false, missing, null/empty, and true. These are declared synthetic catalogues, not newly discovered archived-world facts. The collector does not invent primary properties or install an automatic semantic classifier.

Two initial confounds were corrected before the final check. F3 originally described a card while inheriting grinder kind/category fields; it now consistently says `kind-printed-card`, `cat-printed-materials`, and `product_type="printed card"`. N1/N2 originally used a body name that could imply absent batteries; both now use the neutral `Nera G1 grinder unit`. Independently verified that deleting only `batteries_included=False` is the entire catalogue difference between N1 and N2, with identical instructions/actions. U4 now explicitly records the requirement to include its glossary identically in any future full model requests.

Reviewed final fixture hash: `c5d6199c9856f05aa6124e0d89348b7db522b735869f09f1fded97b60fe855c9`; observation hash: `2fcabf11e00a52b1049ee51ec48a37122cb58af3fce1ee0c5bbfe5d510f2a9b6`. These pins supersede the initial provisional review. No remaining blocking source-fact or C/L isolation defect was found.

## Manual oracle review: all 17 fixtures

| Fixture | Review of source facts and semantic relation |
|---|---|
| U1 missing head | A/B have no head property; geometry remains unknown. C explicitly says flat in both name and property, contradicting the fixture's standard-head request. |
| U2 null | A has `head_type=None`; this supplies no positive or negative geometry. B missing, C flat. Correct unknown/contradicted separation. |
| U2 empty | Same conclusion for empty string; empty is not a documented enum value or false. |
| U3 explicit positive | A explicitly standard; B/C explicitly flat. A alone supports this constraint within the declared full synthetic fixture. Helper metadata still does not certify global index completeness. |
| U4 supplied synonym | Orthogonal→standard is supported **only by the fixture's explicit glossary**, not by general language or the product record alone. That glossary must reach both future model arms identically before expecting supported interpretation. Current observations omit it intentionally. |
| N1 explicit negative | `batteries_included=False` supports without batteries; true contradicts it. Literal token “without” is unnecessary. |
| N2 negative unknown | Corrected neutral unit name makes the missing batteries field genuinely unknown without an artificial body-name convention. N1/N2 now differ only by deleting the explicit false property; independent equality check passed. |
| N3 exact exclusion | Exact A exclusion is clear; B/C remain plausible. This does not settle which refs a later answer should include: its own requirement correctly defers that to supplied citation policy. |
| N4 negative geometry | B standard supports non-flat under the synthetic domain; C flat contradicts it; A is unknown. B's positive support does not erase A's unresolved compatibility. |
| E1 exact identifier | Existing exact SKU establishes identity; siblings alone do not create identifier ambiguity. |
| E2 exact conflict | Named A is 5.0Ah, requested attribute is 2.0Ah; B has 2.0Ah but does not satisfy the identifier. The conjunction cannot be silently repaired by substitution. |
| E3 exact unknown | Exact A identity does not establish missing waterproofing. Unknown is appropriate. |
| E4 unique property | Both kits have case; 2.0Ah explicitly distinguishes B from A's 5.0Ah. Positive property evidence survives lexical stripping. |
| F1 multiple families | Both records explicitly standard and named compact grinder; a family/rank lead cannot establish uniqueness. |
| F2 truncated relevant family | Full fixture contains two explicit supporting tail records, P-N15 **and P-O15**. Neither is visible in the bounded sibling set. A model cannot use omitted full-fixture facts; absence/truncation does not prove no match or uniqueness. The oracle mentions only P-N15 as a witness, not as the only support. |
| F3 lexical distractor | Corrected primary kind/category and product type consistently identify a printed card. Matching grinder marketing words cannot establish that this is an actual grinder. The initial schema contradiction is removed. |
| F4 false/missing/true | False contradicts brushless, absent is unknown, true supports it. This is a good control for implementations that wrongly coerce missing values or booleans by truthiness. |

These judgments assess the supplied facts and conditional relations. They are not an executable arbitrary-answer scorer. A supported property does not automatically require an immediate final SKU when a model's visible catalogue is incomplete; sensible further evidence retrieval must remain distinguishable from a wrong final answer.

## Independently reproduced checks

Ran the initial and corrected verifier with its output writer replaced by an in-memory collector. The regenerated fixtures, observations, isolation details and dependency pins exactly matched the saved JSON files; an independent before/after hash inventory confirmed no files were changed by that run.

Final totals: 17 fixtures, 38 cited-field/value/type assertions, 34 reverse/rotate variants, 44 budget checks, 56 before-cap confounding witnesses, three scope fallbacks. All passed. These are CPython checks only; `native_runtime_checked:false`, zero model calls and zero ECOM calls are correctly disclosed.

An additional independent check examined every L sibling: each equals the actual current `product_view` of its supplied fixture record. No primary product field is fabricated by the ablation. C/L differ only in `lexical_query_tokens_found` and `lexical_query_tokens_absent`; all base matches/order/scores, sibling identities/order, original request text, selection counts, truncation/completeness flags and shared guidance remain equal within each pair.

All requests activate the actual current `sku_lookup_description`; current helper/scope ASTs match the integrated definitions. Calling the real `world_tool` on `WORLD.built=True` demonstrates the observation hook on supplied data. It does not test real catalogue index discovery or prove that the production index is complete.

## Size-selection isolation

The implementation correctly computes C with the full helper and its cap, then deep-copies C and strips labels to produce L. It does **not** refill newly available space in L. Thus shorter L messages contain precisely the same primary evidence.

The early-strip counterfactual establishes why this matters: at a 2,800-byte budget, correct late stripping retains zero sibling rows while early stripping fits one; at 3,400 bytes, late stripping retains one versus two for early stripping. Across 56 tested budgets early removal admits extra rows. That alternative would combine a lexical-label ablation with a retrieval-coverage intervention and cannot be interpreted as the proposed C/L contrast.

At the normal cap, F2 retains 10 of 32 eligible siblings: C is 8,996 bytes and L 7,926 bytes. Both are explicitly truncated; neither contains the supporting tail records. The unchanged oversized-parent fallback is also correct: base evidence is not truncated merely to fit the attachment cap.

The shorter L message necessarily changes prompt length as well as removing lexical content. This does not invalidate C/L construction, but future results cannot distinguish a semantic-label effect from generic length/attention effects without a separate length-matched control. Shared guidance still mentions token diagnostics even in L; that is intentional instruction constancy, not a test of an independently optimized label-free prompt.

## Before any future model diagnostic

Freeze the corrected fixture/source hashes, preserve the source-linked oracle notes, and construct full runtime-format parent/treatment prompts. Supply U4's glossary and any remaining fixture-domain conventions equally to both arms; keep oracle labels/explanations outside the model input. Supply citation policy for N3. Do not evaluate an omitted F2 fact as though it were visible. Preserve post-cap row equality. Record actual exposure, truncation, invalid replies and deferred lookups separately. No model outcome, benchmark improvement or full100 readiness is established by these offline checks.
