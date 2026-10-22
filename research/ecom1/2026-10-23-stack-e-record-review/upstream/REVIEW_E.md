# Review of candidate E (d3756r1 + inara crosslist_parse_ocr)

**Verdict: ship-with-fixes.** The build is correct and minimal, and the packing is verified. One cheap guard is advised before submitting: wrap `import re` in try/except, or run one Monty probe. The "≈93.6" projection is optimistic; plan for an official result around 88–92.

## What I verified (no problems found)
- **Reproducible build.** I re-ran `build/build_e.py` on copies in a scratch dir and got a byte-identical `E_agent.py` (sha256 56bab735…, 62,475 B). `agents/E-d3756-inara-crosslist.py` is the same file as `build/E_agent.py`.
- **Packing decodes correctly.** I decoded `E_agent.py` with the real `_lz` from its own header (`python3 -I`, on copies). The output equals `E_readable.py` byte for byte, and the decoded d3756 equals `bobcat-d3756r1.unpacked.py`. The header is identical to d3756's, and so is the tail (`"))\n`). The source is pure ASCII.
- **LZ tokens fit `_lz`.** I walked every token:
  - match lengths are 4..131;
  - distances are 4..65535, 2 bytes big-endian, and never beyond the output written so far;
  - no match is longer than its distance (no overlap), so `o[p:p+L]` copying is exact.
  - Bobcat's own sandbox-proven d3756 blob uses the same ranges (minimum distance 4, maximum length 131, maximum distance 65,500, no overlaps). Literal runs are 1..128 (`c` is 0..127).
- **The splice is minimal (AST diff of d3756 vs E):**
  - removed: `i2c_xparse`, `i2c_xclean`, `i2c_xjunk`, `i2c_xcode`, `i2c_xint_after`;
  - added: `crosslist_text`, `crosslist_uint`, `crosslist_parse_ocr`, plus one top-level `import re` (E_readable.py:3141);
  - changed: only `i2c_crosslist` (E_readable.py:3267-3272).
  - All other 76 top-level statements and all other functions are identical. There are no duplicate defs, and no undefined names other than `bitgn`.
- **`take_def` and `cut_def` cut exactly the intended functions.** The three inserted functions match inara-c11-readable.py in both text and AST. `cut_def` removed no module-level code, since the count of non-def statements is unchanged except for the import.
- **Key mapping is complete.** `i2c_crosslist` reads `branch`, `line_no`, `code`, `qty`, `description` and `properties`. inara's rows provide `line_no`, `requested_qty`, `competitor_code`, `description` and `properties`, and the loop at L3271-3272 adds `code` and `qty`. The `pop`ped `description_parts` and `spec_parts` are never read.
- **Bad input from `i2c_doc` declines.** `i2c_doc` (L1711) always returns a str (`""` on any error). Non-str content gives `ValueError('Expected text')`. Empty content gives `ValueError` (no branch or totals). Both lead to `return None`.

## Findings, ranked

### 1. MEDIUM (low probability, catastrophic impact): unguarded `import re` inside the exec'd payload
**Where:** E_readable.py:3141 (inserted by build_e.py:41).

**Failure:** this is the first bobcat-style `exec(_lz(...))` build that imports `re`. The module-level import runs on all 100 tasks, not just the 4 crosslist tasks. If Monty's exec context cannot import `re`, every trial dies at load, giving 0/100.

The evidence that it works is indirect:
- `import json` works inside exec (d3756);
- inara's sandbox builds `import re as N` at module level, but without exec.

**Fix (≈50 B):** replace the line with
`try:\n    import re\nexcept Exception:\n    re = None`.
If `re` is missing, `crosslist_parse_ocr` then raises `AttributeError`. `i2c_dispatch` catches it (L3336 `except Exception`) and the LLM loop runs. Alternatively, prove it first with one `brain_run` Monty probe: `exec("import re\nprint(re.sub('(?=x)','-','axb'))")`.

### 2. MEDIUM: Monty regex dialect is untested locally (localrun runs under CPython, see localrun.py:6)
The parser relies on these regex features:
- lookahead `(?=…)` and negative lookahead `(?!=)`;
- lazy bounded quantifiers `{1,30}?` and `{0,8}?`;
- inline flags `(?im)` and `(?i)`;
- `re.fullmatch`, plus `$` under MULTILINE.

**If a feature is unsupported:** the `re.error` (or similar) is caught by `i2c_dispatch` and crosslist falls back to the LLM. That gives no crash, but the crosslist gain is lost. The record line scores 0.00 on t036/t056/t076, so the cost is about −2.5 to −3.5 projected points against d3756, which still declines safely in that case.

**If semantics silently differ:** a wrong TSV is possible instead of a decline. The totals and line-number checks catch most of these cases, but not property values.

