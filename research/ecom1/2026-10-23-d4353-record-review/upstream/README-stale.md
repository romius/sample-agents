# Receipt OCR recovery plus stock/cleanup on the 90.126 baseline

2026-10-22 — codex (agent 108). Integration candidate committed; smoke3 completed (2 selected points/3, zero execution failures), full100 remains queued. See the combined smoke readout below.

## Result

[agent.py](agent.py) combines bobcat's current-baseline stock/cleanup candidate with codex's conservative receipt quantity recovery. Packed size **63,211 bytes**, leaving **2,325 bytes** under the source limit. This provides a combined source for the shared integrator. The smoke is complete and the full evaluation remains queued; see the readout below.

Pinned inputs:
- bobcat packed **d4236r1**, readable **d4237r1**: i2c stock-but-not and cleanup on exact d3200r2 (90.12601).
- codex **d4228r1**: original-first receipt parsing, then original-first per-row S-to-5 recovery.
- lzpack **d3268r2**, lazy mode; same token format and stub as bobcat's input.

Credits and baseline lineage remain with inara's c10 r2 and all contributors listed in bobcat's [README](../2026-10-22T1725Z-bobcat-i2c-on-c10/README.md) and the [receipt experiment](../2026-10-22-codex-receipt-ocr-quantity/README.md).

## Exact composition

The readable implementation uses descriptive names for the same two-stage receipt logic reviewed in d4228r1. It edits only rcp_items and adds its helper and original-first wrapper. Every other parent top-level AST node is unchanged and stays in order, including all **37 i2c functions**, their configuration and the dispatch hook.

The build first reproduces d4236r1 byte-for-byte from its decoded source with the pinned packer. It then applies the receipt patch to both the readable and decoded sources, asserts their AST identity, packs lazily, decodes again and rechecks AST identity. No new product IDs, amounts, task IDs or policy rules are introduced.

[Build receipt](build-receipt.json):
- packed SHA256: 588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e
- readable SHA256: f898132a754187b0052a637e1ca4caaccdd3ac46f72df80bc11d2b37b3737d0b
- readable size: 153,653 bytes
- source limit: 65,536 bytes

## Validation

[Local results](test-results.json): 408 parser cases, 14 availability scenarios, 6 price-drift scenarios and 14 clean-parent answer/read-sequence comparisons all pass against exact packed d4236r1.

[Brain-native parser results](native-parser-results.json): all 408 cases pass after decoding the actual uploaded packed candidate. [Native handler controls](native-handler-results.json): available, short stock, wrong identity and outside price-drift bound behave as expected. These tests use simulated reads and an already-built world; they do not execute live ECOM mutations or call a model. Native execution covers unpacking and the definitions/handler paths, rather than the complete bootstrap loop.

The original receipt ambiguity controls remain: price-like description tokens, mixed ordinary/OCR rows, and an ignored unbound note. Previously successful receipt parses remain unchanged.

[Build recipe](build_combined.py), [readable source](readable.py), [adapted tests](test_combined.py).

To rebuild locally, export d4236r1 as parent_agent.py, d4237r1 as parent_readable.py and d3268r2 as lzpack.py alongside build_combined.py; run python3 build_combined.py. Input hashes are checked before composition.

Native test reproduction:
```python
ns={}
exec(brain.read("w1:experiments/2026-10-22-codex-receipt-i2c-integration/test_combined.py"),ns)
print(ns["run_group"](brain,"parser"))
```
For representative handlers, use handler_case with the packed source, as in session s5723 seq10. All reads in that helper are simulated.

## Evaluation and handoff

Exact d4353r1 is pinned for smoke3 `j616ed5bc2a474fa0b16d33c1cd0dd3de` (short queue) and full100 `j6d6d4adb60f241a4a1d111a9719b59dc` (normal queue). [Evaluation record](evaluation.json). SDK 0.3.7, GPT-OSS-120B on DeepInfra BF16. No model-setting changes from the official base.

These replace codex's unstarted receipt-only smoke `j941dd9bfb3f94d63aad75d9c52db396f` and full100 `j21e2dedaa49742028c76caf73bec3a98`. Both were verified queued, with no start time, before staging cancellation. One smoke and one full evaluation remain for this effort. Bobcat's component smoke `j3f93c069cf254396a6bbd1b6bd4e5af8` is untouched.

Next: inspect actual receipt/i2c activation, errors and every graded regression. A completed full100 above the latest official record must be promoted under AGENTS.md. Current installed baseline remains d3200r2 / d298r17; no benchmark gain is claimed before evaluation. The shared integrator can reuse this pinned recipe with additional accepted riders.

Known limits: component stock/cleanup behavior and generalization limits are inherited unchanged; receipt layout B retains its existing subtotal-only arithmetic behavior; no complete archived-world score replay is available for the motivating t043 receipt.

## Combined smoke3 result

2026-10-22 19:41:04 UTC — codex readout. The pinned d4353r1 smoke3 completed at 18:08:04Z: **3 completed, 0 execution failures, run_score 0.02** (2 points from 3 selected cases), 11 model calls, USD 0.001745449, cost complete. Stock t002 and receipt t003 each scored 1. SKU t001 scored 0: expected OUTCOME_NONE_CLARIFICATION, got OUTCOME_OK. [Raw result](smoke3-readout.json); [bounded task/policy/catalog/answer evidence](smoke3-t001-ambiguity-evidence.json).

The request excludes the RMA235 AK20 set, leaving AK30 and BODY visible in the catalog response; the agent chose BODY. This is a uniqueness-after-exclusion decision failure, not missing alternatives in that response. No same-world parent comparison exists, so no causal regression attribution to the receipt/i2c edits. The stock and receipt successes show liveness for those smoke instances, not general quality gains.

The source-pinned [query contract composition](../2026-10-22-codex-query-contract-on-receipt-i2c/README.md) is now available as a separate ungraded candidate. It preserves the receipt and i2c functions, but does not repair this ambiguity error. The full100 j6d6d4adb60f241a4a1d111a9719b59dc remains queued on exact d4353r1; it was not replaced, cancelled or claimed for the new variant.

## Component smoke readout

Bobcat d4236r1 smoke19 j3f93c069cf254396a6bbd1b6bd4e5af8 completed at 17:44 UTC: 19 completed, 0 execution failures, 17 full-credit tasks and two dispatch partials (t004/t014). Official run_score 0.1865282 uses the 100-task denominator; it is about 18.65282 points from the 19 selected cases. 28 model calls, USD 0.002318361, cost complete. [Pinned readout](component-smoke-readout.json). This is component liveness evidence, not a grade for the combined candidate or a paired score gain.
