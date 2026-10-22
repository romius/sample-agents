# Manual review of all60 responses

These fixed annotations review these exact outputs; they are not an automatic semantic scorer. Full actions, source oracles and response hashes are retained in manual-review.json. No semantic pass total is assigned.

| Record | Case | Arm | Manual assessment |
|---|---|---|---|
| 1 | drill__exclude_ambiguous | parent | Clarifies two eligible variants with supported kit/body descriptions; excluded identifier absent. |
| 2 | drill__exclude_ambiguous | treatment | Clarifies eligible variants; descriptions supported and excluded identifier absent. |
| 3 | drill__unique_property | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 4 | drill__unique_property | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 5 | drill__exact_sku | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 6 | drill__exact_sku | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 7 | drill__unknown_property | treatment | Drops waterproof entirely and treats exact SKU plus unknown attribute as broad variant ambiguity. Lists other kits without preserving requested attribute. |
| 8 | drill__unknown_property | parent | Definitive named-SKU answer silently accepts unsupported waterproof qualifier; source has no waterproof evidence. No affirmative descriptive waterproof sentence is fabricated, but the requested requirement remains unresolved. |
| 9 | drill__conflicting_sku | parent | Retains named 2AH kit versus requested 5AH kit and asks which SKU; descriptions supported by kit fields. |
| 10 | drill__conflicting_sku | treatment | Retains both kit variants and properties in clarification. No semantic change established over parent. |
| 11 | sander__exclude_ambiguous | treatment | Clarification label improves; quotes excluded SKU in negative clause despite no-quote policy. Refs contain eligible variants only. |
| 12 | sander__exclude_ambiguous | parent | OUTCOME_OK enumerates two eligible SKUs. Ambiguity remains; disposition violates unique-only policy, but no excluded item is offered. |
| 13 | sander__unique_property | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 14 | sander__unique_property | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 15 | sander__exact_sku | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 16 | sander__exact_sku | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 17 | sander__unknown_property | parent | Definitive named-SKU answer silently accepts unsupported waterproof qualifier; source has no waterproof evidence. No affirmative descriptive waterproof sentence is fabricated, but the requested requirement remains unresolved. |
| 18 | sander__unknown_property | treatment | Preserves that no record specifies waterproof, without claiming physically nonwaterproof. Broadens candidate refs to unrelated Bosch family, with duplicated CASE ref. Pair spans the two jobs. |
| 19 | sander__conflicting_sku | treatment | Retains 2.5Ah versus 4Ah/50-disc distinctions and asks which SKU. Supported fields; parent already preserved conflict. |
| 20 | sander__conflicting_sku | parent | Explicitly contrasts referenced 2.5Ah kit and described 4Ah/50-disc kit; asks which identity governs. |
| 21 | saw__exclude_ambiguous | parent | Clarifies ambiguity; two eligible refs, no excluded identifier. |
| 22 | saw__exclude_ambiguous | treatment | Clarifies ambiguity; eligible refs. Mentions excluded fine-cut variant descriptively, without identifier; distinguish from measured identifier-quote criterion. |
| 23 | saw__unique_property | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 24 | saw__unique_property | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 25 | saw__exact_sku | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 26 | saw__exact_sku | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 27 | saw__unknown_property | treatment | Drops waterproof entirely; adds other Makita models in prose. Refs stay DeWalt, so foreign-ref metric alone misses the broadened candidate mention. |
| 28 | saw__unknown_property | parent | Definitive named-SKU answer silently accepts unsupported waterproof qualifier; source has no waterproof evidence. No affirmative descriptive waterproof sentence is fabricated, but the requested requirement remains unresolved. |
| 29 | saw__conflicting_sku | parent | Definitive named-SKU answer silently ignores cordless request; source power_source is corded. |
| 30 | saw__conflicting_sku | treatment | Changes to clarification but never mentions cordless versus corded conflict. Lists corded DeWalt and other Makita candidates together without explaining identity/property tradeoff. No semantic repair established. |
| 31 | hedge__exclude_ambiguous | treatment | Clarifies but quotes excluded AK20 SKU in negative clause; refs correctly exclude it. |
| 32 | hedge__exclude_ambiguous | parent | Supported AK10/body alternatives; eligible refs and no excluded identifier. |
| 33 | hedge__unique_property | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 34 | hedge__unique_property | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 35 | hedge__exact_sku | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 36 | hedge__exact_sku | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 37 | hedge__unknown_property | parent | Definitive named-SKU answer silently accepts unsupported waterproof qualifier; source has no waterproof evidence. No affirmative descriptive waterproof sentence is fabricated, but the requested requirement remains unresolved. |
| 38 | hedge__unknown_property | treatment | Drops waterproof entirely; expands candidates to Bosch trimmers and a Stihl mower, violating requested exact identity. |
| 39 | hedge__conflicting_sku | treatment | Retains AK10 versus AK20 choice and asks which SKU. Parent already did this. |
| 40 | hedge__conflicting_sku | parent | Retains AK10 versus requested AK20 kit choice with supported fields. |
| 41 | compressor__exclude_ambiguous | parent | Clarifies base and Silent Plus options with supported names and eligible refs. |
| 42 | compressor__exclude_ambiguous | treatment | Clarifies base/Silent Plus variants; standard is a loose descriptor, not evidence of an extra source attribute. Eligible refs, excluded identifier absent. |
| 43 | compressor__unique_property | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 44 | compressor__unique_property | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 45 | compressor__exact_sku | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 46 | compressor__exact_sku | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 47 | compressor__unknown_property | treatment | Preserves missing waterproof metadata and named SKU; does not assert physical nonwaterproofness. Clarification asks confirmation/details. Generic multiple-products wording remains imprecise. |
| 48 | compressor__unknown_property | parent | Definitive named-SKU answer silently accepts unsupported waterproof qualifier; source has no waterproof evidence. No affirmative descriptive waterproof sentence is fabricated, but the requested requirement remains unresolved. |
| 49 | compressor__conflicting_sku | parent | States exact S variant has 88dB while base/KIT have requested 96dB; cites all three and asks which SKU. |
| 50 | compressor__conflicting_sku | treatment | Preserves 88dB versus96dB conflict but omits requested S grounding ref and offers only base/KIT choices. Citation regression and narrower clarification than parent; values themselves supported. |
| 51 | glasses__exclude_ambiguous | treatment | Quotes excluded AMBER SKU with ASCII hyphens in negative clause. Alternatives and refs are eligible. |
| 52 | glasses__exclude_ambiguous | parent | Quotes excluded AMBER SKU using U+2011 hyphens in negative clause. ASCII-only scorer misses this. Alternatives and refs are eligible. |
| 53 | glasses__unique_property | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 54 | glasses__unique_property | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 55 | glasses__exact_sku | treatment | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 56 | glasses__exact_sku | parent | Exact expected SKU and source reference; no excess clarification. This positive control passes in both arms. |
| 57 | glasses__unknown_property | parent | Definitive named-SKU answer silently accepts unsupported waterproof qualifier; source has no waterproof evidence. No affirmative descriptive waterproof sentence is fabricated, but the requested requirement remains unresolved. |
| 58 | glasses__unknown_property | treatment | Drops waterproof entirely and expands exact-SKU request to family and Uvex alternatives. |
| 59 | glasses__conflicting_sku | treatment | Clear semantic improvement: explains named SKU pack_count10 versus single pair, asks which requirement governs, and cites exact and alternative records. |
| 60 | glasses__conflicting_sku | parent | Definitive 10-pack SKU answer ignores requested single-pair/one-piece pack. |
