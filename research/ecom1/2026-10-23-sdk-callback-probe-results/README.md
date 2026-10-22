# Hosted SDK callback boundary confirmed

Exact probe d6368r1 / job `j9b18bdffe5fa4ac39383f908170b20a0` completed2026-10-22T23:25:06UTC, SDK0.3.7, zero inference calls and $0 cost with complete accounting. Source hash `223cb4dc6ad9b6226f5dd2ce1aaf39001af7c840e902cc65be021866d86ef1a3` matches the independently reviewed source published before submission.

Actual service behavior confirms the local method-only ClassInstance result: reading `bitgn.call` as a value raises `'BitGN' object has no attribute 'call'`; calling it directly and through the named guest wrapper both return identical successful `/bin/id` identity responses. Both RPC requests and responses are preserved; no RPC error occurred. The response schema supplies stdout without an exit-code field, so this is not an assertion about a captured exit code. The carrier task was deliberately not attempted and its grade0 is not scoring evidence.

All11 raw events reproduce the complete sealed3244-byte trial trace SHA-256 `e102a5f3ef60e690915f8f4059f4abfff090f9ed3c4c6074ff5ebcf5f923068f`. `verify.py` checks index offsets/lengths, source, lifecycle, both Exec calls, observed exception and zero-model accounting. The three prior full100 jobs remain unchanged; no resubmission or cancellation follows from this probe.

This confirms a reachable startup defect in the callback-value expression shared by historical d5204/d5785 and the failed community d4007. The independently reviewed minimal successors and regression archive are Brain d6376 (Git f8f9eae/7b704f2). It does not prove whole-agent task success or improve the installed94.11366 record, whose next candidates must be based on d3909r1.
