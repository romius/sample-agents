# Prepared receipt first-action diagnostic runner

Local preparation only: **not submitted, no live model calls, no Brain writes**. This runner implements the internally reviewed fixed20-call plan copied under `inputs/plan/`. It is not an ECOM task-solving agent or a promotion candidate. The carrier task is explicitly unattempted and its grade is irrelevant. Separate dispatch review and authorization remain required.

The original plan seal remains `df20578d1daa74a886ea00d87603d3d06d2ff641aa3bfe9ab13a3f5ded0d25c0`; exact call-plan hash is `6bf14797b4b0f76f56ceb2526a764d533747a2944a847b8dcfa7287c2302429b`. All23 sealed plan files and the seal itself are copied byte-for-byte. The original sibling plan and source/capture packages are unchanged. This artifact contains no repeat of the completed C/L diagnostic: its prior bounded runner is retained only as implementation provenance.

Five fixtures, two arm labels, and two counterbalanced repeats produce20 logical calls in the exact frozen order. A023/A063 are current d4353-generated parent/context requests on historical d4702 observed receipt worlds; B023/U063 are declared benign/hostile upload overlays; V063 is an equal-input request-level noise control. No model output enters another request. The first-action rubric and interpretation limits remain in the original PLAN.md; the runner does not implement a semantic scorer.

Each call passes exactly the frozen positional model/messages and kwargs: `openai/gpt-oss-120b`, `max_completion_tokens=2048`, `reasoning={"effort":"medium"}`, `temperature=0`. The archived SDK0.3.7 guide and fresh03:09 receipt both pin DeepInfra BF16 and forbids provider overrides; none is supplied. Future immutable request events must verify the actual route, quantization, alias, settings and complete request contents. Argument-object default-JSON estimates peak at19,709bytes; private wire encoding and real-provider acceptance remain unverified. Successful future dispatch would establish acceptance only for those concrete requests.

## Runtime behavior

`runner.py` contains the reviewable runtime loop. `build.py` embeds the exact plan/request objects into `readable.py` and uses the pinned self-contained public LZ packer to produce `agent.py`. Packed source is23,837bytes, SHA256 `4237825f66d2215a805d6ddd1823b9bf0e803798ce34b63aeb3b60696673626f`, below65,536bytes. The readable source is intentionally larger and is an offline inspection/test form. Only packed `agent.py` is eligible for any later submitted source-size review. Build asserts both allowed BitGN references are **direct calls**, avoiding method-value extraction across the real native proxy boundary.

The only runtime capabilities are `bitgn.llm` and one terminal `bitgn.answer`. There are no ECOM reads, writes, deletes, Exec calls, task inspection or usage calls. Returned content is not parsed, repaired, scored or executed. Null, malformed and truncated returned values occupy their original cell and processing continues. `status=returned` means a host call returned a value; it is never a semantic success label.

On **any inference exception**, bounded error and stop metadata are printed, and the original exception is rethrown. No guest retry or replacement call follows. Root explicitly approved this conservative policy after plan review: it avoids all undocumented cancellation-message heuristics and may produce a partial diagnostic even for a recoverable error. A negated cancellation phrase is not classified as cancellation; it is simply an exception and stops like every other exception. Fake cancellation tests establish only local stopping behavior. Actual platform cancellation enforcement and formatter remain external facts.

The SDK may perform its own eligible429 retries inside one logical call. This runner neither adds retries nor emulates/disables that host behavior. Twenty is the planned logical-call count, not a provider-attempt or billing quota. Preserve distinct transport IDs and retry events. No source-local retry or follow-on run is authorized by this artifact.

## Bounded output and trace recovery

Output contains only `RECEIPT_BEGIN`, `RECEIPT_REQUEST`, `RECEIPT_RESULT`, `RECEIPT_STOP`, and `RECEIPT_END` records. Request markers contain ordinal, fixture, arm, repeat and full canonical request hash. Returned-result records contain ordinal, status, a32-character response-ID preview and16-character finish-reason preview; an error record contains a32-character error preview. All values are JSON-escaped. Raw content, reasoning, complete errors and usage objects never enter stdout.

