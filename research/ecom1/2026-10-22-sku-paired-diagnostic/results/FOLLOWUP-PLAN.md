# Follow-up: preserve unsupported qualifiers in SKU clarifications

23 October 2026 — independent score-opportunities review. This is a proposed offline validation plan, not a production change or a full100-readiness claim. No paid calls, jobs, candidate changes, or benchmark score gains were made for this review.

## What the completed diagnostic establishes

The sealed 16-call diagnostic reduced false `OUTCOME_OK` choices on the four ambiguous decisions from 2/4 to 0/4. Both arms retained 4/4 correct exact-SKU/unique-variant control decisions. These are immediate next-action observations on four frozen questions from two underlying catalogue contexts, with two repeats; they do not measure full-task accuracy or general effect size. Evidence: [summary.json](summary.json), [verified-calls.json](verified-calls.json), and [frozen-scorer-report.json](frozen-scorer-report.json).

The frozen scorer's treatment 8/8 `correct_final_decisions` is not a semantic-quality certificate. It accepts clarification on the standard-head case without verifying whether that clarification preserves the missing qualifier:

- Call 3 says BODY is a “standard grinder body,” although the shown records do not establish standard head. An unsupported positive attribute was introduced.
- Call 12 offers FLAT, BODY, and 4AH as alternatives while dropping the requested standard-head requirement. The result is a clarification, but it makes the customer resolve a broader request than the one asked.
- Calls 1 and 10 were parent-arm clarifications missing literal candidate SKU names in their messages. The current d4955 formatter already appends those names: [formatter-overlap-results.json](formatter-overlap-results.json) reports only those two messages changed. Do not count this formatting improvement again as a new semantic gain. Formatter replay leaves the standard-head semantic errors unresolved.

Keep the original frozen scorer unchanged. Add a separately named qualifier-preservation assessment, reporting both results rather than retroactively redefining success.

## Existing evidence contract and its limits

The actual attachment is built by [bounded_lookup_evidence.py](../../2026-10-22-sku-evidence-review/bounded_lookup_evidence.py), with original-request scope supplied by [scope.py](../../2026-10-22-sku-evidence-integration/scope.py). It already includes the original `request_description`, actual product names/properties, lexical tokens found/absent, and a warning not to discard unresolved qualifiers. Its existing instruction was insufficient on both treatment standard-head calls.

Important limits to preserve:

- Token coverage is lexical and uses prefix matching. It is not a semantic predicate, a property-value comparison, a negation parser, or evidence that a product lacks an attribute.
- Sibling families are selected from the original match families, then rows are sorted by family order, SKU, and path. An unrelated family may consume the bounded attachment. The attachment reports eligible/returned siblings and truncation; it does not establish complete retrieval.
- `pool_complete` remains false because parent index coverage is unverified. Missing a token from returned rows cannot establish that no matching product exists elsewhere.
- The original matches, order, scores, scope, and product records remain authoritative inputs. A SKU suffix such as BODY describes a supplied configuration only when supported by the record; it does not establish a different property such as head geometry.
- The whole observation is bounded at 9,500 encoded bytes. A longer note can evict a sibling or cause the attachment to be omitted, confounding an apparent wording-only comparison.

## Minimal intervention to test

There are two distinct hypotheses, and the diagnostic does not distinguish them. The preferred first ablation is removal of the derived lexical labels, not another instruction added on faith.

**H-L (representation):** `lexical_query_tokens_found/absent` makes word coverage look like a compatibility checklist. In the actual standard-head fixture, FLAT is the only principal-family row with `head` in `found`; `standard` is absent for all three rows. BODY/4AH list both `standard` and `head` as absent. Thus the derived fields give FLAT apparent progress on the compound qualifier while BODY can be misread as its default opposite. The raw names/properties do not establish that conclusion. Token bags also discard negation scope and fragment numeric/property phrases. This is a plausible mechanism, not a causal finding: the original unannotated parent also chose FLAT, and the bundled treatment improved the outcome label.

**H-T (clarification contract):** a short clarification-specific output contract in the existing `decision_rule` will reduce unsupported positive descriptions and dropped qualifiers. It may fail because similar advice already exists.

Prepare these four **offline observation variants**, not four new paid runs:

| Arm | Change from current sibling attachment | Precise uncertainty it isolates |
|---|---|---|
| C | None | Reference observation from the completed treatment. |
| L | Delete only each sibling's `lexical_query_tokens_found` and `lexical_query_tokens_absent`. | Do the derived labels hurt constraint preservation beyond what raw names/properties and original request provide? |
| T | Replace overlapping sentences in `decision_rule` with the short contract below; retain lexical fields. | Does a clearer clarification contract repair the defect with the current representation? |
| LT | Apply both isolated changes. | Only if justified later: do representation and instruction interact? Do not begin by bundling them and claiming a mechanism. |

