"""Build only from reviewed frozen input copies; never dispatch or infer."""
import copy
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LABELS = {"lexical_query_tokens_found", "lexical_query_tokens_absent"}
SOURCE_PINS = {
    "2026-10-22-sku-history-pressure-review/agent.py": "832be81a5fafec378320d42f3e5697cea00197dfe9bfbb061b2073880a203765",
    "2026-10-22-sku-history-pressure-review/readable.py": "0f7925c41f2783b6617ec7777757bec6fee5971f483159e26b32fae8082f7c41",
    "2026-10-22-huffman-packing-review/pack.py": "4b54f5e0163499a458e29b82817301cda58cdc76b49b622794936ef8b9d6e10f",
    "2026-10-22-inventory-integration/lzpack_dp.py": "ffdf9d25052904b5e64cd1b777f73f2751dea38e40b4a0febe4a7f6ce492ddd5",
    "2026-10-22-inventory-review/lzpack_longest.py": "ed2911781d8eaf932d4f22df95948199640e45e20240e9a5521fd8f27cbedeca",
    "2026-10-22-sku-paired-diagnostic/runner.py": "33e04315140afd2cbe33151f2782b7d40e23a7ba4f6e93d4de8ec6c221463408",
}


def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
def save(name, obj): (HERE / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def observation(request, index):
    header, body = request["messages"][index]["content"].split("\n", 1)
    return header, json.loads(body)


def main():
    dependency = json.loads((HERE / "DEPENDENCIES.json").read_text())
    assert dependency["status"] == "reviewed inputs frozen; unsubmitted"
    for relative, expected in dependency["frozen_files"].items():
        assert sha((HERE / relative).read_bytes()) == expected, ("frozen input changed", relative)
    for relative, expected in SOURCE_PINS.items():
        assert sha((ROOT / relative).read_bytes()) == expected, ("source dependency changed", relative)
    # The original runner is pinned for provenance; local bounded logging fixes
    # community d6210's demonstrated 65,536-byte stdout overflow.
    semantic = json.loads((HERE / "inputs/semantic-fixtures.json").read_text())
    assert len(semantic) == 17 and len({row["case"] for row in semantic}) == 17
    capture = json.loads((HERE / "inputs/runtime-results.json").read_text())
    captures = {row["case"]: row for row in capture["rows"]}
    assert set(captures) == {row["case"] for row in semantic}
    fixtures = []
    sizes = []
    for fixture in semantic:
        name = fixture["case"]
        item = json.loads((HERE / "inputs/requests" / (name + ".json")).read_text())
        assert item["case"] == name
        C, L = item["C"], item["L"]
        args, kwargs = item["captured_sdk_call"]
        assert len(args) == 2 and C == dict(model=args[0], messages=args[1], **kwargs)
        settings = {k: v for k, v in C.items() if k != "messages"}
        assert settings == dict(model="openai/gpt-oss-120b", max_completion_tokens=2048, reasoning={"effort": "medium"}, temperature=0)
        assert {k: v for k, v in L.items() if k != "messages"} == settings
        index = item["changed_message_index"]
        c_header, c_obs = observation(C, index)
        l_header, l_obs = observation(L, index)
        assert c_header == l_header and json.loads(c_header) == fixture["action"]
        stripped = copy.deepcopy(c_obs)
        removed = []
        for ri, row in enumerate(stripped["sku_lookup_evidence"]["siblings"]):
            for field in ("lexical_query_tokens_found", "lexical_query_tokens_absent"):
                assert field in row
                removed.append(dict(message=index, row=ri, field=field, value=row.pop(field)))
        assert stripped == l_obs and removed == item["removed_field_ledger"]
        restored = copy.deepcopy(L)
        for entry in removed:
            l_obs["sku_lookup_evidence"]["siblings"][entry["row"]][entry["field"]] = entry["value"]
        # Reinstate the exact original message text after proving object-level identity.
        assert l_obs == c_obs
        restored["messages"][index]["content"] = C["messages"][index]["content"]
        assert restored == C
        evidence = c_obs["sku_lookup_evidence"]
        assert evidence["pool_complete"] is False
        if name == "U4_supplied_synonym":
            glossary = fixture["future_request_requirements"]["shared_context"]
            for req in (C, L):
                messages = [m["content"] for m in req["messages"] if glossary in m["content"]]
                assert len(messages) == 1 and messages[0].startswith('{"tool": "read", "path": "/docs/catalogue-lookup.md"}\n')
            assert item["shared_glossary_visible_in_both"] is True
        if name == "F2_truncated_relevant_family":
            assert c_obs["indexed_products"] == 32
            assert evidence["eligible_indexed_siblings"] == 16 and evidence["returned_siblings"] == 10
            assert evidence["evidence_truncated"] is True
            assert all(row["sku"] not in ("P-N15", "P-O15") for row in evidence["siblings"])
            assert {row["brand"] for row in c_obs["matches"]} == {"Nera"}
        request_hashes = {}
        for arm, request in (("C", C), ("L", L)):
            data = canonical(request)
            # Check compact representation AND ordinary SDK-side JSON serialization.
            assert len(data) < 65536 and len(json.dumps(request).encode()) < 65536
            assert sha(data) == captures[name][arm + "_sha256"]
            request_hashes[arm] = sha(data)
            sizes.append(dict(case=name, arm=arm, compact_bytes=len(data), default_json_bytes=len(json.dumps(request).encode())))
        fixtures.append(dict(case=name, arms=dict(C=C, L=L), request_sha256=request_hashes))
    # Fixed matrix order; alternate C/L within each repeat, reverse each case on repeat 2.
    plan = []
    for repeat in range(2):
        for index, fixture in enumerate(fixtures):
            for arm in (("C", "L") if (repeat + index) % 2 == 0 else ("L", "C")):
                plan.append(dict(ordinal=len(plan) + 1, case_index=index, case=fixture["case"], repeat=repeat + 1, arm=arm, request_sha256=fixture["request_sha256"][arm]))
    assert len(plan) == 68
    bundle = dict(fixtures=fixtures, plan=plan)
    save("fixtures.json", bundle)
    save("call-plan.json", plan)
    runtime = (HERE / "runner.py").read_text()
    readable = "import json\nFROZEN=json.loads(" + repr(json.dumps(bundle)) + ")\n" + runtime
    readable = readable.encode("ascii", "backslashreplace").decode()
    packed = runpy.run_path(str(ROOT / "2026-10-22-huffman-packing-review/pack.py"))["pack"](readable)
    assert len(packed.encode()) <= 65536
    (HERE / "readable.py").write_text(readable)
    (HERE / "agent.py").write_text(packed)
    save("manual-review-sheet.json", [dict(step=step, response_ref=None, action_class=None, false_OK=None, unsupported_positive_assertion=None, qualifier_loss=None, contradicted_option=None, positive_control_preserved=None, targeted_deferred_lookup=None, malformed=None, provider_error=None, cancelled=None, cited_evidence=None, rationale=None, reviewer=None) for step in plan])
    manifest = dict(status="prepared locally; NOT SUBMITTED", purpose="68-call C-versus-L next-action diagnostic; not a task-solving source, benchmark run, score or promotion candidate", production_source="d5785r1 / readable d5789r1", production_source_hashes={p: h for p, h in SOURCE_PINS.items() if "history-pressure" in p}, diagnostic_packed_bytes=len(packed.encode()), diagnostic_packed_sha256=sha(packed.encode()), diagnostic_readable_bytes=len(readable.encode()), diagnostic_readable_sha256=sha(readable.encode()), fixtures_sha256=sha((HERE / "fixtures.json").read_bytes()), call_plan_sha256=sha((HERE / "call-plan.json").read_bytes()), dependency_sha256=sha((HERE / "DEPENDENCIES.json").read_bytes()), logical_model_calls=68, unique_cases=17, arms=["C", "L"], repeats=2, sdk="0.3.7", provider="deepinfra/bf16 pinned by SDK; private transport encoding not synthesized", settings=settings, native_limits=dict(max_feed_duration_secs=10, max_turn_duration_secs=10, max_suspensions=1000), size_accounting=sizes, paid_calls_during_preparation=0, no_custom_retry=True, stdout_limit_bytes=65536, stdout_protocol="bounded metadata only; raw responses/errors and usage harvested from immutable trace events", runner_sha256=sha((HERE / "runner.py").read_bytes()), cancellation="re-raise errors containing cancel; no subsequent call or carrier Answer", no_ecom_actions=True, carrier_grade="irrelevant; must not be reported as research score", limitations=["No main-agent action is executed from any model reply.", "Only immediate next actions are observed; deferred actions are not task successes.", "SDK may retry eligible provider responses; 68 logical calls is not a bound on transport attempts.", "Counterbalanced repeat order is fixed, not random; repeated requests are not independent tasks.", "L is shorter; label semantics and generic length/attention effects cannot be separated.", "Every attachment says pool_complete=false; no global catalogue coverage claim."])
    save("manifest.json", manifest)
    print(json.dumps({k: v for k, v in manifest.items() if k != "size_accounting"}, indent=2))


if __name__ == "__main__": main()
