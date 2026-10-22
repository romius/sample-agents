"""Capture actual d5785 SDK next-action inputs offline; no model/network calls."""
import ast
import base64
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import pydantic_monty as monty

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CURRENT = ROOT / "2026-10-22-sku-history-pressure-review"
MATRIX = ROOT / "2026-10-22-sku-lexical-ablation-review"
ARCHIVE = ROOT / "2026-10-22-inventory-review"
DIAGNOSTIC = ROOT / "2026-10-22-sku-paired-diagnostic"
TREE_PROTO = ROOT.parent.parent / "proto/bitgn/vm/ecom/ecom.proto"
PINS = {"readable.py": "0f7925c41f2783b6617ec7777757bec6fee5971f483159e26b32fae8082f7c41",
        "agent.py": "832be81a5fafec378320d42f3e5697cea00197dfe9bfbb061b2073880a203765"}
FIXTURE_PIN = "c5d6199c9856f05aa6124e0d89348b7db522b735869f09f1fded97b60fe855c9"
LIMITS = {"max_feed_duration_secs": 10, "max_turn_duration_secs": 10, "max_suspensions": 1000}
LABELS = ("lexical_query_tokens_found", "lexical_query_tokens_absent")
PROXY = '''
class SDK:
 def task(self):return host_task()
 def call(self,method,args):return host_call(method,args)
 def llm(self,*args,**kwargs):return host_llm(*args,**kwargs)
 def answer(self,message,outcome=None,refs=None):return host_answer(message,outcome,refs)
 def usage(self):return {}
bitgn=SDK()
'''


def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
def normalize(obj): return json.loads(json.dumps(obj))
def save(path, obj): path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def tree_nodes(root, path="", depth=0):
    path = (path.rstrip("/") + "/" + root["name"].lstrip("/")).rstrip("/") or "/"
    return [(depth, path, root)] + [item for child in root.get("children", [])
                                  for item in tree_nodes(child, path, depth + 1)]


def tree_contract_evidence():
    contract = TREE_PROTO.read_text()
    assert "Zero means\n  // unlimited recursion." in contract
    archive = ARCHIVE / "record-t091-part0.json"
    events = json.loads(archive.read_text())
    responses = {seq: next(e["data"]["response"] for e in events if e["seq"] == seq) for seq in [12117, 12137]}
    root_nodes = tree_nodes(responses[12117]["root"])
    proc_nodes = tree_nodes(responses[12137]["root"])
    assert max(d for d, _, _ in root_nodes) == 2
    cut_dirs = [(p, n) for d, p, n in root_nodes if d == 2 and n["kind"] == "NODE_KIND_DIR"]
    assert cut_dirs and all("children" not in n for _, n in cut_dirs)
    assert max(d for d, _, _ in proc_nodes) == 4
    return {"contract_file": str(TREE_PROTO.relative_to(ROOT.parent.parent)), "contract_sha256": sha(TREE_PROTO.read_bytes()),
            "contract": "Maximum traversal level from root, matching tree -L. Zero means unlimited recursion.",
            "archived_response_file": str(archive.relative_to(ROOT)), "archived_response_sha256": sha(archive.read_bytes()),
            "root_response_event": 12117, "root_max_depth": 2, "cut_directory_paths": [p for p, _ in cut_dirs],
            "proc_response_event": 12137, "proc_max_depth": 4,
            "request_limitations": "Archive contains RPC responses only; source explicitly calls root / level2 and /proc level0. Contract establishes requested depth semantics; request arguments are not claimed archived.",
            "correction": "Initial capture Host ignored level, leaking synthetic SKU file names into root bootstrap. Regenerated all68 captures with depth cutoff; prior capture was not sent to a model."}


