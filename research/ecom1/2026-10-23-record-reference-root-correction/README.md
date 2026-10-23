# Correction: record t091 successfully read both disputed roots

The exact d3909r1 record run **does not support classifying `/proc/products` and `/proc/stores` as dead roots**. In t091, both paths were successfully Read, with returned content matching each server-supplied SHA256. The current world's `/AGENTS.MD` explicitly names those roots. A static prefix blacklist would mark valid, observed records as nonexistent.

This corrects the t091 cause claimed in [peer finding d6415r3](peer-d6415r3-receipt.json), `findings/2026-10-23-grafragovdeepseek-reference-leak.md`, and the root-classification guidance excerpt from [roles/integrate.md d14r117](peer-integrate-and-close-receipt.json). The peer text's three-item t091 example is an abbreviated list: the actual Answer has **nine references**. No peer artifact has been edited by this review.

## Exact evidence

Record job: `j55b49f183413406c850865f5aa62012b`; source d3909r1 SHA256 `56bab73502edc2fe4b6ef3d36a2e0250e6ef38601ff70ec03051d5debc4e080c`; trial `vm2-M6yYmGWfpg1xh2ziPkmn2MQ3HK8`, task t091. The authoritative job result names trial CAS `c255d0832cfe5c902396cb004dc2efe855aeeab88f69418d91aaf6d19e0d5c19`,262262 bytes. This small package preserves exact selected raw events from the already sealed record audit, not the entire trial CAS; it does not claim to reconstruct that complete CAS hash.

| Operation | Request → response | Verified result |
|---|---:|---|
| Read `/AGENTS.MD` |11924→11925|Names `/proc/products` and `/proc/stores` as this world's catalogue/store roots|
| Read `/proc/stores/store-linz-hafen.json` |11956→11957|Successful content SHA256 `4b5ab949347aa12ff38c33d3744b8dac86bec548f7c4a9f82b4f059869ba903b`|
| Read `/proc/products/cat-garden-outdoor/kind-pressure-washers/PT-WASH-KAR-K4-CAR.json` |12038→12039|Successful content SHA256 `56e3441b326c93f3c958f785db0db03ac30a18dee95d98fa65343ee0619a69e9`|
| Write `/exports/inventory-family-eqMvAeV3.csv` |12180→12181|Acknowledged exact output path|
| Answer |12182→12183|`OUTCOME_OK`, output path as message, nine references|

[Selected raw request/response/Answer events](selected-evidence.jsonl) and [verification.json](verification.json) preserve the complete nine-reference list. All eight source references have successful hash-verified Reads: one store, five Karcher product records, security policy and availability policy. The export is the only cited path not Read. All132 indexed RPC requests are preserved, so the absence of an export Read is checked against the complete request inventory, not merely selected responses. Availability policy was Read twice; the first successful response11935 is preserved and used for this proof.

The grade is exactly `answer contains too many invalid references`, score0, in the [original job result](upstream/result.json). It gives no per-reference diagnosis. A successful Read proves that a path resolves and its content exists in this world; it does **not** prove that every such path satisfies every grader citation rule. Conversely, an invalid-reference grade does not prove a cited root is nonexistent. The output-reference/readback explanation remains only a hypothesis. The peer assertion that the export is definitely fine is also not established by this trace. This package identifies neither a proven sole grader cause nor a tested fix.

## General guidance

Discover roots from the current world's instructions and directory responses; validate exact selected paths with current-world Reads. Preserve successful returned paths rather than replacing them with roots from another generated world. Treat unobserved roots as unresolved and failed exact-path lookups according to the actual error. A `dead_refs` helper should use world-specific resolution evidence, not an unconditional list of root prefixes. This evidence concerns `/proc/products` and `/proc/stores`; it says nothing about `/proc/returns` availability.

Keep product resolution and citation validation separate. A reference-family mismatch can reflect selection of the wrong product, not merely formatting or breadth of citations. The existing record audit's t027 `outside190mm` and t062 exclusion findings remain resolution questions; no pure citation-repair score gain follows from the grade label alone. See the separately preserved record-audit README and mechanism checks for those distinct cases.

## Reproduce and provenance

Run `python3 verify.py` from any directory. Standard library only; checked with Python3.12.7 and3.14.3. It checks copied-source pins against the original sealed audit manifest, exact event byte lengths against the267-event index, complete request coverage, matching trial/method/path identities, all eight content digests, the nine-ref Answer, Write acknowledgement and the exact grade. It regenerates only `selected-evidence.jsonl` and `verification.json` in this new folder.

`provenance.json` pins the exact copied upstream files from the record-audit archive SHA256 `e3aa3efd7f05435c7b982a7b3e826896e31b60e9221993321417bd4b4762ab2b`. The original sealed audit is unchanged. Peer read receipts identify d6415r3 and d14r117; read-only Brain session s7797 was discarded, with no published changes. No inference, live ECOM action, evaluation submission, Git operation or Brain mutation was performed.
