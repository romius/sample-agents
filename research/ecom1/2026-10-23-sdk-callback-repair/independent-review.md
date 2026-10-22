# Independent callback-repair review

23 October 2026. Reviewer: integration_plan. **PASS for the minimal repair, local method-only runtime reproduction and posthoc capture compatibility. No blocking finding.** These are historical-parent mechanism artifacts, not replacements for the newly promoted baseline. No hosted/paid evaluation, Brain write, Git operation, cancellation or original-source modification was performed by this review.

## Exact change and capability boundary

Both readable successors differ from their pinned parent by exactly the same replacement: define `ix_rpc(method,args)` to return the direct call `bitgn.call(method,args)`, and pass `ix_rpc` instead of the value `bitgn.call` to the single `ix_run` entry. Independently reversed that replacement and obtained the parent source byte-for-byte. The existing function bodies are unchanged. The wrapper name does not collide with a parent definition, and the source does not rebind the `bitgn` host.

The callback argument is evaluated before `ix_run` can determine applicability. Consequently the original expression fails even for non-inventory requests when method dispatch is permitted but attribute extraction is not. The new local Python function can cross the internal callback boundary while its eventual host call remains a direct authorized method invocation.

The test uses the actual public pydantic-monty 1.2.0 `ClassInstance` with `allowed_methods` and no eager/lazy attributes. I checked the installed policy source against its preserved hash (`a27e69d1df8c46a24d996b02bb4e0bcb1aea465c3c5b3d51846c78e38f7e82c6`). It distinguishes `lookup_lazy_attrs` from `call_method`; this is a real native boundary rather than the previous source-defined proxy class. Root-supplied community trace evidence motivated the repair, but this review did not independently retrieve that hosted trace. Actual service confirmation belongs to the separate hosted probe.

## Independent reproduction

Verified every original **20-file seal entry**, all **126 dependency pins**, and all **86 archive-dependency pins**. Copied the repair folder to a fresh temporary directory, redirected only output paths there, and ran the pinned build. All **eight generated source/manifest artifacts** reproduced byte-for-byte: readable, prepack, packed and manifest for each parent. Original seals and dependency hashes were rechecked afterwards and remain unchanged.

Reran the focused core verifier:

- Six native successor executions: both parents × readable/prepack/packed, each producing the exact expected CSV and the same full host history as its CPython control.
- Four exact-parent native failure controls: both readable/packed parents fail on the callback value before any RPC or model call.
- Three small native controls: direct call succeeds, method-value extraction fails, named wrapper succeeds.
- One additional independent denial control: when `call` is absent from `allowed_methods`, invoking the wrapper still raises AttributeError and the host receives no call. The wrapper does not widen permissions.

The author's full regression harness correctly replaces native execution in both the main inventory path and the separate recovery harness with methods-only `ClassInstance`, using ten-second feed/turn and 1,000-suspension limits. Its sealed results cover 3 CSV worlds, 16 fault/fallback cases, 6 benign requests and 11 recovery cases across three source forms and two runtimes: **216 executions per successor, including 108 native executions each**. I inspected that adaptation and result coverage rather than redundantly rerunning both complete suites. The 27 advisory replays, parser/handler checks and their inherited limitations are retained. The role-lookalike fixture remains synthetic; this repair review does not make it a reachable identity-output claim.

The source scan inspects decoded packed forms as well as readable forms. It identifies the one affected non-callee `bitgn.call` access in d5204/d5785 and no such accesses in the audited d4702, d4955, d6280 or successor forms. This scan is useful structural evidence, not a substitute for testing every possible host interaction.

## All frozen C/L requests remain identical after repair

Independently reran the entire capture-compatibility check: **34 original-source startup failures** (17 fixtures × readable/packed) and **68 repaired native whole-agent captures** (17 fixtures × readable/packed × two repetitions). Every repaired RPC/model/answer history equals the frozen source-created history, and every final SDK argument list is identical. All **17 C/L pairs, 34 arm requests**, have identical complete content, settings, canonical bytes/hashes and removed-field ledgers to the frozen submitted diagnostic. The fresh report equals the sealed report after removing timing fields; saved host traces are byte-for-byte identical.

This closes a specific runtime-compatibility gap in the earlier capture evidence: the original source-defined SDK proxy allowed forbidden method-value access. It does not establish that the original d5785 was reachable through the real method-only boundary. The repaired source reproduces the captures under that boundary. The d6280 diagnostic itself uses direct calls and does not contain the failing expression. Its frozen inputs and preregistration were not rewritten. L remains a post-cap transformation of C, not a separate production execution.

This is posthoc compatibility evidence, not fresh preregistration, model-benefit evidence, completed-task correctness or full100 improvement. The scripted routing, synthetic worlds and bounded evidence limitations remain.

## Artifact sizes and scope

| Historical parent | Repaired packed bytes | Remaining 65,536-byte headroom | Packed SHA-256 |
| --- | ---: | ---: | --- |
| d5204r1 | 65,307 | 229 | `1b4d188c6809b4111c499cbf0679707409e8e78da9a3e107174b9df4c9a9b2ba` |
| d5785r1 | 60,808 | 4,728 | `ac1ec39aec19ae1ff3ceb794cd95f1bcff5df017fc8c3fd586bf93dcf5921b78` |

Both preserve their parent's packing method and decode exactly to prepack source. The d5204 artifact has little remaining source headroom; passing the current cap is not capacity for arbitrary further additions.

Independent reproduction used Python 3.14.3, python-minifier 3.4.0 and pydantic-monty 1.2.0, with bytecode writes disabled. Temporary outputs: `/var/folders/px/h2tbfkd177v7w8r4xg5h7ycw0000gn/T/callback-independent-v9iqeyvp`. The original full216 suites were not repeated; the focused core, permission-denial control and all capture-equivalence executions were.

The root reports the newly verified/promoted d3909r1 record at 94.11366, with its exact-source audit being handled separately. This package does not audit or replace that record. Reuse the minimal callback primitive and regression tests only where the new baseline's exact code shows the same applicability; do not wholesale-integrate these older parent stacks or infer a next-full100 candidate from this review. The separate BASELINE-SCOPE.md makes the same boundary explicit.

The archive builder's collection/reproduction design includes normalized workspace-relative dependency paths, the pinned public policy source and external runtime versions; it preserves the original seal and excludes generated publication/archive artifacts. I verified its input closure and the same core/capture/rebuild operations independently. Final ZIP sealing is subsequent author work and its eventual hash is not preclaimed here.

This new review sits outside the original 20-file seal. It modifies none of those sealed artifacts.
