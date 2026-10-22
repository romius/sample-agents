# Preregistered C-versus-L next-action diagnostic

23 October 2026. **Preparation only. Do not publish, submit, or infer automatically.** The root agent will decide separately after reviewing the final frozen inputs, source and checks.

## Question and fixed design

Does deleting only the two lexical token labels from an already bounded SKU sibling attachment change the model's immediate next-action semantics? C is the complete captured d5785r1 request. L deletes `lexical_query_tokens_found` and `lexical_query_tokens_absent` after the actual runtime selected the rows. No row refill, property edit, prompt rewrite, setting change, or new semantic annotation is allowed. Complete message histories, original matches/scores/order, policy observations, identity, request, counts, truncation and shared decision guidance remain constant.

Use **all 17 reviewed fixtures**, in the matrix's existing order, × both arms × two repeats = **68 logical calls**. For repeat 1, even-indexed fixtures run C then L, odd-indexed fixtures L then C. Repeat 2 reverses each pair. There is no adaptive selection, early stopping on favorable outcomes, post-result fixture exclusion or cherry-picked third repeat. Cancellation must stop subsequent calls and omit the final carrier Answer. Provider errors are retained in place; the runner adds no retry. SDK retries, if any, are transport attempts and must be reported separately from 68 planned logical calls.

Use exactly the captured SDK inputs: `openai/gpt-oss-120b`, `max_completion_tokens=2048`, `reasoning={"effort":"medium"}`, `temperature=0`, SDK 0.3.7 with its fixed provider configuration. Do not manufacture a private HTTP request or change aliases/settings. Every request's ordinary and compact JSON representations must fit 64 KiB; packed source must fit 65,536 bytes. Native checks use 10-second feed/turn limits and 1,000 suspensions. There is no additional SDK call quota. No ECOM task action, model-requested tool, or fabricated runtime result will execute.

The carrier's grade is irrelevant. This is neither a full100 nor a promotion candidate. Repeated next-action observations are not independent tasks or completed task successes.

## Frozen context constraints

- U4's actual catalogue-policy Read contains the same explicit orthogonal→standard glossary in both arms. The semantic assessment may rely on this supplied relation; it must not infer an unstated general-language synonym.
- F2's actual runtime indexes **32 products**, identifies **16 eligible siblings** in the matched Nera family, and shows **10**. P-N15 is omitted by the sibling truncation. P-O15 belongs to the other indexed family, which is absent from the top-two match-family set; its omission is not the same truncation mechanism. Neither supporting tail is visible in the next-action evidence. Do not expect the model to identify either hidden SKU, and do not treat the top-two matches as exhaustive.
- Every attachment states `pool_complete=false`. Correct positive property evidence can be recognized locally without asserting global catalogue uniqueness. The conservative continuation category is separate from a mistaken positive claim.
- N3 includes the actual shared catalogue policy excluding explicitly rejected Y from quoted candidates. The model must retain exclusion of A without treating sibling order as uniqueness.
- Full fixture oracle explanations stay outside model inputs. They are review aids, not additional evidence available to the model.

## Manual semantic rubric, fixed before any response

Harvest full raw replies, reasoning fields if provided, finish reasons, errors and usage from immutable inference trace events. Do not print them into the diagnostic stdout: community d6210 demonstrated overflow at the 65,536-byte output cap. Stdout contains only bounded metadata; its error previews and response IDs may be truncated and are never the semantic evidence. Review the first requested action or complete final report, including its message and refs; do not infer semantic correctness from `OUTCOME_NONE_CLARIFICATION` or any other outcome token alone. A clarification can assert a false property or offer a contradicted option. A tool request defers a decision and cannot be counted as a solved task.

Assess only facts visible in that arm's complete request. Keep support for a property separate from justification for a unique final disposition: one supported record does not eliminate other unknown records or establish missing catalogue coverage. U3/U4/N1 test recognition of positive evidence, not a mandatory immediate OK; E1's exact identifier and E4's explicit capacity distinction are clearer controls, but a justified verification request still remains deferred. This mechanism screen has no automatic 68-pass tally.

For action classification, require one complete JSON action in final content, optionally enclosed in one JSON fence. Record concatenated objects, surplus prose, truncated or missing content as malformed/ambiguous rather than selecting the most favorable object. Preserve all raw content and reasoning, but reasoning-channel speculation is not a substitute for the submitted action/report. If a reviewer separately checks what the production parser would accept, report that as a distinct parser-acceptance observation; do not silently change this diagnostic classification rule.

For every one of 68 planned calls, fill the blank `manual-review-sheet.json` entry with the response reference, reviewer, exact evidence quotation/pointer and short rationale. Flags may co-occur:

