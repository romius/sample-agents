"""Neutral synthetic requests and manually authored, source-linked evaluation notes.

Oracles describe product constraints, not text-classification algorithms. Their
semantic judgments require independent review; verify.py checks cited facts only.
"""
from copy import deepcopy

MISSING = {"field_absent": True}


def product(sku, name, props=None, family="fam-nera-g1", brand="Nera"):
    record = {"sku": sku, "name": name, "brand": brand, "family_id": family,
              "kind_id": "kind-grinder", "category_id": "cat-tools", "price_cents": 10000,
              "_path": "/proc/catalog/" + brand + "/" + sku + ".json"}
    if props is not None:
        record["properties"] = props
    return record


def grinders():
    return [product("P-G1-A", "Nera G1 grinder body", {"kit": "body only"}),
            product("P-G1-B", "Nera G1 grinder kit", {"kit": "batteries and case"}),
            product("P-G1-C", "Nera G1 flat-head grinder body", {"head_type": "flat", "kit": "body only"})]


def fact(sku, field, expected, relation, explanation):
    return {"sku": sku, "field": field, "expected": expected,
            "relation_to_requested_constraint": relation, "explanation": explanation}


def make(case, description, products, oracle, requirement, query="Nera G1 grinder", **extra):
    return dict(case=case, instruction="need code: " + description + ". answer only with sku.",
                action={"tool": "catalog", "query": query, "limit": extra.pop("limit", 8)},
                products=products, oracle=oracle, required_semantics=requirement,
                policy_glossary=extra.pop("policy_glossary", {}), **extra)