The analytically enumerated maximum program stdout is **17,292bytes**, verified by adversarial tests, leaving48,244bytes below65,536. This bound includes every possible exception position and worst-case12-byte JSON escaping per preview character. It bounds the program's print output, not host-owned traceback/error-event storage. The2MiB fake maximum-response test concerns JSON response bytes, not an assertion about the private provider wire representation.

Recover raw responses/errors and billing from immutable trace events, not stdout previews. Match planned ordinal and canonical request to full trace call IDs, model/provider settings and complete event order. Repeated prompts and response-ID prefixes are not unique keys. `RECEIPT_REQUEST` precedes the host call and does not prove dispatch occurred; a native permission-boundary regression explicitly tests this. `RECEIPT_END` precedes carrier Answer and does not prove that Answer was accepted; another boundary regression covers that case. Reconcile actual Answer acknowledgement and trial end separately.

Retain all20 planned rows. Complete stop/terminal evidence can establish that a suffix was unattempted; absent or truncated events alone mean missing/unknown. An error on the last call still raises and does not emit a carrier Answer. A carrier Answer failure after20 returned calls is a separate failure with all model evidence retained; it is never retried. Full durable cost/token accounting, SDK429 transport attempts and pending/unknown charges must be reconciled against official results. No dollar cost or benchmark gain is asserted.

## Offline checks and reproduction

Use Python3.14.3 with pydantic-monty1.2.0 (already installed in the research runtime). `DEPENDENCIES.json` pins29 copied input files, including the full sealed plan snapshot, archived SDK guide plus the fresh03:09 guidance receipt, public packer, prior logging implementation and public Monty `ClassInstance` source. The copied native source documents the method-only boundary; tests run the installed package. Plan-preparation scripts are preserved provenance, not rerun by this runner build; complete original-world replay remains reproducible through the sibling plan package and its separately pinned upstream dependencies.

Run from any directory:

```
python research/ecom1/2026-10-23-d4353-receipt-handoff/diagnostic-runner/build.py
python research/ecom1/2026-10-23-d4353-receipt-handoff/diagnostic-runner/test_runner.py
python research/ecom1/2026-10-23-d4353-receipt-handoff/diagnostic-runner/reproduce.py
```

`test_runner.py` runs68 complete executions across readable/packed source and CPython/native Monty. Native tests use public method-only `ClassInstance`,10-second feed/turn limits and1000 suspensions; no guest mock SDK is used. Tests check every entered request against the independently reconstructed frozen order and exact original SDK object/hash. They cover normal returned replies, malformed/null/multiple-action/tool-call shapes, maximal2MiB response bodies, long Unicode/log-forging metadata, timeout/503/400/429/unknown/empty errors, simulated cancellation at first/middle/last calls, a long malicious error with cancellation text beyond the preview, negated cancellation wording, nineteen maximal responses followed by a maximal-output exception/stop at ordinal20, and carrier Answer failure. Two additional native permission controls prove request markers and END markers are not dispatch/acceptance evidence. All model-proposed actions remain inert and no usage hook is touched.

`reproduce.py` copies the self-contained runner package to a fresh temporary directory, verifies its input pins, rebuilds, reruns tests and compares all original files byte-for-byte except its own reproduction report and self-referential seal. It also tests input tampering in an isolated copy: changed request content and changed plan order must fail before a runner can be rebuilt. No upstream directory is writable or required during these checks. The interpreter/package remain runtime prerequisites, not bundled binaries.

No actual provider response, first-action improvement, final-answer correctness, security generalization, task-score result, paid submission, or promotion is established by these tests. Full trace-readout and independent manual first-action review are still future work after an authorized dispatch.
