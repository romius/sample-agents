# Alternative minimum-three LZ packing review

Explores length3..130 references and128-byte literal runs, replacing the earlier length4..131 format. This changes the runtime decoder and is not format-compatible with old LZ4 streams. Exact d5204 prepack decodes unchanged; inventory packs to65030 bytes, saving262. SKU definition-only probe remains over limit at66352 bytes.

Checks pass:4255 small optimal-byte oracle inputs,44 vectors,141 checked references including distance65535,2774 length3 references, five malformed streams rejected, both exact native artifact decodes. The inventory artifact also passes216 whole-agent executions (three forms, CPython/native),27 unchanged advisory replays,408 parser and20 handler checks.

Literal cutoffs16/32/48/64/96/128 were also sized. Best65025 bytes is only another5-byte saving. Those alternate cutoff probes have Python roundtrip checks only, not native whole-agent validation. The initial boundary fixture with a3-byte suffix allowed an equally cheap literal; corrected the fixture to a7-byte suffix so a distance65535 reference is required.

Prefer the separately reviewed Huffman-over-existing-LZ4 packer: it saves6215 bytes without changing the inner LZ loop. Retain this experiment for reproducibility; do not combine formats or submit a packing-only paid run. Run reproduce.sh. No paid evaluation or queued source changes.
