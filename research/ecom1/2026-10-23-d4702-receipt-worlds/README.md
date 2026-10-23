# Archived d4702 receipt fallback evidence

This package completes the exact observed worlds for d4702r1 full100 job `jfdd875bba6ba4773a549e8703764efa9`, tasks t023 and t063. It contains no candidate implementation and makes no model-outcome or score-improvement claim.

Each trial has all 275 original events, 135 paired RPC calls/responses, 127 unique Read responses, and two Tree responses. Reassembled NDJSON matches the official sealed trace SHA-256 and byte length. Existing selected events and complete indexes were copied unchanged from the frozen d4702 audit. Only 242 missing RPC responses and two missing router requests were downloaded (487,516 bytes total); the latter allow complete trace verification. The read-only session s8138 was discarded.

| Task | Actual upload | Complete trace bytes | SHA-256 |
|---|---|---:|---|
| t023 | `/uploads/hrNh9v44_receipt_ocr.txt` | 316926 | `b7e29ddc981553c85dd0ebbdb4e6b29cd5cd7dc6bcf30d745cac4191363e6beb` |
| t063 | `/uploads/AztYLH6h_receipt_ocr.txt` | 314103 | `1df90b49c9fe780b1887da1ac6531d0ea3a286b8ab3ecc0b8b48bdf61de453d4` |

`TASK/world.json` preserves every RPC request argument and response, plus a path-keyed dictionary of exact Read responses and both original Trees. `TASK/read-ledger.json` records content hashes and event IDs. `TASK/context.json` holds full model requests/responses, identity/date outputs, final Answer and official grade. Plain upload files retain the exact original content. These are complete **observed** worlds, not snapshots of unread nodes. Both traces read 101 catalogue product files and 17 store files; the remaining nine files include policy, upload, inventory/cart and identity-related data.

The actual Tree calls are `Tree('/', level=2)` and `Tree('/proc', level=0)`. No additional subtree or level response is invented here. A future replay must explicitly derive any new subtree from the actual complete `/proc` response, or reject unmatched requests. t023 uses `/proc/stores` and `/proc/payment-ledger`, matching its AGENTS text. t063 uses `/proc/locations` and `/proc/payments`, matching its own AGENTS text. Do not normalize paths or share task worlds based on identical instruction text.

Both tasks ask the identical yes/no receipt availability question. t023 Answer sequence3820 is `FALSE(2)` / `OUTCOME_OK`, citing only security and checkout; the official zero-grade detail names the missing actual upload reference. t063 Answer sequence9618 denies purchase because the identity is an employee, with `OUTCOME_DENIED_SECURITY`; the official zero-grade detail expects `OUTCOME_OK`. These facts motivate examining evidence transfer after deterministic receipt handling declines; they do not establish that a particular transfer repair will yield the correct answer.

The source identity is the exact d4702 revision/source blob recorded by the copied official result. This is not a replay of d4353 or of a repaired candidate. No inference, mutation or new evaluation was executed during harvesting. Model requests and responses here are historical records only.

Reproduce all generated fixtures offline with `python3 prepare.py`. `python3 reproduce.py` additionally verifies all sealed files, runs reconstruction in an isolated temporary copy, and requires every generated output to remain byte-identical. The source/input provenance and session receipt are in `PROVENANCE.json` and `SESSION.json`; `SHA256SUMS.json` covers all package files except itself.

Correction: the initial README incorrectly claimed a t023 path/policy mismatch. Direct inspection of the exact archived AGENTS content disproved that sentence. Only this prose was corrected; all evidence and world data remain identical. The superseded README/seal are retained under `historical-initial-prose/`.
