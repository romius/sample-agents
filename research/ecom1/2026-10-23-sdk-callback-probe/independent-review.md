# Independent SDK callback probe review

Reviewed by `score_opportunities` on 2026-10-23. Result: **passes offline review for the narrowly scoped actual-SDK diagnostic**. This is not evidence that the full commerce agent starts successfully or achieves any task score. No Brain calls, model calls, submission, Git edits, or production-source changes were performed by this review.

The exact `agent.py` is 1,027 UTF-8 bytes, SHA256 `223cb4dc6ad9b6226f5dd2ce1aaf39001af7c840e902cc65be021866d86ef1a3`. Its only SDK attributes are `call` and `answer`. Source inspection confirms exactly two successful-path `Exec` requests, each with the literal arguments `{"path":"/bin/id"}`: one direct method invocation and one via a named guest function passed through `invoke`. The captured method value is never invoked. There is no inference request, tool-selection generation, world write/delete, or task execution. A successful probe emits bounded mechanism metadata and one explicitly unsupported carrier answer. Identity stdout is compared, not printed.

I independently reran the supplied verifier under cached Python 3.14.3 and installed `pydantic-monty==1.2.0`, with 10-second feed/turn limits and 1,000 suspensions. All four checks passed:

| Host / control | First-class method access | Exec calls | Answers | Result |
| --- | --- | ---: | ---: | --- |
| Ordinary Python SDK object | Allowed | 2 | 1 | Both paths return identical stdout |
| Native method-only ClassInstance | Raises AttributeError | 2 | 1 | Named callback still succeeds |
| Native mismatched identity | Raises AttributeError | 2 | 0 | Assertion rejects unequal stdout |
| Native call capability denied | Raises AttributeError | 0 | 0 | Direct call fails closed |

The rerun reproduced `verification.json` byte-for-byte; all ten existing dependency pins still match. The actual installed public `class_instance.py` hashes to `a27e69d1df8c46a24d996b02bb4e0bcb1aea465c3c5b3d51846c78e38f7e82c6`, matching the archived reference. It separately gates `allowed_methods` and `lazy_attrs`; the test does not pretend to inspect the private Brain SDK wrapper.

The archived monitor supports 100 failed executions and zero recorded model usage for community job `j7d18b4ada01445aca2ebe6bea204d732`. The preserved first failure tail is a slice of event 6 (90,814 total bytes) ending at decoded source line 1369 with `AttributeError: 'BitGN' object has no attribute 'call'`. The source excerpt contains the relevant first-class expression `ix_run(bitgn.task()["instruction"],bitgn.call)`. These support the concrete callback-boundary hypothesis. This probe package does not independently preserve and audit all 100 complete failure bodies, so it should not claim that every failure's terminal exception was individually inspected here. The upstream fake-SDK success receipt explains the exposure gap but is not evidence of real SDK compatibility.

The probe deliberately checks nonempty, equal stdout rather than parsing role syntax or checking an exit-code convention. Consequently, the actual SDK trace must still confirm both responses are successful `/bin/id` identities; equal nonempty error text would not establish that. This is an interpretation limit, not a reason to broaden this diagnostic or alter its pinned source. A live success can establish the named callback crossing the actual method boundary in this carrier context only. It cannot prove handler semantics, full-agent startup, lookalike-role reachability, or score improvement.

Reproduction (from `/tmp`, substituting the repository absolute path):

```sh
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python /Users/Roman_Sinyakov/Documents/Personal/bitgn_pac1/sample-agents/research/ecom1/2026-10-23-sdk-callback-probe/verify.py
```

No blocking source or test defect found. Preserve this review alongside the exact source before the separately authorized one-trial SDK run; interpret that run using its actual request/response events and accounting.
