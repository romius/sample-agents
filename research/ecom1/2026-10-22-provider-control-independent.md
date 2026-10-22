# Independent audit of the provider-control review

23 October 2026. Reviewer: integration_plan. **PASS for the reviewed evidence, qualified conclusions and final reproducible package. No remaining blocking finding.** This review made no paid/model/Brain calls and did not modify the sealed evidence folder or package.

## Results and instruction comparison

Independently checked all 200 result rows and all 200 StartTrial instruction events across the original and control runs. Each run contains exactly t001–t100, without duplicates. Every instruction event's task, run and trial identifiers agree with its result row. Recomputed all instruction hashes and checked both scores, states and immutable trace references in all100-review.json. The 90 reused original instruction events equal their respective pinned local archive events exactly.

The new official score is **0.780781**, against **0.83099496** originally: **−5.021396 points on the 100-point scale**. The control has 74 full-credit, 21 zero and five partial-credit trials. Its partials are t004, t014, t024, t044 and t064, summing to 4.07809275. The individual grade sum is 78.07809275; the official score is 78.0781/100. The review correctly preserves this small aggregation difference and uses official scores for the delta.

Exactly **94 instruction texts differ**. The six equal instructions are t070, t071, t081, t083, t086 and t087; all score one in both runs. Equal text is not evidence of equal runtime files, identity or policy. These results therefore are not 100 paired examples, or six proven pairs of identical worlds. The report appropriately rejects an isolated code/provider/SDK causal interpretation.

Read every zero-grade detail and checked that all 21 zero tasks occur exactly once in the stated categories. Those categories accurately summarize the grader evidence; they are not asserted as complete trace-level diagnoses. Independently summed trial usage: model calls equal 354 originally and 367 in the control; reported costs equal $0.66980710 and $0.072922019. Unknown-cost counts equal zero and four, with one in each failed control trial. The new cost total is incomplete and cannot establish a complete price comparison.

## Source, provider and failure evidence

Both immutable job/result source pins and the included 53,177-byte d2499r1 source agree on SHA-256 `ced402b531e213bef9959b6956006a8d967c0998eb7e31f0e34901f26b0eb3c1`. The recorded SDK versions are 0.3.6 and 0.3.7.

The two archived router request samples explicitly specify Cerebras FP16 versus DeepInfra BF16, with no fallback. Their other non-message request settings agree. The sampled successful responses identify Cerebras and DeepInfra respectively. This verifies the reported sampled routing/provider evidence, not every provider request in either run. It does not remove the 94 changed instructions, world generation, timing/load or SDK confounders.

Checked the four selected timeout event sets against their exact result-trial identities. Each has a single observed llm_error at attempt one with `outcome_unconfirmed=true`, and its agent_error exactly matches the result's traceback. The line-944 unguarded inference failure and one unknown-cost call per failed trial agree with the report. The sampled 429 retry events in t003/t045 refer to earlier, distinct inference calls. Therefore their presence does not prove that 429 caused all four later timeouts. This independent review used the supplied selected events/index extracts; it did not retrieve or exhaustively inspect the full remote traces.

The original t079 events explicitly show Exec `/bin/ls -R /proc/baskets` followed by the narrow runtime-tool-not-found HTTP 404 and agent failure. The isolated audit successfully exercises that exact observed exception and all four observed timeout strings against the unchanged pinned existing guards, including native Monty. These are reachable failure forms already covered by the repair. The tests establish bounded simulated handling, not actual provider recovery, later task completion, recovered billing or score gain. Three agent-level attempts do not bound SDK/provider retry attempts to three.

The local historical d3200r2 result archive independently supports score 0.9012601 (file `2026-10-22-record-integration/record-results.json`, SHA-256 `e1b57394edcf2b6dbc8fc7e1c724c1ceb8291d46f713d6b684ecd481fb738674`). That file is outside this package. I did not freshly query the global leaderboard, so this is corroboration of the cited historical record, not a new live-status assertion. Nothing in the control justifies promotion or a claimed code improvement.

## Isolated reproduction and final archive

Safely extracted all 53 regular archive members into a fresh temporary root, rejecting absolute/traversal paths or links. Verified the local evidence seals and ran the packaged audit.py with Python 3.14.3 and pydantic-monty 1.2.0 from that isolated tree. It passed all100 result/instruction checks, exact guard tests and native Monty execution. All regenerated evidence files, dependencies and manifests were byte-for-byte identical to the extracted originals.

The initial package exposed a cross-version gzip metadata difference: Python 3.12.7 emitted OS header byte 0x13, while Python 3.14.3 emitted 0xff. The decompressed tar was identical, but the compressed hashes differed. The author corrected package.py, with root authorization, to assert gzip magic/method/zero flags and normalize byte nine to 255. This changes only header metadata and leaves the deflate payload and data CRC untouched. I inspected that change and independently compared the final extraction to the already-audited tree: **only package.py and SHA256SUMS.json changed**. All research evidence remained byte-identical, so a redundant full evidence audit was unnecessary.

Independently rebuilt the final package from its isolated extraction under **both Python 3.12.7 and Python 3.14.3**, redirecting only the output path into the temporary tree. Both outputs are byte-for-byte equal to the sealed final archive:

- Final archive: `/tmp/ecom1-provider-control-review.tar.gz`
- Members: **53 files**
- Size: **486,556 bytes**
- SHA-256: **`9d924d0be34646084911d10e5ba376222a36a1e08356a0c0ff6f3cfe1e8aa867`**
- Final independent extraction: `/var/folders/px/h2tbfkd177v7w8r4xg5h7ycw0000gn/T/provider-final-independent-e4alsngv`

This establishes byte-identical reproduction on the two tested Python runtimes and local compression libraries; it does not promise identical deflate output across every possible future zlib implementation. The original archive and sealed evidence directory remained unmodified by the reviewer. This independent review is intentionally outside that package.
