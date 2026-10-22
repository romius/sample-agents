"""Independent postprocessor for the pre-registered 16-call Brain diagnostic.

No model calls, generated actions or commerce RPCs are executed here.
"""
import collections
import json
import pathlib
import sys


def judge(record, fixture):
    out = {"case": fixture["case"], "kind": fixture["criteria"]["kind"],
           "false_ok": False, "wrong_sku_unique": False, "excess_clarification": False,
           "correct_final": None, "exact_sku_and_ref": None,
           "candidate_skus_in_message": None}
    if "error" in record:
        return dict(out, status="provider_error", error=record["error"])
    response = record["response"]
    choice = response.get("choices", [{}])[0]
    content = choice.get("message", {}).get("content") or ""
    out.update(finish_reason=choice.get("finish_reason"), usage=response.get("usage"))
    if choice.get("finish_reason") == "length":
        return dict(out, status="truncated")
    body = content.strip()
    if body.startswith("```") and body.endswith("```"):
        lines = body.splitlines()
        body = "\n".join(lines[1:-1]).strip()
    try:
        action = json.loads(body)
    except (ValueError, TypeError):
        return dict(out, status="malformed")
    if not isinstance(action, dict) or not isinstance(action.get("tool"), str):
        return dict(out, status="malformed")
    tool = action["tool"]
    out["action"] = action
    if tool in {"read", "catalog", "search", "find", "tree", "list", "stat"}:
        return dict(out, status="deferred_lookup")
    if tool != "report_completion":
        return dict(out, status="unexpected_action")
    message, outcome = action.get("message"), action.get("outcome")
    refs = action.get("grounding_refs", [])
    if (not isinstance(message, str) or not message.strip()
            or not isinstance(refs, list) or any(not isinstance(r, str) for r in refs)
            or outcome not in {"OUTCOME_OK", "OUTCOME_NONE_CLARIFICATION",
                               "OUTCOME_DENIED_SECURITY", "OUTCOME_NONE_UNSUPPORTED",
                               "OUTCOME_ERR_INTERNAL"}):
        return dict(out, status="malformed")
    criteria = fixture["criteria"]
    if criteria["kind"] == "exact":
        out["excess_clarification"] = outcome == "OUTCOME_NONE_CLARIFICATION"
        out["wrong_sku_unique"] = outcome == "OUTCOME_OK" and message.strip() != criteria["sku"]
        out["exact_sku_and_ref"] = (outcome == "OUTCOME_OK"
            and message.strip() == criteria["sku"] and criteria["path"] in refs)
        out["correct_final"] = out["exact_sku_and_ref"]
    else:
        out["false_ok"] = outcome == "OUTCOME_OK"
        out["correct_final"] = outcome == "OUTCOME_NONE_CLARIFICATION"
        if criteria["kind"] == "clarify":
            out["candidate_skus_in_message"] = all(s in message for s in criteria["skus"])
            paths = {p["sku"]: p["path"] for p in catalog_observation(fixture)["matches"]}
            out["candidate_refs_present"] = all(paths[s] in refs for s in criteria["skus"])
            out["correct_final"] = (out["correct_final"]
                and out["candidate_skus_in_message"] and out["candidate_refs_present"])
    return dict(out, status="final")


def catalog_observation(fixture):
    text = fixture["arms"]["parent"]["messages"][-1]["content"]
    return json.loads(text[text.index('{"matches"'):])


def analyze(records, frozen):
    plan = frozen["plan"]
    expected = {(x["case"], x["repeat"], x["arm"]): x for x in plan}
    assert len(expected) == len(plan) == 16
    seen = {}
    rows = []
    for record in records:
        step = record["step"]
        key = (step["case"], step["repeat"], step["arm"])
        assert key in expected and step == expected[key] and key not in seen
        seen[key] = True
        row = judge(record, frozen["fixtures"][step["case_index"]])
        row.update(step=step)
        rows.append(row)
    assert set(seen) == set(expected), "Missing planned results; do not silently omit a pair"
    summaries = {}
    for arm in ("parent", "treatment"):
        rr = [r for r in rows if r["step"]["arm"] == arm]
        ambiguous = [r for r in rr if r["kind"] != "exact"]
        unique = [r for r in rr if r["kind"] == "exact"]
        summaries[arm] = {
            "planned_calls": len(rr), "ambiguous_calls": len(ambiguous),
            "unique_calls": len(unique), "false_ok_ambiguous": sum(r["false_ok"] for r in ambiguous),
            "wrong_sku_unique": sum(r["wrong_sku_unique"] for r in unique),
            "wrong_choices_total": sum(r["false_ok"] or r["wrong_sku_unique"] for r in rr),
            "excess_clarification_unique": sum(r["excess_clarification"] for r in unique),
            "correct_exact_sku_and_ref": sum(r["exact_sku_and_ref"] is True for r in unique),
            "correct_final_decisions": sum(r["correct_final"] is True for r in rr),
            "statuses": dict(collections.Counter(r["status"] for r in rr))}
    bykey = {(r["step"]["case"], r["step"]["repeat"], r["step"]["arm"]): r for r in rows}
    transitions = []
    for fixture in frozen["fixtures"]:
        for repeat in (0, 1):
            a = bykey[(fixture["case"], repeat, "parent")]
            b = bykey[(fixture["case"], repeat, "treatment")]
            both = a["status"] == b["status"] == "final"
            transitions.append({"case": fixture["case"], "repeat": repeat,
                "parent_status": a["status"], "treatment_status": b["status"],
                "both_final": both,
                "fixed": both and a["correct_final"] is False and b["correct_final"] is True,
                "regressed": both and a["correct_final"] is True and b["correct_final"] is False})
    return {"arms": summaries, "pairs": transitions, "rows": rows,
        "fixed_pairs": sum(p["fixed"] for p in transitions),
        "regressed_pairs": sum(p["regressed"] for p in transitions),
        "both_final_pairs": sum(p["both_final"] for p in transitions),
        "limits": ["Four questions, two underlying catalogue contexts, two repeats; no population estimate.",
                   "Next action only. Deferred lookups are not completed task successes or unnecessary clarifications.",
                   "No full-agent or official benchmark score effect measured."]}


if __name__ == "__main__":
    records = json.loads(pathlib.Path(sys.argv[1]).read_text())
    frozen = json.loads(pathlib.Path(sys.argv[2]).read_text())
    report = analyze(records, frozen)
    pathlib.Path(sys.argv[3]).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, ensure_ascii=False))