def verify_tree_host(fixture, w):
    host = Host(fixture, copy.deepcopy(w))
    checks = []
    for level in [1, 2, 3, 4, 0]:
        nodes = tree_nodes(host.call("Tree", {"root": "/", "level": level})["root"])
        if level:
            assert max(d for d, _, _ in nodes) <= level
            assert all("children" not in n for d, _, n in nodes if d == level)
        if level == 2:
            assert "/proc/catalog" in [p for _, p, _ in nodes]
            assert not any(p.startswith("/proc/catalog/") for _, p, _ in nodes)
        checks.append({"root": "/", "level": level, "max_depth": max(d for d, _, _ in nodes), "nodes": len(nodes)})
    nodes = tree_nodes(host.call("Tree", {"root": "/proc", "level": 0})["root"])
    assert {p["_path"] for p in fixture["products"]} <= {p for _, p, _ in nodes}
    checks.append({"root": "/proc", "level": 0, "max_depth": max(d for d, _, _ in nodes),
                   "nodes": len(nodes), "all_fixture_product_files_visible": True})
    return checks


def scaffolding():
    files = sorted(ARCHIVE.glob("record-t091-part*.json"))
    events = sorted(sum([json.loads(p.read_text()) for p in files], []), key=lambda e: e["seq"])
    reads = {e["data"]["response"]["path"]: copy.deepcopy(e["data"]["response"])
             for e in events if e["data"]["method"] == "Read" and
             (e["data"]["response"]["path"].startswith("/docs/") or e["data"]["response"]["path"] == "/AGENTS.MD")}
    execs = [e["data"]["response"] for e in events if e["data"]["method"] == "Exec"]
    clock = next(r for r in execs if r["stdout"].startswith("2026-"))
    identity = next(r for r in execs if r["stdout"].startswith("user:"))
    fixture_path = DIAGNOSTIC / "fixtures.json"
    first = json.loads(fixture_path.read_text())["fixtures"][0]
    policy = []
    policy_index = None
    for index, message in enumerate(first["arms"]["parent"]["messages"]):
        text = message.get("content", "")
        if "\n" not in text:
            continue
        header, body = text.split("\n", 1)
        try:
            action = json.loads(header)
        except ValueError:
            continue
        if action == {"tool": "read", "path": "/docs/catalogue-lookup.md"}:
            policy.append(body)
            policy_index = index
    assert len(policy) == 1
    reads["/docs/catalogue-lookup.md"] = {"path": "/docs/catalogue-lookup.md", "content": policy[0]}
    original_agents = copy.deepcopy(reads["/AGENTS.MD"])
    original_text = original_agents["content"]
    before = "Use the files under `/proc/products` as the source of truth for product catalogue."
    after = "Use the files under `/proc/catalog` as the source of truth for product catalogue."
    assert original_text.count(before) == 1
    adapted_text = original_text.replace(before, after, 1)
    assert adapted_text.replace(after, before, 1) == original_text
    reads["/AGENTS.MD"]["content"] = adapted_text
    # Do not retain an archived digest for a synthetically adapted file body.
    reads["/AGENTS.MD"]["sha256"] = sha(adapted_text.encode())
    provenance = {"archived_read_events": {e["data"]["response"]["path"]: e["seq"] for e in events
                  if e["data"]["method"] == "Read" and e["data"]["response"]["path"] in reads},
                  "clock_exec_event": next(e["seq"] for e in events if e["data"]["method"] == "Exec" and e["data"]["response"] == clock),
                  "identity_exec_event": next(e["seq"] for e in events if e["data"]["method"] == "Exec" and e["data"]["response"] == identity),
                  "catalogue_policy": {"file": str(fixture_path.relative_to(ROOT)), "fixture_case": first["case"],
                                       "original_archive_event": first["archive_event"], "arm": "parent", "message_index": policy_index,
                                       "content_sha256": sha(policy[0].encode())},
                  "agents_synthetic_adaptation": {"original_response": original_agents,
                      "before_content_sha256": sha(original_text.encode()), "after_content_sha256": sha(adapted_text.encode()),
                      "replace_once": {"before": before, "after": after},
                      "reason": "Match synthetic /proc/catalog product paths and shared catalogue lookup policy; all other policy clauses unchanged."},
                  "modifications": "Synthetic requests and product files replace archived inventory. One AGENTS catalogue-root reference adapted /proc/products to /proc/catalog. Listings/Tree reconstructed with contract depth semantics. U4 alone appends its exact shared glossary to the catalogue policy; no semantic oracle labels enter requests."}
    return reads, copy.deepcopy(clock), copy.deepcopy(identity), files + [fixture_path], provenance


