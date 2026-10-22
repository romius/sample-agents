# Future readout protocol — no dispatch authorization

The source is prepared but unsubmitted. This file describes evidence collection only if the root later separately authorizes and completes the diagnostic. Do not create another run to repair missing logs automatically.

## Why stdout is metadata only

Community evidence d6210, supplied by the root agent during this preparation, reported failure on the 17th result print: stdout had reached approximately 63,000 bytes and the next print would bring it to 69,158, above 65,536. Its inference responses remained in immutable response traces. Consequently this diagnostic preserves the exact 68-call inference plan but logs only bounded metadata. It never prints complete replies, reasoning, errors or cost objects and never calls usage().

The stdout protocol is:

- `SKU_DIAGNOSTIC_BEGIN`: fixed purpose and planned logical-call count.
- `SKU_DIAGNOSTIC_REQUEST`: planned ordinal, before the call. This remains useful if the call never returns.
- `SKU_DIAGNOSTIC_RESULT`: fixed step metadata (ordinal, case index/name, arm, repeat, canonical request hash), status (`response`, `error`, or `cancelled`), response ID prefix of at most 32 characters, finish-reason prefix of at most 16 characters, and error preview of at most 32 characters when applicable. A response status does not certify valid action syntax or semantics.
- `SKU_DIAGNOSTIC_END`: bounded integer attempted/response/error counts, only after the whole loop completes.

Character caps are tested under worst-case JSON escaping: astral Unicode requires twelve ASCII bytes per character. The largest tested full-run output is 60,216 UTF-8 bytes. Request/case/hash metadata is frozen trusted data; unbounded provider strings cannot enter stdout. The cancellation detector scans the whole exception before rethrowing; a cancellation word beyond the preview still stops subsequent calls.

## Required evidence harvest

1. Preserve the immutable submitted source revision/blob, SDK version, job/run/trial identifiers, exact call-plan and fixture hashes. The intended artifact is the one pinned in the current manifest. A carrier grade must never be presented as research success or a new record.
2. Retrieve all immutable inference request, response and error events and reported usage, plus diagnostic stdout and the terminal run status. Raw reasoning/content must come from those events, **not** from stdout prefixes. If raw events are inaccessible or missing, label evidence incomplete and retain the unknown; do not reconstruct content from metadata or substitute another run.
3. Reconcile planned ordinal with actual logical call identity and request contents. Use source-level SDK inputs where available; document any verified backend normalization rather than guessing provider/private-wire transformations. Preserve provider retry attempts separately. A response-ID prefix is only a hint, not a unique key; full event IDs and exact request evidence are authoritative.
4. Confirm every attempted call's full request equals its frozen arm, including original instruction, settings, full shared policy/identity history, U4 glossary, bounded sibling rows and F2 metadata. If a call is mismatched, label a protocol deviation and exclude it only from causal interpretation while still reporting it in accounting. Do not selectively omit an unfavorable output.
5. Keep all 68 planned entries. For each, link the final response/error or mark unattempted after cancellation. Preserve malformed/length-truncated output and raw error context. Do not merge SDK retries into extra experimental repeats. Do not automatically retry provider errors or cancellation.
6. Apply the separate manual rubric in `PREREGISTRATION.md` to visible evidence and raw final content. Populate the blank review sheet; no runtime output is itself a semantic score. Report deferred tool requests without executing them, and keep ambiguous/contradicted assertions in clarifications visible.
7. Compare both repeats within every fixture and report all C/L disagreements and positive controls, errors, malformed replies and cancellations. Preserve reviewer disagreement and cite the precise response/evidence. No automatic follow-on evaluation, production edit or full100 promotion follows from this readout.

Fake-host verification demonstrates code paths and log bounds only. It does not verify actual transport cancellation, billing behavior, event retention or backend model performance; those require the future immutable records if a run is separately authorized.
