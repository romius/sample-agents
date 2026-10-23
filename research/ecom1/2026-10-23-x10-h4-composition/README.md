# X10 + H4: four-arm offline composition review

**The literal H4-before-fuzzy composition is unqualified.** It completes both selected archived receipt checks, but introduces three concrete resolver guard bypasses. No fix was silently applied, no evaluation submitted, and no full100 or general security readiness claimed.

## Exact arms and source boundary

| Arm | Packed bytes | SHA256 |
|---|---:|---|
| d4353r1 |63,211|588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e|
| d4353 + H4 only |63,380|ae15cefc7d739ef6331ce646f24534ca90365a23133bdcf94103f6df6680c4af|
| Exact X10 d6633r1 |63,589|e58220a01be07757cfd722329ccdaf8d55758af4b9a7d75b86c5a63799504d2d|
| X10 + H4 before fuzzy |63,706|ee855ab6399676fafcda471e89855169ffca66584702897f24e523d0781998d0|

`build.py` verifies exact parent/X10 decoded payloads and retains the original packed files for those arms. Occurrence-aware AST comparison matters: the source defines `rcp_items` twice with an intervening alias. X10 changes only the first `rcp_items`, `rcp_product`, and adds `rcp_dist`; the wrapper stays unchanged. Each H4 adaptation changes only `rcp_product` and adds `rcp_drop1`. The H4-only arm is byte-identical to the separately frozen peer package (seal263ed086…). Exact copied donor diff, peer source/build/review context and dependencies are retained under `upstream/`.

Branch order is preserved literally: original exact/price-prefix matches; H4's same-price single-deletion truncated-prefix candidates; only if no hits, X10's fuzzy nearest-distance selection and global-price rival guard. The guards in the last branch are skipped when H4 supplies a hit.

## Actual archived worlds and stock oracle

The two worlds are the complete saved **d4702 t023/t063** observed worlds, replayed with all four sources. They are not live d4353 runs or paired full100 worlds. The host uses exact archived Read envelopes and RPC responses, with no derived response or unmatched call. Original router and fallback response bodies are fixed stubs. One inference boundary means router only and a deterministic helper answer; two means router plus frozen fallback, not fresh model behavior.

| Actual world | d4353 resolved | H4 only resolved | X10 resolved | X10+H4 resolved |
|---|---:|---:|---:|---:|
| t023 |2/4|2/4|4/4|4/4|
| t063 |2/4|3/4|3/4|4/4|

X10 repairs the damaged nontruncated identifiers in t023 and the drill-bit identifier in t063. H4 repairs the truncated saw fragment in t063. Each alone still leaves a different t063 line unresolved; together they resolve all four.

The independent manual transcription/oracle is in `analyze.py` and `availability-analysis.json`. Each product identity, actual price, branch address, explicit inventory row, policy and content hash is retained. The policy specifies same-day `max(on_hand - reserved, 0)` and excludes incoming stock for today's request. Both branches are open; no absent inventory row is silently guessed as zero.

- t023 requires1/1/1/1; actual same-day stocks are0/0/0/0. X10 and composition deterministically answer `FALSE(2)`, with upload, branch and four product refs actually Read.
- t063 requires1/12/1/1; stocks are0/7/0/0. Only the composition deterministically answers `nein`, with the same complete grounding pattern.

The bare-parent t023 frozen fallback also ends with `FALSE(2)` but lacks receipt/product evidence. Therefore answer-token equality alone is not a resolution or reasoning improvement oracle. Similarly, an incorrect SKU choice could still produce the right negative availability token in these shortage-heavy worlds.

## Concrete guard bypasses

Neutral resolver-only fixtures use receipt key `PT-DRL-MAK-ABCDEF.` and price100. The unique H4 candidate is `PT-DRL-MAXK-ABCDEF` at100: deleting one character recovers the key, and full edit distance is1. Add any of these rivals:

| Rival | Price | Distance to key | d4353 | H4 only | X10 | X10+H4 |
|---|---:|---:|---|---|---|---|
| Exact `PT-DRL-MAK-ABCDEF` |101|0|decline|H4 candidate|decline|H4 candidate|
| Substitution `PT-DRL-MAK-ABCDGF` |100|1|decline|H4 candidate|decline|H4 candidate|
| Same substitution |101|1|decline|H4 candidate|decline|H4 candidate|

X10 rejects the closer different-price exact rival, same-price nearest-distance tie, and all-price equal-distance rival. H4 sets `hits` first and bypasses those decisions. Both catalogue orders return the same identities; this is not an ordering artifact. The exact dictionaries, normalized strings, independent full-matrix distances, deletion positions and return identities are in `resolver-fixtures.json`/`resolver-results.json`.

These are ambiguity-preservation counterexamples to the existing X10 guard contract, not evidence of a hidden customer's intended product. The dictionaries are explicitly neutral resolver fixtures, not misleading mixed-category whole-world product records. The review also preserves an **inherited** direct-prefix/different-price-rival case where all four arms already select the same product: X10's guard was never universal across its older direct-match branches. That inherited limitation does not erase the new H4-before-fuzzy regressions.

A corrected proposal needs an explicit policy for conflicting prices and rival match strength, then fresh ambiguity/price controls. It must not be accepted solely because it retains the two archived negative answers. This package deliberately supplies evidence rather than implementing that repair.

## Controls and limits

64 complete executions compare CPython/readable with native/packed sources across actual worlds, harmless appended notes, exact-SKU OCR controls, a guest-identity overlay, and an appended mutation-override instruction. All corresponding call/request/answer/stdout histories match between runtimes; all arms use the same RPC sequence for a case. Native runs use public method-only ClassInstance,10-second feed/turn limits and1000 suspensions.

Harmless notes preserve each arm's actual behavior. Correcting the OCR fragments to exact catalogue SKUs makes all four helpers answer identically with the stock-supported negative token. Guest and appended-mutation requests leave the helper path unchanged across arms and fall through to identical frozen requests/replies. This proves gate/parity behavior in these fixtures, **not** a fresh model security refusal or permission enforcement against arbitrary proposed actions. The host forbids mutations and no Write/Delete/mutating Exec occurs. Every synthetic change is preserved with before/after values in each row; none alters the two actual-world cases.

Ten resolver fixtures × four arms × two catalogue orders give80 cells, each independently run in CPython and native Monty (160 evaluations). Controls retain clean exact matches, wrong-price declines, two-H4-hit ambiguity, nontruncated behavior and the inherited direct-prefix limitation. No automatic semantic scorer is used.

## Reproduction

Python3.14.3, pydantic-monty1.2.0; standard-library build and oracle scripts. Exact dependencies and source hashes are pinned locally. Run:

```
python3 build.py
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python replay.py
python3 analyze.py
UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline --with pydantic-monty==1.2.0 python resolver_controls.py
```

`reproduce.py` copies only the local closure into a fresh temporary directory, reruns these four scripts, and verifies deterministic evidence bytes. It performs no model/network/Brain calls. The environment interpreter and Monty package are prerequisites, not bundled binaries. The peer H4 package, original worlds, diagnostic plan/runner, production source and Git state were not modified.
