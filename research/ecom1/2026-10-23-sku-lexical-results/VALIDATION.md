# Local validation

Prepared offline on 23 October 2026 for the queued 68-call job. No real 68-call response evidence is present.

- All 30 archived/synthetic checks pass; the original archived16 capture verifier was rerun unchanged against a temporary copy.
- All 16 input dependency hashes match. The frozen diagnostic/capture archive's 99 source members were rehashed and remain unchanged.
- Every audit keeps all planned cells. Missing/truncated inputs produce explicit incomplete/deviation findings. Cancellation alone without complete trace/stdout evidence does not certify unattempted calls.
- Full final events and raw content are preserved for manual review; retries retain distinct attempt identities. Structural reconciliation, billing completeness and semantic review are separate.
- No semantic scorer, inference, live retrieval, Brain edit, Git commit or dispatch occurred.

Reproduction: run `test_validator.py` with Python 3.14.3 using the command in README.md. Its results are solely validator tests. Dependency pins include the frozen requests/plan, original verifier/trace/summary, SDK guide, and source-linked alias/retry/error schema evidence.

Independent review has been requested from integration_plan after their ongoing evidence write. This local validation does not substitute for that review.
