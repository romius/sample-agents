# d4955 full100: complete task review, below the record

Own completed job `j37e3df7ac8564c0899c81a706e0aea9a`, run `run-22rKzjKYfuGdRHhgP1aQeLo5A`, exact d4955r1, finished 2026-10-23T01:48:01.415880Z. Official score **87.107223/100**: 83 full scores, 12 zeros, five dispatch partial scores, 100 completed and zero execution failures. Cost is **$0.054029475**, complete with zero unknown/pending calls; 267 model calls and 1,139,248 tokens (1,049,945 prompt, 89,303 completion). This does not replace the frozen comparison record d4353r1, 94.72095/100.

The submitted source is 63,582 bytes, SHA256 `2f145f03558a944c30398ec59aabb92ea7d891e05889b1a8f348d07d11cbfb20`. Exact builds reproduce d4702 → receipt-header d4848 → d4955 from the included closure. Relative to d4702, only `rcp_items`, `dispatch`, and the new `clarification_skus` function differ. All 23 source/build pins verify. The inherited source already disables the deterministic cleanup route and includes the MSR/Exec404 changes; those are not new d4955 components.

## Every task was reviewed

`all100-review.json` and `.md` contain all 100 actual instructions/hashes, official grades, exact final Answer, complete agent_finished stdout, observations, evidence levels and uncertainty. Full-credit tasks are not treated as independently certified action-by-action successes. `success-evidence/` supplies the independently reviewed 83 successes: 274 exact events and a verified 386-file child seal, with selected supporting evidence for cleanup, output truncation and CSV writing. Its final reports and seal remain unchanged.

All 17 loss indexes are complete (3,119 indexed events). We retain 1,934 primary loss events, including every RPC request, every model response, Answer/ack and stdout, plus selected policy/upload/store/product Read responses and exact router/first-main/final-model requests. Eight complete trial CAS hashes match: five dispatch tasks, t060, t063 and t065. The other nine are explicitly selected traces, not complete CAS reassemblies. Selection and omission rules are preserved in `additional-harvest-plan.json`/`prepare_extra.py`; unrelated bulk catalogue/store responses and most middle inference requests are omitted. All 180 retained loss Read-content hashes verify.

The 100 loss-side model responses reconcile exactly to per-trial calls/tokens/cost: all HTTP200/DeepInfra; 14 null-content responses and seven `finish_reason=length` responses. The complete loss indexes contain no llm_error, llm_retry or agent_error events. This loss-selected sample is not a whole-run provider-error rate. The success review separately preserves five additional length-truncated responses. Printed usage snapshots are not per-trial accounting; official settled usage is authoritative.

Official aggregate 0.87107223 differs from the arithmetic mean of serialized per-trial grades, 0.871072196, by 3.4e-8. Verification reports this tiny discrepancy and its explicit tolerance rather than claiming exact recomputation or inventing its numerical cause. Calls, tokens and settled cost reconcile exactly.

## Findings grounded in the actual traces

- **t002 and t022 are different reference failures.** t002's model itself supplies the carrying-case candidate contradicted by “without carrying case”; CASE is the extra ref. BOX is the explicitly excluded SKU, and this policy variant requires mentioned SKU references. In t022, the model supplies only Silent Plus, while inherited postprocessing adds the explicitly excluded KIT despite the actual policy's “don't quote that Y” exception. A blanket excluded-SKU deletion rule would miss this distinction.
- **t005 and t065 compute correct counts but omit provenance.** Recalculation from the exact store records gives 0 and 1, matching the answers. Neither trial reads catalogue products, and the grader flags all six product refs missing in each. See `inventory-count-verification.json`.
- **t041 and t047 lose product constraints differently.** t041 claims a unique bare Milwaukee body where the oracle requires clarification. t047 narrows a shared design-video family to the workshop layout even though the layout is unspecified. The actual three observed family records include garage at 3990 cents, below the 4024-cent limit; workshop4490 and shed4990 are above it. The model returns0, oracle1. Observed family evidence is preserved; a universal matching rule is not established.
- **Receipt parsing and evidence transfer are separate from denial and typo recovery.** t043 re-reads the receipt but uses corrupted `PT-MOW-EI-GECM36-2X4`, then misses the actual mower ref. t063's first main request lacks the helper's upload, but the model subsequently re-reads it and still denies a read-only availability question as customer-only checkout. Thus transfer alone is not a demonstrated fix for that actual case. Exact envelopes have path/contentType/content/sha256, without a truncation field; absence is not an explicit false flag.
- **t056/t076 are not covered by the published narrow OCR patch.** Twelve parser-only CPython/native executions show exact d4353, d4955 and d6729 hash-scanline sources all reject both actual uploads identically. No input cleanup or successor is proposed here. t056 subsequently clarifies after null replies. t076 spends31 calls/$0.017732644, never executes a Write, then delivers OUTCOME_OK while explicitly saying no TSV was created. Its length-truncated attempted write never reaches the RPC host. Parser coverage, output truncation and completion integrity are distinct issues.
- **t060 refuses a supported sequence; t079 chooses a basket without comparison.** t060 lists files then says multiple deletions cannot fit one action; no Delete occurs. In contrast, the separately reviewed t039 success performs three acknowledged suffix-matching deletes. t079 lists two own baskets, reads only basket-0002 and writes it, claiming it is latest; the grader expects basket-0001. Listing has no timestamps, and basket-0001 contents are unobserved, so its actual timestamp is not invented.
- **Dispatch remains an efficiency loss.** All five plans deliver all ten packages with no misses or invalid penalties. Within this run, t004/t014/t024 have equal actual instructions, all observed Read bytes, nonlifecycle RPC arguments/responses and model requests, and equal partial scores. The equality claim is bounded to those observations, not unobserved state or another source's run.

## Component activation and comparison limits

95 instructions differ from d4353 and 93 differ from d4702. Even identical wording does not prove equal worlds. The small aggregate improvement over d4702 and same-ordinal successes cannot isolate either new component.

In particular, t021 is a single-SKU OUTCOME_OK answer, so the clarification display addition cannot activate there. None of the 100 delivered messages contains the helper's only change marker, ` Candidates: `; no delivered display addition is evidenced anywhere in this run. t023 success establishes receipt-handler completion, not necessity of the new header alternative: its actual upload and products differ from d4702's same-wording task, and this audit has no t023 upload body or same-world parent replay. `component-activation-review.json` records these boundaries explicitly.

## Reproduce without live calls

Use Python3.14.3 with pydantic-monty1.2.0 (the local pinned interpreter is `/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python`). The source builds also passed Python3.12.7; the saved final source report uses3.14.3. From this folder:

```sh
python source_verify.py
python reassemble.py
python prepare_extra.py
python build_loss_review.py
python build_evidence_notes.py
python build_review.py
python verify.py
python check_crosslist_ocr.py
python success-evidence/reproduce.py
```

For an isolated combined check, run `python reproduce.py`; the nine scripts reproduced byte-identically in a temporary copy. Reproduction should run in a copy when preserving the final seal. `source_verify.py` itself rebuilds only in a temporary directory. All parent sources, packer, patches, exact result/instructions, raw chunk receipts and comparison snapshots are included. The parser comparison is deliberately not a whole-agent or score test. Main read-only Brain session s8113 was discarded at02:32:57UTC; success-review session s8115 was also discarded. No paid runs, promotions or live changes were made by this audit.
