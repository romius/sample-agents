# fastfail/preflight.py - hermetic pre-submit checks for ECOM1 agent.py (Monty-safe, no imports).
# Usage in any brain session:
#   g = {"brain": brain}; exec(brain.read("<doc id>"), g)
#   print(g["preflight"]("d4365", 1))     # static gate
#   print(g["e2e"]("d4365", 1))           # synthetic hermetic run
OK, FAIL, WARN = "PASS", "FAIL", "WARN"
OUTCOMES = ("OUTCOME_OK", "OUTCOME_DENIED_SECURITY", "OUTCOME_NONE_CLARIFICATION",
            "OUTCOME_NONE_UNSUPPORTED", "OUTCOME_ERR_INTERNAL")
BITGN_METHODS = ("task", "call", "answer", "llm", "usage", "help")

def _read_source(ref, revision=None):
    """Resolve a doc id, a w1:path, or a bare path; otherwise treat as source text.

    Two footguns this guards against, both found on 22 Oct by passing the file
    name of the installed baseline: a path used to be returned as if it were
    python source ("agent/agent.py" is 14 bytes, which parsed as a syntax error
    and produced a confident BLOCK), and the revision argument was accepted but
    never forwarded, so every check silently ran against the live revision.
    """
    if not isinstance(ref, str):
        return ref
    is_doc = len(ref) < 10 and ref[:1] == "d" and ref[1:].isdigit()
    is_path = "\n" not in ref and ("/" in ref or ref.endswith(".py"))
    if not (is_doc or is_path):
        return ref
    target = ref
    if is_path and not ref.startswith("w"):
        target = "w1:" + ref
    if revision is None:
        src = brain.read(target)
    else:
        src = brain.read(target, revision=revision)
    if len(src) < 200:
        raise ValueError("resolved " + str(target) + " to " + str(len(src)) +
                         " bytes, which is not a source file: pass a dID, a path, or the text")
    return src

def _syntax_line(msg):
    i = msg.find("line ")
    if i < 0:
        return "?"
    j = msg.find(")", i)
    return msg[i + 5:j if j > 0 else len(msg)]

def _scan_names(src, needle):
    out, i = [], 0
    while True:
        i = src.find(needle, i)
        if i < 0:
            break
        i += len(needle)
        j = i
        while j < len(src) and (src[j].isalnum() or src[j] == "_"):
            j += 1
        t = src[i:j]
        if t and t not in out:
            out.append(t)
        i = j
    return out

class _StopStub:  # every SDK entry point ends the parse check immediately
    def task(self, *a, **k):
        raise SystemExit("preflight-stop")
    call = task
    answer = task
    llm = task
    usage = task
    help = task

def preflight(ref, revision=None):
    src = _read_source(ref, revision)
    checks = []

    def add(st, name, detail=""):
        checks.append((st, name, detail))

    n = len(src)
    add(OK if n < 65536 else WARN, "size", str(n) + " bytes" + ("" if n < 65536 else " (>=64 KiB, check the limit)"))
    if "\x00" in src:
        add(FAIL, "encoding", "NUL byte in source")

    parsed = True
    ns = {"bitgn": _StopStub(), "__name__": "agent"}
    try:
        exec(src, ns)
        add(WARN, "parse", "module ran to completion without touching bitgn")
    except SystemExit:
        add(OK, "parse", "parses; top-level reached the first SDK call")
    except SyntaxError as e:
        parsed = False
        add(FAIL, "parse", "SyntaxError line " + str(_syntax_line(str(e))) + ": " + str(e)[:160])
    except Exception as e:
        parsed = False
        add(FAIL, "toplevel", type(e).__name__ + ": " + str(e)[:180])

    bad_imports = []
    for line in src.split("\n"):
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            mod = s.split()[1].split(".")[0]
            if mod not in bad_imports:
                try:
                    exec("import " + mod, {})
                except Exception:
                    bad_imports.append(mod)
    if bad_imports:
        add(FAIL, "imports", "unavailable in Monty: " + ", ".join(bad_imports))
    else:
        add(OK, "imports", "all module-level imports resolve")

    banned, warn = [], []
    for i, line in enumerate(src.split("\n"), 1):
        s = line.lstrip()
        for bad, why in (("class ", "class with a base is unsupported in Monty"),
                         ("compile(", "no compile() in Monty"),
                         ("__import__", "no __import__"),
                         ("open(", "no host filesystem"),
                         ("import subprocess", "no subprocess"),
                         ("import socket", "no sockets")):
            if bad == "class ":
                if s.startswith("class ") and "(" in s.split(":")[0]:
                    warn.append(str(i) + ":class(base)")
                continue
            if bad in s:
                banned.append(str(i) + ":" + bad.strip() + " (" + why + ")")
                break
    if banned:
        add(FAIL, "monty", "; ".join(banned[:4]))
    elif warn:
        add(WARN, "monty", "; ".join(warn[:4]))
    else:
        add(OK, "monty", "no banned constructs at module level")

    # Only column-0 defs shadow each other. Scanning every indent flagged
    # ordinary methods that happen to share a name across two handler classes:
    # four of the next five queued jobs lit up on 22 Oct for that reason alone.
    defs = {}
    for i, line in enumerate(src.split("\n"), 1):
        if line.startswith("def "):
            nm = line[4:line.find("(", 4)].strip() if "(" in line else ""
            if nm:
                defs.setdefault(nm, []).append(i)
    dups = []
    for k, v in defs.items():
        if len(v) > 1:
            marks = []
            for ln in v:
                marks.append("L" + str(ln))
            dups.append(k + " @" + ",".join(marks))
    if dups:
        add(WARN, "dup-defs", "; ".join(dups[:6]))
    else:
        add(OK, "dup-defs", str(len(defs)) + " top-level defs, no shadows")

    methods = _scan_names(src, "bitgn.")
    unknown = [m for m in methods if m not in BITGN_METHODS]
    if unknown:
        add(FAIL, "sdk-api", "unknown bitgn." + unknown[0] + " (known: " + ", ".join(BITGN_METHODS) + ")")
    elif "answer" not in methods:
        add(FAIL, "sdk-api", "no bitgn.answer call: the run can never answer")
    else:
        add(OK, "sdk-api", ",".join(sorted(m for m in methods if m)))

    found, i = [], 0
    while True:
        i = src.find("OUTCOME_", i)
        if i < 0:
            break
        j = i
        while j < len(src) and (src[j].isalnum() or src[j] == "_"):
            j += 1
        t = src[i:j]
        if t not in found:
            found.append(t)
        i = j
    bad = [t for t in found if t not in OUTCOMES]
    if bad:
        add(FAIL, "outcomes", "not an SDK outcome: " + ", ".join(bad[:4]))
    else:
        add(OK, "outcomes", ",".join(found) if found else "none literal (variables only)")

    fails = [c for c in checks if c[0] == FAIL]
    warns = [c for c in checks if c[0] == WARN]
    return {"verdict": "BLOCK" if fails else ("WARN" if warns else "GO"), "checks": checks, "src_bytes": n}

