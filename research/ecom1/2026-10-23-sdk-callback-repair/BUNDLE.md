# Deterministic repair evidence archive

The archive contains workspace-root-relative paths for both successors, the exact d5204/d5785 readable/prepack/packed parents, audit parents d4702/d4955/d6280, build and test dependencies, original and new capture evidence, independent reviews, and the pinned public `pydantic_monty/class_instance.py` policy source. This public policy file is preserved for inspection; Python/minifier/Monty remain externally installed dependencies with recorded versions. It is not represented as a standalone replacement for the Monty package.

Run from the workspace root:

```sh
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python research/ecom1/2026-10-23-sdk-callback-repair/build_archive.py
```

The builder requires the independent repair review before sealing, and enforces Python 3.14.3, zlib build/runtime 1.2.12, python-minifier 3.4.0 and pydantic-monty 1.2.0. It writes `repair-evidence.zip`, `archive-manifest.json` with every member's hash/size, and `archive-verification.json` with the ZIP hash/size and checks. Those generated outputs, Python caches, other ZIPs, and publication/submission documents are excluded from the ZIP. The existing original 20-file SHA256SUMS is preserved unchanged; it does not seal the later archive additions or include itself.

All member names are normalized from resolved paths under the workspace; the protocol contract is `proto/bitgn/vm/ecom/ecom.proto`, never a `../` member. Entries are sorted with fixed 1980-01-01 timestamps and regular-file mode 0644, using ZIP_DEFLATED level9. Two writes must match exactly, as must a third write using the builder from an isolated extraction. Reproducibility is within the recorded Python/zlib runtime, not across arbitrary compressors.

Isolated extraction rebuilds both candidates, checks all eight source/manifest files byte-for-byte, and runs the focused method-only ClassInstance tests: six candidate/form native worlds against the CSV oracle and CPython history, four original-parent startup failures, and three direct-call/attribute-load/wrapper controls. It also reproduces the 68 native repaired capture runs and 34 parent failures, requiring the saved full histories and canonical C/L request hashes to match. Original capture timing bytes are preserved in the archive; fresh timings are compared only after excluding timing fields, and only temporary extracted files are restored. The complete 216-case suites are included with their prior results and are not redundantly rerun while sealing.

All original member files are rehashed unchanged before writing the archive. No sealed probes/root files, original inputs, Brain content, Git history or live evaluations are modified.
