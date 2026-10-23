# Independent review: initial receipt handoff prototype

**Not qualified for evaluation. One concrete new request-size regression remains.** This review pins helper `47caf25b…`, build `05a27dea…`, and packed prototype `be2da6a9…`; later revisions require a new review result. No prototype file was edited. The local published-plan counterpart is pinned in `results.json`.

## Finding: protected transfer can introduce an oversized later request

`build.py` replaces the pre-loop boundary with handoff plus `bootstrap_count = len(messages)`. That permanently protects the transferred source messages. The inherited loop only removes pairs while the message count is greater than protected-prefix count plus two. A single most-recent action/observation pair is therefore retained regardless of byte size; the forced completion append has no subsequent size check either.

The reproducible `history_cap_counterexample` starts with a synthetic valid44,000-character bootstrap payload, captures an8,900-character receipt, and then adds an ordinary Read of2,200 CJK characters. Under the exact default-JSON byte measurement used by the agent/plan:

| Measurement | Bytes |
|---|---:|
| Candidate prefix after accepted handoff |53,588|
| Later action/Read-observation pair |13,373|
| Parent message list after trimming |57,447|
| Candidate message list after trimming |66,961|

The initial candidate prefix passes54,000. The later candidate message list alone exceeds65,536, before request wrapper/settings; the corresponding parent list remains below that size. Thus this is an additional transfer-induced failure, not merely a parent overflow restatement. The script reproduces the source loop logic; it is not an actual SDK wire or native execution test. The parent also has unrelated pre-existing cap weaknesses for sufficiently large observations and forced completion.

Required resolution: make the transfer contribution removable under later pressure without falsifying source/provenance history, or separately scope and validate robust pre-dispatch bounding for every model call. Do not declare the mechanism qualified merely because its first request fits. Retain this parent/candidate contrast as a regression control, plus actual SDK-encoder assertions and forced-report stress tests.

## Controls that passed

Seventeen structural groups cover complete transfer, exact existing-observation deduplication, repeated-call idempotence, conflicting prior bytes, conflicting prior metadata, server-truncated sources, >10,000-character sources, Unicode escaping exceeding per-observation byte limits, oversized metadata, near-limit bootstrap rejection, five invalid capture shapes, generic reference ablation, injection-shaped source text, missing metadata, and three archived witness projections.

- Actual t023/t063 policy/upload responses appear completely in their projected fallback requests. Actual t043's already-visible observations leave its projected message list byte-identical. These are saved-request projections, not full-world replays or evidence of improved model behavior.
- Conflicting prior content or metadata yields a content-unavailable descriptor; new upload provenance is not promoted. Existing prior messages remain unchanged. Truncated/oversized sources likewise yield descriptors; oversized metadata or an over-budget total rejects the transfer without provenance changes.
- Complete matching ordinary observations remain untouched. A raw ordinary observation does not contain a prior content hash, so body equality cannot prove metadata equality; preserving identical body evidence is defensible, but documentation should not call this universal hash-verified deduplication.
- Capture copies actual returned metadata when available, without fabricating hashes. It does not independently verify SHA256 correctness or require all metadata fields. Those guarantees depend on the actual Read service and successful response shapes; malformed synthetic metadata is not proof of a live service defect.
- The per-invocation clear and callsite placement preserve the strict receipt gate and do not route answered helpers through handoff. No broad memory serialization or new RPC is introduced by the helper.

## Automatic references and authority limits

The script uses the actual parent `note_policy_read` and generic `merged_refs`, with the specialized `receipt_refs` callback explicitly stubbed to identity. Context-only/provenance-only/combined controls demonstrate that registering a successful upload Read automatically adds its path for OK, clarification, and unsupported outcomes even for the fixed unsupported identity explanation. Security-denied outcomes do not receive that automatic upload reference; the policy reference is still appended. This isolates a reference effect only. It is not a full final-answer path audit, and it cannot justify a semantic improvement claim.

Injection-shaped OCR bytes survive unchanged in an ordinary user-role Read observation and do not replace the system message. The helper itself performs no action or privilege change. This structural result does **not** establish that a model will treat every injected string as data or that a later attempted Write/Delete will be rejected. Existing security authority and actual action guard controls still need whole-agent/native testing. No source text is executed by this review.

## Build and reproduction

`build_reproduce.py` copies the exact six build inputs into a fresh temporary directory, rebuilds there under Python3.12.7, and verifies all five generated outputs byte-identical to the prototype, while asserting original files unchanged. The corrected build decoder API works. Packed size64,474 bytes leaves1,062 bytes under the source cap. Exact hashes are in `build-results.json`.

Run:

```
python3 independent/review.py
python3 independent/build_reproduce.py
```

The source-derived controls run in CPython only. Parent-owned tests are responsible for native Monty method-only host behavior, full helper-success/gate parity, actual SDK request capture, full reference dispatch, and long-history qualification. No model calls, Brain calls, paid evaluation, production edit, or score estimate occurred.