For L, construct the current bounded attachment **first**, then remove the two lexical fields from its selected rows. Preserve the exact rows, order, counts, original matches, and truncation flag. Removing fields before the cap-selection loop can admit extra siblings and would confound the ablation. This is a deliberate observation-only test, not a new retrieval optimizer. Raw names/properties and the original request remain visible, so L removes no primary product evidence and introduces no learned semantic classifier.

The proposed T contract is:

> In a clarification, repeat the requested qualifier that remains unverified and say the shown records do not establish it. Describe rows as possible alternatives, not confirmed matches, until their names or properties support that qualifier. Do not infer an opposite property from a missing word or field. An exact SKU resolves identity, but does not erase a conflicting or unverified requested attribute.

Both changes are generic: no product, family, task ID, “standard head,” or expected answer belongs in the implementation. Retain the original policy/security caveat and lexical-ranking warning. T should replace overlapping existing sentences instead of continually appending prose.

Do **not** compute `unresolved_qualifiers` or `compatible=false` from `lexical_query_tokens_absent`. Do not label an absent `head_type`, an absent word “standard,” and an explicit `head_type="flat"` as equivalent evidence. Do not introduce an automatic SKU choice, refusal, or answer rewrite in this experiment.

These are falsifiable observation hypotheses, not demonstrated fixes. Offline checks can prove the ablation is isolated and evidence-preserving, but cannot prove that removing lexical labels changes model reasoning. A subsequent structured constraint representation would need its own extraction/provenance evaluation and a new plan.

## Fresh offline fixture design

Build a small artificial catalogue with neutral names and IDs (for example F-A/F-B and P-A/P-B/P-C), explicit properties, and a human-readable fixture oracle. Keep its records separate from the archived benchmark catalogue. Instantiate the real parent `world_tool`, scope function, and attachment builder; do not fabricate a treatment observation by hand. Use accepted SKU-only request forms.

The oracle is based on supplied records and any supplied policy glossary, not token counts. For each requested constraint, record an exact request span plus a source field/value or the absence of supporting evidence. Distinguish supported, explicitly contradicted, and unknown. These labels belong in evaluation fixtures, not in the model's observation unless a later separately tested extractor actually produces them.

| Fixture | Request/evidence contrast | Required behavior; prohibited shortcut |
|---|---|---|
| U1: unspecified head | Ask for a standard-head grinder; BODY and KIT records contain no head information; FLAT explicitly states flat head. | Clarification must preserve “standard head” and its evidentiary uncertainty. It must not call BODY standard or present FLAT as satisfying the request. Targeted retrieval is deferred. |
| U2: missing/null/empty | Repeat U1 with the relevant field absent, null, then empty string. | No positive or negative attribute inference from any of these states. Unknown remains unknown. |
| U3: supported positive | Add an explicit standard-head property to exactly one otherwise eligible record. | The new positive evidence can resolve that constraint; do not insist on clarification solely because earlier variants lacked the property. Other unresolved constraints still matter. |
| U4: documented synonym | A supplied glossary equates a neutral synonym to the requested property; record uses only the synonym. | Absent literal words do not force rejection or uncertainty when supplied evidence establishes the equivalence. No unsourced synonym mapping. |
| N1: explicit negative satisfied | Request a tool without batteries; BODY has `batteries_included=false`, KIT has true. | Preserve negation; the false field supports the negative constraint. Do not reject BODY because “without” is absent from its name. |
| N2: negative unknown | Remove BODY's battery field while keeping KIT's true field. | BODY is now unknown, not automatically battery-free. Clarify/retrieve rather than converting absence into false. |
| N3: explicit SKU exclusion | Request a family but not P-A; P-B and P-C remain plausible. | Exclude only P-A and retain ambiguity between P-B/P-C. Follow the supplied policy on excluded-SKU references; do not infer that all other attributes are satisfied. |
| N4: lexical negation trap | Request “not the flat-head version”; one record explicitly flat, one explicitly standard, one has no head field. | The standard record supports this constraint; unknown record remains unresolved. The word “head” and score cannot override negation. |
| E1: exact identifier control | Name an existing exact SKU with no additional conflicting requirement. | Return that SKU/ref when otherwise allowed. No new generic clarification because sibling evidence is present. |
| E2: exact SKU conflict | Name P-A and request 2.0Ah; P-A explicitly has 5.0Ah, another SKU has 2.0Ah. | Ask which requirement should govern; do not silently substitute the other SKU or suppress the contradiction. |
| E3: exact SKU plus unknown | Name P-A and require waterproofing; the property is absent. | Preserve that unverified attribute; exact identity alone is not evidence of waterproofing. |
| E4: explicit unique variant | Two kits share a case; only one explicitly has the requested battery capacity. | Preserve the existing positive-control behavior; “has case” alone is ambiguous, while the distinguishing property can resolve it. |
| F1: several families | Two families share a broad description; the first family contains a plausible high-scoring row. | A score lead or first family does not prove uniqueness across represented families. Ask a discriminating question or retrieve. |
| F2: relevant family truncated | Place supporting/contradicting rows after the byte cap; then permute family and SKU ordering. | Report bounded evidence honestly. No global absence/uniqueness conclusion from omitted rows. Do not silently change the byte cap or expand retrieval in this wording experiment. |
| F3: irrelevant lexical distractor | Add a different family whose marketing name contains every request token but whose explicit model/property conflicts. | Lexical coverage must not displace actual identity/property evidence. |
| F4: supported false versus absent | Ask for a brushless model; compare `brushless=false`, absent field, and true field. | Treat contradiction, unknown, and support distinctly; do not conflate false with missing via truthiness. |

