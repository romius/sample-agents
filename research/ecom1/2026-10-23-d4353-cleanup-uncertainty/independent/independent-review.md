# Independent review: PASS for bounded cleanup uncertainty handling

The candidate changes only the exception branch of `i2c_cleanup` on exact d4353r1/d4354r1. I found no blocker to preserving this as an offline candidate. This review supports its error handling, not a score improvement or automatic promotion. Candidate packed source is 63,339 bytes, SHA256 `66c90c1fd2787768a1e1068007bb57c37cbcb568f206ae0dc44ff52b6da123a7` (2,197 bytes below 65,536).

I verified all 32 original seal entries and all 19 source pins. In an isolated temporary copy, the exact parent build and all nine generated artifacts reproduce byte-for-byte, including the author's 136 whole-agent executions and clean reproduction report. Original sealed files remain unchanged. Python 3.14.3 and public pydantic-monty 1.2.0 were used; the native host is a method-only `ClassInstance`. No live ECOM operations or model calls occurred.

Source inspection confirms the result returned by the error branch is accepted by `i2c_dispatch`, delivered directly through `bitgn.answer`, and marks the task answered. It does not return `None`, so a successfully delivered error result cannot trigger the later model loop. The loop returns before another Delete. The only reported confirmed deletions are prior successful RPC returns; the failing path remains explicitly unconfirmed even when the simulated server removed it before throwing. Empty DeleteResponse acknowledgements are consistent with the pinned proto. This is an acknowledgement boundary, not a re-read of server state.

I added 32 fresh complete-agent executions: eight scenarios × readable/packed × CPython/native. The controls cover the previously untested third selected deletion, HTTP 400, timeout after effect, empty exception text, a 100,000-character unknown error, Unicode error text, ValueError-shaped failure, healthy behavior, and host rejection of Answer following simulated cancellation. Assertions check the exact mutation prefix, acknowledged versus actual simulated removal, unchanged remaining contents, exact final message/outcome, one router inference only, no unknown RPCs, no later Delete or model fallback, and parity between all four forms. The long error remains bounded in stdout. In the cancellation control the attempted error Answer is rejected and execution terminates; the candidate does not claim a delivered completion or continue mutation.

The cancellation control is synthetic and does not establish the live SDK's cancellation formatter or committed cancellation behavior. The inherited broad Exception catch remains. An exception from the final Answer itself propagates; this is preferable to re-entering mutation, but leaves final delivery unconfirmed. Existing path/listing assumptions, supported instruction grammar, policy/identity handling, and any concurrent modification between listing and deletion remain outside this patch. The historical t039 failure was a malformed model action in d4702; no observed server Delete error is claimed. The exact archived world, with explicitly simulated fourth acknowledgement, is useful reachability evidence for the deterministic d4353 route, not proof that this candidate fixes t039's historical failure or improves the aggregate benchmark.

Reproduce independently from the workspace using the pinned interpreter:

```sh
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python research/ecom1/2026-10-23-d4353-cleanup-uncertainty/independent/reproduce.py
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python research/ecom1/2026-10-23-d4353-cleanup-uncertainty/independent/counterexamples.py
```

The absolute interpreter path is the current local pinned environment, not an archive dependency; requirements.txt identifies the package version for another environment. Both scripts write only under `independent/`; the parent reproduction runs in a temporary copy. Detailed results are in `reproduction.json` and `counterexample-results.json`.
