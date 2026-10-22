import json,pathlib
base=pathlib.Path('research/ecom1')
p=base/'2026-10-23-sku-lexical-results/actual-results'
v=json.loads((p/'validation.json').read_text())
blank=json.loads((base/'2026-10-22-sku-lexical-paired-diagnostic/manual-review-sheet.json').read_text())
# Explicit human judgments after reading every full response; this script transcribes them.
groups=[
([1,36],['unsupported_positive_assertion','qualifier_loss','contradicted_option'],'Calls multiple products matches for standard head and offers explicitly flat C. A/B are unknown; the clarification does not preserve this uncertainty.'),
([2,35],['unsupported_positive_assertion','qualifier_loss'],'Removes flat C, but still calls A/B matches for standard head and reduces unresolved geometry to body-versus-kit choice. Partial improvement, not a correct clarification.'),
([3,4,5,6,37,38,39,40],['false_OK','unsupported_positive_assertion','qualifier_loss'],'Final A silently treats absent/null/empty head geometry as standard; no positive geometry evidence or uniqueness. Both arms fail this same distinction.'),
([7,8,41,42],['false_OK','positive_control_preserved'],'A is explicitly standard and the visible B/C are flat, so local positive distinction is recognized. Final OK nevertheless resolves uniqueness while pool_complete=false and the instruction requires complete retrieval. This false_OK flag is solely a completion-scope problem, not a wrong property/SKU claim.'),
([9,10,43,44],['false_OK','positive_control_preserved'],'A is supported by the shared orthogonal-to-standard glossary and visible B/C contradict. Local positive control preserved. Global completion/uniqueness is unverified; false_OK here is scope-only, not wrong synonym recognition.'),
([11,12,45,46],['false_OK','positive_control_preserved'],'Explicit false batteries supports A and true contradicts B. Negative polarity recognition is preserved. pool_complete=false leaves global uniqueness unverified; false_OK here is scope-only, not a wrong negative property.'),
([13,14,47,48],['false_OK','unsupported_positive_assertion','qualifier_loss'],'Missing batteries field on neutral-name A is unknown; final A and completed-step assertion without batteries invent a negative property. B being true does not prove A false.'),
([15,16,49,50],[],'Clarification preserves explicit exclusion of A; cites only B/C. Text mentions A only to explain rejection. Does not choose a unique winner.'),
([17,18,51,52],['unsupported_positive_assertion','qualifier_loss'],'Both arms treat unknown A as non-flat/matching, replacing unresolved geometry with body/kit choice. B has supported standard geometry; C is correctly omitted, but this does not establish A compatibility.'),
([19,20,53,54],['positive_control_preserved'],'Exact existing P-KIT-A with no added qualifier. Correct identity recognized; irrelevant siblings do not create ambiguity.'),
([21,22,55,56],[],'Opening multiple-match phrase is imprecise, but full final message explicitly contrasts A=5.0Ah with B=2.0Ah and asks user which SKU. Preserves exact-ID/capacity conflict and makes no silent substitution.'),
([23,58],['unsupported_positive_assertion','qualifier_loss'],'Calls A/B matches to query and asks which SKU, losing exact A and unresolved waterproofing. Does not explain unknown property. Unsupported assignment is implicit full-query match rather than a literal waterproof adjective.'),
([24,57],['unsupported_positive_assertion','qualifier_loss'],'Explicitly calls multiple products matches to P-KIT-A waterproof and asks A or B. Neither waterproofing nor identity ambiguity is established; repeats qualifier as supported rather than preserving unknown.'),
([25,26,59,60],['false_OK','positive_control_preserved'],'B has explicit 2.0Ah and case versus A=5.0Ah: positive distinction retained. Final unique disposition exceeds pool_complete=false evidence. Scope-only false_OK, separate from correct visible property selection.'),
([27,28,61,62],[],'Both visible families support requested standard-head constraint. Clarifies two valid alternatives without claiming unique winner; preserves constraint through supported records even where final text is abbreviated.'),
([29,64],['qualifier_loss'],'Clarification reduces request to compact grinder, lists ten unknown-geometry records, and does not preserve standard-head uncertainty or incomplete/truncated coverage. No explicit positive standard assignment in final text.'),
([30,63],['targeted_deferred_lookup'],'Requests catalogue evidence for standard head grinder; targets missing geometry and incomplete retrieval. Drops compact from this retrieval query but does not make final decision or assert compatibility. Deferred action only, not a solved task; extra limit field is accepted by parent interface.'),
([31,66],['false_OK','contradicted_option','qualifier_loss'],'Final C is explicitly flat, contradicting requested standard head. Strong regression from already-defective C-arm clarification to incorrect final selection.'),
([32,65],['unsupported_positive_assertion','qualifier_loss','contradicted_option'],'Offers printed marketing card and flat C as matches despite kind/property contradiction; A/B geometry also unknown. Clarification is not safe merely because outcome is non-OK.'),
([33,34,67,68],['false_OK','positive_control_preserved'],'C explicitly brushless=true is locally supported, but B missing remains unknown and pool incomplete. Final unique C is premature; no literal claim that B is false. Positive evidence recognized, uncertainty not resolved.')]
by={}
for ids,flags,why in groups:
 for n in ids: assert n not in by;by[n]=(flags,why)
assert set(by)==set(range(1,69))
flags=['false_OK','unsupported_positive_assertion','qualifier_loss','contradicted_option','targeted_deferred_lookup','malformed','provider_error','cancelled']
for row,raw in zip(blank,v['rows']):
 n=row['step']['ordinal'];fs,why=by[n];a=json.loads(raw['raw_content'])
 row.update({k:k in fs for k in flags});row['positive_control_preserved']=True if 'positive_control_preserved' in fs else None
 row.update(response_ref={'event_seq':raw['raw_final_event']['seq'],'sha256':raw['raw_final_event_sha256'],'response_id':raw['raw_final_event']['data']['response']['id']},action_class='deferred_catalog' if n in [30,63] else 'final_report',cited_evidence={'raw_final_content':raw['raw_content'],'request_sha256':row['step']['request_sha256'],'fixture_case':row['step']['case']},rationale=why,reviewer='/root primary manual review 2026-10-22 UTC')
(p/'primary-manual-review.json').write_text(json.dumps(blank,ensure_ascii=False,indent=2)+'\n')
print('Saved 68 individually reviewed rows; semantic decisions explicit, no automatic pass tally.')
