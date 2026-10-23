# d4955: all 83 full-credit final-log reviews

Exact job `j37e3df7ac8564c0899c81a706e0aea9a`, source d4955r1, run `run-22rKzjKYfuGdRHhgP1aQeLo5A`. This directory closes the successful-task portion of the parent all100 audit. Every row in `success-review.json` retains the actual instruction, official grade, exact final Answer and acknowledgement, complete agent_finished stdout, event refs, and explicit manual observation. `manual-notes.tsv` is the judgment source; reconstruction is not an automatic semantic grader.

All 83 Answer requests, 83 successful acknowledgements, and 83 complete stdout events are preserved. Twenty-five additional targeted events bring the total to274. Event UTF-8 lengths match server indexes, task/trial identities match official results and StartTrial inputs, and three Read content hashes match their server SHA256. The16,139-byte t094 response is reconstructed from three contiguous chunks with exact offsets. Official full-trace CAS descriptors are retained but complete trial CAS blobs are **not** reassembled or certified here.

Material observations despite grade1:

- t021 and t091 each recover one explicitly logged malformed action. Separately, t025 twice and t081/t091/t094 each receive an HTTP200 model response ending with `finish_reason=length`; the next indexed event is another model request, without an intervening RPC. These five responses are preserved, including concatenated action objects and the truncated t094 clarification. They are not classified as transport errors.
- t025 also attempts List on a branch JSON file and receives HTTP400 `not a directory`, then successfully reads the record.
- t039's model action loop succeeds: all three literal `.tmp` files in the seven-entry listing receive successful Delete acknowledgements, and final sorted paths match. This is a concrete counterexample to a blanket assertion that model-loop cleanup always fails; it does not invalidate t060's separate all-files failure or establish a score delta. No post-delete filesystem readback is claimed.
- t091 writes a seven-column CSV with five K4 rows and successfully Stats the export. Its complete event index has no later Read. This is not a demonstrated citation failure, and forecast values are not independently recomputed.
- t081's final employee fields and t094's price match targeted Reads. t001 uses actual Unicode narrow spaces; JSON escaping is not a literal-output defect.
- Crosslist t016/t036 stdout provides only a preview marker, so this audit does not certify their output rows. t100's final explanation leaves its blocker disjunctive.

Full-credit results are preserved, not regraded. Tail events and stdout are not complete action transcripts: no universal authorization, no unintended-mutation certification, no complete reference/policy/catalogue oracle, and no total-count correctness claim. Targeted checks make narrower assertions only. All agent_finished usage objects show zero model calls, while official successful-trial usage sums to167 model calls; the former are placeholders, not evidence of zero execution cost. A cumulative job usage footer in stdout is not per-trial cost.

## Reproduction and provenance

Python3 standard library only; no model/network/Brain calls:

```
python3 build_review.py
python3 check_support.py
python3 seal.py --check
```

Run from any working directory. The scripts resolve this directory and require the parent `result.json` and `instructions-all100.json`, pinned in `event-manifest.json`. Preserve that directory relationship when copying. `reproduce.py` copies this closure plus those two exact inputs to a temporary directory, verifies seal hashes before execution, reconstructs all generated files, and verifies byte-identical output. It does not fetch traces.

Raw Brain receipts are authoritative retrieval evidence, including exact programs, session start, and final discard. Session s8115 was read-only and discarded without publishing. Tail indexes were bounded using the next actual StartTrial sequence; t100 was discovered separately. Five complete targeted indexes are retained. Every extracted event has a receipt provenance link and local SHA256. The explicit member seal excludes only itself, Python caches, and future publication directories; no paid calls, production changes, or Git changes were made by this review.
