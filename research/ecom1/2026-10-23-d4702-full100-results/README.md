# d4702 full100 result audit

**87.08894/100, below the exact current record of94.72095/100. Do not promote.** Job `jfdd875bba6ba4773a549e8703764efa9`, run `run-22rKo2UTyvRLgWXdqqZ49dSgi`, source **d4702r1**, completed2026-10-23T01:00:39.202364Z. All 100 trials completed with no execution failures:83 full credit,12 zeros,5 dispatch partials. Official usage is244 model calls,771806 tokens and **USD0.034498464, complete**. `result.json` retains the official job and result; agent stdout usage snapshots are not substituted for settled accounting.

## What was reviewed

`all100-review.json` and `.md` cover **every actual StartTrial instruction, official grade, final Answer RPC and full agent_finished stdout**. Every JSON row includes the exact instruction hash, complete answer parameters/outcome, full stdout, event paths/hashes, evidence level, observation, diagnosis and uncertainty. The83 full-credit rows were reviewed against their instructions and logs; full credit is not independent semantic certification of every business fact or action.

`success-evidence/` preserves the parallel review of all83 successes, including271 exact events:249 Answer/acknowledgement/agent_finished events and22 supporting RPC events for t079/t091. Seven additional Read-content hashes are verified. These are complete final logs and sampled tail indexes, not complete successful-trial CAS reconstructions. Its372-file seal is verified without modifying the independently prepared package. All successful-task finishing usage snapshots show zero model calls, while settled successful-task usage totals179; settled official accounting remains authoritative.

Success credit does not hide reliability signals. Six cases recover eight malformed-action responses. t079 unnecessarily reads two foreign-owner baskets during discovery before correctly appending one requested line to its own newest basket; targeted evidence shows no foreign data in the final answer or Write, and the policy status of those discovery reads remains unresolved. t091 recovers a SQL connection failure (exit1, not Exec404), receives a successful CSV Write acknowledgement, but returns a leading space before the path; future stock columns are not independently recomputed. Crosslist preview logs alone do not establish correct TSV contents. The full per-task caveats are preserved.

All17 loss indexes are complete and their offsets cover the official trial byte counts. Every loss retains **all RPC requests, all model responses, final Answer and agent_finished**, plus relevant policy, upload, product and model-input evidence. Eight complete scopes—five dispatches, t016, t039 and t060—reconstruct exact official CAS hashes. Nine larger scopes retain selected immutable events; their concatenated selected-event hashes are explicitly **not** whole-trial CAS hashes. `reassembly-verification.json` and `verification.json` distinguish these scopes. Raw Brain requests/responses and chunk receipts are preserved.

All65 model responses across the17 losses have HTTP200. The complete indexes contain no inference error, retry or agent_error events. Nine replies have null final content:3 in t016,2 in t043,4 in t074. These are final-content/agent-control failures, not demonstrated transient transport failures. Executing action-shaped reasoning text is not proposed.

## Loss mechanisms

| Cases | Observed mechanism | Limit or next useful check |
|---|---|---|
| t004,t014,t024,t044,t064 | Deterministic dispatch returns all10 assignments with no invalid or missed packages. Official gain is below the task maximum. | Planner unchanged; optimize against exact wave data. Do not derive the score formula from gain/max. |
| t016 | OCR parser declines a tilde-prefixed total. Fallback has3 consecutive null final contents. Forced reply is a read action, then ERR_INTERNAL. | Current hash-scanline OCR candidate does not cover this input. Tilde removal alone exposes another footer blocker. |
| t022 | Model includes the12-piece set; final reference processing additionally inserts excluded5LONG. Grading accepts4-piece only. | Actual policy forbids quoting excluded Y. Removing5LONG alone cannot fix the extra12-piece selection. |
| t023 | Receipt helper declines a corrupted SKU; fallback answers based on employee identity and omits the OCR reference. | Grader reports missing OCR grounding; do not claim this validates its availability reasoning. |
| t039 | Four target files are listed, only three Delete RPCs execute. A malformed reply contains the fourth intended deletion. Final Answer falsely claims all four. | d4702 removed the deterministic cleanup route. Separate native matched-world replay isolates that change. |
| t042 | Model selects190mm despite excluding190mm; final reference processing adds explicitly excluded160. Required216 is missing. | Both product qualification and policy-sensitive reference handling need attention. |
| t043 | Receipt helper declines; fallback reports NO with incomplete product evidence. Reference repair adds only two of four required products. | Preserve exact OCR and partial-reference evidence; retrying HTTP200 is not a demonstrated fix. |
| t047 | Answer1 versus expected0. The cited download guide costs1290 cents below1395 cap and belongs to the visible field-guide family. | **Semantic target remains unresolved.** Visible evidence does not justify inventing a hidden qualifier or hardcoded zero rule. |
| t060 | Model lists the directory then refuses because it believes multiple deletions cannot be done in one action. No deletion occurs. | Sequential actions were possible; deterministic cleanup route was removed. |
| t062 | Model selects the excluded plain125 product and omits required150. Final refs include CASE. | Actual catalogue policy lacks the excluded-Y exception; grader does not flag CASE as extra. Blanket exclusion-reference removal is unsafe as a general rule. |
| t063 | Corrupted OCR SKU causes helper decline; fallback denies a read-only availability question because the identity is not a customer. | Repair task interpretation and evidence recovery without weakening authorization rules. |
| t067 | Counts160 and190 as two matches despite “larger”; expected1.216 is over budget. | Test family-relative qualifiers rather than task IDs or unrestricted substring rules. |
| t074 | Four null final contents; after one valid action, forced reply is search rather than completion. Generic30-step-limit answer follows. | The message is inaccurate for this short path. A bounded final-content recovery experiment is separate from transport retry. |

