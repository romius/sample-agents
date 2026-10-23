# Revision2: bounded pressure-boundary review

**The initial transfer-induced overflow counterexample is repaired. Full-agent and SDK wire qualification remains pending.** Exact reviewed packed source is `1594a8403c660542dca851898ffc17a9cd0dd999f34dc854b09acf94f169497f`; helper/build/readable pins are in `results.json`. Initial review and results remain unchanged.

Eight independent structural groups pass with exact CPython3.14.3/native Monty1.2.0 parity under10-second feed/turn and1000-suspension limits. They cover added-message counts0/1/2, repeated pressure, the original overflow, benign byte identity, a forced-stop message crossing the threshold, an inherited parent overflow, and range stability after ordinary history-pair pruning. The harness extracts actual helper and parent observation definitions; provenance callback is deliberately a no-op, so these tests concern message removal rather than full reference dispatch.

The original66,961-byte candidate message list now loses only the handoff's exact contiguous range and becomes the exact57,447-byte parent list. Zero additions are a no-op;1/2 additions are removed once, bootstrap count is restored, and repeated pressure cannot delete unrelated history. A benign9,596-byte request retains all observations byte-identically. On the forced path, a55,875-byte history becomes56,037 after the stop instruction; pressure removes its own additions and preserves that final instruction, yielding the exact45,971-byte parent counterpart.

Both generated-source callsites were inspected and asserted: pressure runs before normal loop trimming and after the stop instruction, before forced final inference. Pair trimming cannot shift the protected initial range before pressure; when pressure fires, the range is removed and its count set to zero before subsequent parent logic.

This is a narrow fix. An inherited parent-sized104,149-byte retained pair is still oversized after removing handoff observations; the revision does not claim to solve it. Provenance already registered during transfer remains after context removal. That is defensible as an actual-read record, but any later automatic reference effect must remain separate from claims that the model currently sees or used the receipt. Existing security/ref filtering and model behavior are not proved by pressure tests.

Required before qualification: actual method-only full-agent request snapshots and SDK envelope measurements for main and forced paths, helper success/gate parity, full final-reference controls, and source-cap/build closure. No paid/model/Brain calls or prototype edits occurred.

Reproduce offline:

```
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python independent/revision2/review.py
```
