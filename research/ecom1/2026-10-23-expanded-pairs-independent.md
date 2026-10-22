# Independent semantic review of all 60 expanded-pair actions

23 October 2026. Reviewer: integration_plan. Reviewed every raw final action against its frozen request, visible catalogue records, supplied policy, PLAN and source-record oracles. **The evidence intervention suppresses definitive OK outcomes on difficult requests, while retaining all sampled unique controls, but several replacement clarifications remain wrong or incomplete. General-agent readiness is not established.** No overall semantic pass count or actual task-score improvement is inferred.

Record numbers below are one-based positions in `2026-10-23-expanded-pairs-review/records.json`; each record includes its initial/continuation job label and immutable response event number. P means parent; T means treatment. This is the original evidence attachment versus parent, not the later C/L lexical-label ablation.

## Independent completeness and evidence checks

All 60 records match the 60-step frozen plan in order, have distinct response IDs, identify DeepInfra, finish with `stop`, and contain one parseable `report_completion` action. There are no malformed, deferred or missing final actions among these 60 records. Independently reconstructed every complete request from frozen bootstrap, instruction, catalogue action and the arm-specific observation; **all 60 canonical request hashes match** the frozen plan. No inference was rerun.

Every returned grounding reference resolves to a product visible in that arm's request. The problem with the four cross-family lists is selection relevance, not invented files. Every cross-family record cited in those four treatment responses was already present in the shared parent `base.matches`; the treatment did not first introduce those facts.

Input pins reviewed:

| Input | SHA-256 |
| --- | --- |
| records.json | `130f7ca07c0ac08efaf6aa434f259955fc3ab74659bdaaeae7127a4393d6bd3f` |
| frozen.json | `d74918a3c14437a11d57b04b1e984145848fd7cfca270f5553195a5c32ebccbd` |
| upstream/oracles.json | `0aaff6108d86365c19b67d0c0bcffe225aa5333b8020f947ccaeb74d10f078c4` |
| upstream/PLAN.md | `a732062c96d63d5454aa6b0b9d3eeb1d13eda3aa58aa66266849307fbee9bbb5` |

## What the mechanical 9 → 0 result means

The parent has six definitive OK responses that silently drop waterproof, two OK responses to conflicting identity/property requests, and one ambiguous exclusion response marked OK while enumerating two SKUs. Thus the nine include **eight single-SKU answers and one multiple-SKU enumeration**, not nine false unique selections. Treatment changes all nine outcomes to clarification. That is a real change in response disposition; it is not proof of nine correct resolutions.

Four treatment waterproof messages still discard waterproof and ask which product the user means despite an exact SKU already being supplied: drill #7, saw #27, hedge #38 and glasses #58. They do not explicitly assert waterproofness, but the generic “multiple products match” wording and candidate lists fail to preserve the unresolved constraint. Hedge #38 mentions having evaluated waterproof only in `completed_steps_laconic`; it does not communicate the missing-property issue in the answer. A process claim is not a substitute for the needed clarification.

Sander #18 and compressor #47 do preserve waterproof as absent from the available evidence. Sander still adds unrelated Bosch references and duplicates a CASE reference. Compressor is the stronger improvement: it says the exact SKU exists but “does not have a waterproof property” and asks for confirmation/details. In context that is a statement about missing catalogue data, not a supported assertion that the product is non-waterproof.

The clearest conflict improvement is glasses #59 versus #60: T explicitly distinguishes the named 10-pack (`pack_count=10`) from the requested single pair and asks which requirement was intended. The saw conflict is not repaired semantically: T #30 drops the cordless conflict and offers corded DeWalt products alongside different Makita identities as “multiple products [that] match.” Its clarification label conceals contradicted candidates and loss of the original exact-ID conflict.

## All 12 unique controls per arm

For all six unique-property and all six exact-SKU cases, both arms return precisely the expected SKU, `OUTCOME_OK`, and its sole correct visible product reference. I checked all 24 final messages/references and the actual property/name fields, not only outcome tokens. No sampled positive-control regression or excess clarification appears.

