# Exact record receipt fallback review

The community mirror d4814r1 raised a possible compound employee/receipt failure in record d3200r2 t043. The archived Read at event5955 is byte-for-byte identical, including response metadata, to our already saved archived_receipt.json. Its receipt SHA256 is fb1a7aaac8872d800a48e08045ac82bc3fe97f3c96049cdc05e632f2096cff98.

Both record and queued candidate rcp_request already accept the observed emp0099 identity and feasibility wording. Record rcp_items returns None; the original-first S-for-5 recovery already queued in d4702/d4955/d5204 recovers all four rows, subtotal524800 cents. CPython and native Monty agree. No extra employee handler is justified by this trace. The observed availability policy makes feasibility read-only; it does not authorize checkout.

This proves the parser blocker is reachable and covered, not that the entire task now passes. The failed trace contains no catalogue/store Reads. Do not borrow those values from another generated world or describe this as a hidden-grade recomputation. Exact record trace events are retained in record-t043-events.json (Brain d5225).

Run reproduce.sh. No paid evaluation, new candidate, submitted-source edit, or promotion.
