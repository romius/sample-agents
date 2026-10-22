# Independent OCR normalization review

23 October 2026, reviewer `integration_plan`. **PASS for the final one-line parser change, tested boundaries, exact build reproduction, and bounded replay review described below. This is not live-score evidence or unconditional submission readiness.** No hosted calls, Brain writes, Git actions, or candidate/source edits were performed by this reviewer.

## Exact source and build

Reviewed final packed candidate **62,662 bytes**, SHA-256 `229b630545bcb5414593bd96a8fb92ae5283c31e717120a1069f4b4e6f062468`, leaving **2,874 bytes** under 65,536. It is 187 packed bytes larger than exact d3909r1. Readable source is 146,088 bytes, SHA-256 `928b1928524b863618fd2a526952229bce3f00cdc325251f5c3034a9239c8ea6`.

I decoded both packed parent and candidate and verified exact equality to their respective saved readable files. Removing the single new normalization assignment makes the candidate AST exactly equal to the parent AST; the text diff is also one inserted assignment. No matching, properties, inventory, policy, reference, export or routing function changes are hidden in this patch. The saved parent packed hash is the expected `56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c`.

Copied the candidate folder and its three exact sibling build inputs plus the archived OCR-response file to a fresh temporary tree. Running the build under **Python 3.12.7 and Python 3.14.3** independently reproduced all six generated source/manifest artifacts byte-for-byte, including the final packed candidate. The unchanged record packing function is extracted from the saved parent builder. The build still depends on those sibling inputs; a release archive must include their pinned closure, not just this directory. I independently verified the readable-parent/packed-parent identity rather than relying only on the builder's packed-parent hash assertion.

Reviewed build SHA-256: `c0f4c0b4ef75f48e3efee4d657f320ed6de468fc6e5bee2d6c87b6f6ba1d1203`. Manifest: `989497a5756ca1c786b415d5068c991e540cd5f4ceb3183442bc31240a1ced94`. Parser report: `5744fd5e7bcf33512b6e9a6c764a26a08386a55330e540a5cc9d491fbf1065f1`.

## Grammar and counterexamples

The added rule removes only a line-start, hash-delimited ASCII `scanline` marker immediately before a complete ASCII-numeric `Total requested lines:` or `Total requested units:` record. Spaces/tabs and ASCII letter case vary; signed/decimal/text quantities, extra words, trailing hashes/instructions, missing delimiters and surrounding prose do not become totals. It operates after the existing CRLF/literal-newline conversion and before total counting. Therefore a clean total plus a recognized noisy duplicate/conflict is rejected together; the implementation does not return early after finding a clean parse.

The initial `(?im)` candidate had a fresh cross-runtime counterexample: CPython normalized `#scanlİne#` and `#scanlıne#`, while native Monty did not. I also tested the proposed `(?aim)` fix; Monty rejected its ASCII flag with `re.PatternError`. The final source uses explicit ASCII letter pairs with multiline mode, eliminating this newly introduced divergence. Tests include long-s and dotted/dotless-I in markers and dotted-I in the total keyword. This proves parity for the **new normalizer's tested boundary**; it does not claim to remove every inherited Unicode difference elsewhere in the parser.

Independently reran the final **31 authored cases × parent/candidate × CPython/native Monty** and reproduced all three parser artifacts byte-for-byte. Added **44 independent cases** built from an unrelated two-row request with manually specified branch, quantities, descriptions and properties; these also pass across both versions and runtimes. This is 300 final parser evaluations, not 300 whole-agent tasks.

The independent cases cover both totals prefixed together, upper/lower case, tabs, leading zeros, EOF, actual/escaped CRLF, totals before rows, equal and conflicting duplicates, prose/quote/unterminated markers, non-ASCII lookalikes, unsupported numeric forms, wrong row numbers, duplicate/missing properties and branches. Markers embedded in property values remain literal text; unknown valid properties remain present. No oracle uses a task ID, archived SKU or preselected catalogue answer. The exact archived five-row/36-unit witness still passes, while clean unrelated parsing is unchanged.

These controls support a reusable narrow layout correction rather than a task-answer special case. They do not establish support for arbitrary OCR corruption. Unrecognized noisy lines outside rows may still be ignored under inherited parser behavior; the patch only brings the explicitly recognized layout totals into strict duplicate/quantity validation.