| Family / expected SKU | Property support checked | Unique-property records P / T | Exact-SKU records P / T |
| --- | --- | --- | --- |
| Drill — PT-DRL-BOS-GSR55-2AH | `kit="2x2.0Ah batteries and charger"` | 4 / 3 | 5 / 6 |
| Sander — PT-SND-EIN-TERS18-25 | `kit="2.5Ah battery and charger"` | 13 / 14 | 16 / 15 |
| Saw — PT-SAW-DEW-DWE575K-SITE | `kit="case and rip fence"` | 24 / 23 | 25 / 26 |
| Hedge — PT-HDG-STI-HSA50-AK10 | `kit="AK 10 battery and charger"` | 33 / 34 | 36 / 35 |
| Compressor — PT-CMP-EIN-TEAC270-50S | `noise_db=88` | 44 / 43 | 45 / 46 |
| Glasses — PT-SAFE-3M-SF400-10PK | clear name/lens style and `pack_count=10` | 53 / 54 | 56 / 55 |

These are results on the frozen local controls, not proof of global catalogue completeness or regenerated task performance.

## Remaining 18 pairs: individual assessments

Together with the controls above, this table accounts for every one of the 60 final actions.

| Case | P / T records | Independent assessment |
| --- | --- | --- |
| Drill exclusion | 1 / 2 | Both ask which of the two eligible drill variants; both refs exclude 5AH. No substantive improvement. |
| Drill waterproof | 8 / 7 | P silently returns the named SKU. T stops OK but still loses waterproof and invents an identity-choice problem among three drill variants. |
| Drill conflict | 9 / 10 | Both expose 2.0Ah versus 5.0Ah and ask which SKU. Correct property contrast retained; no new semantic repair. |
| Sander exclusion | 12 / 11 | P enumerates two eligible SKUs under an incorrect OK outcome. T asks for clarification with the two correct refs, but echoes the expressly excluded identifier in its message. Improved disposition with a separate quotation-policy regression. |
| Sander waterproof | 17 / 18 | P silently returns the named SKU. T notes that none specify waterproof; useful qualifier improvement, undermined by unrelated Bosch refs, generic identity ambiguity and a duplicate CASE ref. This pair straddles the initial and continuation jobs. |
| Sander conflict | 20 / 19 | Both distinguish named 2.5Ah kit from 4.0Ah/50-disc kit and ask which is intended. P states the identity conflict more explicitly; both preserve its substantive facts. |
| Saw exclusion | 21 / 22 | Both clarify between BASE and SITE with correct refs. T's extra “excluding the fine-cut set” wording is not a new selection improvement. |
| Saw waterproof | 28 / 27 | P silently returns SITE. T loses waterproof, lists three DeWalt variants and additionally mentions “other Makita models” without framing them as alternatives to the exact identity. |
| Saw conflict | 29 / 30 | P unqualifiedly returns the corded SITE SKU for a cordless request. T stops OK but still offers three corded DeWalt variants and five other-identity Makita variants without stating the actual conflict. Not a clean repair. |
| Hedge exclusion | 32 / 31 | Both retain AK10 and BODY with correct refs. T newly echoes the excluded AK20 identifier in the message; it does not select or cite AK20 as a candidate. |
| Hedge waterproof | 37 / 38 | P silently returns AK10. T loses waterproof in the answer, broadens to other Stihl/Bosch identities and even a mower, despite the exact requested identity. |
| Hedge conflict | 40 / 39 | Both distinguish AK10 versus AK20 and ask which. Correct constraint contrast retained; no new repair. |
| Compressor exclusion | 41 / 42 | Both clarify between base and Silent Plus, with the two correct refs. T uses descriptive variants instead of literal SKU names; existing formatter behavior makes that a raw-wording difference, not lost/new final-agent coverage. |
| Compressor waterproof | 48 / 47 | P silently returns 50S. T identifies missing waterproof evidence for that exact SKU and asks for confirmation/details, retaining the correct sole ref. Substantive improvement without proving an eventual answer. |
| Compressor conflict | 49 / 50 | Both correctly state 50S=88dB versus requested 96dB. T omits the named 50S grounding ref and asks only about the 96dB siblings; this is a citation gap/narrower clarification than P, not a fabricated or unsupported factual assertion. |
| Glasses exclusion | 52 / 51 | Both offer all five eligible variants and no excluded ref. Both nevertheless echo the excluded AMBER identifier; P uses nonbreaking hyphens, which evade the mechanical literal-ID check. |
| Glasses waterproof | 57 / 58 | P silently returns 10PK. T drops waterproof, broadens to other 3M variants and two Uvex products, and does not retain the exact-ID/unknown-property distinction. |
| Glasses conflict | 60 / 59 | P unqualifiedly returns 10PK despite a one-piece request. T correctly describes `pack_count=10`, distinguishes the one-pair CLEAR alternative, and asks whether the user means 10-pack or single pair. Clear substantive improvement. |

