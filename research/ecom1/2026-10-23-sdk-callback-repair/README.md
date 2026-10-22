# Method-only SDK callback repair

These are separate offline successors of exact d5204r1 and d5785r1. Submitted source bytes, frozen lexical diagnostic inputs, and preregistration remain unchanged. No Brain edit, model request, hosted diagnostic, full100 submission, or Git commit was performed here.

The root reported a new completed community run, `j7d18b4ada01445aca2ebe6bea204d732` / `d4007r1`, with all 100 trials failing before model calls. Its error is `AttributeError: 'BitGN' object has no attribute 'call'` when passing `bitgn.call` into `ix_run`. This root-supplied live evidence motivated the repair; this directory independently reproduces the capability boundary locally and does not claim to have retrieved that live trace.

## Reachability and exact change

Monty's actual `ClassInstance(host, allowed_methods={...})` permits calls to approved methods but, with default `eager_attrs=None` and `lazy_attrs=None`, does not expose those methods as readable attribute values. The previous source-defined SDK class allowed ordinary bound-method extraction and therefore masked the startup failure.

The vulnerable expression evaluates the callback argument **before** `ix_run` checks whether the request is applicable. Consequently a benign non-inventory request also fails before reaching fallback, RPCs or the model. The exact d5204 and d5785 readable/packed parents reproduce this on both archived inventory worlds and a benign request, with zero RPCs, writes, answers and model calls.

The only source change is:

```python
def ix_rpc(method,args):
 return bitgn.call(method,args)

IX_RESULT=ix_run(bitgn.task()["instruction"],ix_rpc)
```

Removing that new function and reverting the one callsite reproduces the original source byte-for-byte. Every pre-existing function AST remains identical. Direct method calls remain subject to the same host policy. This repairs a reachable startup failure; it does not establish downstream task correctness or score improvement.

| Parent | Successor bytes | Headroom | Successor packed SHA-256 |
| --- | ---: | ---: | --- |
| d5204r1 | 65,307 | 229 | `1b4d188c6809b4111c499cbf0679707409e8e78da9a3e107174b9df4c9a9b2ba` |
| d5785r1 | 60,808 | 4,728 | `ac1ec39aec19ae1ff3ceb794cd95f1bcff5df017fc8c3fd586bf93dcf5921b78` |

Each successor has its own `readable.py`, `prepack.py`, `agent.py`, `manifest.json` and `integration-results.json` under its parent-named subdirectory. Original packing methods are preserved: minimum-cost LZ for d5204 and Huffman over minimum-cost LZ for d5785. Both decode exactly to their prepack source and fit the 65,536-byte limit.

## Verification

`verify.py` uses real native `ClassInstance` method-only exposure, not an invented proxy or AST rewrite. It demonstrates direct-call success, two method-value failures, and named-wrapper callback success. It audits every non-callee `bitgn` attribute in readable and decoded packed sources: one `bitgn.call` value in each d5204/d5785 parent; none in d4702, d4955, the short d6280 diagnostic, or either successor's three forms.

Each successor passes the full 216 inventory/recovery regressions: 3 CSV oracle worlds, 16 fault cases, 6 benign requests, and 11 recovery cases across readable/prepack/packed × CPython/native. **108 native executions per successor use the real ClassInstance boundary**, including the recovery harness. Native limits are 10 seconds per feed/turn and 1,000 suspensions. All six forms/runtimes have identical outputs and preserve the existing CSV oracle, fallback, recovery and write behavior. The suite also retains its 27 advisory replays and parser/handler checks. Advisory replay/model-capture limitations remain those of the original suite; this is not a live grader.

`RUNTIME.json` pins Python 3.14.3, python-minifier 3.4.0, pydantic-monty 1.2.0 and the actual ClassInstance policy source hash. `DEPENDENCIES.json` pins original source/build and replay/fixture inputs. Source warnings about the inherited `\d` string are unchanged; reproduction commands suppress only those SyntaxWarnings.

## Posthoc C/L capture compatibility

The submitted d6280 diagnostic contains only direct SDK calls and has no affected method-value expression. Its frozen requests were captured from original d5785 using a source-defined SDK class, however, so those captures did not previously establish reachability through the method-only runtime boundary.

`verify_capture_equivalence.py` records that gap explicitly: all 17 fixtures × original readable/packed forms (34 runs) fail at startup through ClassInstance with no model or RPC calls. It then executes the repaired d5785 for all 17 fixtures × readable/packed × two repetitions = **68 native whole-agent captures**, using only method-authorized ClassInstance and the preserved fixture worlds/host behavior. Every full RPC/model/answer history equals its frozen capture; all 17 C/L pairs (34 arm requests) have identical full histories, settings, source-level SDK parameters and canonical request bytes/hashes to the submitted diagnostic. The exact final SDK argument list also matches.

The L arm is still derived by deleting only the same two lexical arrays from already-selected rows, exactly as preregistered; it is not a separate production execution. `capture-equivalence.json` and `capture-host-traces.json` are new **posthoc runtime compatibility evidence**, not edits to frozen inputs, a new preregistration, an automatic semantic score, or proof of production completeness. The source-defined routing/fixture limitations remain. All frozen capture/diagnostic files were rehashed unchanged afterwards.

## Reproduce offline

From the workspace root, using the recorded cached runtime:

```sh
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python -W ignore::SyntaxWarning research/ecom1/2026-10-23-sdk-callback-repair/build.py
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python -W ignore::SyntaxWarning research/ecom1/2026-10-23-sdk-callback-repair/verify.py
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python -W ignore::SyntaxWarning research/ecom1/2026-10-23-sdk-callback-repair/verify_capture_equivalence.py
```

The root is preparing a separate minimal hosted SDK diagnostic to confirm the real service boundary without LLM calls. Hosted verification and any later evaluation/publication decision remain separate. Independent review has been requested from integration_plan; local checks do not substitute for that review.
