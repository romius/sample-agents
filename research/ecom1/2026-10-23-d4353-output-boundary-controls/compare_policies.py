"""Offline acceptance-policy comparison only; never executes candidate agent code."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
cases=json.loads((P/'cases.json').read_text());results=json.loads((P/'results.json').read_text())
observed={r['case']:r for r in results['results'] if r['form']=='readable'}
rows=[]
for c in cases:
 r=observed[c['name']];choice=c['response']['choices'][0];content=choice['message']['content'];finish=choice['finish_reason']
 # This is a syntactic whole-text JSON check on fixed scripted payloads only.
 try:whole=json.loads(content);exact_report=isinstance(whole,dict) and whole.get('tool')=='report_completion'
 except (ValueError,TypeError):whole=None;exact_report=False
 prefix_report=c['payload_name'].startswith(('clarification_','readonly_OK_','report_prefix_'))
 action=whole.get('tool') if isinstance(whole,dict) else None
 base_accept=(prefix_report or action is not None) and (c['stage']=='main' or prefix_report)
 current_accept=base_accept and (c['stage']=='forced' or finish!='length')
 # Comparisons preserve forced report-only filtering except explicitly unsafe unified dispatch.
 reject_length=base_accept and finish!='length'
 drop_finish_guard=base_accept
 report_exception=exact_report or (c['stage']=='main' and finish!='length' and action is not None)
 unsafe_unified_dispatch=prefix_report or action is not None
 rows.append({'case':c['name'],'stage':c['stage'],'finish_reason':finish,'whole_text_json':whole is not None,'exact_whole_report':exact_report,
 'observed_injected_payload_accepted':current_accept,'observed_answer':r['answers'][0],
 'observed_inference_calls':r['counts'],'observed_mutation_dispatches':len(r['synthetic_effects']),
 'counterfactual_acceptance_only':{'reject_all_length_keep_phase_filter':reject_length,'drop_finish_guard_keep_phase_filter':drop_finish_guard,'exact_whole_report_exception_keep_main_stop_actions':report_exception,'unsafe_uniform_dispatch_any_parseable_action':unsafe_unified_dispatch}})
(P/'policy-matrix.json').write_text(json.dumps({'scope':'Fixed payload acceptance comparison, not candidate execution or semantic score. Existing parse_step accepts first complete JSON prefix. Whole-report exception is a hypothetical policy, not an implementation recommendation.','rows':rows},ensure_ascii=False,indent=2)+'\n')
lines=['# Source-control decision table','','All rows are scripted native whole-agent controls, with exact readable/packed parity. “Accepted” refers to the injected payload; a later recovery report is separate. Effects are in-memory fake RPC dispatches.','','| Payload | Main accepted | Forced accepted | Main / forced effects | Whole JSON report |','|---|---:|---:|---|---:|']
for c in [c for c in cases if c["stage"]=="main"]:
 n=c['payload_name'];a=next(r for r in rows if r['case']=='main_'+n);b=next(r for r in rows if r['case']=='forced_'+n)
 yes=lambda v:'yes' if v else 'no'
 lines.append(f"| {n} | {yes(a['observed_injected_payload_accepted'])} | {yes(b['observed_injected_payload_accepted'])} | {a['observed_mutation_dispatches']} / {b['observed_mutation_dispatches']} | {yes(a['exact_whole_report'])} |")
(P/'decision-table.md').write_text('\n'.join(lines)+'\n')
print('Wrote',len(rows),'fixed-payload acceptance comparisons; no candidate executions.')
