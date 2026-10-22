# Independent offline trace-validator review

Reviewer: `integration_plan`, 23 October 2026. This review uses local, archived, and explicitly synthetic evidence only. No Brain calls, inference, production edits, dispatches, or Git operations were performed. This file is outside the original seven-file seal.

## V2 final disposition

**PASS for the bounded offline structural validator, with the evidence limitations below. Use v2 rather than the preserved original.** All identified identity/schema/provider/count contradictions now produce deviations. Actual retry transport-ID semantics have been incorporated, separately from experimental logical ordinals. There is no remaining blocker from this review to using v2 for a future complete trace readout. A new event schema, incomplete transport capture, or different runtime representation still requires review rather than being silently accepted.

I independently verified both seven-file seals, the original 16 dependency pins, and all **64 v2 dependency pins**. I reran the final **50-test** suite in an isolated copy, including its unchanged archived16 verifier and the archived continuation accounting assertions. The generated `test-results-v2.json` is byte-identical to the sealed report. The original files and seal remain unchanged. Final reviewed pins:

| Artifact | SHA-256 |
| --- | --- |
| `validate_trace_v2.py` | `737b19d45ed6dd8af7495a2baab56ae0bfba622989e65d13a4ad75410e875cf2` |
| `test_validator_v2.py` | `3e99617c48b6d3e0dfe877bd5fe3b9d1c34a25998a59f60a1eef7302f1ce0fd0` |
| `test-results-v2.json` | `5d6524239346843f511a4f7d6abc1a94fc6537a0c773c7f8e15d259e50b44a21` |
| `SHA256SUMS-v2` | `96a892ba06e26313952880b36a74c07a38f3708786f1395cfacd85df55cded77` |

The archived continuation establishes **47 distinct transport requests, 43 logical starts, and durable model_calls=47**. It does not provide a complete locally available immutable retry trace: some retry records are indexes. V2 documentation makes this distinction correctly. Positive whole-chain validation remains synthetic, using archived schemas, until the target's complete trace is available.

Beyond the supplied suite, I constructed a four-attempt first logical call, with three rejection/retry pairs, fresh transport IDs 1–4, and the remaining 67 planned calls unchanged. V2 reconciles **68 logical calls and 71 provider attempts**, preserves all four transport IDs for the first row, and keeps billing incomplete because the 429s have no explicit usage. Independently removing the middle retry event, changing its next_attempt, changing the third request's temperature, or changing a retry event's model each produces the appropriate deviation. The existing suite also rejects incomplete/interleaved chains and same-prompt attempts without a legitimate retry transition; a new attempt1 remains a distinct logical call.

Requested provider routing and observed provider evidence are now separate. A present contradictory provider or model is rejected; a missing provider remains explicitly unknown. Missing/mismatched durable call counts block complete accounting. Lifecycle request identities and final trial state are checked. Cancellation plus wrong source/trial identity does not establish unattempted cells. Exact fixture/plan/request comparisons and all-cell retention remain intact.

The validator does not independently authenticate receipts supplied by its caller or download immutable evidence. Future summaries must still be joined to actual job/source/trace receipts as documented. Structural reconciliation, billing completeness, and manual semantic judgment remain distinct. This pass does not establish future availability of complete trace bodies, any real68 output, semantic success, or score improvement.

Final test-copy location: `/var/folders/px/h2tbfkd177v7w8r4xg5h7ycw0000gn/T/sku-validator-v2-independent-uge3_yp5`. No sealed source or test files were edited by this reviewer.

## Original version: historical correction findings

The original validator is a useful structural reconciler but should not yet be described as rejecting every unknown schema or contradictory identity/accounting field. I reproduced all 30 supplied tests in an isolated temporary copy; its `test-results.json` was byte-identical to the sealed report. I also verified all seven sealed files and all 16 dependency hashes. Original validator SHA-256: `2db07cad39e371a6793e5d975779d10735cec4df051d8889eb606afdafbbd2c3`; original test report: `74e0b155bfb1a0c8db0b2cac83db38bcac2986334f12d688100212593db2fa64`.

