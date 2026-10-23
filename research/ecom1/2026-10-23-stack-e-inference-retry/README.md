# STACK E inference retry ownership: bounded offline comparison

This experiment is based only on exact **d3909r1**, packed SHA-256 `56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c`, readable SHA-256 `d6ae7201e116520be92f1e81f83a15644a167eb4003c32c0026f905d27d884eb`. Neither the live agent nor the separate OCR repair is modified. No hosted job, paid inference, Brain publication or Git operation was performed.

**Hypothesis:** one guest inference retry function can preserve recovery from recognized transport failures while removing the record's overlapping broad main-loop retry and subsequent forced inference. The SDK should continue to own qualifying 429 retries. This is a mechanism experiment, not a score improvement claim or a dispatch recommendation.

## Exact paths and two comparisons

The record has four direct inference callsites: policy router, `i2c_llm_narrow`, main action loop, and forced report. The router and constraint helper catch inference exceptions and fall back. The constraint helper also sits below `i2c_dispatch` and a top-level dispatch catch. The main loop retries every caught exception through `invalid_steps`, up to three attempts starting from zero, then issues a separate forced-report request. Its final catch can consume cancellation and attempt an internal-error answer. Prior malformed or length-truncated replies share that record counter, so three is an upper count, not a universal count.

Two separate candidates are retained:

- **SDK-only comparison**, `readable.py` / `agent.py`: removes the main exception retry and forced inference following that failure, propagates recognized cancellation through all relevant catches, preserves ordinary router/helper fallback, and reports the inference failure accurately. It intentionally adds no guest transient recovery.
- **Bounded guest owner**, `guest-owned/readable.py` / `agent.py`: starts from that comparison and routes all four inference sites through `inference_call`. Only this helper performs guest retries, at most three identical invocations. It excludes 429, 400, other unrecognized statuses, unknown text and recognized cancellation. Main exhaustion cannot re-enter the broad retry loop or the forced-report inference.

The guest owner recognizes explicit TimeoutError/connection-exception prefixes, including the observed SDK `Inference outcome/cost unconfirmed: TimeoutError: ...` wrapper, and anchored HTTP 502/503/504 messages. Object-shaped HTTP JSON bodies containing any `id`, `choices` or `usage` key are excluded. Malformed object/array-shaped JSON and all array-shaped bodies are also excluded. Independent review caught the initial array-envelope omission; no actual array-shaped provider error was observed. This is a bounded error-text classifier, not proof that the first request was free or had no generation. **Timeout/connection cost remains unknown** until actual traces establish it; a repeated inference can incur additional cost. World actions are never wrapped or replayed by this helper.

Cancellation checks use explicit leading forms and known exception wrappers, not a search for any occurrence of “cancel”. The initial broad keyword version falsely aborted ordinary router fallback for `HTTP 503 request was not cancelled; upstream unavailable`; that counterexample and original candidate are preserved under `initial-keyword-candidate/`. The final detector passes it and `invalid cancellation_policy`. Parent review additionally identified `OpenRouter HTTP 503: request cancelled`, its unconfirmed-cost wrapper and `error.message` JSON cancellation as bypasses of the intermediate prefix matcher. The final shared detector normalizes these envelopes and all three have whole-agent controls; negated JSON messages remain eligible for recognized transient recovery. The actual SDK cancellation formatter was not observed in local receipts, so coverage is limited to the tested forms. SDK documentation independently says real committed cancellation blocks subsequent host calls even if guest code catches its error; the parent's synthetic post-cancellation calls therefore do **not** prove that real paid requests or mutations can occur after cancellation.

## Results

Native public Monty 1.2.0 `ClassInstance` exposes only `task`, `call`, `answer`, `llm`, `usage`, with default lazy attributes disabled. Exact whole packed and readable sources execute against archived t076 RPCs plus explicitly fake inference/mutation boundaries. The original noisy OCR declines deterministic handling and reaches the actual general loop. No source functions are replaced in whole-agent execution.