def all_fixtures():
    cases = []
    unknown = [fact(s, "properties.head_type", MISSING, "unknown", "Body/kit names do not establish head geometry.")
               for s in ["P-G1-A", "P-G1-B"]]
    flat = fact("P-G1-C", "properties.head_type", "flat", "contradicted", "Explicit flat geometry conflicts with the requested standard geometry.")
    cases.append(make("U1_missing_head", "Nera G1 standard head grinder", grinders(), unknown + [flat],
                      "Preserve standard head as unverified for A/B; do not call A standard or offer C as satisfying it."))
    for suffix, value in [("null", None), ("empty", "")]:
        products = grinders()
        products[0]["properties"]["head_type"] = value
        cases.append(make("U2_" + suffix, "Nera G1 standard head grinder", products,
                          [fact("P-G1-A", "properties.head_type", value, "unknown", "Null/empty is no positive or negative evidence.")] + [unknown[1], flat],
                          "Preserve the unknown qualifier; no absent/null/empty-to-false coercion."))
    products = grinders()
    products[0]["properties"]["head_type"] = "standard"
    products[1]["properties"]["head_type"] = "flat"
    cases.append(make("U3_explicit_positive", "Nera G1 standard head grinder", products,
                      [fact("P-G1-A", "properties.head_type", "standard", "supported", "Direct property supports the request."),
                       fact("P-G1-B", "properties.head_type", "flat", "contradicted", "Explicit incompatible property."), flat],
                      "A uniquely satisfies the head constraint within this full synthetic fixture; do not infer global coverage from helper metadata."))
    products = deepcopy(products)
    products[0]["properties"]["head_type"] = "orthogonal"
    cases.append(make("U4_supplied_synonym", "Nera G1 standard head grinder", products,
                      [fact("P-G1-A", "properties.head_type", "orthogonal", "supported_with_supplied_glossary", "Fixture glossary explicitly equates orthogonal and standard head.")],
                      "Literal absence of standard is not negative evidence when supplied glossary supports equivalence.",
                      policy_glossary={"head_type": {"orthogonal": "standard"}},
                      future_request_requirements={"shared_context": "For this catalogue, head_type orthogonal means standard head.",
                          "must_appear_identically_in_both_complete_runtime_format_requests": True,
                          "offline_observation_alone_supplies_glossary": False}))
    products = [product("P-BAT-A", "Nera G1 grinder unit", {"batteries_included": False}),
                product("P-BAT-B", "Nera G1 grinder kit", {"batteries_included": True})]
    cases.append(make("N1_explicit_negative", "Nera G1 grinder without batteries", products,
                      [fact("P-BAT-A", "properties.batteries_included", False, "supported", "Explicit false supports without batteries."),
                       fact("P-BAT-B", "properties.batteries_included", True, "contradicted", "Explicit true conflicts with without batteries.")],
                      "Do not require the literal token without in a product name; preserve negative polarity."))
    products = deepcopy(products)
    del products[0]["properties"]["batteries_included"]
    cases.append(make("N2_negative_unknown", "Nera G1 grinder without batteries", products,
                      [fact("P-BAT-A", "properties.batteries_included", MISSING, "unknown", "The batteries field is absent and the neutral unit name supplies no battery-inclusion claim."),
                       fact("P-BAT-B", "properties.batteries_included", True, "contradicted", "Explicit true conflicts.")],
                      "Do not convert missing batteries data into false."))
    cases.append(make("N3_exact_exclusion", "Nera G1 grinder but not P-G1-A", grinders(),
                      [fact("P-G1-A", "sku", "P-G1-A", "excluded_by_request", "Exact identifier is explicitly excluded."),
                       fact("P-G1-B", "family_id", "fam-nera-g1", "remaining_candidate", "Another family member remains."),
                       fact("P-G1-C", "family_id", "fam-nera-g1", "remaining_candidate", "Another family member remains.")],
                      "Exclude A only; B/C remain ambiguous. Candidate reference policy must be supplied before later answer evaluation."))
    products = grinders()
    products[1]["properties"]["head_type"] = "standard"
    cases.append(make("N4_negative_geometry", "Nera G1 grinder not the flat-head version", products,
                      [unknown[0], fact("P-G1-B", "properties.head_type", "standard", "supported", "Explicit standard is not flat in this fixture."),
                       fact("P-G1-C", "properties.head_type", "flat", "contradicted", "Negation excludes explicit flat head.")],
                      "B supports the constraint, A remains unknown, C contradicts it; no blanket unique claim while A unresolved."))
    kits = [product("P-KIT-A", "Nera G1 grinder kit", {"battery_ah": 5.0, "case_included": True}),
            product("P-KIT-B", "Nera G1 grinder kit", {"battery_ah": 2.0, "case_included": True})]
    cases.append(make("E1_exact_identifier", "P-KIT-A", kits,
                      [fact("P-KIT-A", "sku", "P-KIT-A", "supported", "Exact existing SKU with no conflicting additional constraint.")],
                      "Do not introduce generic ambiguity merely because siblings exist.", query="P-KIT-A"))
    cases.append(make("E2_exact_conflict", "P-KIT-A with 2.0Ah batteries", kits,
                      [fact("P-KIT-A", "properties.battery_ah", 5.0, "contradicted", "The named SKU explicitly has 5.0Ah, not requested 2.0Ah."),
                       fact("P-KIT-B", "properties.battery_ah", 2.0, "supports_attribute_but_not_identifier", "Cannot silently substitute B for the exact requested A.")],
                      "Ask which conflicting requirement governs; no silent substitution or unqualified exact-SKU answer.", query="P-KIT-A"))
    cases.append(make("E3_exact_unknown", "P-KIT-A waterproof", kits,
                      [fact("P-KIT-A", "properties.waterproof", MISSING, "unknown", "Exact identifier establishes identity, not waterproofing.")],
                      "Preserve waterproof as unverified.", query="P-KIT-A"))
    cases.append(make("E4_unique_property", "Nera G1 grinder kit with case and 2.0Ah batteries", kits,
                      [fact("P-KIT-A", "properties.battery_ah", 5.0, "contradicted", "Case is shared; capacity distinguishes the variants."),
                       fact("P-KIT-B", "properties.battery_ah", 2.0, "supported", "Distinctive requested capacity is explicit.")],
                      "Do not discard positive property evidence because literal tokens are absent or helper pool coverage is unverified."))
    families = [product("P-MULT-A", "Nera compact grinder", {"head_type": "standard"}),
                product("P-MULT-B", "Oros compact grinder", {"head_type": "standard"}, "fam-oros-g2", "Oros")]
    cases.append(make("F1_multiple_families", "compact standard head grinder", families,
                      [fact(p["sku"], "properties.head_type", "standard", "supported", "Both families explicitly satisfy this constraint.") for p in families],
                      "No unique claim from first-family/score ordering.", query="compact grinder"))
    many = []
    for i in range(16):
        for brand in ["Nera", "Oros"]:
            props = {"configuration": "plain", "description": "neutral detail " * 20}
            if i == 15:
                props["head_type"] = "standard"
            many.append(product("P-" + brand[0] + str(i).zfill(2), brand + " compact grinder", props,
                                "fam-" + brand.lower(), brand))
    cases.append(make("F2_truncated_relevant_family", "compact standard head grinder", many,
                      [fact("P-N15", "properties.head_type", "standard", "supported_in_full_fixture", "Supporting row may be outside bounded observation; not evidence visible to the model when omitted.")],
                      "Truncation does not support global absence or uniqueness.", query="compact grinder", limit=2))
    distractors = grinders() + [product("P-DIST-A", "standard head Nera G1 grinder compatible marketing card",
                                      {"head_type": "flat", "product_type": "printed card"}, "fam-card", "Oros")]
    # This is a real card with misleading marketing words, not an inconsistent
    # record that would require inventing precedence between schema fields.
    distractors[-1]["kind_id"] = "kind-printed-card"
    distractors[-1]["category_id"] = "cat-printed-materials"
    cases.append(make("F3_lexical_distractor", "Nera G1 standard head grinder", distractors,
                      [fact("P-DIST-A", "kind_id", "kind-printed-card", "contradicted", "Primary kind explicitly identifies a card, not a grinder."),
                       fact("P-DIST-A", "category_id", "cat-printed-materials", "contradicted", "Primary category agrees with card type."),
                       fact("P-DIST-A", "properties.product_type", "printed card", "contradicted", "Property agrees with primary type; matching marketing words do not establish a grinder.")],
                      "Full token coverage does not override contradictory product evidence.", query="standard head Nera G1 grinder"))
    brush = [product("P-BR-A", "Nera G1 grinder", {"brushless": False}),
             product("P-BR-B", "Nera G1 grinder", {}), product("P-BR-C", "Nera G1 grinder", {"brushless": True})]
    cases.append(make("F4_false_missing_true", "Nera G1 brushless grinder", brush,
                      [fact("P-BR-A", "properties.brushless", False, "contradicted", "Explicit false differs from missing."),
                       fact("P-BR-B", "properties.brushless", MISSING, "unknown", "Absent is unknown."),
                       fact("P-BR-C", "properties.brushless", True, "supported", "Explicit true supports the request.")],
                      "Keep false, absent, and true distinct; no truthiness-based coercion."))
    return cases