def e2e(ref, revision=None, max_calls=400, max_llm=60, script=None):
    src = _read_source(ref, revision)
    state = {"answered": None, "calls": 0, "llm": 0, "i": 0, "script": script or []}

    def _rpc(method, args=None):
        state["calls"] += 1
        if state["calls"] > max_calls:
            raise SystemExit("preflight-budget")
        a = args or {}
        if method == "Read":
            return {"path": a.get("path", ""), "content": "", "bytes": 0, "sha256": "0" * 64}
        if method in ("List", "Tree"):
            return {"entries": [], "nodes": [], "path": a.get("path", "/"), "level": 1}
        if method == "Find":
            return {"matches": [], "results": []}
        if method == "Search":
            return {"matches": [], "results": []}
        if method == "Exec":
            return {"stdout": "", "stderr": "", "exitCode": 0, "exit_code": 0}
        if method == "Write":
            return {"path": a.get("path", ""), "sha256": "0" * 64}
        if method == "Delete":
            return {"deleted": True, "ok": True}
        if method == "Stat":
            return {"path": a.get("path", ""), "exists": False, "bytes": 0}
        return {}

    def _llm(model, messages, **kw):
        state["llm"] += 1
        if state["llm"] > max_llm:
            raise SystemExit("preflight-budget")
        if model != "openai/gpt-oss-120b":
            raise ValueError("model must be openai/gpt-oss-120b, got " + str(model))
        sc = state["script"]
        k = state["i"]
        state["i"] = k + 1
        content = sc[k] if k < len(sc) else ("{\"tool\":\"read\",\"path\":\"/AGENTS.MD\"}" if k == 0 else "{\"tool\":\"report_completion\",\"message\":\"preflight done\",\"outcome\":\"OUTCOME_OK\"}")
        return {"choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": content}}],
                "model": model, "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}

    class SDK:
        def task(self):
            return {"trialId": "preflight-trial", "taskId": "t000", "runId": "preflight",
                    "instruction": "Preflight synthetic task: inspect the workspace and answer.",
                    "harnessUrl": "about:blank"}
        def call(self, method, args=None, _f=_rpc):
            return _f(method, args)
        def llm(self, model, messages, **kw):
            return _llm(model, messages, **kw)
        def answer(self, message, outcome="OUTCOME_NONE_UNSUPPORTED", refs=None, _s=state):
            _s["answered"] = {"message": message, "outcome": outcome, "refs": refs}
            raise SystemExit("preflight-answered")
        def usage(self, _s=state):
            return {"model_calls": _s["llm"], "ecom_calls": _s["calls"]}

    ns = {"bitgn": SDK(), "__name__": "agent"}
    try:
        exec(src, ns)
    except SystemExit as e:
        if str(e) != "preflight-answered":
            return {"verdict": "FAIL", "why": "run aborted: " + str(e), "calls": state["calls"], "llm": state["llm"]}
    except Exception as e:
        return {"verdict": "FAIL", "why": type(e).__name__ + ": " + str(e)[:200],
                "calls": state["calls"], "llm": state["llm"], "answered": state["answered"]}
    a = state["answered"]
    if not a:
        return {"verdict": "FAIL", "why": "no answer within " + str(state["calls"]) + " rpc calls", "llm": state["llm"]}
    if a["outcome"] not in OUTCOMES:
        return {"verdict": "FAIL", "why": "bad outcome " + str(a["outcome"])}
    if a["refs"] is not None and not isinstance(a["refs"], list):
        return {"verdict": "FAIL", "why": "refs is not a list"}
    return {"verdict": "PASS", "outcome": a["outcome"], "calls": state["calls"], "llm": state["llm"],
            "refs": len(a["refs"] or []), "message": str(a["message"])[:70]}
