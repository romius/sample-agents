# Independent review: inference retry ownership comparison

**Disposition: PASS for the bounded offline comparison. Neither candidate is selected automatically, submitted, combined with OCR, or established as a full100 score improvement.** Reviewed exact d3909r1 parent and both alternatives. The SDK-only variant loses legitimate second-invocation recovery; the single guest owner preserves the tested recovery while limiting repeated calls for a single inference request. Real cost, provider error-format coverage and benchmark effects remain unmeasured.

## Frozen bytes and reproduction

The author seal contains 34 files: `SHA256SUMS` SHA256 `c33ca9387be7ec2cf0d9fc4d400ba8e747396e33c0ec7a7746967d0fb106815c`. All entries and 14 separately pinned dependencies verify. The exact record parent is 62,475 bytes, SHA256 `56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c`; its readable and original packing source are pinned in the closure.

| Source | Packed bytes | SHA256 | Headroom under 65,536 bytes |
| --- | ---: | --- | ---: |
| SDK-only terminal guard | 63,107 | `f97714ccf8ab8de4acab2b21e5545b40be589fb90711aae1948888a60b54df60` | 2,429 |
| Single guest owner | 63,514 | `513cbdd7b856ebd21149b9d91c58220031668a174fbab0ea1f0c1ddd0952a20d` | 2,022 |

`independent/reproduce.py` copies the sources and dependency closure to an isolated temporary directory, verifies dependency hashes, rebuilds, and runs `test_native.py`, `test_guest.py`, and `test_helper_whole.py` using Python 3.14.3 and native Monty 1.2.0. I ran it successfully. All 11 source/build artifacts reproduce exactly; six test reports/request/fixture files reproduce byte for byte. The script confirms the author's input files remain unchanged. Results are recorded in `independent/reproduction.json`.

This independently reran **194 whole-agent executions**: 84 parent/SDK-only, 86 guest-owner, and 24 helper-path executions. It also reran 28 native classifier and 10 isolated nested-helper controls. These counts are execution coverage, not independent tasks or semantic passes. Public methods-only ClassInstance, 10-second feed/turn limits and 1,000 suspensions are used; no live SDK backend, inference provider, Brain mutation or paid call was executed.

## Exact change and path coverage

Only three pre-existing function ASTs change: `route_policy_docs`, `i2c_llm_narrow`, and `i2c_dispatch`. The SDK-only version adds `inference_cancelled`; the guest variant additionally adds `inference_retryable` and `inference_call`. No pre-existing function is removed. The remaining changes are explicit top-level cancellation propagation, main inference-failure termination, suppression of the subsequent forced call following that failure, and its final error message. The guest variant replaces all four direct inference callsites with one helper; its only remaining `bitgn.llm` call is inside that helper.

The exact `dispatch` and `recoverable_lookup_error` source segments/ASTs remain unchanged. The separate broad Exec404 recovery issue is preserved, not silently repaired here. The ready OCR parser change is absent. This remains a retry-only mechanism comparison against exact d3909.

Router, actual helper, main and forced-report inference paths are exercised. The helper whole-agent fixture overlays an explicitly synthetic task, catalogue policy and router response onto archived catalogue/Tree data; no source function is replaced. Its successful `{}` helper response proves recovered inference followed by the existing fallback, not correct constraint extraction or task success. Isolated AST helper tests are reported separately and are not substituted for whole-agent reachability.

The main-path positive control is material: a first 503 followed by a valid second reply recovers under the record and guest owner; SDK-only stops after the first error. Persistent recognized main failures produce three record main attempts plus a forced call, one SDK-only call, or three guest calls with no forced call. Unknown errors, 400 and exhausted 429 receive one guest invocation under either candidate. Mixed 503→400 and timeout→unknown stop at the terminal error. Malformed/length correction behavior remains separate; reaching forced reporting through those paths is retained. Forced 503 recovery and timeout exhaustion, as well as forced 400/429/unknown and cancellation, are explicitly exercised.

Repeated guest requests preserve exact model, messages and settings. The wrapper only covers inference; Write, Delete404 and mutating Exec503 controls execute the mutation once. A successful Write preceding later failed inference also stays single. This establishes non-replay in the tested source paths; it does not establish external transactional semantics for all possible actions.

## Cancellation and fresh counterexample

Wrapped/unwrapped OpenRouter HTTP503 cancellation, JSON error-message cancellation, ordinary cancellation forms and cancellation overlapping connection text propagate without a second inference call in the candidates. Negated `request was not cancelled` and benign `invalid cancellation_policy` retain their appropriate transient or terminal behavior. Committed real SDK cancellation itself prevents later host calls according to the pinned guide; a fake host that allows calls after a synthetic cancellation exception does not demonstrate a reachable real post-cancellation mutation or paid-call bug.

My additional `check-classifier.py` runs 10 fresh syntax controls plus raw/wrapped strings from all four actual timeout receipts under CPython and native Monty. The first review found that `OpenRouter HTTP 503: [broken` and a synthetic JSON array containing generation fields were retried because the original parser checked only `{` bodies. The author conservatively changed the predicate to inspect both object/array-shaped bodies and require a dictionary. The final source rejects both controls; CPython/native outputs agree. Initial observations and the original retry fragment remain preserved in `initial-classifier-observations.json` and `initial-guest-retry.py`; final observations are in `classifier-observations.json`.

These array envelopes are synthetic boundary cases, not observed provider events. The correction supports the documented rejection boundary; it does not establish that an actual paid failure was reachable. Cancellation/error classification remains deliberately bounded string parsing, not a complete semantic or provider error contract.

## Accounting and remaining limitations

The four actual timeout receipts t003/t045/t056/t059 independently pin the same `TimeoutError: The read operation timed out` form. Each actual agent error confirms the unconfirmed-outcome/cost wrapper. They are four occurrences of one form, not four distinct error grammars. Retrying an unconfirmed timeout can incur additional generation/cost; these receipts do not show that retry is free or successful.

The pinned SDK guide states qualifying 429 rejections have at most five internal attempts and 60 seconds total waiting per `llm` invocation. The fake host demonstrates invocation arithmetic only. Persistent exhausted 429 can compose the record's three main calls plus forced call into 20 hypothetical HTTP attempts, versus one candidate invocation and up to five. Mixed 429 retries ending in 503 can compose three guest invocations into 15 HTTP attempts for that one logical request. Router/helper fallbacks and later prompts are separate logical requests. None of these figures is a global trial quota, observed candidate physical-attempt count, or cost guarantee. Actual 47-transport/43-logical evidence from the separately reviewed expanded-pairs validator is not silently treated as an execution of these candidates or included in this package's 14-dependency closure.

One preserved output limitation is visible in the reproduced forced-error controls: after three malformed main replies followed by forced timeout/400/429/unknown failure, the terminal answer still says the sample reached its “30-step limit.” That explanation is inaccurate for those controls. Main inference-failure wording is corrected, but forced-branch wording is inherited. This does not invalidate the retry-count and mutation assertions and is not silently counted as a fixed reporting behavior.

There is no guest backoff and no demonstrated live provider recovery or score effect. A structured host retry/cancellation contract and shared physical-attempt budget would be stronger than this string classifier. The comparison is reviewable and reproducible; choosing an alternative or integrating it with OCR requires a separate explicit integration/evaluation decision.
