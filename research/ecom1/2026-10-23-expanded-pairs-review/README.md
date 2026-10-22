# Independent review: expanded parent-versus-evidence SKU diagnostic

Reviewed 22 October 2026, final evidence read 23:06 UTC; community folder uses a 23 October date. This is **parent versus complete evidence attachment**, not the separate C/L lexical-label ablation. The evidence lowers false definitive OK dispositions, but does not resolve the main semantic concern: some clarification answers discard the very qualifier or identity conflict they should preserve.

The exact directory `experiments/2026-10-23-codex-sol-61-sku-expanded-pairs` was checked repeatedly. At the first session's final read (22:52 UTC), it had no combined60 analysis/manual publication. A later check while completing wire verification found author README d6300r1, manual audit d6297r1 and scorer d6208r2. These are preserved separately under `author-final/`; our earlier v1 mechanical result and independent annotations remain intact. All60 author message/ref/outcome/trace joins match the independently retrieved responses. The author agrees that the observation change is not ready for general-agent integration.

## Sources and accounting

| | Initial job | Continuation |
|---|---|---|
| Job | `j7edfd43910a7441995278f36018c1440` | `j9b8c85def8734dff9af15bcfd48ad4cc` |
| Source | d6181r1 | d6204r1 |
| Source SHA | `f2e7afbe5ef69216552567abbf026c8e3aa64b6c9dc949b1d80d548586d8b4e8` | `85e7c54b63e6cbd355ed94e924fcceb72502bf79bebfe27691d8599b055ff28f` |
| Successful logical responses | 17 | 43 |
| Reported attempts/model_calls | 21 | 47 |
| Host429 rejections | 4 | 4 |
| Reported cost, complete | $0.004641967 | $0.011755251 |

Total: **60 logical responses, 68 attempts, $0.016397218 complete, zero unknown-cost calls**. The initial carrier hit its output limit after response17; that unprinted response is retained from its immutable response event. The continuation runs only frozen `plan[17:]`, with no replaced model response. The sander unknown-property pair straddles jobs. Carrier grade0 is irrelevant to this diagnostic.

Frozen fixtures SHA `d74918a3c14437a11d57b04b1e984145848fd7cfca270f5553195a5c32ebccbd`; oracles SHA `0aaff6108d86365c19b67d0c0bcffe225aa5333b8020f947ccaeb74d10f078c4`. Both packed sources decode to exactly the same frozen fixture dictionary. Offline stub execution of the exact sources reproduces every canonical request hash and all43 continuation requests against the original plan slice. Within each of30 pairs, settings and every prior message agree; the final observation differs only by `sku_lookup_evidence` attachment. No real model call is made by this review.

**Actual wire identity is also verified.** All68 `llm_request` events (1,500,385 bytes) were read with bounded `trace_event` chunks and saved as exact raw server JSON under `wire/`. Every local event byte count matches its trace index. After removing only SDK-added `provider` and `stream`, all message contents and settings—including seed, temperature, reasoning, model and max_tokens—hash exactly to the frozen plan. No alias or text normalization is needed. All eight retry payloads are identical; the initial drill unique-property parent request had three consecutive429 rejections and succeeds on attempt4. Dates, call/attempt numbers, response correspondence, canonical payload hashes and raw-event hashes are preserved in `wire-verification.json`. These are actual captured events, not synthesized raw requests.

## Mechanical dispositions, independently reproduced

The unchanged author scorer reports **9→0 false definitive OK** among18 ambiguity/unknown/conflict cases: one excluded-variant ambiguity, six unsupported waterproof qualifiers, and two exact-SKU/property conflicts. Parent's ambiguous sander answer enumerates two SKUs; it is a wrong OK disposition, not a false unique choice. The other eight are single-SKU OK responses. **12/12 unique-property/exact-SKU controls pass in both arms**, with the expected SKU and correct sole reference, and no excess clarification. All60 responses are final actions: no deferred, malformed, truncated or inference-error response was silently dropped.

These are disposition and exact-control measurements, not nine semantic repairs. [MANUAL-ALL60.md](MANUAL-ALL60.md) gives a fixed manual annotation for every response. [manual-review.json](manual-review.json) retains each complete action, instruction, response hash and trace-event locator; [records.json](records.json) retains the complete raw provider responses, including reasoning. No automatic semantic scorer or semantic pass total is introduced.

## Findings that matter for C/L

**Four of six treatment unknown-property answers drop waterproof completely:** drill record7, saw27, hedge38 and glasses58. They instead ask which variant the user wants, despite an already supplied exact SKU. Parent gave unsupported definitive OK for all six. Treatment's label improves, but those four questions do not preserve the unresolved attribute.

Sander record18 does state that no family record specifies waterproof; it also cites unrelated Bosch variants and repeats one CASE reference. Compressor record47 explicitly says waterproof is not recorded, preserves the requested SKU and asks for confirmation/details. Read in context, this concerns missing metadata; it does **not** establish or explicitly claim the physical product is nonwaterproof. Its generic multiple-products wording is imprecise. These two differ materially from the four complete qualifier omissions and must not be flattened into the same outcome-only score.

