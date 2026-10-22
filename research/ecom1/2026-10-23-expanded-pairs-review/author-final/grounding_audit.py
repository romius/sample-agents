"""Join the human review of every final message/ref with immutable raw rows.

Manual assessments concern source-field truth, qualifier retention and candidate
eligibility separately. No model judge or product implementation is used.
"""
import collections,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
records=json.loads((HERE/'records.json').read_text())
oracles={o['case']:o for o in json.loads((HERE/'oracles.json').read_text())}
pool=json.loads(pathlib.Path('/tmp/bitgn-paired-research-20261023/world-fixtures.json').read_text())['t021']['products']
paths={r['_path']:r for r in pool}
retained_unknown={'sander','compressor'}
foreign_unknown={'sander','saw','hedge','glasses'}
audit=[]
for ordinal,r in enumerate(records,1):
    case=r['step']['case'];family,kind=case.split('__');arm=r['step']['arm'];o=oracles[case]
    a=json.loads(r['response']['choices'][0]['message']['content'])
    refs=a.get('grounding_refs',[]);catalog_refs=[p for p in refs if p.startswith('/proc/catalog/')]
    assert all(p in paths for p in catalog_refs)
    entry={'ordinal':ordinal,'case':case,'arm':arm,'trace_job':r['trace_job'],'trace_seq':r['trace_seq'],
      'message':a['message'],'refs':refs,'outcome':a['outcome'],
      'all_catalog_refs_exist':True,'duplicate_catalog_refs':len(catalog_refs)-len(set(catalog_refs)),
      'literal_name_and_technical_property_claims_supported':True,
      'source_fields':{},'requested_qualifier_retained':None,'cross_family_candidate_offer':False,
      'identity_scope_widened_without_explanation':False,'notes':[]}
    if kind in ['exact_sku','unique_property']:
        entry['notes']=['Correct exact SKU/ref. For property control, supplied field uniquely identifies this family variant; no unnecessary question.']
        entry['source_fields']={o['chosen_record']['_path']:o['chosen_record']['properties']}
    elif kind=='exclude_ambiguous':
        entry['notes']=['All eligible remaining family candidates are cited; excluded SKU is not offered/cited as a candidate.']
        if family=='sander' and arm=='parent':entry['notes'].append('Returns two SKUs with OK; this is an enumeration/disposition error, not a false unique selection.')
        if (family in ['sander','hedge','glasses'] and arm=='treatment') or (family=='glasses' and arm=='parent'):
            entry['notes'].append('Acknowledges excluded SKU in text; violates frozen strict no-quote-Y text criterion, but does not offer it as eligible. Unicode hyphens normalized for mention detection.')
        if family=='saw' and arm=='treatment':entry['notes'].append('Acknowledges excluded fine-cut set by descriptive name, no excluded SKU/ref.')
        if family=='compressor' and arm=='treatment':entry['notes'].append('Standard is shorthand for the base listing, not an evidenced additional technical property; Silent Plus is the actual other name.')
        entry['source_fields']={x['_path']:{'name':x['name'],'properties':x['properties']} for x in o['source_records']}
    elif kind=='unknown_property':
        entry['source_fields']={x['_path']:{'name':x['name'],'properties':x['properties'],'waterproof_field':'absent'} for x in o['source_records']}
        entry['requested_qualifier_retained']=arm=='treatment' and family in retained_unknown
        if arm=='parent':
            entry['notes']=['Exact SKU identity is real, but naked OK silently drops the requested waterproof attribute. Absence of the field is not a physical negative.']
        else:
            entry['identity_scope_widened_without_explanation']=family!='compressor'
            entry['cross_family_candidate_offer']=family in foreign_unknown
            if family in retained_unknown:
                entry['notes'].append('Mentions waterproof evidentiary gap; qualifier retention improves. This alone is not full task resolution.')
            else:entry['notes'].append('Generic which-SKU clarification omits waterproof; raw CLAR label is not semantic acceptance.')
            if family=='sander':entry['notes'].append('Exact Einhell SKU request widens to other Einhell kits and Bosch GEX125 refs; Bosch CASE ref duplicated. Names are real, eligibility for the named identity is unsupported.')
            if family=='saw':entry['notes'].append('Offers other Makita models in text while original identity is exact DeWalt SKU; no waterproof qualification.')
            if family=='hedge':entry['notes'].append('Exact Stihl hedge-trimmer SKU request widens to Bosch hedge trimmers and a Stihl lawn mower. These are real records, not matches for the fixed identity.')
            if family=='glasses':entry['notes'].append('Exact 3M 10-pack SKU request widens to other 3M variants and Uvex products while dropping waterproof.')
            if family=='compressor':entry['notes'].append('Keeps named SKU and evidentiary caveat. Does not have a waterproof property is ambiguous wording: only field absence is known, not a physical non-waterproof rating. Count as wording risk, not a proven negative-attribute fabrication.')
    else:
        entry['source_fields']={x['_path']:{'name':x['name'],'properties':x['properties']} for x in o['source_records']}
        entry['requested_qualifier_retained']=not (family=='saw' or (family=='glasses' and arm=='parent'))
        if family=='saw':
            entry['notes']=['Named DeWalt record explicitly has power_source=corded while request requires cordless.']
            if arm=='parent':entry['notes'].append('Definitive named-SKU OK ignores explicit contradiction.')
            else:
                entry['cross_family_candidate_offer']=True;entry['identity_scope_widened_without_explanation']=True
                entry['notes'].append('CLAR offers corded DeWalt plus cordless Makita without retaining cordless or explaining identity-versus-power conflict. Names are authentic; claim that candidates match the full description is unsupported/contradicted.')
        elif family=='glasses' and arm=='parent':entry['notes']=['Returns 10-pack SKU despite requested single-pair one-piece pack; properties.pack_count=10 explicitly conflicts with 1.']
        else:entry['notes']=['Question contrasts actual conflicting capacity/kit/noise/pack values; both identity and property alternatives remain visible. Technical descriptions are supported.']
    audit.append(entry)
summary={}
for arm in ['parent','treatment']:
    rows=[r for r in audit if r['arm']==arm];unknown=[r for r in rows if r['case'].endswith('__unknown_property')];conflict=[r for r in rows if r['case'].endswith('__conflicting_sku')]
    summary[arm]={'reviewed_final_messages':len(rows),'existing_catalog_refs_only':all(r['all_catalog_refs_exist'] for r in rows),
      'unknown_attribute_mentioned_as_unverified':sum(r['requested_qualifier_retained'] is True for r in unknown),
      'unknown_attribute_dropped':sum(r['requested_qualifier_retained'] is False for r in unknown),
      'conflict_attribute_retained':sum(r['requested_qualifier_retained'] is True for r in conflict),
      'conflict_attribute_dropped':sum(r['requested_qualifier_retained'] is False for r in conflict),
      'cross_family_candidate_offer_answers':sum(r['cross_family_candidate_offer'] for r in rows),
      'unexplained_identity_scope_widening_answers':sum(r['identity_scope_widened_without_explanation'] for r in rows),
      'new_explicitly_invented_technical_values_found':0}
(HERE/'manual-grounding-audit.json').write_text(json.dumps({'scope':'Human review of all60 final messages and catalogue refs, not hidden reasoning. Missing qualifier/incorrect eligibility is separate from invented name/property. No aggregate semantic accuracy claim.','arms':summary,'rows':audit},indent=2)+'\n')
print(json.dumps(summary,indent=2))
