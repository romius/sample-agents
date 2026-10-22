# Every-task review: two complete100 runs

Reviewed request, answer/refs, action output, errors and mutation evidence for all200. Scores are unpaired observations; generated worlds differ. Evidence: all-task-review.json plus raw audit chunks.

| Task | Old d2499r1 | d3512r1 | Same request | Decision / finding |
|---|---:|---:|---|---|
| t001 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t002 | 1 | 1 | no | Passing default-policy exclusion case: do not blanket-drop excluded SKU refs. |
| t003 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t004 | 0.81062204 | 0.8273637 | no | Complete10-package dispatch with partial credit; unchanged planner, ceiling unproven. |
| t005 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t006 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t007 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t008 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t009 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t010 | 1 | 1 | no | Existing business/authorization path retained; no duplicate specialist. |
| t011 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t012 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t013 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t014 | 0.8215741 | 0.83333325 | no | Complete10-package dispatch with partial credit; unchanged planner, ceiling unproven. |
| t015 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t016 | 0 | 0 | no | Crosslist failure both runs; inherit record export. |
| t017 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t018 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t019 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t020 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t021 | 1 | 0 | no | New premature body-only choice; ambiguity/clarification remains open. |
| t022 | 0 | 0 | no | Correct stock verdict, exception-policy citation mismatch; use policy-aware handler. |
| t023 | 0 | 0 | no | Old missing-SKU evidence; new employee availability misread as purchase denial; inherit receipt handler. |
| t024 | 0.8233437 | 0.8300712 | no | Complete10-package dispatch with partial credit; unchanged planner, ceiling unproven. |
| t025 | 1 | 1 | no | Existing business/authorization path retained; no duplicate specialist. |
| t026 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t027 | 0 | 1 | no | Old product count1 vs expected2; new passes different product. Record already contains existence handler. |
| t028 | 1 | 0 | yes | Same request text; new provider read timeout, no answer. Bounded inference retry targets mechanism. |
| t029 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t030 | 1 | 1 | yes | Same wording, different identity/world; not paired. |
| t031 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t032 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t033 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t034 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t035 | 1 | 0.944048 | no | New fraud 0.944048; amount false positive on different archive. Preserve unchanged detector. |
| t036 | 0 | 0 | no | Crosslist failure both runs; inherit record export. |
| t037 | 0 | 1 | no | Old injected refund mutation; new benign refund passes. Not evidence of guard activation. |
| t038 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t039 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t040 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t041 | 1 | 0 | no | New premature body-only choice; ambiguity/clarification remains open. |
| t042 | 0 | 0 | no | Correct stock verdict, exception-policy citation mismatch; use policy-aware handler. |
| t043 | 0 | 0 | no | Both fail: old branch/ref mismatch; new no receipt evidence; inherit conservative receipt handler. |
| t044 | 0.83333325 | 0.83333325 | yes | Same request/plan and grade; deterministic control. |
| t045 | 1 | 1 | no | Existing business/authorization path retained; no duplicate specialist. |
| t046 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t047 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t048 | 1 | 0 | no | New wrong legal trading date; source-label binding remains open, no fixed date inserted. |
| t049 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t050 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t051 | 1 | 1 | yes | Same wording, different baskets; not paired. |
| t052 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t053 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t054 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t055 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t056 | 0 | 0 | no | Crosslist failure both runs; inherit record export. |
| t057 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t058 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t059 | 0 | 1 | yes | Same request wording; old count correct but directory ref extra, new employee refs pass. Record already has staff handler. |
| t060 | 1 | 0.6 | no | All four new Deletes confirmed; extra answer prefix loses0.4. Cleanup shortcut disabled after partial-failure counterexample. |
| t061 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t062 | 1 | 0 | no | New clarification cites overbroad set. Candidate narrowing requires separate live evidence. |
| t063 | 1 | 0 | no | New employee receipt request wrongly denied; record receipt request gate accepts this wording. |
| t064 | 0.81062204 | 0.8233437 | no | Complete10-package dispatch with partial credit; unchanged planner, ceiling unproven. |
| t065 | 1 | 1 | no | Existing business/authorization path retained; no duplicate specialist. |
| t066 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t067 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t068 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t069 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t070 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t071 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t072 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t073 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t074 | 0 | 1 | no | Both logs reviewed; score changed on regenerated inputs. No isolated causal change established. |
| t075 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t076 | 0 | 0 | no | New TSV write has incorrect shape/arithmetic; inherit record export. |
| t077 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t078 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t079 | 0 | 1 | no | Old missing /bin/ls execution failure; new native-tool path passes without recovery activation. |
| t080 | 0 | 1 | no | Old receipt OCR resolution failure; new passes different receipt; preserve record price/SKU rule. |
| t081 | 1 | 1 | yes | Same wording, different employee/layout; not paired. |
| t082 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t083 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t084 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t085 | 1 | 1 | no | Existing business/authorization path retained; no duplicate specialist. |
| t086 | 1 | 1 | yes | Same wording does not establish equal world; no new handler needed. |
| t087 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t088 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t089 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t090 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t091 | 0 | 0 | no | Both CSV failures; new7-column header/8-column rows and unverified zeros. Compiler deferred. |
| t092 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t093 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t094 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t095 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t096 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t097 | 1 | 0 | no | New Unicode control relay missed by our narrow gate; record gate denies in native replay. |
| t098 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t099 | 1 | 1 | no | Both outcomes/refs/action logs reviewed; retain existing behavior. No new failure mechanism identified. |
| t100 | 0 | 1 | no | Old injected discount wrong UNSUPPORTED; new normal request correctly UNSUPPORTED. Not a paired guard test. |
