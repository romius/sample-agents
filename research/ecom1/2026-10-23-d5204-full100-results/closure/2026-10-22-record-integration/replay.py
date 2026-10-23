"""replay-kit / replay.py — run an agent.py against recorded ECOM1 trial worlds, offline.

usage: python3 replay.py AGENT.py WORLD.json [WORLD.json ...] [--llm MODE] [--json] [--show-output]

A fake `bitgn` serves every ECOM rpc from the world's recorded request/response pairs
(exact method + arguments; then a loose match on the same method and path/root; Tree
requests can be cut from a recorded level-0 Tree of an ancestor). Anything else raises
the runtime's 404 and is listed as a miss. Write/Delete are captured, not applied.
Answer is captured and compared with the recorded Answer and grade.

--llm MODE
  fail       any model call raises (default): proves a deterministic path needs no model
  router     first call returns {"docs": []}-style routing from --route PATH (repeatable),
             later calls raise
  recorded   check each recorded model request before returning its reply (collect with --llm);
             legacy response-only worlds remain advisory, with unknown request fidelity
  script:F   F is a JSON list of reply strings, served in order
--route PATH  doc path returned by the router stub (with --llm router)
Dependency-free CPython. LLM behaviour is NOT simulated: only recorded or scripted replies.
"""
import contextlib
import io
import json
import sys


def events_of(world):
    for e in world["events"]:
        if "data" in e:
            yield e["kind"], e["data"]
        elif "body" in e:
            b = json.loads(e["body"])
            yield b["kind"], b["data"]


def key(method, args):
    return method + " " + json.dumps(args, sort_keys=True)


class Miss(Exception):
    pass


def sdk_request(model, messages, parameters):
    parameters = dict(parameters)
    if "max_completion_tokens" in parameters:
        value = parameters.pop("max_completion_tokens")
        if "max_tokens" in parameters and parameters["max_tokens"] != value:
            raise ValueError("conflicting completion-token aliases")
        parameters["max_tokens"] = value
    if "reasoning_effort" in parameters:
        value = {"effort": parameters.pop("reasoning_effort")}
        if "reasoning" in parameters and parameters["reasoning"] != value:
            raise ValueError("conflicting reasoning aliases")
        parameters["reasoning"] = value
    return dict(parameters, model=model, messages=messages)


def recorded_request(data):
    request = dict(data["request"])
    provider = request.pop("provider", None)
    pinned = {"only": ["cerebras/fp16"], "quantizations": ["fp16"], "allow_fallbacks": False, "require_parameters": True}
    if provider is not None and provider != pinned:
        raise ValueError("unsupported provider configuration in recording")
    if request.pop("stream", False) is not False:
        raise ValueError("streaming recording is unsupported")
    model, messages = request.pop("model"), request.pop("messages")
    allowed = {"max_completion_tokens", "max_tokens", "temperature", "top_p", "stop", "seed", "frequency_penalty", "presence_penalty", "reasoning", "reasoning_effort"}
    if set(request) - allowed:
        raise ValueError("unsupported recorded request parameters")
    return sdk_request(model, messages, request)