**194 whole-agent executions passed:** 84 parent/SDK-only comparisons across 21 scenarios, 86 bounded-owner executions across 43 scenarios, and 24 helper-path executions across three versions, two forms and four error scenarios. Packed/readable requests, actions and answers agree. Ten additional isolated nested-helper controls and 28 native classifier cases passed. These isolated controls are labelled separately from whole-agent reachability. The 24 whole-helper executions use the explicitly recorded synthetic task/catalogue-policy/router overlay over archived catalogue files and Tree responses; no agent function is replaced. A successful `{}` helper reply proves recovery into the existing fallback, not correct constraint extraction or task resolution.

| Scenario after successful router | Record | SDK-only | Bounded guest owner |
| --- | --- | --- | --- |
| One 503, then a valid reply | 2 main attempts, recovery | 1, internal error | 2, recovery |
| Persistent recognized 503/timeout | 3 main + 1 forced | 1 main | 3 main, no forced |
| 400, unknown error, exhausted 429 | 3 main + 1 forced | 1 main | 1 main |
| Recognized cancellation | 3 main + 1 forced in non-cancelling fake host | 1 then propagate | 1 then propagate |
| Write followed by persistent 503 | write once; 3 later main + forced | write once; 1 later main | write once; 3 later main, no forced |

All four archived provider-control timeout receipts (t003/t045/t056/t059) contain the same TimeoutError string, and each complete agent_error confirms the exact unconfirmed-cost wrapper. These are four observations of one error form, not four distinct formats. The guest owner also recovers after one observed-form timeout, one connection reset, one 502, and two 504 failures. Mixed 503→400 and timeout→unknown sequences stop immediately at the terminal error. Main retry requests retain the exact model/messages/settings. Malformed JSON and length-stop correction behavior stays separate; forced reporting remains available when the loop ends for those reasons, and its own transient inference uses the same bounded helper.

SDK 0.3.7 retries qualifying 429 rejections internally at most five attempts / 60 seconds waiting, only absent generation IDs, choices and usage. Exhausted 429 is not retried by the guest owner. A declared fake-policy control shows the record can request four separate SDK invocations (three main plus forced), potentially 20 HTTP attempts for that request sequence; either candidate requests one SDK invocation, up to five attempts. **Mixed classes still compose:** if each SDK invocation first consumes four 429 retries and then returns a 503, the bounded guest helper can make three SDK invocations / up to 15 HTTP attempts. The suite explicitly retains this counterexample. “Three attempts” means guest invocations, not a global HTTP, cost or trial quota. No server retry implementation was executed by these fake-policy controls.

Router/helper terminal errors still permit their pre-existing fallback to a different logical prompt; “terminal” means no retry of that inference request. Main terminal/exhausted error suppresses subsequent forced inference. The SDK-only comparison loses legitimate second-request recovery; it is not presumed preferable. The bounded guest candidate better meets the requested recovery objective in these controls, but more calls can cost more and there is no guest sleep/backoff. A host-supported retry budget/error contract would be stronger than parsing strings.

`dispatch` and `recoverable_lookup_error` remain byte-identical AST source segments. Write, Delete404, and mutating Exec503 error controls each invoke the mutation exactly once. The parent's known broad Exec404 recovery is intentionally unchanged; narrowing missing-executable versus missing-record recovery is a **separate** repair. Neither candidate silently incorporates that change.

## Reproduction and scope

```sh
python3 research/ecom1/2026-10-23-stack-e-inference-retry/build.py
python3 research/ecom1/2026-10-23-stack-e-inference-retry/test_native.py
python3 research/ecom1/2026-10-23-stack-e-inference-retry/test_guest.py
python3 research/ecom1/2026-10-23-stack-e-inference-retry/test_helper_whole.py
```

Requires Python 3.14.3 and `pydantic-monty==1.2.0`; no network or model service is used. The unchanged record packing function is copied to `parent-build.py`; the builder extracts only its LZ function and preserves the record decoder. Manifests pin source bytes and confirm packed decoding equals readable source and both candidates fit 65,536 bytes. Exact source, public ClassInstance source, SDK guide, archived timeout and world dependencies are hashed in `DEPENDENCIES.json`. `fake-requests.json` files retain full fake inference histories; test reports retain actions/answers and explicit counterexamples.

The successful record's existing retry behavior is not dismissed: second-request recovery is an explicit positive control. What is supported now is bounded ownership, precise request preservation, cancellation controls and non-replay of mutations. Live error-format coverage, paid cost recovery and score impact remain unmeasured. Independent review is still required before any proposed integration or evaluation.
