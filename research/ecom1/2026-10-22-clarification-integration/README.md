# Receipt header and clarification display integration

Romius, 22 October 2026. Strongest verified baseline: **inara d3200r2, 90.12601/100**, refreshed at 19:23 UTC. Our d3512r1 scored82.69149. `agent/BASELINE.md` already matches Brain d7r28. See the sibling record-integration/INTEGRATION-PLAN.md and TASK-REVIEW.md for the complete component plan and all200 reviewed tasks.

## Exact lineage and hypothesis

Verified d3200r2/d3201r2 → reconstructed codex donor d4354r1 → our frozen d4702r1 (63209 bytes, pending full100) → offline header component d4848r1 → this candidate. The pending integrations are code parents, not stronger verified baselines. This experiment does not depend on their eventual scores.

Two additional changes are supported independently:

1. Accept a standalone damaged receipt quantity heading such as `Item t Unit Total`, while preserving original-first quantity parsing, arithmetic and SKU/price checks. Bobcat's archived d4807r1 receipt is recovered; the broader `UNIT TOTAL` substring alternative incorrectly accepts `Review unit total`. Header-only source d4848r1 and all14 native counterexamples are saved in the sibling receipt-header-review folder.
2. When an existing clarification cites at least two actual indexed products, display their missing SKU values. Preserve the original message, outcome and references. Use actual SKU fields and paths, including anchored references; do not infer SKU values from filenames. Exact record t021 establishes ambiguous kits and missing candidate text. Adaptation credits thingy's d4485r1 R2. The contradictory-qualifier filter d4545r3 is deliberately excluded; it selects the wrong “standard head” product and is sensitive to qualifier order.

No provider, model, reasoning-effort or input-generation change is introduced. No task-ID branches or known-answer constants are present. t041's incorrect OK remains open. Showing candidate SKUs addresses text completeness, not semantic disambiguation.

## Inherit, preserve and defer

Inherit the record's crosslist export, receipt availability/SKU-price matching, injection gate, Delete-404 containment, staff count, fractional discounts, product existence and3DS exactly once. Preserve d4702's tested policy-aware stock evidence, original-first quantity OCR, narrow missing-executable Exec404 branch and bounded inference retries at four sites. The separate cleanup shortcut remains inactive because a two-file counterexample falsely reports success after a partial Delete failure. The broad union of injection guards remains excluded because benign HTML/quoted-role cases expose false positives. The inherited record guard still has those known limitations.

The Exec404 path requires404, `not_found`, and the missing runtime-tool message; generic404 and other errors propagate. The retry helper uses at most3 inference attempts, preserves options, excludes HTTP4xx/429 and propagates exhausted/unknown errors. No runtime mutation is retried. This adds potential cost when provider outcomes are unknown.

## Reproducibility and evidence

Packed source: **63582/65536 bytes**,1954 spare; SHA256 `2f145f03558a944c30398ec59aabb92ea7d891e05889b1a8f348d07d11cbfb20`. `build.py` pins the exact parent hash and checks decoded packed/readable AST equality. Readable source is retained. Packer d3268r2 and all parent artifacts are preserved in sibling folders and the Git archive. `dependencies.json` and `SHA256SUMS` pin the inputs.

Validation:14 native display controls, two exact-world completion-action replays,27 advisory archived-world comparisons,408 parser controls and20 receipt-handler cases. The27 replay outcomes, references, runtime calls, inference counts and existing fidelity gaps are unchanged; none activate the new display helper. Separate t021 action replay activates it and includes both SKUs; t041 is unchanged. Whole-agent recovery tests additionally exercise the exact packed candidate in native Monty, readable CPython and packed CPython. Results are saved, not inferred from a static source scan.

Archived replays do not regrade the hidden oracle, regenerate model actions or fully reproduce provider requests. Seven existing replay worlds lack some requested Read responses. Only seven instruction strings matched across our prior two runs, and even those may have different worlds. The older run used Cerebras; d3512r1 and the record used DeepInfra. Task IDs alone cannot establish a causal gain. A higher live score would be an official record, not proof that every added component helped.

## Evaluation and promotion

Before submitting, refresh instructions, latest record and queue. The overnight authorization permits at most2 of our full100s outstanding and one new full100 per30minute cycle. d4702's run stays immutable. This source tests the two independently justified additions without assuming its parent's unfinished outcome. No short paid evaluation is necessary to retest the already exercised parser/display mechanisms; the first20 tasks would not include the exact t021 case.

Promote only a completed100 official run_score strictly above the latest record, using the exact tested bytes. Immediately update shared agent/agent.py, BASELINE, README and Integrate together, preserving costs, failures, regressions and causal limitations. Ties/lower/partial results do not replace the record. Continue research after either result.
