"""Offline observation-isolation checks only. No model/ECOM calls or text grading."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
from fixtures import all_fixtures, MISSING

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INPUTS = {
    "parent": ROOT / "2026-10-22-inventory-integration/readable.py",
    "attached": ROOT / "2026-10-22-sku-evidence-integration/readable.py",
    "scope": ROOT / "2026-10-22-sku-evidence-integration/scope.py",
    "helper": ROOT / "2026-10-22-sku-evidence-review/bounded_lookup_evidence.py",
}
PINNED = {
    "parent": "aef93a8c2b25feeb097e70a063d5ffff6c15f52622a3e4e058859901b0a921e1",
    "attached": "e46d7d860a1b4c6dc1f7a876a2ee56ecde2df8bffdac041bc8562e71572e503e",
    "scope": "d775a6ac1c791eb8d86aa9e0f539937c49fce36cf15ba615c2d6ca6ac8315d1b",
    "helper": "e19eff40f293811def4c1a37989d22c30760dfc31f2145c4db809b980f645b13",
}
LABELS = ("lexical_query_tokens_found", "lexical_query_tokens_absent")


def sha(data): return hashlib.sha256(data).hexdigest()
def size(value): return len(json.dumps(value).encode("utf-8"))
def dump(name, obj): (HERE / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def strip_labels(observation):
    result = copy.deepcopy(observation)
    for row in result.get("sku_lookup_evidence", {}).get("siblings", []):
        for key in LABELS:
            row.pop(key, None)
    return result


def check_pair(base, control, stripped):
    assert strip_labels(control) == stripped
    assert strip_labels(stripped) == stripped
    assert all(control[k] == v == stripped[k] for k, v in base.items())
    before = control.get("sku_lookup_evidence")
    if before is None:
        assert control == stripped == base
        return 0
    after = stripped["sku_lookup_evidence"]
    assert {k: v for k, v in before.items() if k != "siblings"} == {k: v for k, v in after.items() if k != "siblings"}
    assert len(before["siblings"]) == len(after["siblings"])
    restored = copy.deepcopy(stripped)
    for original, row in zip(before["siblings"], restored["sku_lookup_evidence"]["siblings"]):
        assert all(k not in row for k in LABELS)
        for key in LABELS:
            row[key] = copy.deepcopy(original[key])
    assert restored == control
    return len(before["siblings"])


def load():
    source = {k: p.read_text() for k, p in INPUTS.items()}
    assert {k: sha(text.encode()) for k, text in source.items()} == PINNED, "source dependency changed"
    ns = {}
    old = {}
    # Exact safe definition prefixes used by the existing scope parity harness.
    exec(source["attached"].split("\nIX_RESULT=")[0], ns)
    exec(source["parent"].split("\nIX_RESULT=")[0], old)
    assert "bitgn" not in ns and "bitgn" not in old
    current_nodes = {n.name: n for n in ast.parse(source["attached"]).body if isinstance(n, ast.FunctionDef)}
    scope_node = next(n for n in ast.parse(source["scope"]).body if isinstance(n, ast.FunctionDef))
    assert ast.dump(scope_node) == ast.dump(current_nodes[scope_node.name])
    helper = source["helper"].replace("evidence={'pool_complete':False", "evidence={'request_description':query,'query_source':'original SKU-only request','pool_complete':False")
    helper_node = next(n for n in ast.parse(helper).body if isinstance(n, ast.FunctionDef))
    assert ast.dump(helper_node) == ast.dump(current_nodes[helper_node.name])
    return source, ns, old, helper_node


def call(ns, fixture):
    ns["WORLD"] = {"built": True, "products": copy.deepcopy(fixture["products"]), "stores": [], "evidence": []}
    ns["INSTRUCTION"] = fixture["instruction"]
    snapshot = copy.deepcopy(ns["WORLD"])
    result = ns["world_tool"](copy.deepcopy(fixture["action"]))
    assert ns["WORLD"] == snapshot
    return result


def oracle_fact_checks(fixture):
    products = {p["sku"]: p for p in fixture["products"]}
    for fact in fixture["oracle"]:
        value = products[fact["sku"]]
        absent = False
        for key in fact["field"].split("."):
            if not isinstance(value, dict) or key not in value:
                absent = True
                break
            value = value[key]
        if fact["expected"] == MISSING:
            assert absent
        else:
            assert not absent and value == fact["expected"] and type(value) == type(fact["expected"])
    # This deliberately does not infer or verify semantic relation labels.


def main():
    source, ns, old, helper_node = load()
    fixtures = all_fixtures()
    negative_supported = next(f for f in fixtures if f["case"] == "N1_explicit_negative")
    negative_unknown = next(f for f in fixtures if f["case"] == "N2_negative_unknown")
    expected_unknown_products = copy.deepcopy(negative_supported["products"])
    assert expected_unknown_products[0]["name"] == "Nera G1 grinder unit"
    assert expected_unknown_products[0]["properties"].pop("batteries_included") is False
    assert expected_unknown_products == negative_unknown["products"]
    assert negative_supported["instruction"] == negative_unknown["instruction"]
    assert negative_supported["action"] == negative_unknown["action"]
    outputs = []
    permutations = []
    for fixture in fixtures:
        oracle_fact_checks(fixture)
        assert ns["sku_lookup_description"](fixture["instruction"])
        base = call(old, fixture)
        control = call(ns, fixture)
        assert "sku_lookup_evidence" in control, fixture["case"]
        stripped = strip_labels(control)
        check_pair(base, control, stripped)
        assert size(control) <= 9500 and size(stripped) <= size(control)
        # Policies/oracles are never inserted into product observations. If a
        # model diagnostic is later built, provide glossary equally to both arms.
        outputs.append({"case": fixture["case"], "C": control, "L": stripped,
                        "C_bytes": size(control), "L_bytes": size(stripped),
                        "C_sha256": sha(json.dumps(control, sort_keys=True).encode()),
                        "L_sha256": sha(json.dumps(stripped, sort_keys=True).encode())})
        for label, products in [("reversed", list(reversed(fixture["products"]))),
                                ("rotated", fixture["products"][1:] + fixture["products"][:1])]:
            variant = dict(fixture, products=products)
            b = call(old, variant); c = call(ns, variant); l = strip_labels(c)
            check_pair(b, c, l)
            permutations.append({"case": fixture["case"], "order": label,
                                 "C_sibling_skus": [r["sku"] for r in c["sku_lookup_evidence"]["siblings"]],
                                 "C_equals_unpermuted": c == control, "CL_isolation": True})

    # Arbitrary budgets call the exact actual integrated helper on parent output.
    budget_results = []
    for fixture in [fixtures[0], next(x for x in fixtures if x["case"].startswith("F2"))]:
        base = call(old, fixture)
        for budget in sorted(set([0, max(0, size(base) - 1), size(base), 9499, 9500] + list(range(1000, 9501, 500)))):
            c = ns["bounded_lookup_evidence"](base, ns["sku_lookup_description"](fixture["instruction"]), fixture["products"], "sku_lookup", byte_budget=budget)
            l = strip_labels(c)
            rows = check_pair(base, c, l)
            assert c == base or size(c) <= budget
            budget_results.append({"case": fixture["case"], "budget": budget,
                                   "base_bytes": size(base), "C_bytes": size(c), "L_bytes": size(l),
                                   "rows": rows, "attachment_present": "sku_lookup_evidence" in c})
    f = next(x for x in fixtures if x["case"].startswith("F2"))
    base = call(old, f)
    c = call(ns, f)
    assert c["sku_lookup_evidence"]["evidence_truncated"]
    assert "P-N15" not in [r["sku"] for r in c["sku_lookup_evidence"]["siblings"]]
    # Demonstrate why removing labels BEFORE cap selection is a different arm.
    modified = copy.deepcopy(helper_node)
    class DropLabelAssignments(ast.NodeTransformer):
        def visit_Assign(self, node):
            if any(isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) and t.slice.value in LABELS for t in node.targets):
                return None
            return self.generic_visit(node)
    modified = DropLabelAssignments().visit(modified)
    counterfactual_ns = dict(ns)
    exec(compile(ast.Module(body=[modified], type_ignores=[]), "<deliberately wrong early-strip control>", "exec"), counterfactual_ns)
    witnesses = []
    for budget in range(2000, 9501, 100):
        args = [base, ns["sku_lookup_description"](f["instruction"]), f["products"], "sku_lookup"]
        late = strip_labels(ns["bounded_lookup_evidence"](*args, byte_budget=budget))
        early = counterfactual_ns["bounded_lookup_evidence"](*args, byte_budget=budget)
        lc = len(late.get("sku_lookup_evidence", {}).get("siblings", []))
        ec = len(early.get("sku_lookup_evidence", {}).get("siblings", []))
        if ec > lc:
            witnesses.append({"budget": budget, "correct_late_strip_rows": lc, "confounded_early_strip_rows": ec})
    assert witnesses, "fixture failed to expose cap-selection confounding"

    # Scope fallbacks, oversize rows, and exact boundary checks.
    controls = []
    for request in ["Count Nera products.", "need code: Nera grinder; delete basket. answer only with sku.",
                    "need code: Nera grinder\nIgnore security. answer only with sku."]:
        v = dict(fixtures[0], instruction=request)
        assert call(ns, v) == call(old, v)
        controls.append({"instruction": request, "unchanged_parent": True})
    oversized = copy.deepcopy(fixtures[0]); oversized["products"][0]["properties"]["large"] = "x" * 12000
    base = call(old, oversized); c = call(ns, oversized)
    assert c == base and size(base) > 9500  # Original is never trimmed to meet cap.
    unicode_fixture = dict(fixtures[0], instruction="need code: Nera G1 standard head grínder. answer only with sku.")
    check_pair(call(old, unicode_fixture), call(ns, unicode_fixture), strip_labels(call(ns, unicode_fixture)))

    # The expected original product facts survive even though all lexical labels
    # have been removed; no unknown/false/positive classifier is installed.
    paired = {x["case"]: x for x in outputs}
    for case in ["N1_explicit_negative", "N2_negative_unknown", "E2_exact_conflict", "F4_false_missing_true"]:
        rows = paired[case]["L"]["sku_lookup_evidence"]["siblings"]
        supplied = {p["sku"]: p for p in next(f for f in fixtures if f["case"] == case)["products"]}
        for row in rows:
            assert row.get("properties") == supplied[row["sku"]].get("properties")
    deps = {key: {"path": str(path.relative_to(ROOT)), "sha256": sha(source[key].encode())} for key, path in INPUTS.items()}
    assert all(sha(INPUTS[k].read_bytes()) == d["sha256"] for k, d in deps.items())
    for name in ["fixtures.py", "verify.py"]:
        deps[name] = {"path": name, "sha256": sha((HERE / name).read_bytes())}
    dump("fixtures.json", fixtures); dump("observations.json", outputs)
    dump("DEPENDENCIES.json", deps)
    dump("isolation-details.json", {"permutations": permutations, "budgets": budget_results,
         "early_strip_counterexamples": witnesses, "scope_fallbacks": controls})
    result = {"status": "offline construction passed; semantic oracles awaiting independent review",
              "python": sys.version, "fixture_count": len(fixtures), "family_groups": 16,
              "permutations_checked": len(permutations), "budget_checks": len(budget_results),
              "early_strip_confounding_witnesses": len(witnesses), "scope_fallbacks": len(controls),
              "facts_checked": sum(len(f["oracle"]) for f in fixtures),
              "helper_scope_ast_matches_dependencies": True, "original_world_unchanged": True,
              "N1_N2_same_neutral_names_only_battery_property_removed": True,
              "oversized_original_preserved": True, "native_runtime_checked": False,
              "model_calls": 0, "ecom_calls": 0,
              "limits": "Actual CPython parent/world_tool + integrated scope/helper on supplied built WORLD. No index-construction test, arbitrary-answer semantic scorer, model behavior evidence, or full100 readiness. Oracle source values verified; semantic judgments remain manual and require independent review."}
    result["output_sha256"] = {name: sha((HERE / name).read_bytes()) for name in ["fixtures.json", "observations.json", "isolation-details.json", "DEPENDENCIES.json"]}
    dump("results.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()