def world(fixture, scaffold):
    reads, clock, identity, _, _ = scaffold
    reads = copy.deepcopy(reads)
    glossary = fixture.get("future_request_requirements", {}).get("shared_context")
    if glossary:
        reads["/docs/catalogue-lookup.md"]["content"] += "\n\n## Synthetic fixture glossary\n" + glossary + "\n"
    for product in fixture["products"]:
        record = {k: copy.deepcopy(v) for k, v in product.items() if k != "_path"}
        path = product["_path"]
        reads[path] = {"path": path, "content": json.dumps(record)}
    listings = {}
    for path in reads:
        parts = path.strip("/").split("/")
        for i, part in enumerate(parts):
            directory = "/" + "/".join(parts[:i]) if i else "/"
            child = "/" + "/".join(parts[:i + 1])
            node = {"name": part, "path": child, "kind": "NODE_KIND_FILE" if i == len(parts) - 1 else "NODE_KIND_DIR"}
            entries = listings.setdefault(directory, {"path": directory, "entries": []})["entries"]
            if node not in entries:
                entries.append(node)
    return {"instruction": fixture["instruction"], "reads": reads, "listings": listings,
            "clock": clock, "identity": identity, "shared_glossary": glossary}


class Host:
    """Read-only in-memory transport, adapted from inventory Host/ReplayHost.

    Tree is reconstructed from files in insertion order with root depth zero,
    positive level cutoff and level zero unlimited (ecom.proto contract).
    Responses are simulated, not captured live service responses.
    """
    def __init__(self, fixture, fixture_world):
        self.fixture = fixture
        self.world = fixture_world
        self.calls = []; self.models = []; self.answers = []; self.external_count = 0
        self.actions = [copy.deepcopy(fixture["action"]),
                        {"tool": "report_completion", "message": "OFFLINE_CAPTURE_STOP",
                         "outcome": "OUTCOME_NONE_CLARIFICATION", "grounding_refs": []}]

    def event(self): self.external_count += 1
    def task(self):
        self.event()
        return {"instruction": self.world["instruction"]}

    def call(self, method, args):
        self.event()
        self.calls.append([method, copy.deepcopy(args)])
        if method == "Tree":
            level = args.get("level", 0)
            assert isinstance(level, int) and level >= 0, "unsupported synthetic Tree depth"
            def node(path, depth=0):
                result = {"name": path.rstrip("/").split("/")[-1] or "/", "kind": "NODE_KIND_DIR"}
                if level == 0 or depth < level:
                    children = [node(e["path"], depth + 1) if e["kind"] == "NODE_KIND_DIR" else
                                {"name": e["name"], "kind": e["kind"]}
                                for e in self.world["listings"].get(path, {}).get("entries", [])]
                    if children:
                        result["children"] = children
                return result
            return {"root": node(args.get("root", "/"))}
        if method == "Read":
            if args["path"] not in self.world["reads"]:
                raise RuntimeError('BitGN HTTP 404: {"code":"not_found"}')
            return copy.deepcopy(self.world["reads"][args["path"]])
        if method == "List": return copy.deepcopy(self.world["listings"][args["path"]])
        if method == "Exec":
            assert args["path"] in ["/bin/id", "/bin/date"], "unexpected executable"
            return copy.deepcopy(self.world["identity" if args["path"] == "/bin/id" else "clock"])
        if method == "Stat":
            if args["path"] in self.world["reads"]:
                return {"path": args["path"], "kind": "NODE_KIND_FILE"}
            raise RuntimeError('BitGN HTTP 404: {"code":"not_found"}')
        raise AssertionError(("unexpected or mutating RPC", method, args))

    def llm(self, *args, **kwargs):
        self.event()
        self.models.append(normalize([args, kwargs]))
        router = "route a store request" in args[1][0]["content"]
        response = {"docs": ["/docs/catalogue-lookup.md"]} if router else self.actions.pop(0)
        return {"choices": [{"message": {"content": json.dumps(response)}, "finish_reason": "stop"}]}

    def answer(self, message, outcome=None, refs=None):
        self.event(); self.answers.append([message, outcome, refs]); return {}
    def usage(self): return {}