Starting from `test_validator.synthetic()`, independently applying each mutation below and then calling `audit(events, summary)` returned `reconciled`, `cost_complete=true`, and no problems:

| Mutation | Gap |
| --- | --- |
| Append a correctly enveloped `new_unreviewed_event` | Unknown non-LLM event kinds are silently ignored, despite the stated fail-closed schema policy. |
| Change StartTrial request `arguments.trialId` to `another-trial` | The returned trial and event envelope are checked; the requested trial identity is not. |
| Change `agent_finished.data.state` to `failed`, retaining an answered summary | Contradictory terminal lifecycle evidence is not reconciled. |
| Set trial usage `model_calls=99` for the 68-attempt trace | Cost and token sums match, but a contradictory durable call count is accepted. Retry semantics must be established before choosing the count to compare. |
| Set the first successful response body's `provider` to `Cerebras` | The exact requested DeepInfra route is enforced, but a contradictory observed provider is not checked. The prior archived verifier also checked requested routing only. |

These counterexamples were sent to the author. They do not demonstrate corruption of any actual experiment. They demonstrate missing checks in the original offline utility. The separately versioned correction and final re-review are described above; the original sealed evidence was not replaced.

During that correction the author found a more consequential mismatch with actual retry evidence: SDK 0.3.7 allocates a **new transport `data.call` ID for each retry attempt**. I independently checked the expanded-pairs initial request files: event sequences 12, 15, 18 and 21 have call IDs 4, 5, 6 and 7, with attempt numbers 1, 2, 3 and 4. The original synthetic retry test incorrectly reused one call ID. Consequently passing that test does not establish that v1 can reconcile real retried inference. V2 must separate the planned logical ordinal from all transport IDs and join attempts only through observed retry transitions, request identity and order. This is a required correction, not merely a documentation qualification.

## Checks that already hold

The frozen fixture and call-plan hashes are pinned; each wire request is compared in full after only the documented completion-token alias and exact provider/stream additions. Logical call IDs, attempt identities, request order, and stdout metadata are cross-checked. A missing entire call invalidates reconciliation rather than turning positional alignment into a certified match. Full response/error events remain available for manual review; a malformed JSON answer or length stop is preserved, not counted as semantic success.

I independently joined the alias evidence to the correct archived job and event: source `d2499r1`, SDK 0.3.7, event 564/call 10 has wire `max_tokens=1024`, no `max_completion_tokens`, and canonical event hash `678eed946337c3e603e9072e5a6aea8b4347330b283638019f223c7275221166`. The unchanged original archived16 verifier also reproduces successfully. Its requests already use `max_tokens`, so that reproduction alone is not evidence for the alias.

The explicit 429 test keeps 69 provider attempts separate from 68 logical calls and leaves unpriced rejection usage unknown. Missing terminal events, unobserved retry events, generation evidence before retry, wrong requests, interleaved calls, truncated capture/stdout, and immutable trace hash mismatches all produce deviations. Billing completeness is a separate flag from structural reconciliation; reported totals cannot impute missing per-attempt cost as zero.

Cancellation preserves all 68 planned cells. I additionally removed calls and markers after ordinal 3, removed Answer/END, and marked the summary failed without any cancellation signal: all 65 later cells remained `missing_or_unattempted_unknown`; none became `unattempted_after_cancellation`. A missing in-flight terminal response remains incomplete even when cancellation is explicit. The frozen runner recognizes cancellation through its SDK exception text; this review does not claim a broader semantic cancellation parser.

There are no actual outputs from the queued 68-call experiment in this directory. Neither the synthetic tests nor a future structural `reconciled` result establish semantic correctness, a model win, a full100 score gain, or readiness for baseline promotion.