**Saw conflict record30 changes OK to clarification but loses the actual contradiction.** The instruction names `PT-SAW-DEW-DWE575K-SITE` and requests cordless; the exact primary source says `properties.power_source: "corded"`. Treatment lists DeWalt variants plus five Makita alternatives, never saying cordless/corded or asking which requirement governs. Glasses conflict record59 is a clearer substantive improvement: it explicitly contrasts named `pack_count:10` against the requested single pair, asks which requirement governs, and cites exact and alternative records.

Drill, sander and hedge conflict distinctions were already retained by the parent and remain retained. Compressor treatment record50 correctly contrasts S=88dB with requested96dB, but drops the requested S grounding reference and offers only base/KIT choices; parent record49 cited all three. This is a citation and clarification regression, not an invented noise value.

**Foreign-family refs rise from0 parent responses to4 treatment responses:** sander unknown18, saw conflict30, hedge unknown38 and glasses unknown58. Saw unknown27 also mentions other Makita models in prose without citing them, which a refs-only metric misses. Crucially, **every foreign cited record was already present in the shared parent `base.matches`**. The evidence attachment did not introduce previously unavailable foreign rows. This is changed selection/candidate contamination in the answer; it cannot be attributed to lexical labels alone. All60 cited paths resolve to visible rows; no fabricated path was found. [foreign-reference-provenance.json](foreign-reference-provenance.json) preserves the explicit check.

**The original v1 ASCII identifier scorer misses one excluded quote.** It reports parent0/treatment3 excluded-SKU quotations. Manual reading finds parent1/treatment3: parent glasses record52 quotes the excluded AMBER SKU using U+2011 nonbreaking hyphens. All four mentions are negative exclusion clauses, not offers to supply the excluded product, and their refs correctly exclude it. Nevertheless, the frozen policy explicitly prohibits quoting excluded SKU identifiers. Preserve the distinction between that policy violation and offering an excluded candidate. Treatment saw record22 also mentions the excluded fine-cut variant descriptively, without its identifier; the narrow identifier metric does not decide that broader policy interpretation. The author subsequently published scorer r2 with explicit Unicode-hyphen normalization. Running r2 on the same60 records changes only the parent glasses excluded-quote flag and its aggregate (0→1); all other per-response mechanical fields remain equal. This is recorded as a post-observation diagnostic correction, not backdated into the original scorer.

## Implications and limits

Keep qualifier retention, exact identity/property conflicts, unknown-versus-false, and candidate/ref contamination as separate manual dimensions in C/L. A CLAR label alone is insufficient. Include semantic reading of Unicode SKU text and prose-only alternatives; do not retrofit a regex improvement into the original reported mechanical score. The observed parent-versus-C changes cannot distinguish lexical found/absent labels from additional sibling evidence, decision-rule text or other attachment contents. They neither demonstrate that deleting labels will help nor replace the queued C/L diagnostic.

These are30 development hold-outs over six real families in one archived world, one matched-seed pair per question. The history-repaired successor's next-observation behavior is shared, but live router/retrieval, full action follow-through and history pressure are not exercised. No full100 readiness, aggregate task-score improvement or deployment recommendation follows. Existing production sources, queued diagnostics and original fixtures were not changed.

## Reproduce and audit scope

```sh
python3 research/ecom1/2026-10-23-expanded-pairs-review/verify.py
python3 research/ecom1/2026-10-23-expanded-pairs-review/package.py
```

The verification uses Python's standard library only. It checks exact source and fixture hashes, fake-transport request reproduction,30 field-only pairs,17+43 response mapping, all68 actual wire events and retries, attempt/cost accounting, unchanged v1 mechanical results, separately reproduced v2 correction, all60 manual-annotation and author-join response pins, and visible-ref provenance. The annotations remain manual judgments on frozen text; verification does not infer arbitrary-text correctness. Source archives are copied under `upstream`; decoded files are explicitly derived artifacts. [DEPENDENCIES.json](DEPENDENCIES.json) records exact Brain document/revision/size/hash. [SHA256SUMS.json](SHA256SUMS.json) pins local files. Full server trace CAS references are retained in the result snapshots; selected successful and429 response events are local.

Read-only Brain sessions s7491 and s7555 ended with discard and zero document/job changes; receipts are in [brain-session.json](brain-session.json) and [brain-wire-session.json](brain-wire-session.json). The author publication snapshot is separately retained under `author-final/`. Independent review is published separately by integration_plan, so it is not falsely represented as authored by this review. This direct-LLM carrier evidence does not validate startup of any full commerce agent; it remains valid independently of the parent's separate native-host bound-method startup investigation. The package excludes bytecode caches and publication files and normalizes gzip OS metadata for reproducible builds.