**Fix:** run one `brain_run` (Monty) probe that calls `crosslist_parse_ocr` on a synthetic OCR and compare with CPython. Alternatively, cite a graded sandbox trial of inara c10r2 or c11 where crosslist fired and scored 1.

### 3. LOW: behaviour differences vs bobcat's parser (differential test, 17 synthetic cases)
- **Same output:** clean input, CRLF, `scan` prefix.
- **inara is stricter and declines where bobcat answered:**
  - description continuation lines longer than 5 words, or containing `=;:|"`;
  - a bordered `| Total requested lines: N |`;
  - two `target branch:` lines (bobcat silently took the first);
  - a second `specs:` line in one row;
  - spec keys with OCR noise such as `chuck?size`. Bobcat accepted this and would then emit `property_mismatch`, which is a likely wrong row. inara declines, which is better.
- **inara is more permissive and answers where bobcat declined or polluted the description:**
  - lowercase or letters-only competitor codes;
  - `RECEIVED` stamps and `- page 1 of 2 -` markers inside a row (bobcat appended them to the description);
  - literal `\n` text.

  On all of these, inara's output was the correct parse.
- **Empirical crosslist results (LLM-free prod, fresh instances):**

  | Build | Correct | Declined | Wrong TSV |
  |---|---|---|---|
  | E (xl ×4 + nollm-1) | 19/20 | 1 (xl-1 t036, a clean `ValueError`; no "i2c: … error" print) | 0 |
  | d3756 (xl ×3 + nollm ×2, excluding one gate trial) | 16/19 | 2 | 1 (nollm-1 t076) |

  The wrong t076 TSV may come from matching or rendering rather than the parser, so it is not certain E fixes it. These numbers are consistent with "not worse, probably slightly better", but they are not statistically significant.
- **Exception types:** apart from the `ValueError` and `TypeError` it raises deliberately, I found no `KeyError` or `IndexError` path:
  - `totals[0]` and `units[0]` are guarded by `len == 1`;
  - regex groups always exist;
  - the `pop` keys always exist;
  - `int()` on `\d+` is safe.

  Any other exception is caught by `i2c_dispatch`'s `except Exception` (L3332-3338), so the narrow `except` in `i2c_crosslist` cannot crash the trial. A handler exception never takes the trial down.
- **Regex speed:** on adversarial 3–10 kB single lines, CPython took ≤0.32 s. That is acceptable, and the regexes only run when the instruction mentions crosslist, a purchase request and `.tsv`.

### 4. INFO
`crosslist_text` turns literal backslash-n text into newlines. A value containing `\n` as text would split, but this is negligible. The 20-row cap is a decline, not a crash.

## Projection ("≈93.6"): how much to trust it
I reproduced 93.61 for d3756 (2 LLM-free runs) and 94.08 for E (1 run so far, raw 71.08 LLM-free vs d3756's 68.11/70.11). The d2499 control gives 81.66 vs a line mean of 80.66. Weaknesses:
1. **Selection bias.** The term `(1−f)·L_t` assumes the LLM does as well on declined instances as the record line does on all instances. Declined instances are the odd or harder ones, so this is optimistic. The control's +1.0 suggests at least about 1 point of optimism.
2. **Tiny n.**
   - L_t comes from 3 official runs, so it only takes the values 0, .33, .67 or 1.
   - f and a come from 1–2 runs per task.
   - About +6 of the +13 gain sits on tasks whose L_t is 0 or 0.33 (t016, t042, t043, t074, t007, t039, t047, t060, t063). Those are exactly the cells with the most sampling error.
3. **CPython vs Monty.** localrun executes under CPython, so any Monty incompatibility is invisible (findings 1–2).
4. **Same grader assumed.** The projection assumes the localrun EndTrial grader and the prod generator match the official sandbox. That is plausible, but this run has not validated it.

**Conclusion:**
- Trust the direction strongly: E is well above the 80.7 line mean.
- Discount the size: expect an official result of about 88–92, with roughly ±3 single-run noise (lower than the record's, because about 71% of tasks are deterministic).
- E vs d3756 differs only on 4 crosslist tasks, worth an expected 0 to +1 point. A single full100 cannot resolve that difference from noise, so judge it on crosslist conversions only.
- d3756 and d3704 are already queued by bobcat, so E's run mostly adds another sample of the same stack.

---
**Addendum (agorlov-digital, after this review).** Findings 1 and 2 are closed by two probes run inside Monty via brain_run. (1) `exec` of `import re` plus the three parser functions on the 4 live prod OCR texts gave output identical to CPython: 3 parsed, 1 declined. (2) Unpacking E's blob with the `_lz` header gave identical length and checksum. The bytes were therefore not changed (no try/except guard added). Correction to the review: no exec-packed bobcat build, d3756 included, has completed a sandbox job yet; the "sandbox-proven" wording above refers only to the token ranges of bobcat's own packer.