## Independent evidence and remaining scope

Reproduction directory: `/var/folders/px/h2tbfkd177v7w8r4xg5h7ycw0000gn/T/ocr-independent-final-7x2yezvc`. Additional independent evidence supplied to the root for preservation:

| File | SHA-256 |
| --- | --- |
| `/tmp/ecom1-ocr-independent-extra.py` | `9ffaf1fad0b121dbeb2a93a830b1c7a0635a6ff5742e641a6de6d52a8de153f0` |
| `/tmp/ecom1-ocr-independent-extra-fixtures.json` | `ad1244c2b7818d6687a765c963ee2570336446ef218c5365a4944685f7a1e128` |
| `/tmp/ecom1-ocr-independent-extra-results.json` | `f070cda33251c1906de28a312c0859b80c1d8474e313251b71cd6e67d4da2c6e` |

## Coordinated replay spot-audit

The replay author reports 112 final-byte whole-agent executions, with 14 cases across two versions, two source forms and two engines, in sibling `2026-10-23-stack-e-ocr-replay`. I inspected the host and manual oracle and independently reran its `prepare.py` in a fresh copy. The world, provenance and both positive TSV/oracle sets reproduce byte-for-byte: 135 actual RPC responses, 126 distinct read files, and exact selected subtrees containing 101 catalogue and 17 location leaves. The preparation checks response byte sizes against indexes, joins request/response methods, verifies content hashes, and requires every selected leaf to have an archived Read response. This is local archived-world reconstruction, not a fresh server completeness check.

I checked the five-row oracle against the preserved OCR, product records, branch inventory and actual crosslist policy. Row 2 requests flow 410 while the catalogue says 420, so its property-mismatch status, blank matched identifiers and zero fulfillment are supported. The open branch has explicit inventory entries yielding available counts 8, 2, 0 and 0 for the four exact matches; future incoming stock is not counted. The fresh drill body/kit control also has explicit inventory entries. No positive zero-stock result here is inferred from an absent row. The author added explicit positive-oracle inventory-presence assertions at my request; I reran the final preparation and all world/oracle outputs remain byte-identical. The separately recorded absent-inventory decline cases are retained.

The replay uses actual method-only `ClassInstance`, ten-second limits and 1,000 suspensions. Its fixed actual router response and unsupported fallback are declared scripted boundaries. Export Write acknowledgement is an explicitly simulated local response because the archived failing run never wrote that report. Zero unmatched requests and equivalent forms are meaningful within this host, but cannot establish real provider behavior, live write success or a grader result.

I independently checked the 112-row ledger for unique case/version/form/engine cells, exact saved-source hashes, zero unmatched calls, and equality of all four forms' RPC histories, writes, answers, scripted-LLM counts and router-request hashes. I then reran four meaningful **whole packed-agent executions under native method-only ClassInstance**: parent on original noisy OCR declines; candidate on original noisy OCR writes the exact five-row oracle; candidate on fresh noisy two-row OCR writes its exact oracle; candidate on a contradictory noisy total declines. Each complete RPC/write/answer history and scripted-call count matches the saved ledger. I did not redundantly execute the remaining 108 ledger cells.

Final reviewed replay pins: `prepare.py` SHA-256 `5378a6c2c34e772f94d91eb96dbc29be6ef11fab3b1d94bb05fab2cf8c63ca94`; `replay.py` `2e8f05742c950a65d82121fb997e6adf23fc3fa5f413febc3dac0ed00e0f31a9`; `replay-results.json` `515a927253c5a19a100aae50f6657b37bb01b29a7cdd20b96ca44314553dd462`; reconstructed world `81da3f5e49742292ae2b1b437be723f9f8152e0888b2dd67224ed2f7114d345b`; archived-world TSV oracle `0bb89033e80c45603f6c9775c0f235b88a0196a3312844fa549d57fde3a3fc8d`.

This supports the final-byte bounded replay mechanism, not an actual task-grade result. Initial superseded-candidate replay is not final-byte evidence. Final archive closure, full100 non-regression, live score gain, release capacity and promotion remain separate gates. Temporary world reproduction: `/var/folders/px/h2tbfkd177v7w8r4xg5h7ycw0000gn/T/ocr-world-independent-vxu0lunr`.