For U/N/E/F fixtures, add deterministic order permutations and equivalent request spellings that the existing scope actually accepts. Record unsupported forms as unchanged fallback, not as evidence of semantic success. Include the archived four cases only as regression controls; they are not fresh holdouts.

## Offline checks before any further model diagnostic

1. Freeze fixture records, source-field oracles, requests, observations, scorer rules, and hashes before examining new model outputs. Independently review the oracles, especially negation and exact-SKU conflicts.
2. Assert all four observation variants preserve parent matches/order/scores, product fields, scope fallback, row order, sibling set, and completeness metadata. For C/L, reinserting exactly the two removed fields must restore full request equality; for C/T, restoring only the note must do so; LT must equal sequential application of these transformations in either order. If note growth evicts rows or suppresses the attachment, fail isolation and shorten it. No variants may spend freed bytes on more siblings.
3. Exercise zero budget, budget just below the unchanged base observation, cap boundary, oversized properties, omitted properties, non-ASCII request text, and multi-family ordering. Confirm the original observation remains intact when an attachment cannot fit. Preserve the 9,500-byte limit.
4. Run the actual current d4955 completion formatter over proposed answer fixtures. Confirm it adds names only where expected and neither erases qualifiers nor turns contradictory/unknown descriptions into supported ones. Do not credit the note for fixes already supplied by the formatter.
5. Add adversarial scorer fixtures, including the exact call-3 and call-12 answers. Both must fail qualifier preservation despite their clarification outcome. A cautious answer explicitly retaining the unresolved qualifier must pass. An exact-SKU positive answer must not fail merely for omitting irrelevant sibling discussion.
6. Preserve raw answers, references, selected action, finish reason, and errors separately. A relevant read/search is deferred, not a successful final clarification. An unsupported positive claim remains an error even when the outcome is `OUTCOME_NONE_CLARIFICATION`.
7. Add representation-specific controls: exact word absent but supported synonym present; every word present but negated/contradictory property; “standard head” split across unrelated fields; and an irrelevant marketing name containing the tokens. Confirm L strips only annotations and leaves those source facts unchanged. Permute a candidate's name token order without changing properties and show that the fixture oracle stays fixed even if lexical annotations change. This establishes why lexical coverage cannot serve as the correctness oracle.

These steps test construction and measurement without inference. They cannot prove the model will obey the new contract.

## Evidence needed for the next decision

If all offline gates pass and a new model diagnostic is separately chosen, the first minimal comparison should be **C versus L** on unresolved-qualifier fixtures and positive controls. This tests a clear representation uncertainty without adding instructions or a larger guard. C versus T is a separate option if the team prioritizes the output-contract hypothesis; LT is a later interaction test, not the initial attribution claim. No new paid test should be dispatched merely because this plan exists: first publish the reproducible offline fixture matrix, isolation assertions, and precise selected comparison.

Use the same contemporary parent/formatter, inference settings, byte limits, counterbalanced arm order, and frozen case oracles. The old bare-parent arm is contextual evidence only; it does not isolate either follow-up mechanism.

Pre-register separate counts for: false unique choices; unsupported positive attributes; dropped/contradicted qualifiers; correct explicit unknowns; exact-SKU/unique-property regressions; candidate-name formatting before/after the formatter; deferred retrieval; malformed/error/truncated outputs. Keep all cases and raw outputs. Manually inspect semantic claims against exact record fields rather than classifying success solely by outcome label.

Required evidence to continue: preservation of the original unresolved qualifier on the archived failure and fresh analogues; no new absent-word-as-false inference; no silent exact-SKU substitution on conflicts; no excessive clarification in supported exact/unique controls; and no hidden attachment-coverage change. Report per-case evidence and remaining failures, not an aggregate “clarification success” number. Small paired repeats support only the sampled cases.

Even a successful next-action diagnostic would leave full-agent retrieval follow-through, multiple-observation/history-budget effects, security routing, overall cost, and regenerated-task score untested. It would justify considering an isolated integration validation step, not announcing full100 readiness or promoting a candidate.
