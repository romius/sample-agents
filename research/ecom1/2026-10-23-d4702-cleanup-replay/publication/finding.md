# Removing cleanup coverage exposed two archived failures

romius · 2026-10-23 01:40 UTC. [Evidence README](../experiments/2026-10-23-romius-d4702-cleanup-replay/README.md), archive d6742, independent check d6744, local Git2c90aed.

Exact d4353r1 retains deterministic cleanup. d4702r1 removes its module registration while leaving the function unchanged. Full100 scores94.72095 versus87.08894 are unpaired:92 instructions differ. This finding does not attribute the aggregate7.63201-point drop.

For actual d4702 t039, frozen replay matches all seven model wire requests, every RPC and the final Answer: three of four `.tmp` files are deleted; the fourth action is malformed JSON, then the model claims all four were deleted. In the same world, the parent selects all four exact List entries and completes after only the shared router response. The fourth Delete acknowledgement is simulated because it was never observed live.

For actual d4702 t060, replay matches all three model wire requests, the unsupported Answer and zero Deletes. The parent selects all nine files in the same world; all nine Delete acknowledgements and state effects are simulated. Neither test measures a new live grade.

The48 t039 cells plus8 t060 cells cover both sources, readable/packed forms and CPython/native runtimes. Fresh suffix, directory/no-match and partial-error controls are included. All56 reproduce from clean extraction with sealed files unchanged. Independent root review repeated clean extraction and all56 cells. Archive:27 members,2,469,825 bytes, SHAe86ff6a49ab13d90f8088bc705e5dd9b445eeae9ead089d8d0409f4ff8bf9917.

Decision: preserve successful deterministic cleanup in the new baseline. The inherited handler still catches an unconfirmed fourth-Delete error and returns partial OUTCOME_OK. That needs a separate narrow repair for uncertain effects; neither blind mutation retries nor model fallback after side effects is justified. This experiment made no production patch or paid call.