def execute(source, fixture, w, native, pool):
    host = Host(fixture, copy.deepcopy(w))
    started = time.monotonic()
    if native:
        with pool.checkout(limits=LIMITS) as session:
            session.feed_run(PROXY + source,
                external_lookup={"host_task": host.task, "host_call": host.call, "host_llm": host.llm, "host_answer": host.answer},
                print_callback=lambda *args: None)
    else:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(source, {"bitgn": host})
    elapsed = time.monotonic() - started
    assert elapsed < 10 and host.external_count < 1000
    assert not host.actions and len(host.answers) == 1
    assert host.answers[0][0] == "OFFLINE_CAPTURE_STOP", host.answers
    assert len(host.models) == 3, "expected router + catalog action + captured next action"
    product_paths = {p["_path"] for p in fixture["products"]}
    reads = {a["path"] for m, a in host.calls if m == "Read"}
    assert product_paths <= reads
    assert any(m == "Tree" and a.get("root") == "/proc" for m, a in host.calls)
    assert ["Tree", {"root": "/", "level": 2}] in host.calls
    assert ["Tree", {"root": "/proc", "level": 0}] in host.calls
    assert "/docs/catalogue-lookup.md" in reads
    result = normalize({"calls": host.calls, "answers": host.answers, "models": host.models,
                        "external_count": host.external_count})
    return result, elapsed


def make_pair(models, fixture):
    args, kwargs = copy.deepcopy(models[-1])
    assert len(args) == 2
    control = {"model": args[0], "messages": args[1], **kwargs}
    tree_header = json.dumps({"tool": "tree", "root": "/", "level": 2}) + "\n"
    bootstraps = [m["content"][len(tree_header):] for m in control["messages"]
                  if m.get("content", "").startswith(tree_header)]
    assert len(bootstraps) == 1
    bootstrap_nodes = tree_nodes(json.loads(bootstraps[0])["root"])
    assert max(d for d, _, _ in bootstrap_nodes) == 2
    assert not any(p.startswith("/proc/catalog/") for _, p, _ in bootstrap_nodes)
    assert all("children" not in n for d, _, n in bootstrap_nodes if d == 2)
    stripped = copy.deepcopy(control)
    changed = []
    ledger = []
    for i, message in enumerate(stripped["messages"]):
        text = message.get("content", "")
        if "\n" not in text:
            continue
        header, body = text.split("\n", 1)
        try:
            action = json.loads(header); observation = json.loads(body)
        except ValueError:
            continue
        if not isinstance(action, dict) or action.get("tool") != "catalog" or not isinstance(observation, dict):
            continue
        evidence = observation.get("sku_lookup_evidence")
        if evidence is None:
            continue
        original = copy.deepcopy(observation)
        assert evidence["request_description"] in fixture["instruction"]
        for row_index, row in enumerate(evidence["siblings"]):
            for key in LABELS:
                ledger.append({"message": i, "row": row_index, "field": key, "value": row.pop(key)})
        message["content"] = header + "\n" + json.dumps(observation)
        changed.append(i)
        assert {k: v for k, v in observation.items() if k != "sku_lookup_evidence"} == {k: v for k, v in original.items() if k != "sku_lookup_evidence"}
    assert len(changed) == 1 and ledger
    restored = copy.deepcopy(stripped)
    i = changed[0]
    header, body = restored["messages"][i]["content"].split("\n", 1)
    observation = json.loads(body)
    for change in ledger:
        observation["sku_lookup_evidence"]["siblings"][change["row"]][change["field"]] = change["value"]
    restored["messages"][i]["content"] = header + "\n" + json.dumps(observation)
    assert restored == control
    assert all(control["messages"][j] == stripped["messages"][j] for j in range(len(control["messages"])) if j != i)
    glossary = fixture.get("future_request_requirements", {}).get("shared_context")
    if glossary:
        for arm in [control, stripped]:
            hits = [m["content"] for m in arm["messages"] if glossary in m.get("content", "")]
            assert len(hits) == 1 and hits[0].startswith('{"tool": "read", "path": "/docs/catalogue-lookup.md"}\n')
    assert len(json.dumps(control, separators=(",", ":")).encode()) <= 65536
    return {"C": control, "L": stripped, "changed_message_index": i,
            "removed_field_ledger": ledger, "shared_glossary_visible_in_both": bool(glossary)}


