# Local preparation validation

23 October 2026. **NOT SUBMITTED.** No real model call, Brain operation or ECOM action occurred. No new benchmark result or score is claimed.

Final runtime inputs were frozen after integration_plan independently reran all 68 capture executions and verified Tree depth plus the disclosed AGENTS catalogue-root correction. The reviewed capture pins are `23b0ad73a34376be0dae1908a062eb26aefab214231c1c7300e5e876ad10e5bb` (capture source), `a770f30a8c502bab0f36bd561fa6d3d9b859521367dc22a32528da8c114c223e` (capture results), and `88b79794912d5f8ad3bade09574d61589f7febab20c1b76c7d8af79d669d0ea1` (capture dependencies). The snapshot operation checked all 11 capture dependencies and 22 artifact pins, copied 28 files byte-for-byte, and checked that the upstream files had not changed while copying. Copies and the final independent review live in `inputs/`; `DEPENDENCIES.json` records every path/hash. Later capture changes do not silently change this diagnostic.

The build confirms all 17 requests match actual captured positional SDK arguments and keyword settings. Exactly 104 lexical fields are removed across 17 C/L pairs; reinsertion restores C. Both arms retain identical rows and all other messages/settings. U4's glossary is present exactly once in an actual shared policy-read observation. F2 is checked as 32 indexed / 16 eligible / 10 shown, truncated, with Nera-only initial matches and neither tail SKU shown.

| Generated artifact | Value |
|---|---|
| Packed source size | 28,738 bytes, below 65,536 |
| Packed SHA-256 | `dc5e1951f404dca549fe97a6fd38de36419ece9ecd0c3aa07d4f6369998bda3e` |
| Readable size | 543,012 bytes; packaging input, not the submitted source |
| Readable SHA-256 | `52c33ff84e7f1dfb59a83d5c80af787688518530640262b34a15f02fa3cf79e7` |
| Fixtures SHA-256 | `c2dd7b4f5917d6118351becaa7d9aeee7cd2c7d510cb1c5eb5076bb202b57571` |
| 68-call plan SHA-256 | `89550772dc28c05a1f73d06d5c09d325e7c78de5fb7e89fd5d2c7c1490ff97a5` |

`verification.json` records **40 fake-host executions**: readable/packed × CPython/native × ten scenarios. All passed exact request/order/hash assertions, bounded metadata checks, and output parity. Scenarios are success; call-3 timeout; every-call timeout; raw/malformed response shapes; cancellation on calls 1/34/68; huge content/reasoning/usage with maximal Unicode ID/finish metadata; oversized Unicode errors; and a cancellation token after 20,000 Unicode characters. Exceptions are logged as status plus a bounded preview without custom retry; cancellation emits its bounded status and rethrows before subsequent calls, the end marker and carrier Answer.

**Community d6210 changed the logging design before submission.** The earlier raw-response runner overflowed stdout in that separate community experiment. This artifact now never prints raw model replies, reasoning, content, usage objects or full errors. Normal 68-call stdout is **21,456 bytes**. Maximal Unicode metadata produces **60,216 bytes**, below the 65,536-byte cap; oversized Unicode error logs are **48,656 bytes**. Every execution checks total UTF-8 stdout. Hypothetical model tool actions never execute. The runner AST references only llm and answer; usage() is never called. Full raw responses/errors and cost evidence must be harvested from immutable inference trace events, then linked by ordinal/request hash and any untruncated trace identifiers. See `TRACE-READOUT.md`.

All individual paired requests are below the input cap: compact JSON ranges **13,588–20,982 bytes** and default JSON reaches at most **21,031 bytes**. Exact fixtures and the 68-call plan were unchanged by the stdout repair.

Native validation used pydantic-monty 1.2.0, ten-second feed/turn limits and 1,000 suspensions. These timings measure offline codec/harness execution, not provider latency. Fake-host calls and fake usage fields embedded in adversarial responses are test data, not model or billing records. Simulated cancellation proves the runner branch, not the external SDK's platform cancellation mechanism. The source under examination remains unchanged d5785r1/d5789r1; this diagnostic does not run it against the carrier task.

`PREREGISTRATION.md` and the blank `manual-review-sheet.json` define the assessment separately from the runner. They distinguish visible supported facts, unresolved qualifiers, contradictions, immediate final decisions, justified deferred lookups, malformed outputs and errors. No classifier turns an outcome token into semantic correctness. The root agent must review the prepared artifact before deciding any publication or evaluation.
