# Independent paired-diagnostic review

Reviewed 22 October 2026 by the integration-plan subagent. No source edits, paid calls, jobs or queue changes were made. Packed diagnostic SHA-256: `7901ca19bdd8ec9204199a870738836e8625e2a940f582a0e165e2e989341ddc` (18,592 bytes). SKU candidate under investigation: `b2243fac0096044b1350f55f2955b26ac444094b6c765a399a462c55ddc8b3dd`.

## Verdict

Ready as a bounded next-action diagnostic. No blocking construction or SDK compatibility defect found. It does not execute model-requested tools, solve the carrier task, estimate a full100 score, or qualify any source for promotion. Any carrier grade is irrelevant.

## Checks performed

1. Independently compared each frozen parent request against its source archive event. Both archived cases retain all messages exactly. The only removed transport keys are `stream:false` and the exact pinned provider object. Derived controls change exactly message slots 7 (request), 8 (catalog action) and 9 (catalog observation); all other archived messages and inference parameters remain equal.
2. Removed only the treatment's `sku_lookup_evidence` field and reconstructed its catalog observation. The resulting complete request equals the corresponding parent arm in all four cases. The model sees no preregistered answer criteria: criteria remain outside `request`.
3. Confirmed request-description evidence retains the original request's qualifiers. The actual catalog hook generates the attachment; parent matches, ordering and scores are untouched. The first three attached siblings are the intended DeWalt or Metabo family. All attachments truthfully report truncation and unverified completeness.
4. Independently checked DeWalt catalogue properties: 2AH = `2x2.0Ah batteries and case`, 5AH = `2x5.0Ah batteries and case`, BODY = `body only`. The ambiguous case genuinely shares its case requirement across both kits; the unique-variant control supplies an actual distinguishing battery property. The exact-SKU control names an existing record without a contradictory qualifier.
5. Confirmed exactly 16 planned logical model calls: four cases, two arms, two repeats. Each case uses AB then BA or BA then AB. There is no outcome-driven branching, custom retry, model-requested RPC execution, or call to `bitgn.task`/`bitgn.call`.
6. Verified manifest hashes for `agent.py`, `readable.py` and `fixtures.json`. Full treatment request JSON sizes were 24,145; 24,186; 24,231; and 24,781 bytes, comfortably below the 64 KiB SDK request limit even before considering the very small transport additions.
7. Independently reran all eight verification executions (two source forms × CPython/native Monty × success/simulated provider error), without rewriting verification output files. Passed exact call sequence/requests, 16 result records, error preservation, one final unsupported answer, and no ECOM RPC access. Native checks used 10-second execution/1,000-suspension limits.
8. Read live `brain.sandbox.sdk()` in a read-only session (`s7042`, subsequently discarded). SDK 0.3.7 explicitly accepts `max_tokens` or `max_completion_tokens`, `temperature`, and `reasoning`; supports only `openai/gpt-oss-120b`; and pins `deepinfra/bf16`. Thus the archive's `max_tokens:2048`, medium reasoning and temperature zero are valid. Dropping caller-specified `provider` and `stream` is required by this SDK and preserves the pinned transport behavior.

## Interpretation and operational limits

- The bound is 16 **logical** `bitgn.llm` calls, not necessarily 16 HTTP attempts. SDK 0.3.7 can retry eligible 429 rejections up to five total attempts per call, so the theoretical attempt ceiling is 80. There is no custom retry. Report actual usage, attempts, missing costs and failed calls; the manifest already discloses automatic retries.
- A returned Read/catalog action is a next action, not a completed answer. Do not label a sensible verification read as a failed exact-SKU/unique-variant answer, nor assume it eventually succeeds. Report such continuations separately. Only a returned `report_completion` supports judging its actual message, outcome and refs.
- Truncated or malformed replies and provider errors remain results, not opportunities to silently retry, drop an arm or substitute historical output. The runner records them; postprocessing must retain them.
- Historical prompts belong to the source run. This diagnostic isolates the effect of one observation on those frozen contexts, not the entire current pending agent lineage. Even archived parent reproductions can vary across time/provider execution. The contemporaneous parent arm is the control; the old answer is contextual evidence only.
- Two repeats on four cases are a mechanism screen, not eight independent tasks, a confidence interval, or evidence for an aggregate score gain. Do not tune against these outputs and then present the same cases as independent confirmation.
- All four attachments are truncated beyond the principal family. This is intentional tested behavior, but a result cannot support a global retrieval-completeness claim. Record returned/eligible sibling counts with the output.
- Native fake hosts prove mechanics and source/runtime compatibility. Live SDK documentation establishes supported parameters. Neither proves live inference behavior or future full100 outcomes.
- The `trials:1` / `queue:short` fields are submission metadata, not enforcement inside the runner. Submit one pinned short carrier trial if proceeding; do not use this source for a production full100. Existing full100 jobs should remain untouched.

No further pre-submission source change is requested by this review.
