# Independent semantic review of all 16 SKU responses

Reviewed 23 October 2026 (Europe/Berlin). This is a readout of the completed frozen diagnostic, not a new scoring rule, paid evaluation or production edit. `frozen-scorer-report.json` remains unchanged.

## Conclusion

The evidence attachment changed both standard-head responses from an unsupported exact FLAT selection to clarification, while preserving all eight exact-SKU/unique-variant control answers across both arms. That supports a narrow observation: the treatment suppressed two false `OUTCOME_OK` outputs in these frozen prompts.

It does **not** establish four newly solved pairs or eight semantically correct treatment responses. Treatment call 3 invents a standard-head implication for BODY; treatment call 12 presents the incompatible FLAT variant as an option and loses the unresolved standard-head condition. The DeWalt wording improvement overlaps the actual parent formatter: parent calls 1 and 10 already clarify and cite both correct kits, and d4955-lineage dispatch appends both SKU values before answering.

No clean new fully supported task resolution over the existing formatted parent is demonstrated by these four prompt pairs. This is narrower than saying the treatment has no useful effect: avoiding a false definitive answer is useful mechanism evidence, but the replacement response still needs to preserve the original constraint faithfully.

## All-call assessment

Call numbers are one-based execution order, as in `verified-calls.json`. Repeats 0 and 1 are two samples of each frozen question, not independent tasks.

| Call | Case / arm / repeat | Independent assessment |
|---|---|---|
| 1 | Kit ambiguity / parent / 0 | Correct ambiguity and two correct catalogue refs; raw message lacks full SKUs. Existing formatter adds both. |
| 2 | Kit ambiguity / treatment / 0 | Supported clarification naming both kits and their actual battery/case properties. Same decision and refs as parent. |
| 3 | Standard head / treatment / 0 | Partial behavioral improvement only: clarification instead of wrong OK, but labels BODY “standard grinder body” without evidence and asserts multiple products match. Does not preserve the unknown head qualification. |
| 4 | Standard head / parent / 0 | Unsupported exact FLAT choice, OUTCOME_OK. Flat-head is not established as satisfying standard-head. |
| 5 | Exact SKU / parent / 0 | Correct exact 2AH SKU, OUTCOME_OK, exact catalogue ref. |
| 6 | Exact SKU / treatment / 0 | Correct exact 2AH SKU, OUTCOME_OK, exact catalogue ref. |
| 7 | Unique battery variant / treatment / 0 | Correct 2AH variant and ref; actual record states 2x2.0Ah batteries and case. |
| 8 | Unique battery variant / parent / 0 | Correct 2AH variant and ref. |
| 9 | Kit ambiguity / treatment / 1 | Supported clarification; same content as call 2. |
| 10 | Kit ambiguity / parent / 1 | Correct ambiguity and both correct refs; raw SKU omission repaired by the existing formatter. |
| 11 | Standard head / parent / 1 | Same unsupported FLAT/OUTCOME_OK choice as call 4. |
| 12 | Standard head / treatment / 1 | Partial improvement only: no definitive choice, but offers FLAT alongside BODY/4AH without saying standard head is unresolved or asking about head geometry. Original qualifier has effectively disappeared. |
| 13 | Exact SKU / treatment / 1 | Correct exact 2AH SKU/outcome/ref. |
| 14 | Exact SKU / parent / 1 | Correct exact 2AH SKU/outcome/ref. |
| 15 | Unique battery variant / parent / 1 | Correct 2AH variant/outcome/ref. |
| 16 | Unique battery variant / treatment / 1 | Correct 2AH variant/outcome/ref. |

All 16 responses are complete `report_completion` actions with finish reason `stop`; none are provider errors, truncations, malformed actions or deferred lookups. Their actions agree with the frozen scorer rows and call plan. Capture verification records 16 provider attempts, matching frozen requests and $0.004214326 total reported cost. No carrier grade is used here.

## Why the standard-head clarifications remain deficient

The actual catalogue supplies:

- BODY: `Metabo W 18 LTX 125 angle grinder body`.
- 4AH: `Metabo W 18 LTX 125 angle grinder kit 2x4.0Ah`.
- FLAT: `Metabo W 18 LTX 125 flat-head grinder body`.

The BODY and 4AH properties list battery platform, disc size, power/speed/voltage and restart protection; neither establishes head geometry. Absence of the word flat is not positive evidence of standard head. Call 3's “standard grinder body” and “Multiple products match the request” assert more than those records support. Excluding FLAT does not make the remaining variants verified matches.

Call 12 accurately describes FLAT as flat-head but offers it under “Which one do you need?” without acknowledging the conflict with the user's standard-head request. It also reduces the completed-step description to “Metabo W18 125 grinder.” Merely switching the outcome label to clarification does not show that the missing constraint was retained.

A faithful response would explicitly preserve that the catalogue does not confirm the requested standard-head geometry, request clarification about that condition or seek further evidence, and avoid presenting a known flat-head variant as a compatible match. This is a semantic review criterion already motivated by the frozen case's unresolved-qualifier rationale, not a retroactive replacement of its mechanical score.

## Frozen scorer versus semantic evidence

The frozen scorer reports parent 4/8 versus treatment 8/8 `correct_final_decisions`, four fixed pairs and zero regressions. Those are reproducible **mechanical rubric outputs**:

- For `kind='unresolved'`, `correct_final` checks only `outcome == OUTCOME_NONE_CLARIFICATION`. It does not inspect message support, qualifier preservation, incompatible options or references. Its `forbidden_sku` criterion is not used by that branch. Consequently both deficient standard-head clarifications count as correct.
- For `kind='clarify'`, the scorer requires full candidate SKUs inside the raw message as well as refs. This penalizes the two parent model replies before the already-present SKU display formatter runs.

Retain those original numbers for auditability, but do not translate them into “four semantic fixes,” “8/8 correct answers,” or measured added final-agent coverage. The supported numeric observations are: standard-head false OK falls from 2/2 to 0/2; both treatment clarifications retain semantic defects; exact/unique controls are correct 4/4 per arm; both DeWalt parent clarifications already become SKU-complete through existing dispatch.

## Actual formatter overlap verification

`verify_formatter_overlap.py` replays all 16 captured actions through the actual definitions and `dispatch` from `2026-10-22-clarification-integration/readable.py`, using the frozen catalogue, policies and each request. Its answer-only host rejects every ECOM RPC. This is not a rewritten imitation of the formatter.

Result: only parent calls **1 and 10** change message text. Both gain:

`Candidates: PT-IMP-DEW-DCF887-2AH, PT-IMP-DEW-DCF887-5AH`

All outcomes remain unchanged; no ECOM RPC is issued. Treatment wording in calls 2/9 is richer, but it does not add missing SKU display coverage to this parent lineage. The formatter does not fix semantic disambiguation: it leaves calls 3/12's unsupported implications and calls 4/11's wrong OK untouched. These action replays do not claim that a full live agent would generate the same replies or receive a particular grade.

Reproduce locally:

```sh
python3 research/ecom1/2026-10-22-sku-paired-diagnostic/results/verify_formatter_overlap.py
```

The source hash and all input/output action pairs are saved in `formatter-overlap-results.json`. Frozen diagnostic sources, records and scorer output were not edited. No paid calls or Brain mutations occurred.
