# Null-final effort diagnostic: pre-result adjudication supplement

**Local author artifact complete; independent review pending. No submission or paid call.** The original frozen diagnostic folder is unchanged. This package pins its inputs and closes the author-side parser/fixture-definition gap identified by independent runner review. It does not certify model performance or authorize dispatch.

Read `ADJUDICATION.md` for the fixed visible-evidence boundaries of A016, A074, B056 and B076, the separate four-call V016 equal-input group, strict syntax versus actual source parsing, and the requirement for two independent manual reviews of all20 outputs. No semantic autoscorer is provided. `review-coverage-template.json` is an empty20-row coverage ledger with UNOBSERVED status, not a result sheet; hide its arm/fixture mapping during initial partial blinding.

`INPUT-PINS.json` pins23 exact copied diagnostic inputs, including packed/readable d4702/d4955/d4353, all four exact requests and preceding responses, the frozen call plan and original seal. `extract_parsers.py` extracts exact source segments for FIELDS, OUTCOMES, REQUIRED_ARGUMENTS, normalize_action, first_action_object and parse_step, with source line ranges and segment hashes. All three parser extracts are byte-identical, SHA256 `b62c0ee1a8bbb0bdc9283259853cb88f1a4132a786501de594b0da8165861097`.

`strict_schema.py` is the separately declared entire-plain-JSON contract. It deliberately distinguishes actual source aliases/fences/wrappers/first-object behavior. `test_parsers.py` passes69 CPython source-parser evaluations and69 strict checks across23 synthetic cases/three exact sources. Tests include valid Read/report/Write, missing fields, wrong types, null/prose/partial content, aliases, wrapper/fences, duplicate keys and trailing objects. A false completion and invented Write deliberately pass syntax: semantic support is a separate manual dimension. These are pure extracted-parser controls, **not native whole-agent executions** or inference tests. Existing native runner verification is separate. The main length guard is documented as source control flow, not part of parser acceptance.

Reproduce offline with Python3.12.7 (stdlib only):

```sh
python3 research/ecom1/2026-10-23-null-effort-adjudication/reproduce.py
```

This validates23 pins and regenerates five files exactly in a standalone temporary copy. `prepare.py` only documents copying from the original sibling; it is not needed to reproduce. `make_template.py` reconstructs the empty coverage ledger from the frozen call plan. `SHA256SUMS.json` seals author files, excluding itself, caches and later independent/publication material.

Handover: independent reviewer should review the source extraction, strict contract and every fixture boundary before any payment decision. If outputs are later authorized and collected, use full immutable requests/responses/provider/cost evidence, prepare partial-blind review inputs, preserve both initial manual sheets, unblind/reconcile without rewriting disagreements, and keep V016 outside the16-call effort comparison. No follow-up execution is authorized by this artifact.
