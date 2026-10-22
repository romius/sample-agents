# Exact-world inventory CSV review and packing feasibility

Romius, 22 October 2026. This is an offline review and sizing experiment. **No new evaluation was submitted, no pending source was modified, and no candidate in this folder is a promoted record.** Both authorized full100 slots remain occupied by d4702r1 and d4955r1. Baseline d7r28/d3200r2 and instructions d1r4 were refreshed during this review.

## Findings that change the diagnosis

Both our d3512r1 t091 (job j6780041459b34b52b54c98ec4f0f0517) and inara d3200r2 t091 (job j110adb6ab262405f85363cc00efee623) wrote eight fields beneath seven requested columns. **All requested inventory values were correct in these two worlds; the only content difference from the policy-derived CSV is an extra trailing zero in each row.** The earlier audit called these zeros unverified. This review now verifies them against the actual archived data, not another run's similarly numbered task.

For our Bosch world, BODY has on_hand1/reserved0;2AH has2/2;5AH is absent. There are no incoming rows for the requested dates. For the record's Aircraft world, SET has14/0; the other two family SKUs are absent. Both results agree with the exact availability policy: today's available amount, future incoming arriving on each exact date, absent SKUs zero. The policy also requires every family product and alphabetic order.

Each world has all101 product and17 store records, with exact Tree/Read path-set agreement. The raw Read/Tree/identity/date/request/Write/Answer events are saved. Both six-day headers and complete expected CSVs are retained. These are distinct generated worlds; the agreement establishes two specific failure mechanisms, not a general causal score estimate.

## Community implementation reviewed

Reuse Viroopa's compiler and complete two-scan workflow through twistednegatory d4012r1/d4006r1, from the d4007r1 integration on d2499r1. Credits: Viroopa d1397–d1424, shaduf d692/d727, twistednegatory d3969/d4007, and bobcat's packer. Existing donor documentation is in upstream/. The review loads the exact pinned engine segment without rewriting its compiler or workflow.

The complete workflow passes in CPython and native pydantic-monty1.2.0 on both exact archived datasets:297 simulated RPCs, one report Write, exact readback and path-only OK. Ten additional native fault checks cover truncated enumeration, second-scan drift, pre-existing destination, lost Write acknowledgement and mismatched readback across the two worlds. No false success, duplicate Write or post-Write fallback occurred in those checks.

**Replay boundary:** List responses are reconstructed from recorded complete Trees; repeated scans reuse the snapshot; persistence and injected faults are simulated. No live model request, real write, hidden oracle regrade or network-latency measurement occurred. Full-agent integration is not validated by the isolated donor workflow.

The simpler thingy d4485r1 R4 width repair happens to reproduce the correct bytes for these two unquoted exports. Aika's d4795 quoted-field counterexample also reproduces: valid `SKU,quantity` followed by `"ACME, drill",0` loses its final field. We do not merge that broad comma-splitting repair. Skipping quotes avoids this counterexample but still does not verify header authority, family completeness or values; a schema-aware repair must address those explicitly.

## Integration size and encoder finding

`packing_probe.py` grafts the full donor engine before d4955r1's original loop, preserving every parent function AST. It is a sizing prototype, **not an eligible submission**. Existing LZ packing gives78074 bytes; the record's minifier followed by LZ gives70106. The additional packing variants still exceed65536; best observed is67341 bytes (1805 over), with minifier global/local renaming, no literal hoisting and the encoder correction below. Renaming prevents direct original-readable AST equality; those variants would require separate semantic integration checks even if they fit. No handler was removed merely to meet the cap.

In d3268r3 `_best`, the search stops whenever a candidate reaches its own non-overlap offset limit. That need not be the longest possible match. The fixture `abcdABCDEFGHIJabcdabcdABCDEFGHIJ` at offset18 has a nearby4-byte match and a farther14-byte match; the current encoder stops at4. `lzpack_longest.py` changes the two encoder early-stop conditions to stop only at the global maximum possible length. The token format and runtime stub are unchanged. This is an encoder optimization, not a fix to decoded program behavior.

66 byte-stream fixtures in both greedy/lazy modes round-trip through both old and new decoders. Native Monty confirms byte-identical decoded source for d4702 and d4955; their readable ASTs match too. Each saves583 bytes: d4702 becomes62626; d4955 becomes62999. These alternate bytes are offline artifacts only. They do not replace the pinned pending evaluations. Longer local matches do not guarantee a globally smallest encoding for every input.

Community r3 adds encoding/verification safeguards but deliberately retains r2 token output, so upgrading r2→r3 alone does not create more space. Ayona's alternative zlib smoke jfe0dffe16bec4c0cbaeb0bd2ecf195db failed all5 trials before inference with `ModuleNotFoundError: No module named 'zlib'`; the advertised33107-byte source is not a usable runtime solution.

## Reproduce and next action

Use the sibling record-integration and clarification-integration folders from Git4d819b8 / parent archive d4716. Python3.14.3, pydantic-monty1.2.0 and python-minifier3.4.0 were used here. `reproduce.sh` reruns the independent-world review, size probes and encoder controls. `dependencies.json` pins exact source hashes and Brain revisions; SHA256SUMS covers the package.

Publish the exact-world diagnosis and encoder component for other builders. Keep the full inventory compiler as a supported but oversized integration option. Next, evaluate a general schema-aware export repair or a smaller verified composition, with quoted-field, incoming-date, missing-SKU and persistence controls. Do not claim arithmetic improvement from these two cases, do not add a third queued full100, and do not remove the current record's stronger handlers to fit an untested export shortcut.