def same_json(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(same_json(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(same_json(a, b) for a, b in zip(left, right))
    return left == right


class FakeBitgn:
    def __init__(self, world, llm="fail", routes=None, script=None):
        self.responses, self.loose = {}, {}
        self.task_info, self.recorded_answer, self.llm_replies = {}, None, []
        self.llm_requests, requests, seen_requests = [], {}, set()
        self.llm_recording_issue = None
        self.llm_request_difference = None
        self.llm_requests_checked = 0
        trial_finished = False
        pending = {}
        for kind, data in events_of(world):
            method = data.get("method")
            if kind == "agent_finished":
                trial_finished = True
            if kind == "rpc_request" and method:
                pending[method] = data.get("arguments") or {}
                if method == "Answer":
                    self.recorded_answer = data.get("arguments")
            elif kind == "rpc_response" and method and "response" in data:
                args = pending.pop(method, None)
                if method == "StartTrial":
                    self.task_info = data["response"]
                elif args is not None and method not in ("Write", "Delete", "Answer", "EndTrial"):
                    self.responses.setdefault(key(method, args), data["response"])
                    anchor = args.get("path") or args.get("root")
                    if anchor:
                        self.loose.setdefault(method + " " + anchor, data["response"])
            elif kind == "llm_request":
                identity = (data.get("trial_id"), data.get("call"), data.get("attempt", 1))
                if identity in seen_requests or identity[1] is None or identity[2] != 1:
                    self.llm_recording_issue = "ambiguous or retried model request"
                seen_requests.add(identity)
                requests[identity] = data
            elif kind == "llm_response":
                if data.get("status", 200) != 200 or "response" not in data:
                    self.llm_recording_issue = "model-error recording requires advisory replay"
                    continue
                self.llm_replies.append(data["response"])
                identity = (data.get("trial_id"), data.get("call"), data.get("attempt", 1))
                request = requests.pop(identity, None)
                try:
                    self.llm_requests.append(recorded_request(request) if request is not None else None)
                except (KeyError, TypeError, ValueError) as exc:
                    self.llm_requests.append(None)
                    self.llm_recording_issue = str(exc)
        if (not trial_finished or self.recorded_answer is None) and self.llm_recording_issue is None:
            self.llm_recording_issue = "recording lacks a finished trial with Answer"
        self.llm_capture_complete = (world.get("llm_requests_recorded") is True and not requests
                                     and trial_finished and self.recorded_answer is not None
                                     and all(request is not None for request in self.llm_requests)
                                     and self.llm_recording_issue is None)
        if not self.llm_capture_complete and self.llm_recording_issue is None:
            self.llm_recording_issue = "complete model requests were not recorded"
        if not self.task_info.get("instruction"):
            self.task_info["instruction"] = world.get("instruction")
        self.grade = world.get("grade")
        self.mode, self.routes, self.script = llm, routes or [], script or []
        self.writes, self.deletes, self.answers = [], [], []
        self.misses, self.derived, self.loose_hits, self.llm_calls = [], [], [], 0

    # --- ECOM runtime -------------------------------------------------------------
    def task(self):
        return dict(self.task_info)

    def call(self, method, args):
        if method == "Write":
            self.writes.append(args)
            return {"path": args.get("path")}
        if method == "Delete":
            self.deletes.append(args)
            return {}
        k = key(method, args)
        if k in self.responses:
            return json.loads(json.dumps(self.responses[k]))
        if method == "Tree":
            derived = self.subtree(args.get("root", "/"))
            if derived is not None:
                self.derived.append(k[:160])
                return derived
        anchor = args.get("path") or args.get("root")
        if anchor and method + " " + anchor in self.loose and method in ("Read", "Stat", "List"):
            self.loose_hits.append(k[:160])
            return json.loads(json.dumps(self.loose[method + " " + anchor]))
        self.misses.append(k[:160])
        raise RuntimeError('BitGN HTTP 404: {"code": "not_found", "message": "not recorded in this world"}')

    def subtree(self, root):
        for k, response in self.responses.items():
            if not k.startswith("Tree "):
                continue
            args = json.loads(k[5:])
            base = args.get("root", "/").rstrip("/")
            if args.get("level") != 0 or not (root.rstrip("/") + "/").startswith(base + "/"):
                continue
            node = response.get("root")
            for part in [p for p in root[len(base):].split("/") if p]:
                node = next((c for c in node.get("children") or [] if c.get("name") == part), None)
                if node is None:
                    break
            if node is not None:
                return {"root": json.loads(json.dumps(node))}
        return None

    def answer(self, message, outcome="OUTCOME_NONE_UNSUPPORTED", refs=None):
        self.answers.append({"message": message, "outcome": outcome, "refs": refs or []})
        return {}

    def usage(self):
        return {}

    def help(self):
        return "replay-kit fake bitgn"

    # --- model --------------------------------------------------------------------
    def request_fidelity(self):
        if self.mode != "recorded":
            return None
        if self.llm_request_difference is not None or self.llm_calls != len(self.llm_replies):
            return False
        return True if self.llm_capture_complete else None

    def llm(self, model, messages, **parameters):
        self.llm_calls += 1
        n = self.llm_calls
        if self.mode == "recorded":
            if self.llm_request_difference is not None:
                raise Miss("model request mismatch already stopped recorded replay")
            if n > len(self.llm_replies):
                self.llm_request_difference = {"index": n - 1, "fields": ["call_count"]}
                raise Miss("agent asked for model reply %d; only %d recorded" % (n, len(self.llm_replies)))
            expected = self.llm_requests[n - 1]
            if expected is not None:
                try:
                    actual = sdk_request(model, messages, parameters)
                    fields = [key for key in sorted(set(expected) | set(actual))
                              if key not in expected or key not in actual or not same_json(expected[key], actual[key])]
                except ValueError as exc:
                    fields = [str(exc)]
                if fields:
                    self.llm_request_difference = {"index": n - 1, "fields": fields}
                    raise Miss("model request %d differs: %s" % (n, ", ".join(fields)))
                self.llm_requests_checked += 1
            return json.loads(json.dumps(self.llm_replies[n - 1]))
        if self.mode.startswith("script:"):
            if n > len(self.script):
                raise Miss("script has %d replies; agent asked for %d" % (len(self.script), n))
            return reply(self.script[n - 1])
        if self.mode == "router" and n == 1:
            return reply(json.dumps({"docs": self.routes}))
        raise Miss("model call %d with --llm %s" % (n, self.mode))


def reply(content):
    return {"choices": [{"message": {"content": content}, "finish_reason": "stop"}], "usage": {}}


def run(agent_path, world_path, llm="fail", routes=None, script=None):
    world = json.load(open(world_path, encoding="utf-8"))
    fake = FakeBitgn(world, llm, routes, script)
    out, error = io.StringIO(), None
    with contextlib.redirect_stdout(out):
        try:
            exec(compile(open(agent_path, encoding="utf-8").read(), agent_path, "exec"),
                 {"bitgn": fake, "__name__": "agent"})
        except Miss as exc:
            error = "stopped: " + str(exc)
        except Exception as exc:  # the agent crashed: in the sandbox this trial gets no answer
            error = "crash: %s: %s" % (type(exc).__name__, exc)
    final = fake.answers[-1] if fake.answers else None
    rec = fake.recorded_answer
    same = None
    if final is not None and rec is not None:
        same = (final["message"] == rec.get("message") and final["outcome"] == rec.get("outcome")
                and sorted(final["refs"]) == sorted(rec.get("refs") or []))
    return {"world": world_path, "task": fake.task_info.get("taskId"), "instruction": fake.task_info.get("instruction"),
            "answer": final, "recorded_answer": rec, "same_as_recorded": same, "recorded_grade": fake.grade,
            "writes": fake.writes, "deletes": fake.deletes, "llm_calls": fake.llm_calls,
            "rpc_misses": fake.misses, "loose_hits": fake.loose_hits, "derived_trees": fake.derived,
            "llm_requests_match": fake.request_fidelity(), "llm_requests_checked": fake.llm_requests_checked,
            "first_llm_difference": fake.llm_request_difference, "llm_recording_issue": fake.llm_recording_issue,
            "error": error, "stdout": out.getvalue()}


def main(argv):
    llm, routes, script, as_json, show = "fail", [], None, False, False
    paths = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--llm":
            llm = argv[i + 1]
            i += 2
        elif a == "--route":
            routes.append(argv[i + 1])
            i += 2
        elif a == "--json":
            as_json, i = True, i + 1
        elif a == "--show-output":
            show, i = True, i + 1
        else:
            paths.append(a)
            i += 1
    if llm.startswith("script:"):
        script = json.load(open(llm[7:], encoding="utf-8"))
    if len(paths) < 2:
        raise SystemExit(__doc__)
    results = [run(paths[0], w, llm, routes, script) for w in paths[1:]]
    if as_json:
        print(json.dumps(results, indent=1))
        return
    for r in results:
        print("==", r["world"], r["task"] or "")
        print("  instruction:", (r["instruction"] or "")[:150].replace("\n", " "))
        print("  llm calls: %d | rpc misses: %d %s | loose: %d | derived trees: %d | %s" % (
            r["llm_calls"], len(r["rpc_misses"]), r["rpc_misses"][:2], len(r["loose_hits"]),
            len(r["derived_trees"]), r["error"] or "ok"))
        for w in r["writes"]:
            print("  WRITE", w.get("path"), len(w.get("content") or ""), "bytes")
        for d in r["deletes"]:
            print("  DELETE", d.get("path"))
        print("  answer:  ", json.dumps(r["answer"])[:300])
        print("  recorded:", json.dumps(r["recorded_answer"])[:300], "| grade", (r["recorded_grade"] or {}).get("score"))
        print("  same as recorded:", r["same_as_recorded"])
        print("  model request fidelity:", r["llm_requests_match"], "|", r["first_llm_difference"] or r["llm_recording_issue"] or ("verified" if r["llm_requests_match"] is True else "not checked in this mode"))
        if show:
            print("  --- agent stdout ---\n" + r["stdout"][-3000:])


if __name__ == "__main__":
    main(sys.argv[1:])
