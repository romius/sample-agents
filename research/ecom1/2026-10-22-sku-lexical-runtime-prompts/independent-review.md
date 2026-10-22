# Independent runtime-capture review

23 October 2026. Reviewer: integration_plan. **PASS for offline request construction after the Tree-depth and AGENTS-root corrections. No remaining blocking finding in the reviewed capture.** This is not a model-performance result or authorization to dispatch calls. Any future diagnostic still needs its own frozen design and execution review.

## Independent checks on the final captures

Independently executed all 17 fixtures against both immutable readable and packed sources in CPython 3.14.3 and pydantic-monty 1.2.0: **68 final executions passed**. Compared each complete captured trace, answer stub, and three SDK invocations to the saved artifacts. Verified all 11 dependency hashes and 22 artifact hashes. Maximum independently observed final execution time was 0.125 seconds; native limits are ten seconds for feed/turn and 1,000 suspensions. This is a fresh full rerun after the corrections, in addition to the initial 68-execution review.

The source constructs its own index through Tree and Read. No WORLD injection is present. All 74 synthetic product records across the 17 fixtures are actually read; their supplied JSON contains exactly the fixture's primary fields, excluding only the transport `_path` key. The current `world_tool`, scope parser, bounded helper, and index builder match the earlier reviewed source by AST.

All 17 complete C requests equal the final captured SDK call, including model and settings. Each full request contains its original fixture instruction exactly as a user message. Every L request changes one observation message and removes only the two sibling lexical arrays after selection and capping. Exactly 104 fields are removed across the pairs. Restoring their ledger recreates C. Query, original matches/scores/order, sibling facts/order, counts, truncation metadata, policy, and other messages/settings remain identical. The model is `openai/gpt-oss-120b`, with 2,048 maximum completion tokens, medium reasoning, and temperature zero. Final compact JSON totals are 251,507 bytes for C and 245,009 for L; these are not token counts or price estimates.

U4's exact glossary is delivered through an actual catalogue-policy Read and is present exactly once in both arms. N3's shared catalogue policy includes the excluded-product exception. Thirty-seven of the 38 explicit source-fact assertions are visible in the captured catalogue observation, preserving missing/null/empty/false/true distinctions. The remaining assertion is deliberately hidden F2 evidence, discussed below. Oracle labels themselves are not supplied to the agent.

## Corrections independently verified

The original simulated Tree ignored positive depth. Its root bootstrap request asks for level two but received deeper brand directories and SKU filenames. The archived t091 Tree response at sequence 12117 stops at depth two, omitting directory children there. The corrected Host implements root depth zero, positive depth cutoff, and level zero unbounded, matching the pinned `ecom.proto` contract. Independently checked levels 1–4 and zero for all 17 worlds, including omission of children at the cutoff. All final captured root-bootstrap observations stop at depth two and contain no SKU filenames. The separate `/proc` level-zero traversal still exposes every fixture product for actual indexing. The archive holds responses, not archived request arguments; current source and the proto establish the request semantics. Equality between arms alone would not have resolved the original extra evidence.

The scaffold also combined archived AGENTS naming `/proc/products` with a catalogue policy and synthetic files using `/proc/catalog`. Verified the final AGENTS body equals the preserved archived response at sequence 12119 with exactly one `/proc/products` → `/proc/catalog` replacement. All remaining AGENTS bytes and metadata are unchanged apart from the correctly recomputed digest. Original security and availability policy response objects remain exactly equal to their archive. Before/after content hashes and the reversible clause replacement are recorded in `scaffolding-provenance.json`. This is a disclosed synthetic fixture adjustment, not evidence that the combined context occurred in a live workspace.

## F2 interpretation and limits

F2 indexes **all 32 products**. Actual directory traversal groups brands; the top two matches are P-N00 and P-N01, both in the Nera family. Consequently 16 siblings are eligible, and the cap exposes P-N00 through P-N09. P-N15 is truncated; P-O15 belongs to a family not selected for the attachment, although it is indexed. The earlier prebuilt-WORLD matrix interleaved families and expanded 32 eligible siblings. This difference is preserved, rather than adjusting ranking to reproduce the artificial index order.

The hidden supporting records are full-fixture facts, not model-visible evidence. A subsequent assessment must allow justified further retrieval or preservation of uncertainty and must not require identification of hidden SKUs. Truncation cannot establish global absence or uniqueness. Likewise a unique visible positive property does not prove global coverage while the helper explicitly marks coverage unverified.

C/L isolates removal of two sibling diagnostic arrays, not all lexical information: original scores, ordering, query text, and shared guidance remain. Request length also changes, so this two-arm design cannot separate semantic-label effects from length/attention effects.

The scripted router and first action establish a controlled path, not real model choices. Final completion is an inert stub. Tree/List/Read are reconstructed synthetic transport, and captured SDK arguments are not private HTTP wire bytes. No model decisions, semantic outcomes, paid calls, grading, full100 score gain, or production readiness were tested. No source, fixture, production candidate, completed diagnostic result, or Brain document was changed by this review.

## Final pins and reproduction

The independently rerun source remains d5785r1 packed (`832be81a5fafec378320d42f3e5697cea00197dfe9bfbb061b2073880a203765`) / d5789r1 readable (`0f7925c41f2783b6617ec7777757bec6fee5971f483159e26b32fae8082f7c41`), with fixture SHA-256 `c5d6199c9856f05aa6124e0d89348b7db522b735869f09f1fded97b60fe855c9`.

| Final artifact | SHA-256 |
| --- | --- |
| capture.py | `23b0ad73a34376be0dae1908a062eb26aefab214231c1c7300e5e876ad10e5bb` |
| results.json | `a770f30a8c502bab0f36bd561fa6d3d9b859521367dc22a32528da8c114c223e` |
| DEPENDENCIES.json | `88b79794912d5f8ad3bade09574d61589f7febab20c1b76c7d8af79d669d0ea1` |
| worlds.json | `ca513e0b7f864b36ebb125c0d22abfc52d98971afb6ee35bb03ae3e00c894876` |
| host-traces.json | `8726d6011c25b155faca4a84accaf52b5f730017ec6c275e002b3f6e8f8984a6` |
| scaffolding-provenance.json | `11f4a74a5244bb31d7ed83c1ef6809c1132fb873e8622c4d6828234743f4da6c` |
| tree-depth-evidence.json | `a408010fea1ea90b8ce23c360549feb3b13b59a7ef7ec9f192858583aeda2193` |

The read-only independent rerun imported `capture.py` with `PYTHONDONTWRITEBYTECODE=1`, loaded the pinned fixtures and sources, called `scaffolding`, `world`, `execute` for each source/runtime combination, and compared every returned capture to `host-traces.json`. It called `make_pair` and compared every returned field to the saved request files. Separate assertions verified all dependency/artifact hashes; exact primary product JSON; the AGENTS one-reference edit and archived other policies; Tree cutoff and full indexing; exact SDK parameters; and every visible oracle field including type-sensitive null/false checks. The environment was `UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python -W ignore::SyntaxWarning`. No capture output was regenerated by the reviewer.