## Citation and candidate-list regressions

Four treatment final actions include cross-family catalogue references: #18 sander waterproof (Bosch GEX125), #30 saw conflict (Makita DHS680), #38 hedge waterproof (Bosch hedge trimmers and a Stihl mower), and #58 glasses waterproof (Uvex Pheos). Parent has no cross-family refs in this sample. These are real source records already visible to both arms, but the answers fail to distinguish them from satisfying the original exact-identity request. Saw waterproof #27 also mentions Makita models without corresponding foreign refs, so a refs-only audit misses that extra candidate-list contamination.

The mechanical excluded-ID finding of P=0, T=3 misses P glasses #52 because its identifier uses U+2011 nonbreaking hyphens. Normalizing Unicode dash characters yields **one parent and three treatment messages echoing the excluded exact identifier**: P #52; T #11, #31, #51. This is a literal shared-policy quotation violation in “excluding Y” language, **not selection or recommendation of the rejected product**. No excluded SKU is present in these grounding-reference lists, and all six exclusion pairs cite exactly the eligible family records. These counts concern final answer messages and refs, not internal completed-step summaries. The saw treatment's descriptive “excluding the fine-cut set” is separately visible above and is not counted as an exact identifier echo.

Compressor conflict T #50 supplies a further citation weakness outside those tallies: it describes the requested 50S product's 88dB field but cites only the two 96dB siblings. P #49 cites all three. The stated 88dB fact is supported by the visible record; the missing citation should not be mislabeled as hallucination.

The prior d4955 formatter already appends candidate SKU names from cited refs. This review therefore assigns no new semantic coverage merely for literal SKU strings appearing in raw treatment messages. Appending identifiers cannot by itself restore a dropped waterproof/cordless qualifier, remove unrelated candidates or repair excluded-identifier quotations.

## Interpretation limits and conclusion

The design is 30 derived development requests over six families in one archived world, one parent/treatment observation per request with matched seed/settings and alternating order. It is not a random task population or multiple independent repetitions. The initial output-cap failure and continuation preserve responses but put one pair across job/time boundaries. This review verifies the supplied complete-response dataset and frozen request hashes; the primary provenance audit separately checks immutable transport attempts, trace recovery and cost reconciliation.

Outcome changes, positive controls, qualifier preservation, candidate relevance and citation compliance must remain separate observations. I do not aggregate them into an invented clean-repair count. The glasses conflict and compressor waterproof response show concrete improvements; other changed outcomes conceal residual errors, and exclusion/citation behavior regresses in specific places. Under the frozen PLAN's requirement for coherent qualifiers/descriptions, **the systematic remaining semantic failures block general-agent readiness**. No production candidate was changed, no tool action was executed from these outputs, and no full100 or actual task-completion gain is established.
