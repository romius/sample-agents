# Narrow receipt fallback evidence plan

Status: **plan only**. No candidate source, new model call, benchmark submission or production change. The exact parent is d4353r1/d4354r1; this is separate from OCR normalization, inference retries, Exec404 and cleanup uncertainty handling.

## Applicability and observed counterexamples

`prepare_plan.py` verifies that d4353 and observed d4702 have identical ASTs for receipt availability, source selection, item/product/store resolution, reference merging and read-provenance helpers. The d4353 readable SHA is `f898132a754187b0052a637e1ca4caaccdd3ac46f72df80bc11d2b37b3737d0b`. Exact function locations and hashes are in `applicability.json`. This establishes the same source boundary, not the same score or world in the two live runs.

| Actual case | Successful helper Read | First fallback model request | Observed gap |
|---|---|---|---|
| t023 | Availability policy3567; upload3571, SHA098af54b… |3818, eight messages | Neither full OCR nor its path is present. Model immediately answers based on employee identity and omits upload grounding. |
| t063 | Availability policy9365; upload9369, SHAb395a9a5… |9616, eight messages | Neither full OCR nor its path is present. Model denies a read-only availability question because the identity is not a customer. |
| t043 control | Availability policy6347; upload6351, SHAdc2ff9f1… |6376, later request with22 messages | OCR is already fully visible after the model rereads it. Product grounding still fails. Duplicate transfer is not a solution here. |

The exact three Read/model-request witnesses per case are copied byte-for-byte. The complete audit remains sealed separately and was published as Brain archive6775/finding6778. No sealed audit file is changed by this plan.

`receipt_availability` directly calls Read for its policy and selected upload. If parsing or unique product/branch resolution fails, it returns None after printing a diagnostic. Those direct reads do not call `note_result`/`note_policy_read` and do not append observations to `messages`. The caller proceeds through the normal helper chain and then the model loop with its earlier bootstrap. Thus the model can have less evidence than the deterministic helper already read.

The existing `rcp_request` gate is narrow: one of three complete benign receipt wordings, an employee user ID and the exact RoleEmployee role. `rcp_upload` selects the explicitly named upload, or a unique matching file; multiple unnamed files produce no selected path. Preserve those rules. Do not broaden identity matching or invent a “latest” file.

## Proposed smallest boundary

Capture a **per-invocation pending record** only inside this receipt helper, containing the successful availability-policy Read and the one actual successful selected-upload Read. Do not scan or serialize WORLD, LEDGER, global caches, catalogue records, baskets, staff or other customer records. Do not issue extra Reads to reconstruct them.

Only if the helper returns None after that upload was successfully read, and the agent still needs its normal model fallback, consider transferring those two observed sources using the existing Read observation format. Preserve original bytes, actual request/response path, content hash and any truncation metadata. The upload remains source data, not a new instruction or authorization. The availability policy is the actual file already read; security policy still governs. If the helper answered, never alter its answer or prompt path.

Use normal provenance handling only for those successful Reads, rather than marking every discovered path as read. Explicitly distinguish the context effect from automatic reference repair: registering an upload in LEDGER may make t023 pass a reference check even if the model still gives an unsupported identity-based explanation. Offline diagnostic variants should isolate context-only, provenance-only and combined behavior with a fixed simulated final answer before any model experiment. No semantic success should be inferred from reference addition alone.

Deduplicate by the exact observed source path/content hash and presence of its complete existing observation, not merely a filename substring. A prior reference or a truncated excerpt is not full evidence. Already-present matching observations should leave the request byte-identical. Conflicting versions require an explicit uncertainty path; do not overwrite an earlier source silently or combine inconsistent documents.

## Payload and history bounds to preregister

Proposed conservative test limits, to be validated against the actual SDK encoder before implementation is approved:

