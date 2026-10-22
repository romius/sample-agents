# Independent prepared-diagnostic review

23 October 2026. Reviewer: integration_plan. **PASS for the reviewed offline artifact and design; no remaining blocking finding.** This does not submit the diagnostic, authorize a follow-on run, establish real trace availability, or claim a model/benchmark improvement.

## Seal and independent reproduction

Verified all **44 entries** in the original SHA256SUMS, whose SHA-256 is `88a550900235f1775e75924477791b0273d09441e9fc51041ab8723e573403a4`. Verified all **28 frozen input copies** byte-for-byte against their pinned upstream provenance, including the independently reviewed Tree-depth and AGENTS-root corrections. No original sealed file was modified by this review.

Copied the artifact to a fresh temporary directory, imported the sealed build/verifier with only their output directory redirected there, and ran the build against its pinned original source dependencies. The rebuilt packed source, readable source, fixtures, call plan, blank manual review sheet, and manifest were all **byte-for-byte equal** to the six sealed originals. Then ran the sealed verifier on that temporary rebuild. All **40 executions** passed; the full verification report equals the sealed report after excluding timing fields. Rechecked the original 44 hashes afterwards.

Environment: Python 3.14.3, pydantic-monty 1.2.0, offline cached uv environment, `PYTHONDONTWRITEBYTECODE=1`. Native execution used ten-second feed/turn limits and 1,000 suspensions. Temporary reproduction directory: `/var/folders/px/h2tbfkd177v7w8r4xg5h7ycw0000gn/T/sku-independent-diagnostic-cb5muwac`. No model, ECOM, network, or Brain operation was performed.

## Calls, pairing and resource bounds

The plan retains every one of the 17 cases and has exactly two C and two L calls per case, 68 logical calls total. The second repeat reverses each pair's arm order. Each executed request equals its frozen arm and canonical request hash, with the captured model, 2,048 completion-token maximum, medium reasoning and temperature zero. The runner adds no retries. Provider retries are explicitly separate transport attempts; 68 is not asserted as their upper bound.

C equals the actual captured SDK request. L removes only the two sibling lexical arrays after row selection and capping; reinsertion restores C. Both full histories retain the same evidence, settings, original lexical ranking, policy and guidance. The U4 glossary is actually read and shared; F2 preserves the real 32 indexed / 16 eligible / 10 visible records. Hidden supporting N15/O15 are not model-visible oracle facts. Compact requests are 13,588–20,982 bytes; maximum ordinary JSON request size is 21,031 bytes. The packed artifact is 28,738 bytes, below the 65,536-byte source limit.

The runner references only `bitgn.llm` and one terminal `bitgn.answer`. It does not fetch usage, call task/runtime APIs, parse or repair model actions, execute tool requests, or score responses. The carrier Answer states that the task was not attempted. Carrier grade is excluded from research outcomes.

## Stdout, failures and cancellation

The reviewed runner prints fixed request metadata and capped ID/finish/error strings only. It never dumps raw content, reasoning, responses, usage or full errors. The tests cover malformed response shapes, hypothetical destructive tool requests that must not execute, individual/all-call provider failures, huge content/reasoning/usage, astral-Unicode IDs and finish reasons, oversized Unicode errors, and a cancellation token after 20,000 Unicode characters.

All four source/runtime forms reproduce the same metadata. The largest observed complete output is **60,216 UTF-8 bytes**, below 65,536. I additionally calculated a conservative mixed-status bound directly from all 68 frozen steps: choose the largest separately possible response/error/cancelled record for every ordinal, use 12-byte JSON escaping per astral character, and allow an overlarge two-digit response/error end count. This yields **60,217 bytes**, leaving **5,319 bytes** below the source stdout limit. This bound concerns the diagnostic's prints under ordinary JSON-decoded SDK values, not unrelated platform logs.

Simulated cancellation on calls 1, 34 and 68 stops later calls, rethrows, and omits the end marker and carrier Answer. The same holds when the cancellation word lies beyond the printed preview. Non-cancellation provider errors remain in their planned positions and do not trigger custom retries. These tests establish the runner's exception behavior, not the platform's transport cancellation machinery; a host cancellation outside this Python exception path may leave only the preceding request marker.

## Semantic assessment and trace recovery

The fixed manual rubric correctly separates property support, unresolved qualifiers, contradictions, unjustified uniqueness, exact-ID conflicts, positive controls, justified deferred lookups, malformed final content and provider failures. A clarification outcome alone cannot count as correctness. All planned rows remain, including errors and unattempted post-cancel entries; there is no automatic success tally or selection of a favorable repeat.

The stdout prefixes are explicitly insufficient for semantic assessment: truncated IDs are not unique keys and previews are not raw evidence. TRACE-READOUT requires immutable full request/response/error events, reported usage, source/job/trial identity, exact plan reconciliation and separate provider-attempt accounting. If those events are missing, the required outcome is incomplete evidence, without reconstructing text or launching a replacement run automatically. This recovery plan is appropriate, but no local fake-host test can establish that a future service run will retain/reveal all events. Actual trace reconciliation is a mandatory later check before causal or semantic interpretation.

Results would describe this immediate next-action boundary only. L still contains lexical scores/order and guidance, and is shorter; any difference cannot isolate label semantics from attention/length. Scripted upstream routing, incomplete coverage metadata and synthetic worlds limit transfer to production. No task-completion, full100, promotion or score-gain claim follows from this review.

## Reviewed pins

| Artifact | SHA-256 |
| --- | --- |
| agent.py, 28,738 bytes | `dc5e1951f404dca549fe97a6fd38de36419ece9ecd0c3aa07d4f6369998bda3e` |
| readable.py | `52c33ff84e7f1dfb59a83d5c80af787688518530640262b34a15f02fa3cf79e7` |
| fixtures.json | `c2dd7b4f5917d6118351becaa7d9aeee7cd2c7d510cb1c5eb5076bb202b57571` |
| call-plan.json | `89550772dc28c05a1f73d06d5c09d325e7c78de5fb7e89fd5d2c7c1490ff97a5` |
| runner.py | `1967934b4c116cc3e93df7f915345a568776d6a3cb8d591f91e822d52e89df52` |
| build.py | `7367f07833484519705397e1b0a8a0e3e4c666134aa5f51920a704b86ad7d4a1` |
| verify.py | `661e866dbb77d1c4bce69d076b851c9eb9700d2b0402af97c45407af595203b5` |
| PREREGISTRATION.md | `40a05874b42ab4d2f603365349daac7b209f4371e7726b5f4bcd93427cb9c16a` |
| TRACE-READOUT.md | `7210b6fe66614def11b9b5f45b9bf050b65404f685cee2f36e01bccbe1e1fe42` |

This review file is a new artifact outside the original 44-file seal; it does not alter that seal.
