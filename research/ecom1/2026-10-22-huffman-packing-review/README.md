# Huffman packing with unchanged decoded agent

The submitted d5204r1 inventory agent is65292 bytes, only244 below the65536 limit. A canonical Huffman outer layer around its existing LZ4 tokens reduces the same prepack source to59077 bytes:6215 saved,6459 headroom. This is a build/headroom improvement, not an observed benchmark-quality improvement. No provider, agent logic, queued source or official baseline changed.

Exact inventory artifact SHA256:0a75eafef17089209235a33b21d0f0e242fb6d5a78149cc9b85461b96fff4d7e. It decodes to prepack SHA256:597e2791292cf23b58d5eeba88e0878f34725c3c86d95ee9605995a189dd7259. Readable source remains d5206r1, SHA256:aef93a8c2b25feeb097e70a063d5ffff6c15f52622a3e4e058859901b0a921e1. Exact parent is locally frozen and in Brain archive d5211r1 (Git cedfcd64b9ca7252240d1acfc249d4ea9541f4c2).

Format:4-byte big-endian decoded-token count,256 canonical code-length bytes,MSB-first payload with zero padding. Tree construction is deterministic by frequency/minimum symbol. Inner LZ4 loop is AST-identical to the parent. Build-time decoder strictly checks framing and codebook validity. Runtime trusts the fixed build-validated embedded payload; it is not an untrusted-stream validator and accepts some malformed inputs the build rejects.

Initial native testing rejected int.from_bytes as unsupported. Replaced only that runtime operation with four-byte arithmetic before the passing checks and before any evaluation submission. No paid run was submitted for either variant.

Evidence:549 roundtrip vectors,64 brute-force optimal-cost cases,six strict malformed rejections,two exact native artifact decodes. Independent review adds569 vectors,9841 exhaustive ternary strings,256 brute-force tree-cost cases andseven native exact-token comparisons. Actual code width maximum11. Whole-agent suite passes216 executions,27 unchanged advisory replays,408 parser and20 handler checks. Advisory replays have the inherited incomplete-world limitations; they are not fresh full100 scores. Single local decode timings in results are observations, not latency guarantees.

The unused SKU-definition-only source also packs to60256 bytes (SHA256:23fddac7313fd6b7d35ad8b174b2697cd5a06e45bc8d2406aeee3d9baa4c1b8e). It has no routing hook or demonstrated model outcome and is NOT an evaluation candidate. Only its decoder equivalence, not full semantic integration, is claimed.

Use this packing process for the next independently justified candidate after refreshing the strongest verified baseline. Do not mutate queued revisions or spend a paid run solely on compression. Run reproduce.sh after restoring dependency folders with their pinned sources. Build output size-results.json deliberately says validation pending; passing evidence is in codec-results.json, independent_review_results.json and integration-results.json. Re-running tests refreshes result timings; artifact bytes must reproduce exactly.
