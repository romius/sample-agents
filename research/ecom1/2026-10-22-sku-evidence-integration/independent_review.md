# Independent review of SKU evidence integration

Reviewed by the integration-plan subagent on 22 October 2026. Read-only candidate review; no Brain jobs, baseline changes, or submitted-source changes. This review pins the initially inspected packed SHA-256 `d67c34604edf2c8157b72ab91a1355ffbff83c7bca7ff78040d411eb9253e6f5` (60,737 bytes), readable `d4622cf363fdfae34e110d7f4e0ab4354a3f8a6120ba77ed36e2cfb224f9a0cb`. Later scope changes require refreshing the hashes/tests.

## Verdict

The bounded observation integration is mechanically sound in the tested cases. It preserves the original description, including negation and decimals, instead of trusting a model-shortened catalog query. It preserves the original catalog matches, ordering, scores and note; no SKU is chosen and no answer or authorization is rewritten. Family expansion is limited to families found in the parent's displayed results. `pool_complete` remains false because the parent index does not establish completeness. This is an ungraded child of pending d5204r1, not a measured improvement over the verified record.

One scope issue was reproduced: the initial blacklist rejects selected action verbs, not all mixed intents. The following initially returned a non-null description and therefore could receive the observation attachment:

- `sku for Acme drill and cancel my order pls. sku only.`
- `sku for Acme drill and email the invoice pls. sku only.`
- `need code: Acme drill\tand cancel my order. answer only with sku.` (literal tab between drill and and)

These are false-positive observation scopes, not authorization bypasses: downstream actions remain controlled by the existing agent/policies. Add known verb controls if desired, but document the scope as conservative syntactic coverage and avoid claiming a complete semantic mixed-intent parser. Adding another finite list cannot prove every mixed request is excluded. The parent agent has acknowledged this and is addressing it.

## Independent checks performed

- Re-ran `verify_scope.py` and `verify_whole_lookup.py` under Python 3.14 / pydantic-monty 1.2.0, suppressing their result-file writes. Both passed: 200 archived request scope checks, two exact-catalogue qualifier-loss cases, native parity and malformed/out-of-scope cases; 30 whole-agent executions and five parent controls.
- Added read-only checks for retained `but not the 5.0Ah kit`, `2.0Ah ... without a case`, exact `PT-EXACT-123`, and `standard head` text. All are retained in the extracted description; this does not assert that lexical tokens solve those constraints.
- Exercised 12 synthetic siblings at total observation budgets 0, 500, 1,000, 2,000, 4,000 and 9,500 bytes. Budgets through 1,000 returned the unchanged base; 2,000/4,000 returned 3/10 siblings with truncation true; 9,500 returned all 12 with truncation false but pool completeness still false. Original fields and input world stayed unchanged. All attached observations fit the requested total budget. An unchanged base may itself exceed the requested budget, intentionally: the helper does not truncate parent evidence.
- Verified all three manifest hashes against actual files and packed size 60,737 bytes, leaving 4,799 bytes.

The whole-agent tests script the model's actions and final answer. Their identical answers establish no automatic answer rewrite, not that the live model is unaffected or improved. The general archived replay report likewise cannot establish model equivalence when full prompts were not captured; it explicitly lists that limitation and RPC misses. Native execution establishes runtime compatibility, not grader credit.

## Recommended paired prompt diagnostic

Four cases × two arms × two repeats gives 16 model calls: archived ambiguous t021/t041, one exact-SKU control, and one genuinely single-compatible variant control. This is a small mechanism diagnostic, not a full100, a baseline promotion, or a reliable effect-size estimate.

Freeze each case's complete original prompt, catalog/policy facts, tool schema, inference settings and expected answer criteria before calling the model. The treatment arm should differ only by the actual `sku_lookup_evidence` field inserted at the catalog observation the candidate would change. Preserve all other messages and parent fields byte-for-byte. If reconstructing historical messages or supplying a synthetic final-report request is necessary, label that reconstruction; do not call it an exact archived execution. Do not compare a new prompt against historical model output as if it were a paired control.

Predeclare outcomes:

- t021: when both actual kits satisfy the case request, clarify and identify both; do not force a SKU from rank alone.
- t041: preserve the unresolved `standard head` qualifier; lexical presence of `head` in `flat-head` does not resolve it.
- Exact SKU: return the named SKU when it exists and no contradictory explicit constraint is present, with its correct reference.
- Single-compatible variant: return the unique compatible product rather than defaulting to clarification because siblings exist. Establish compatibility from actual attributes, not absent words.

Capture exact request/response bytes, finish reason, schema validity, outcome, SKU/reference set and usage. Counterbalance arm order across repeats (AB then BA). Report every result, including malformed/truncated output. Two repeats are not independent tasks or a statistical significance test. If a response requests another tool action, preserve that fact; do not score an answer that was never generated or feed the old response sequence as proof of the treatment's behavior.

Meaningful additional controls/pitfalls:

- Exact SKU plus a contradictory qualifier: do not silently privilege the SKU over the user's condition.
- Explicit negation (`without batteries`, `not the guide-rail bundle`) and a positive qualifier shared by two siblings (`with case`). Lexical token absence is not proof of negation.
- A true unique match whose distinguishing attribute is missing from one incomplete record: unresolved is safer than a uniqueness claim.
- Wrong-family/no-family top hits: the helper cannot introduce a family the parent search never retrieved.
- Zero-row or truncated attachment and the no-attachment budget fallback: track actual exposure, not merely assignment to treatment.
- Multiple catalog calls: added observations can consume the parent's history budget and change trimming. The single-observation diagnostic does not test that full-loop interaction.
- Do not loosen acceptance thresholds or tune the prompt after seeing these four outputs and then reuse the same cases as independent validation. Any iteration needs a separately labeled follow-up and fresh controls.

Keep all existing full100 jobs untouched and do not add a new full100 based on offline mechanics or this 16-call diagnostic alone.