Exact event sequences, findings and uncertainty are recorded per case in `loss-review.json`. `excluded-sku-counterexamples.json` preserves the model-versus-final-reference distinction and the contrary policy context in t062.

A general fallback boundary is also observable. The receipt helpers read their uploads, but the first main-model requests in t023 and t063 contain neither full OCR content nor its path. They retain only eight bootstrap, policy and instruction messages. In t016 the explicit instruction preserves the upload path, but the helper-read OCR content is also absent. This is an evidence-transfer gap, not merely malformed input. The t043 control shows its later request does contain the whole OCR after the model explicitly rereads it, yet product grounding still fails. `fallback-context-review.json` pins the exact Read and model-request sequences; testing evidence transfer should therefore remain separate from qualification and reference repairs.

## Parent and comparison limits

d4702 is a **direct derivative of d4353r1/d4354r1**, on the earlier inara d3200r2 source. It adds the exact d4445r1 MSR wrapper at four inference sites, removes `cleanup` from `I2C_MODULES`, and ports the explicit missing-Exec branch from d3513r1 while preserving the Delete404 guard. The source build manifest identifies the changed AST nodes; all other parent nodes are preserved. Exact packed/readable parents, donors, packer and build are included. A clean temporary build reproduces d4702 packed and readable bytes exactly.

Current record job `j6d6d4adb60f241a4a1d111a9719b59dc`, source d4353r1, has216 model calls, USD0.030785032 complete, and679006 tokens. The observed score difference is **−7.63201 points**, not a paired causal estimate: **92/100 actual instructions differ bytewise**. In particular, record t022 and t042 are injected requests while our corresponding requests are benign catalogue questions. Eight wording matches still do not establish equal world state. Current record copies are pinned in `comparison/`; the independent record audit owns their original harvest.

One control has identical **observed dispatch inputs and actions**: t024. Both complete29-event traces are preserved and their official CAS hashes verified. Actual instruction bytes, all six Read contents (AGENTS, security, dispatch policy, wave, packages and lanes), all11 non-StartTrial/EndTrial RPC argument/response pairs, and the single model request's parameters/messages are equal. This includes root Tree, date/identity stdout and final Answer/acknowledgement. The score is0.8233437 in both runs. Trial/run identity wrappers and timestamps are excluded; no equality of unobserved world files is asserted. `compare_t024.py` and its comparison JSON specify this coverage. It supports unchanged behavior for that one wave only.

## Actual OCR falsification

`t016-uploaded-ocr.txt` is exact Read response2628 following request2627, SHA256 `50296b921e09ba7340b743ce4cd991d6f41e9cab90d4daa88348805a8bdb7e7d`. The requested-lines record starts with ` ~~ ~~  `, not a hash-delimited ASCII `scanline` marker. Exact d4702, d4353 and current63411-byte hash-scanline candidate all reject it identically in CPython and native Monty.

Deleting that exact prefix counterfactually exposes the second blocker: `x x x ////  =========:===============-========:=================.=======:====.===` while still parsing the final row's specifications. Deleting both exact observed strings allows five rows/28 units to parse. This is **stagewise parser diagnosis, not an accepted patch or whole-agent result**. An unknown meaningful-prose control in the same position rejects, as do duplicate/conflicting totals and a Unicode tilde control. A broad “ignore unknown lines” repair could erase real requirements.

`t016-observed-world.json` contains only actual observed RPC requests/responses from the complete trace. No catalogue or store record was read before failure, so it is explicitly sparse. No full actual world or matching-product oracle is invented. The parent owns further OCR work separately; the published hash-scanline candidate is not relabeled as covering this case.

## Reproduce offline

From this directory, run `python3 reassemble.py t004 t014 t016 t022 t023 t024 t039 t042 t043 t044 t047 t060 t062 t063 t064 t067 t074`, `python3 build_review.py`, `python3 build_evidence_notes.py`, `python3 compare_t024.py`, and `python3 verify.py`. The independently sealed success package also provides `python3 success-evidence/build_review.py` and `python3 success-evidence/verify_targeted.py`. Run `python check_t016_ocr.py` with pydantic-monty1.2.0 for the parser comparison. Author parser checks use Python3.14.3/Monty1.2.0; the structural/source check also runs with local Python3.12.7. A standard `patch` executable is needed for exact parent reconstruction. Scripts read local evidence only and do not make model or ECOM calls.

Read-only Brain session s7984 closed with `brain.discard()`; no workspace changes were published, no evaluation submitted, no baseline changed and no live agent edited. The separate earlier retry-comparison archive remains untouched.
