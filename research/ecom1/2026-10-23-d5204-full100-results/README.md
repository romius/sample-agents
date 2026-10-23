# d5204 completed full100: every trial failed at callback-value access

Job `j2f9717b672c04c9a94f1df3219579692`, run `run-22rLKF8bmYV6huGenJqrnWgj8`, finished2026-10-23T01:48:29.320245Z. The official run is completed/evaluated with100 completed trials,100 failed executions, score0, zero model calls and $0 reported cost with complete accounting. There are no cancelled, skipped or unselected trials.

Every failure was audited from its **complete sealed trace**, rather than inferred from the first trial or the truncated result error. All100 fail while evaluating the `bitgn.call` argument as a first-class value:

```python
# Readable source line3914
IX_RESULT=ix_run(bitgn.task()["instruction"],bitgn.call)
# Exact submitted decoded/minified payload line2094
AE=Db(bitgn.task()['instruction'],bitgn.call)
```

All100 full agent errors end with `AttributeError: 'BitGN' object has no attribute 'call'`, at packed wrapper line11 then decoded module line2094. There is no inventory-handler frame: attribute evaluation fails before `ix_run` is invoked. Every full error has SHA256 `6b23be01946b50e35cbe3da550e70a0505181e6197b3a53986e23b31f1896e6f`; this equality is checked independently for each trial, not assumed. AST inspection confirms the failing node is an Attribute used as an argument, not a direct method call. It does not establish the private host implementation; the earlier hosted boundary probe independently confirms the method/value distinction.

## Exact scope of the evidence

All100 complete traces, totaling13,422,710 bytes, match their individual official sealed CAS hashes. `audit.py` verifies600 full events, per-event indexed lengths, byte offsets, sequence/kind/time, trial IDs, run ID and task IDs. Each trial has exactly this sequence:

1. StartTrial request and successful response, including the complete task instruction.
2. The full agent_error and agent_finished with failed state, empty stdout and zero ECOM/model counters.
3. EndTrial request and successful `TRIAL_STATE_DONE` response.

There are no Read/Tree/Exec/Write/Delete/Answer or inference events in any of the100 trial traces. Harness StartTrial/EndTrial RPCs are preserved and are not mislabelled agent ECOM actions. `agent_finished.output` is explicitly empty in every trial, not missing. Each per-trial usage record has zero calls/tokens/cost and complete accounting. All100 post-SubmitRun grades are available, score0, with “no answer provided”; earlier agent_finished grades are still unavailable and are not treated as final grades.

`all-task-review.json` preserves every instruction, instruction hash, trial ID, full-error hash, source failure location, all six event sequence numbers, final stdout, cost/usage and EndTrial response. `instructions.json` is a compact input-only view. `failure-template.txt` preserves the common **full** error, while every individual trace also contains it. The official API trial error and agent_finished error are truncated to2,000 characters and cannot establish the terminal exception; `audit.py` verifies those are exact prefixes of their full corresponding agent_error.

`official-result.json` retains the complete official result API object, including job/source identity, every trial grade and usage, all trace receipts and run metadata. It is a reconstruction of the API object's deterministic JSON serialization, not a claim to have downloaded the summary CAS blob's original bytes. All100 **trial** CAS blobs are reconstructed and byte-verified. The run-level21303-byte trace receipt is preserved in the official object, but the run-level trace itself was not downloaded; this is not needed to establish the six-event lifecycle of every selected trial.

## Source and previous mechanism evidence

The exact submitted source is d5204r1,65,292 bytes, SHA256 `0cb742d544039b1d9dc4a862021ee1bfe3967c2ced8082756525e075b6c1ca67`, SDK0.3.7. This matches both job source_blob and official result source SHA. It is the original defective submission, not the named-wrapper successor.

The local inventory integration closure is preserved under `closure/`: unchanged builder, readable source, minified prepack, packed agent, manifest, submission receipt, d4955r1 parent, d4012r1 inventory donor, minifier template, minimum-cost LZ packer and the original pinned dependencies. Every dependency listed in the archived manifest is length/hash checked. The unchanged builder recreates packed agent, readable source, prepack and manifest byte for byte in an isolated temporary directory with python-minifier3.4.0. The packed source is separately decoded and checked against the exact prepack before reading its failure line. No source or candidate was modified.

`prior-probe/` is preserved historical evidence from the already completed zero-inference SDK callback probe d6368r1/job `j9b18bdffe5fa4ac39383f908170b20a0`. Its sealed3244-byte trace SHA `e102a5f3ef60e690915f8f4059f4abfff090f9ed3c4c6074ff5ebcf5f923068f` and prior verification are retained. It showed first-class attribute access raises while direct/named-wrapper calls succeed; the carrier task was intentionally not solved. This audit does **not** repeat that probe or rerun any provider call. The copied README is historical and contains then-current baseline references; those are not current baseline claims.

The minimal callback successors were already prepared and independently reviewed in sibling `2026-10-23-sdk-callback-repair`. This actual full100 failure confirms that original d5204's business handlers never ran. It does not test the successor, the inventory algorithm, the remaining task handlers or current-record task quality. No business correctness analysis, counterfactual success estimate, score-gain claim, promotion, cancellation or new evaluation follows from this zero result.

## Lossless harvest and reproduction

Tracebacks repeat the entire65KB packed source line and a65KB underline. To avoid copying them repeatedly through tool output, the read-only harvest replaces exact JSON-escaped source-line fragments and long homogeneous underline runs with explicit dictionary tokens. The full API result similarly factors repeated exact error/usage/grade strings. Counts and lengths are retained; no error suffix is dropped or summarized. `decode_evidence.py` reverses every replacement using the exact pinned submitted source and recorded dictionary values, restores all full traces/indexes and the complete API object, then `audit.py` verifies each trace against its independent official CAS hash. Unexpected or nonmatching errors would remain in the transferred text and fail the uniform-mechanism assertions; the factoring does not assume identical failures.

Raw factored batches and API chunks remain in `evidence/`, with the exact server-side helper source in `harvest-functions.py`. Read-only session s8116 ended with discard. No Brain documents, jobs, production sources or Git state were changed by this audit.

With Python3.14.3 and `python-minifier==3.4.0`, run `python reproduce.py`. It copies the package, removes205 generated outputs, decodes all evidence again, repeats the complete audit and exact source rebuild, and requires all205 outputs to be byte-identical. There are no network, Brain, model or live-probe calls in reproduction.