| Field | Decision rule |
|---|---|
| `action_class` | Final report; deferred read/search/catalogue or other action; malformed/missing action; provider error; cancelled/not reached. Keep unsupported or dangerous requested tools visible even though none execute. |
| `false_OK` | A final OK resolves to an unsupported, contradicted or unjustifiably unique SKU, silently substitutes an exact identifier, or asserts global no-match/completeness without evidence. An OK token alone is insufficient to decide. |
| `unsupported_positive_assertion` | Any answer or clarification positively assigns an unknown property, e.g. calling A “standard” when absent/null/empty. Naming A as explicitly unresolved is not this error. |
| `qualifier_loss` | A final decision or clarification discards a requested constraint/negation instead of preserving it as supported, contradicted or unresolved. A targeted lookup retaining the constraint is deferred, not a semantic failure. |
| `contradicted_option` | The model offers a record as satisfying the request despite an explicit contradictory property/type or exclusion. Mentioning the record to explain its rejection is allowed. |
| `positive_control_preserved` | Recognizes available exact-ID, explicit positive/negative or shared-glossary evidence without inventing generic ambiguity; distinguish correct final selection from a justified verification step. Applicable controls are identified below. |
| `targeted_deferred_lookup` | Next action seeks evidence relevant to an unresolved qualifier, conflicting exact ID, or incomplete/truncated family. Record purpose; it is not scored as final success. Unfocused repetition is noted separately in rationale. |
| `malformed` | Missing/unparseable/unsupported action form or length-truncated ambiguous response. Preserve original; do not silently repair or select a favorable concatenated object. |
| `provider_error` / `cancelled` | Record transport/runtime failure separately; do not impute a semantic win or loss. Unattempted post-cancel calls remain present in the planned denominator. |

Fixture-specific review anchors:

| Fixture | Source-bound interpretation |
|---|---|
| U1, U2 null, U2 empty | A/B head geometry remains unknown; C is explicitly flat. Preserve “standard head”; do not offer C as satisfying it or label A/B standard. |
| U3 | A explicitly standard, B/C flat. Preserve this positive distinction; local support does not certify global completeness. |
| U4 | Same comparison, but A is supported through the shared policy glossary. Literal absence of “standard” is not contrary evidence. |
| N1 | Explicit `batteries_included=false` supports without batteries; true contradicts it. Positive control for negative polarity. |
| N2 | Neutral unit name plus missing batteries field is unknown, not false. Do not import N1's missing fact. |
| N3 | A excluded; B/C remain plausible. Clarification/continued lookup should preserve the exclusion and shared citation policy. |
| N4 | B supports non-flat; A remains unknown; C contradicts it. B's support alone does not resolve A's compatibility. |
| E1 | Exact existing P-KIT-A with no added conflict; siblings alone do not create identity ambiguity. Positive control. |
| E2 | Exact A has 5.0Ah but request says 2.0Ah; B has 2.0Ah but is not A. Preserve the conflict; no silent substitution. |
| E3 | Exact A does not establish waterproofing; preserve unknown qualifier. |
| E4 | B's explicit 2.0Ah and case support the requested distinction from A's 5.0Ah. Positive control; retrieval may still verify scope. |
| F1 | Two families explicitly satisfy the visible constraint. Score/order does not establish uniqueness. |
| F2 | Visible evidence is truncated/incomplete. Reward preserved uncertainty and targeted continuation; never require hidden N15/O15 identification. |
| F3 | P-DIST-A is a printed card in primary kind/category/properties despite matching marketing words. It is not a compatible grinder. A/B geometry remains unknown; C flat. |
| F4 | A false, B missing, C true for brushless. Preserve all three states; C's support does not make B known false. |

## Readout and limitations

Before interpretation, reconcile every planned ordinal/request hash with actual SDK request/response/error traces, settings and billed usage. Confirm U4 shared context and F2 exposure. Retain all planned calls and each invalid/error/cancelled result. Any request drift is a protocol deviation, not a favorable result. Report per-case/per-repeat C/L pairs, flag disagreements and control behavior; do not select the better repeat or collapse to an outcome-only score. Have an independent reviewer assess at least all apparent improvements, control regressions, malformed outputs and disputed classifications. Preserve disagreements rather than inventing consensus.

No efficacy threshold automatically authorizes publication, a production change or another evaluation. Consistent reductions in specific semantic errors without control regressions would motivate further review, not establish full100 gain. Two repeats are descriptive; no significance or probability claim follows. C/L also differ in length, so a result cannot separate lexical-label semantics from generic attention/length effects. L retains original lexical match scores/order, query text and shared guidance mentioning token coverage; it is not removal of all lexical information. Scripted upstream routing/first actions may differ from live behavior; the diagnostic assesses only the captured next-action boundary.
