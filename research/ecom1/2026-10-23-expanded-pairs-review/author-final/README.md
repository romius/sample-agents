# Expanded paired SKU acceptance

23 October2026, codex-sol-61. Completed30 new questions/6 actual families/60 paired model responses. **Tested observation change not ready for general-agent integration.** See [finding](../../findings/2026-10-23-codex-sol-61-sku-expanded-result.md).

Primary counts: unsupported single-SKU OK8/18→0/18; plus erroneous multi-SKU OK1→0; excess CLAR0/12→0/12; correct positive SKU+ref12/12 each. Treatment still drops waterproof in4/6 cases, drops cordless in the saw conflict, and makes five unexplained cross-family candidate offerings. Names/technical values are grounded; compatibility descriptions remain unreliable. No overall accuracy claim.

Plan d6184 and labels d6186 precede inference. Source d6181r1 and continuation d6204r1 pin original observation candidate d5620r1/readable d5635r1, pending parent d5204r1, actual world d4972r1. Bootstrap from earlier frozen d5624 archive. Shared baseline d3200r2 remains90.12601. Model gpt-oss-120b, DeepInfra BF16, SDK0.3.7, temp0, medium, max_tokens2048, matched seed20261023, one AB/BA pair/question. Only sku_lookup_evidence differs; all68 actual HTTP requests independently checked against frozen content/settings/provider.

Raw generations: [records.json](records.json), [initial events](initial-response-events.json), [continuation events](continuation-response-events.json). Source-field audit: [manual-grounding-audit.json](manual-grounding-audit.json), human annotations joined by [grounding_audit.py](grounding_audit.py). Mechanical metrics: [report.json](report.json), [analyze.py](analyze.py), [11 scorer checks](scorer-checks.json). [Costs/provenance](costs-and-provenance.json):60 unique billed generations+8 zero-cost SDK429 rejections, USD0.016397218,355158tokens, no unknown/pending costs.

Reproduce mechanical metrics without inference:

```sh
python analyze.py records.json fixtures.json oracles.json reproduced-report.json
```

No semantic scorer infers success from CLAR. Human audit supplies explicit source fields, exact message/ref, job/trace event and symptom flags for all60 answers; review these instead of treating mechanical outcomes as task grades. `grounding_audit.py` contains the human assessments; to recreate its joined JSON, stage d4972r1 as `/tmp/bitgn-paired-research-20261023/world-fixtures.json`.

Initial carrier failed on captured stdout64KiB after17 successful generations; all17 recovered, including last unprinted response. Continuation runs only frozen plan[17:],43 calls, compact index log. No original generation repeated. One pair crosses jobs. Trial grades are irrelevant; no ECOM actions performed. See [CONTINUATION.md](CONTINUATION.md), exact source/manifests and both settled result/usage files. A duplicated zero-cost response event from incremental retrieval was removed by seq;60 generation IDs were unique throughout.

`reproducibility.zip` d6185 is the pre-inference package. The final results archive adds raw outputs, audit, costs and scripts. Full original builder reconstruction also uses the earlier d5624 fixture bootstrap; both archives retain exact inference payloads, so metrics can be reproduced with the command above without rebuilding or resubmitting. The source-field oracles and all request hashes are retained as standalone documents. No new full100, current-record source edit or promotion. Next work is the existing d6134 isolated C/L/T follow-up, faithful unknown/conflict questions, candidate eligibility and whole-agent composition with history repair d5785.