- At most one selected receipt source and one already-read availability policy.
- At most12KiB serialized upload observation and16KiB serialized combined pending observations.
- The complete serialized message list after transfer must fit within54KiB, below the existing56000-byte trimming threshold; verify the actual SDK0.3.7 request remains below65536 bytes with model/provider/settings included.
- Measure UTF-8 bytes **after the same JSON escaping used for dispatch**. Character counts are insufficient, especially for Unicode, quotes and backslashes.
- Never silently truncate a receipt and treat it as complete. For an oversized or already-truncated source, transfer only a bounded path/hash/explicit-incomplete descriptor if it fits, allowing normal narrower retrieval. If even that cannot fit, preserve the original fallback and record a bounded diagnostic.
- Append at the final transition to the model loop only if still unanswered. Review `bootstrap_count` and the existing pair-trimming logic together, so source observations are neither accidentally removed nor allowed to exceed the protected-prefix budget. Stress-test long subsequent histories.

The exact witness projections are small: Python default-JSON request sizes would change from16730 to19352 bytes for t023 and16699 to19134 for t063 if both observations were appended. These are offline size estimates, **not** actual SDK wire-conformance results or model outcomes. Blindly appending to the t043 control would duplicate already visible data; it is included to prevent that design mistake.

## Required controls before any candidate or evaluation

| Control | Required result |
|---|---|
| Actual t023/t063 helper decline | Transfer exactly the selected successful policy/upload evidence; preserve instruction, model, provider and inference settings. No extra RPC or mutation. |
| No receipt request / non-employee / appended override / invalid identity | Existing gate behavior and request bytes unchanged; no source transfer. |
| No upload, ambiguous unnamed uploads, zero or multiple prefix matches | No invented source, path or content; preserve uncertainty. |
| Explicit named upload among several files | Only that actually read source is eligible; no other files included. |
| Policy wording changed or policy Read failed | No implied validation and no upload transfer from an unexecuted branch. |
| Upload Read failed or returned no valid complete content | No successful-read provenance fabricated. Preserve the original error/fallback. |
| Helper success | Exact old answer, refs, actions and absence of fallback inference unchanged. |
| Already fully transferred source, including t043 | No duplicate observation or unnecessary new request bytes. |
| Path only / partial excerpt / truncated source | Do not claim the complete OCR is already present or silently promote partial evidence. |
| Foreign basket/staff/payment/catalogue entries elsewhere in memory | None copied, cited, reread or promoted by this mechanism. |
| Injection text within uploaded OCR | Preserve existing instruction hierarchy and denial controls; data cannot grant authority or cause mutation. |
| Long ASCII, multibyte Unicode, escaped newlines, quotes/backslashes, near-limit bootstrap | Exact byte bounds and honest incompleteness; no request-cap breach. |
| Long subsequent history | Correct pair pruning, bounded protected prefix and no inadvertent duplicate source. |
| Same path with conflicting bytes/hash | Explicit uncertainty; no silent replacement or merged invented record. |
| Fixed simulated final OK/denied/clarification answers | Separate message-transfer effects from automatic ref additions, and preserve security-specific ref filtering. |
| Read-only receipt query followed by attempted Write/checkout | Transfer itself performs no action and does not broaden permission; existing action policy remains authoritative. |

Use public native Monty with the method-only ClassInstance host, plus readable/packed parity. No first-class BitGN method extraction. Preserve original request/provider settings and source-size limits. Snapshot actual host calls and model request bytes at each boundary; structural tests are not an outcome-only semantic scorer.

Before claiming exact whole-agent replay of t023/t063, harvest the remaining archived RPC responses needed for their world-building path. The current audit intentionally retains selected loss events, not both full worlds. A different full-world fixture with these OCR texts would be a declared overlay and could only support a mechanism test, not a same-world live comparison. t043 is a useful visibility/duplication control but not proof that source transfer repairs its separate grounding problem.

After structural validation, a separately authorized, counterbalanced next-action diagnostic could assess whether the model uses the receipt and availability policy, preserves uncertainty about corrupted SKUs, and avoids false role-based denials. Inspect messages and factual support manually. Do not count a reference-only grade change as correct task reasoning, combine this with unrelated candidates, or predict a full100 gain from these selected losses.