def main():
    fixture_file = MATRIX / "fixtures.json"
    assert sha(fixture_file.read_bytes()) == FIXTURE_PIN
    fixtures = json.loads(fixture_file.read_text())
    assert len(fixtures) == 17
    sources = {name: (CURRENT / name).read_text() for name in PINS}
    assert {name: sha(s.encode()) for name, s in sources.items()} == PINS
    current = {n.name: n for n in ast.parse(sources["readable.py"]).body if isinstance(n, ast.FunctionDef)}
    old = {n.name: n for n in ast.parse((ROOT / "2026-10-22-sku-evidence-integration/readable.py").read_text()).body if isinstance(n, ast.FunctionDef)}
    for name in ["world_tool", "sku_lookup_description", "bounded_lookup_evidence", "build_world"]:
        assert ast.dump(current[name]) == ast.dump(old[name])
    scaffold = scaffolding()
    tree_evidence = tree_contract_evidence()
    tree_evidence["fixture_checks"] = {}
    rows = []; all_traces = {}; worlds = {}
    (HERE / "requests").mkdir(exist_ok=True)
    with monty.Monty() as pool:
        for fixture in fixtures:
            w = world(fixture, scaffold); worlds[fixture["case"]] = w
            tree_evidence["fixture_checks"][fixture["case"]] = verify_tree_host(fixture, w)
            captures = []; durations = []
            for name, source in sources.items():
                for native in [False, True]:
                    capture, elapsed = execute(source, fixture, w, native, pool)
                    captures.append(capture)
                    durations.append({"source": name, "runtime": "Monty" if native else "CPython", "seconds": round(elapsed, 6)})
            assert all(item == captures[0] for item in captures), fixture["case"]
            pair = make_pair(captures[0]["models"], fixture)
            # Preserve exact source-level SDK calls alongside normalized requests;
            # normalization does not pretend to reproduce private HTTP transport.
            pair["captured_sdk_call"] = captures[0]["models"][-1]
            pair["case"] = fixture["case"]
            pair["provenance"] = "Synthetic catalogue/request, archived identity/clock/policies with one AGENTS catalogue-root reference adapted; depth-limited synthetic Tree; scripted router and first action; actual source-created post-catalogue request."
            catalog_observation = json.loads(pair["C"]["messages"][pair["changed_message_index"]]["content"].split("\n", 1)[1])
            evidence = catalog_observation["sku_lookup_evidence"]
            if fixture["case"] == "F2_truncated_relevant_family":
                assert "P-N15" not in [r["sku"] for r in evidence["siblings"]]
                assert evidence["evidence_truncated"]
            filename = "requests/" + fixture["case"] + ".json"
            save(HERE / filename, pair)
            all_traces[fixture["case"]] = captures[0]
            row = {"case": fixture["case"], "request_file": filename,
                   "C_sha256": sha(canonical(pair["C"])), "L_sha256": sha(canonical(pair["L"])),
                   "C_compact_bytes": len(json.dumps(pair["C"], separators=(",", ":")).encode()),
                   "L_compact_bytes": len(json.dumps(pair["L"], separators=(",", ":")).encode()),
                   "message_count": len(pair["C"]["messages"]), "changed_message_index": pair["changed_message_index"],
                   "removed_lexical_fields": len(pair["removed_field_ledger"]),
                   "catalogue_records_read": len(fixture["products"]), "rpc_count": len(captures[0]["calls"]),
                   "external_hook_count": captures[0]["external_count"], "form_runtime_parity": True,
                   "shared_glossary_actually_read_and_visible": pair["shared_glossary_visible_in_both"], "durations": durations}
            row["catalogue_evidence"] = {"indexed_products": catalog_observation["indexed_products"],
                "eligible_indexed_siblings": evidence["eligible_indexed_siblings"], "returned_siblings": evidence["returned_siblings"],
                "evidence_truncated": evidence["evidence_truncated"], "pool_complete": evidence["pool_complete"]}
            rows.append(row); print(f"PASS {fixture['case']}:4 executions,{row['rpc_count']} RPCs,{row['C_compact_bytes']}->{row['L_compact_bytes']} bytes")
    save(HERE / "worlds.json", worlds); save(HERE / "host-traces.json", all_traces)
    save(HERE / "scaffolding-provenance.json", scaffold[4])
    save(HERE / "tree-depth-evidence.json", tree_evidence)
    dependencies = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in scaffold[3] + [fixture_file, CURRENT / "readable.py", CURRENT / "agent.py",
        ROOT / "2026-10-22-sku-evidence-integration/readable.py", HERE / "capture.py"]}
    assert sha(fixture_file.read_bytes()) == FIXTURE_PIN
    assert {name: sha((CURRENT / name).read_bytes()) for name in PINS} == PINS
    dependencies["../../" + str(TREE_PROTO.relative_to(ROOT.parent.parent))] = sha(TREE_PROTO.read_bytes())
    save(HERE / "DEPENDENCIES.json", dependencies)
    result = {"status": "offline request capture and C/L isolation passed; not a model diagnostic",
              "source": {"packed": "d5785r1", "readable": "d5789r1", "hashes": PINS,
                         "lineage": "d3200r2 record -> own pending d4955/d5204 -> scoped SKU evidence d5620 -> forced-report history repair d5785"},
              "python": sys.version, "native_limits": LIMITS, "fixtures": len(rows), "agent_executions": 4 * len(rows),
              "real_model_calls": 0, "network_calls": 0, "paid_cost_usd": 0,
              "scripted_llm_invocations": 12 * len(rows), "rows": rows,
              "size_accounting": {"unit": "UTF-8 compact JSON bytes, not tokens", "sum_C_bytes": sum(r["C_compact_bytes"] for r in rows),
                                  "sum_L_bytes": sum(r["L_compact_bytes"] for r in rows),
                                  "future_inference_cost_estimate": None, "reason": "No tokenization, provider billing quote, or real inference; bytes are not converted into tokens or dollars."},
              "limitations": "Real source/decoder runs against a scripted in-memory Host, not live ECOM. Depth-aware Tree/List/Read inventory reconstructed from synthetic files; AGENTS product root minimally adapted. WORLD never injected. Router and first action forced, final output stubbed. SDK inputs captured before any private transport/provider processing. No future model actions, grading, efficacy or full100 readiness claim."}
    result["artifact_sha256"] = {str(p.relative_to(HERE)): sha(p.read_bytes()) for p in sorted((HERE / "requests").glob("*.json"))}
    result["artifact_sha256"].update({name: sha((HERE / name).read_bytes()) for name in ["worlds.json", "host-traces.json", "scaffolding-provenance.json", "tree-depth-evidence.json", "DEPENDENCIES.json"]})
    save(HERE / "results.json", result)
    print("PASS all17 fixtures,68 complete agent executions; no model/network calls")


if __name__ == "__main__": main()
