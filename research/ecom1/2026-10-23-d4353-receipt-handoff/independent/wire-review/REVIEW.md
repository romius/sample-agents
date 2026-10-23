# Offline SDK0.3.7 request-envelope assessment

**Defensible conclusion: the saved receipt request projections satisfy conservative, explicitly conditional JSON envelope bounds. Private SDK wire encoding is not verified.** This is an offline review of exact archived request objects and the saved SDK guide, not a provider probe or a new model evaluation. Initial/revision2 reviews are unchanged.

## Evidence boundary

The copied SDK guide says model requests are limited to64KiB, pins `deepinfra/bf16`, prohibits provider overrides, and documents completion-token aliases. It does not specify serialization options, the exact bytes counted by its request-limit guard, or the private transport implementation.

The three exact `llm_request` event records contain structured `request` values: `model`, `messages`, `reasoning`, `temperature`, `max_tokens`, `stream`, and `provider`. They establish the logged request values, including the SDK-observed alias `max_tokens=2048`, temperature0, medium reasoning, nonstreaming, and provider-only BF16/no-fallback settings. They do **not** contain an independently identified raw HTTP request body. Reserializing the nested object—or using its original spelling inside the trace journal—does not turn it into proof of transmitted bytes. HTTP headers/provider-internal forwarding and private limit-check encoding remain outside this evidence.

These are the archived d4702 t023/t063 missing-evidence witnesses and t043 already-visible control used in the published fallback plan. Applying the d4353 prototype to their messages is a declared counterfactual projection, not a same-world d4353 live run. All copied events and guide receipt are pinned byte-for-byte in `input-provenance.json`; the pure observation definition is an explicitly documented AST-source extraction. No complete trial CAS is independently recertified in this review.

## Complete observed-envelope measurements

The script preserves every non-message request value and measures four encodings: Python default ASCII-escaped JSON, compact ASCII-escaped JSON, default UTF-8 JSON, and compact UTF-8 JSON. Default escaped JSON is the largest **among these four**. It is not an upper bound over arbitrary pretty-printing, slash escaping, extra wrapper fields, or an unspecified private encoder.

| Archived task | Actual object, default JSON | Projected full object | Projected messages |
|---|---:|---:|---:|
| t023 |16,730|19,734|19,475|
| t063 |16,699|19,516|19,257|
| t043 control |25,485|25,485|25,226|

These include the prototype's metadata annotations, unlike the earlier plan's smaller two-observation estimate. t043 remains byte-identical at the message-value level. No provider, model, inference setting, or original message is changed.

For the fixed archived settings, default JSON adds exactly259 bytes beyond the serialized message list:14 for the containing `messages` object,32 model,35 reasoning,18 temperature,20 max_tokens,17 stream, and123 provider. Therefore a54,000-byte message list projects to54,259 bytes (11,277 margin); a56,000-byte list projects to56,259 (9,277 margin). This conditional calculation includes the observed provider settings rather than guessing a constant wrapper allowance.

Stress fixtures measure ASCII, CJK, emoji, quotes/backslashes and newlines after JSON escaping. For example2,200 CJK characters occupy6,600 UTF-8 bytes but produce a13,533-byte full default-escaped envelope;1,100 emoji occupy4,400 UTF-8 bytes but the same13,533-byte escaped envelope. A7,000-character quote/backslash payload becomes14,333 bytes. Character counts or unescaped UTF-8 sizes would be insufficient. Exact tables are in `results.json`.

## History and forced completion

Adding the same observed envelope to the independent history witness yields:

| History | Default full envelope bytes |
|---|---:|
| Parent |57,706|
| Initial prototype |67,220|
| Revision2 after pressure |57,706|
| Revision2 forced report |57,868|
| Parent forced report |57,868|
| Inherited parent oversized pair |104,408|

Revision2 removes its transfer contribution and restores exact parent messages on the demonstrated overflow, including the forced-stop instruction. It does not make every future request globally bounded: parent logic can retain an oversized final pair, and the inherited104,408-byte example still fails the conditional size bound. Earlier independent revision2 tests confirm the pressure behavior in native Monty as well as CPython; this wire review does not pretend that native pure-function parity identifies a private HTTP serializer.

## Recommended qualification wording

“Offline structural and native checks confirm the receipt handoff preserves recorded model/provider/settings values, deduplicates the already-visible control, and removes its own context contribution under pressure. The complete archived-request projections are below64KiB using default ASCII-escaped JSON and three measured no-larger JSON variants. This is bounded request-object qualification, not verification of private SDK wire bytes or a global fix for inherited parent request overflow. No semantic or full100 improvement is established.”

If the acceptance gate requires **exact private wire conformance**, that requirement is blocked by missing authoritative encoder/limit-check evidence. Full-agent scripted-host captures can strengthen actual call-boundary values and control flow but cannot, by themselves, reveal the private transport's serialization. Do not spend a paid model call merely to relabel a reserialized object as raw wire evidence. Separately address inherited parent caps if a universal request-bound guarantee is desired.

## Reproduction

```
python3 independent/wire-review/review.py
```

Python standard library only. All script inputs are local copies under `inputs/`, verified before use. Output is deterministic `results.json`; no network, Brain, model/provider call, production edit or source mutation occurs.
