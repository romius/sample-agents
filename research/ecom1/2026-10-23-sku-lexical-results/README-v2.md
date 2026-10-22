# Validator v2: reviewed schema corrections

Use `validate_trace_v2.py` for future readout. The original validator, original 30-test report, seven-file SHA256SUMS, and frozen diagnostic evidence are preserved unchanged. The original validator has known false acceptances documented by independent review and should not certify future results. This revision contains no real 68-call result data and makes no semantic or model-performance claim.

## Corrected boundaries

- Reject unknown event kinds across the whole trace, not just `llm_*`. The reviewed set is `rpc_request`, `rpc_response`, `llm_request`, `llm_response`, `llm_retry`, `llm_error`, `agent_finished`, and `agent_error`. An unreviewed lifecycle kind or schema requires an explicit reviewed adapter; it is not silently ignored.
- Require StartTrial and EndTrial request `arguments.trialId` to match the sealed trial identity. Retain the existing response-side identity and run-ID checks, and check StartTrial request/response ordering.
- Require `agent_finished.state` to agree with the final trial-summary state (only canceled/cancelled spelling is normalized). An agent error cannot coexist with an answered trial without a finding. Job state `completed` may still contain a failed trial; those two different levels are not conflated. Agent-finished transient usage is not substituted for settled durable accounting.
- Require trial `usage.model_calls` to equal the number of observed HTTP request attempts, and any supplied job aggregate to agree with the trial. Missing/non-integer or inconsistent counts prevent complete billing reconciliation.
- Preserve strict requested provider routing. When a response body's `provider` is present, require the observed archived value `DeepInfra`; contradictory values are deviations. Missing response provider remains explicitly unknown in `provider_audit` rather than being invented from the request. A present response-body model must match the requested model. This distinguishes requested routing from observed-provider evidence.

## Retry identity correction from actual archives

The SDK assigns a **new durable call ID per HTTP attempt**. The earlier synthetic test wrongly reused the same call ID across retry attempts. V2 retains every transport ID and groups candidate logical chains by ordered `attempt` numbers. It then requires the full preceding `llm_retry` event, matching `next_attempt`, an eligible 429 without generation evidence, correct sequence boundaries, and identical model/request contents for the planned ordinal. Request and response events within each attempt must share their transport ID; a retry must use a fresh ID. A new attempt1 remains a separate logical request even if its prompt is identical. Candidate grouping is never accepted without those validations.

The archived continuation `j9b8c85def8734dff9af15bcfd48ad4cc` provides 47 full wire requests with 47 distinct durable call IDs, 43 attempt1 logical starts, and 4 retry attempts. Both its settled job and trial summaries report `model_calls=47`. For example, transport call2/attempt1 at sequence8 is followed by call3/attempt2 at sequence11 with an identical request. `retry-schema-evidence-v2.json` and `DEPENDENCIES-v2.json` pin these facts and their sources.

Those local archives contain full request bodies and a durable summary, but only indexes for some retry events. They establish transport-ID/count semantics; they are **not** represented as a complete immutable trace accepted by this validator. Positive full-chain tests are explicitly synthetic, using observed event schemas. Future real trace reconciliation still requires the full retry bodies; index entries alone are insufficient.

## Validation and use

Fifty offline checks pass, plus direct assertions over the archived47/43 accounting evidence. The suite reruns the original archived16 verifier unchanged against temporary copies. Tests retain the original matrix and add the reviewer's four counterexamples, provider/model contradictions, missing versus unknown provider, fresh-ID retries, model-call accounting, incomplete/interleaved chains, unrelated same-prompt calls, missing suffix without cancellation, and cancellation with wrong identity.

```sh
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python research/ecom1/2026-10-23-sku-lexical-results/test_validator_v2.py
python3 research/ecom1/2026-10-23-sku-lexical-results/validate_trace_v2.py \
  --trace /absolute/path/to/trial-trace.ndjson \
  --summary /absolute/path/to/summary.json \
  --output /absolute/path/to/trace-audit-v2.json
```

Input summary/receipt requirements and the manual rubric remain those documented for v1. `reconciled` means structural evidence reconciliation, never semantic correctness or task success. Billing completeness is separate. Missing per-attempt cost, including an unpriced 429, is never assigned zero. All 68 cells remain; truncated/missing traces stay incomplete, and unattempted cells require valid cancellation evidence and an intact trace/stdout prefix. No follow-up model calls, model actions, Brain writes, or automatic replacement jobs occur.

The v2 files are separately sealed after testing; they do not replace the original seal. Independent v2 re-review has been requested.
