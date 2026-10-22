# Narrow crosslist OCR layout repair on STACK E

Unsubmitted candidate based exactly on verified d3909r1. One line normalizes hash-delimited `scanline` layout prefixes only when they precede a complete, anchored numeric `Total requested lines:` or `Total requested units:` record. All existing strict parsing, row/property matching, policy checks and export behavior remain unchanged.

The archived winning-run t076 OCR has a prefixed units total and fails the record parser before catalogue matching. Removing only this layout prefix yields five rows and36units with the actual descriptions/properties. This is input-derived parsing, with no task-ID branch, answer constant or product special case in the candidate.

Normalization occurs before the strict parser counts totals. A valid plain total plus another recognized noisy total must therefore reject as duplicate or conflicting. Returning the original successful parse before inspecting recognized noise would miss this counterexample. Prose prefixes, incomplete/unterminated markers, trailing instructions and other row text are not stripped.

Exact candidate: **62,554 bytes**, **2,982 bytes headroom**, SHA-256 `bea10fc33c26ad138cc6eca3c77e7239f771213b4cf7faea399465c367001660`. Readable source145,993bytes. The unchanged record LZ algorithm packs it; decoded bytes exactly equal readable source. Exact parent packed/readable/build files and hashes are saved beside the candidate. `build.py` pins the record hash and extracts only the existing packing function.

Initial validation: **28 parser cases × two versions × CPython/native Monty passed**, covering actual OCR, clean controls, alternate spacing/case/hash layouts, CRLF/literal newlines, duplicate/conflicting totals, wrong totals, misleading prose, malformed prefixes, duplicate branches and illegible specifications. These are parser checks, not whole-agent or live-score evidence. The report preserves accepted/rejected behavior for both versions, including deliberate tightening when a previously ignored noisy duplicate becomes visible.

Before any submission: complete independent review, archived-world whole-handler/agent replay with a separately derived TSV oracle, broader clean crosslist and benign-request regressions, pinned runtime/build reproduction, and Git+Brain preservation. No model call or hosted evaluation has been made for this candidate. The normal two-outstanding full100 limit still applies; all three existing full100 jobs remain untouched.

Reproduction from the workspace:

```sh
python3 -W ignore::SyntaxWarning research/ecom1/2026-10-23-stack-e-ocr-repair/build.py
/private/tmp/ecom1-uv-cache/archive-v0/r9YlNqEbpR-drZJxnu69d/bin/python -W ignore::SyntaxWarning research/ecom1/2026-10-23-stack-e-ocr-repair/test_parser.py
```

Initial build used Python3.12.7; parser tests used Python3.14.3 and pydantic-monty1.2.0. Clean extracted rebuild and full dependency manifest remain release gates.
