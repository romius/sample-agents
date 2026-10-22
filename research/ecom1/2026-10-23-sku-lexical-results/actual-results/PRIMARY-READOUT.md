# Primary manual review of all 68 completed responses

The primary reviewer read every full final response, checked its source-bound fixture and frozen rubric, and populated `primary-manual-review.json`. This is a manual semantic assessment; the code that transcribed the judgments is not an automatic scorer. Independent assessment is pending and any disagreements will be retained.

**Do not integrate lexical-label deletion on this evidence.** Both counterbalanced repeats show the same material tradeoffs:

| Fixture | C (labels retained) | L (labels removed) | Interpretation |
|---|---|---|---|
| U1 missing geometry | Clarification offers flat C and calls unknown A/B matches | Omits C but still calls A/B standard-head matches | Partial removal of one contradicted option; unsupported property inference remains |
| U2 null/empty; N2 missing batteries | Incorrect final A in both repeats | Same incorrect final A | Neither version fixes unknown-vs-known inference |
| U3 explicit standard; U4 shared glossary; N1 explicit false; E4 capacity/case | Recognizes supported visible product | Same recognition | Positive evidence retained; incomplete pool still does not establish global uniqueness |
| N3 explicit SKU exclusion | Excludes A, cites B/C, clarifies | Same | No excluded-A citation regression; mentioning A as rejected is not selecting it |
| N4 non-flat request | Treats unknown A as non-flat | Same implication | Both conflate unknown A with supported B |
| E1 exact identifier | Correct A | Correct A | Exact-ID control preserved |
| E2 exact ID versus capacity conflict | Explicitly contrasts A=5.0Ah and B=2.0Ah, asks user | Same | Conflict retained despite imprecise opening phrase |
| E3 exact A waterproof | Invents identity ambiguity, does not preserve unknown waterproofing | Same | Clarification outcome alone is insufficient |
| F1 two supported families | Clarifies two valid alternatives | Same | No unique winner asserted |
| F2 truncated family | Drops standard-head qualifier and asks among ten unknown-geometry records | Requests `catalog` for `standard head grinder` | More relevant deferred lookup in both repeats; no tools were executed, no task success demonstrated |
| F3 misleading marketing card | Defective clarification offers printed card and flat grinder | Final OK selects explicitly flat C | L produces an incorrect terminal answer in both repeats; C was already defective |
| F4 false/missing/true | Selects supported C but does not resolve unknown B | Same | Local positive recognition is not uniqueness evidence |

The primary sheet separates wrong-property/wrong-SKU false OK from **scope-only false OK**: U3/U4/N1/E4 select a visibly supported record, but each attachment explicitly states `pool_complete=false`, and the shared decision rule requires complete retrieval before claiming uniqueness. Those rows retain `positive_control_preserved=true` and are not represented as wrong-property choices. F4 also has a specific unresolved B, independently of the incomplete pool. An exact identifier in E1 can resolve identity without searching all siblings.

All 68 final contents are single parseable JSON actions: 66 final reports and two deferred catalogue requests. No malformed/length-truncated replies, provider errors, cancellations, transport retries or missing ordinals were observed. The two catalogue requests carry an extra `limit` key; the actual `world_tool` catalog dispatcher explicitly reads `function.get("limit", 8)` alongside `query` (repaired d5785 readable.py:659), so this is not treated as a malformed action. This is distinct from executing the request or proving its eventual success.

Provider accounting reconciles all 68 attempts to DeepInfra and the fixed SDK0.3.7/request settings: 224,504 prompt +23,883 completion tokens, complete cost $0.012366758. Full raw response/reasoning and request data are preserved in the CAS-verified traces. Reasoning is not substituted for final action semantics.

The repeats are descriptive observations, not independent benchmark tasks or a statistical claim. C/L differ in length as well as two token-label arrays. They retain lexical scores/order and shared guidance; scripted upstream routing may differ from a live agent. This experiment does not test STACK E's deterministic early-answer paths, including its observed `outside` exclusion failures. No full100 score gain or broad production readiness follows.
