"""Bounded observation-only port of codex-sol-61 d4922r1.

Caller must explicitly establish SKU-lookup scope after existing security/policy
routing. This module does not parse intent, choose a SKU, or change an answer.
words/haystack/product_view are the pinned parent functions in the caller scope.
"""
import json

def bounded_lookup_evidence(base, query, all_products, scope, byte_budget=9500):
    if scope != 'sku_lookup':
        return base
    if not isinstance(byte_budget,int) or isinstance(byte_budget,bool) or byte_budget<0 or byte_budget>9500:
        raise ValueError('observation byte budget')
    if not isinstance(query,str) or len(query)>4096 or len(all_products)>2048:
        return base
    families=[]
    for product in base.get('matches',[]):
        family=product.get('family_id')
        if isinstance(family,str) and family and family not in families:
            families.append(family)
    if not families:
        return base
    wanted=list(dict.fromkeys(words(query)))
    fields=['sku','name','brand','family_id','kind_id','category_id']
    rows=[];invalid=0
    for product in all_products:
        if not isinstance(product,dict):
            invalid+=1;continue
        if product.get('family_id') not in families:
            continue
        if not isinstance(product.get('sku'),str) or not isinstance(product.get('_path'),str):
            invalid+=1;continue
        hay=haystack(product,fields)
        covered=[t for t in wanted if t in hay or (len(t)>=4 and any(
            h.startswith(t) or t.startswith(h) for h in hay if len(h)>=4))]
        row=product_view(product)
        row['lexical_query_tokens_found']=covered
        row['lexical_query_tokens_absent']=[t for t in wanted if t not in covered]
        rows.append(row)
    rows.sort(key=lambda p:(families.index(p['family_id']),p['sku'],p['path']))
    result=dict(base)
    evidence={'pool_complete':False,'completeness_reason':'Parent index coverage is unverified.',
        'eligible_indexed_siblings':len(rows),'invalid_indexed_records':invalid,
        'returned_siblings':0,'evidence_truncated':bool(rows),'siblings':[],
        'ranking_semantics':'Lexical retrieval only; not confidence or uniqueness.',
        'decision_rule':'For SKU lookup compare original request constraints with actual sibling names and properties. '
          'A score lead does not prove one variant. Missing words do not prove negative properties; token coverage is diagnostic, '
          'not a constraint solver. Do not discard unresolved qualifiers. Verify exact SKU or unique compatible product; '
          'otherwise clarify and name candidate SKUs. Complete retrieval before claiming uniqueness. Existing security and runtime policies remain authoritative.'}
    result['sku_lookup_evidence']=evidence
    # The original observation is never truncated or altered to fit this addition.
    if len(json.dumps(result).encode('utf-8'))>byte_budget:
        return base
    for row in rows:
        evidence['siblings'].append(row)
        evidence['returned_siblings']=len(evidence['siblings'])
        evidence['evidence_truncated']=evidence['returned_siblings']<len(rows)
        if len(json.dumps(result).encode('utf-8'))>byte_budget:
            evidence['siblings'].pop()
            evidence['returned_siblings']=len(evidence['siblings'])
            evidence['evidence_truncated']=True
            break
    assert len(json.dumps(result).encode('utf-8'))<=byte_budget
    return result
