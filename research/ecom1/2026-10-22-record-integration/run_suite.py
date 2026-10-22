"""inara: offline regression suite for ECOM1 agents on recorded record-run worlds.

usage: python3 run_suite.py AGENT.py [WORLDS_DIR] [--json OUT.json] [--kit KIT_DIR]   (defaults: ./worlds, ./kit)

Every world is a complete recorded trial of the 78.30 record job j44887765 (replay-kit format, collected with --llm; old worlds contain only model replies). The agent runs against a fake `bitgn` (replay-kit replay.FakeBitgn, --llm recorded): ECOM rpcs are served from the recorded responses and the model returns the recorded replies in order.

Per world it compares RPC arguments, Answer with sorted refs, model requests and their placement among RPCs. identical is True only with complete verifiable request capture, False for a detected difference/error, and None for an otherwise matching advisory replay. The recorded grade is historical. Changed model inputs stop replay before a stale reply. Dependency-free CPython 3.
"""
import contextlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def recorded_sequence(kit, world, include_llm=False):
    seq = []
    for kind, data in kit.events_of(world):
        if include_llm and kind == "llm_request":
            seq.append("LLM")
            continue
        method = data.get("method")
        if kind != "rpc_request" or not method or method in ("StartTrial", "EndTrial"):
            continue
        args = data.get("arguments") or {}
        if method == "Answer":
            seq.append(answer_key(args.get("message"), args.get("outcome"), args.get("refs")))
        else:
            seq.append(kit.key(method, args))
    return seq


def first_difference(actual, recorded):
    for i in range(max(len(actual), len(recorded))):
        a = actual[i] if i < len(actual) else None
        b = recorded[i] if i < len(recorded) else None
        if a != b:
            return {"index": i, "agent": (a or "<end>")[:240], "recorded": (b or "<end>")[:240]}
    return None


def answer_key(message, outcome, refs):
    return "Answer " + json.dumps({"message": message, "outcome": outcome, "refs": sorted(refs or [])}, sort_keys=True)


def run_world(kit, agent_path, world_path):
    world = json.load(open(world_path, encoding="utf-8"))
    fake = kit.FakeBitgn(world, "recorded")
    calls, timeline = [], []
    real_call, real_answer, real_llm = fake.call, fake.answer, fake.llm

    def call(method, args):
        calls.append(kit.key(method, args))
        timeline.append(calls[-1])
        return real_call(method, args)

    def answer(message, outcome="OUTCOME_NONE_UNSUPPORTED", refs=None):
        calls.append(answer_key(message, outcome, refs))
        timeline.append(calls[-1])
        return real_answer(message, outcome, refs)

    def llm(model, messages, **parameters):
        timeline.append("LLM")
        return real_llm(model, messages, **parameters)

    fake.call, fake.answer, fake.llm = call, answer, llm
    error = None
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            exec(compile(open(agent_path, encoding="utf-8").read(), agent_path, "exec"),
                 {"bitgn": fake, "__name__": "agent"})
        except kit.Miss as exc:
            error = "model: " + str(exc)
        except Exception as exc:
            error = "crash: %s: %s" % (type(exc).__name__, exc)
    rec = recorded_sequence(kit, world)
    rpc_difference = first_difference(calls, rec)
    first = first_difference(timeline, recorded_sequence(kit, world, include_llm=True)) if fake.llm_capture_complete else rpc_difference
    task = (fake.task_info or {}).get("taskId") or world.get("task")
    final = fake.answers[-1] if fake.answers else None
    request_match = fake.request_fidelity()
    identical = False if first is not None or error is not None or request_match is False else request_match
    return {
        "world": os.path.basename(world_path), "task": task,
        "class": (int(task[1:]) - 1) % 20 + 1 if task and task[1:].isdigit() else None,
        "recorded_grade": (world.get("grade") or {}).get("score"),
        "identical": identical, "same_rpc_sequence": rpc_difference is None,
        "first_rpc_difference": rpc_difference,
        "llm_requests_match": request_match, "llm_requests_checked": fake.llm_requests_checked,
        "first_llm_difference": fake.llm_request_difference, "llm_recording_issue": fake.llm_recording_issue,
        "calls": len(calls), "recorded_calls": len(rec),
        "llm_calls": fake.llm_calls, "recorded_llm_replies": len(fake.llm_replies),
        "first_difference": first, "error": error, "rpc_misses": fake.misses[:6],
        "answer": final, "recorded_answer": fake.recorded_answer,
    }


def main(argv):
    kit_dir, out_json, rest = os.path.join(HERE, "kit"), None, []
    i = 0
    while i < len(argv):
        if argv[i] == "--json":
            out_json, i = argv[i + 1], i + 2
        elif argv[i] == "--kit":
            kit_dir, i = argv[i + 1], i + 2
        else:
            rest.append(argv[i])
            i += 1
    if not rest:
        raise SystemExit(__doc__)
    agent = rest[0]
    worlds_dir = rest[1] if len(rest) > 1 else os.path.join(HERE, "worlds")
    sys.path.insert(0, kit_dir)
    import replay as kit  # replay-kit replay.py
    paths = sorted(os.path.join(worlds_dir, n) for n in os.listdir(worlds_dir) if n.endswith(".json"))
    rows = [run_world(kit, agent, p) for p in paths]
    rows.sort(key=lambda r: (r["class"] or 0, r["task"] or ""))
    print("%-6s %-5s %-6s %-9s %-11s %-6s %s" % ("task", "class", "grade", "identical", "calls", "misses", "first difference / error"))
    for r in rows:
        diff = r["error"] or ""
        if r["first_difference"]:
            d = r["first_difference"]
            diff = ("#%d agent=%s | recorded=%s " % (d["index"], d["agent"][:90], d["recorded"][:90])) + diff
        print("%-6s %-5s %-6s %-9s %4d/%-6d %-6d %s" % (r["task"], r["class"], r["recorded_grade"], r["identical"],
                                                         r["calls"], r["recorded_calls"], len(r["rpc_misses"]), diff[:230]))
    same = sum(r["identical"] is True for r in rows)
    unknown = sum(r["identical"] is None for r in rows)
    print("identical %d/%d worlds; unknown request fidelity %d" % (same, len(rows), unknown))
    print("misses = rpcs absent from the recording (404 in replay); a new handler that needs unrecorded reads declines here,")
    print("so its target worlds show the record's fallback answer, not the handler's live behaviour.")
    if out_json:
        json.dump({"agent": agent, "rows": rows}, open(out_json, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
