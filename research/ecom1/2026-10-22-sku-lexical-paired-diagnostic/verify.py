"""Fake-host parity, exact ordering, raw-output, error and cancellation tests.

Only llm/usage/answer hooks are exposed. No model or ECOM call is performed.
"""
import ast
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import time

import pydantic_monty as monty

HERE = Path(__file__).resolve().parent
LIMITS = dict(max_feed_duration_secs=10, max_turn_duration_secs=10, max_suspensions=1000)
PROXY = '''class Proxy:
 def llm(self,*a,**k):return host_llm(*a,**k)
 def usage(self):return host_usage()
 def answer(self,*a,**k):return host_answer(*a,**k)
bitgn=Proxy()
'''


def canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
def sha(data): return hashlib.sha256(data).hexdigest()


class Host:
    def __init__(self, bundle, expected_plan, scenario):
        self.bundle, self.expected_plan, self.scenario = bundle, expected_plan, scenario
        self.calls, self.answers, self.replies = [], [], []
        self.expected_results = []
        self.usage_calls = 0
    def llm(self, model, messages, **kwargs):
        request = dict(model=model, messages=copy.deepcopy(messages), **kwargs)
        index = len(self.calls)
        assert index < 68, "extra logical call"
        step = self.expected_plan[index]
        expected = self.bundle["fixtures"][step["case_index"]]["arms"][step["arm"]]
        assert request == expected and sha(canonical(request)) == step["request_sha256"]
        self.calls.append(request)
        error_message = None
        if self.scenario == "provider_error_3" and index == 2 or self.scenario == "all_provider_errors":
            error_message = "SIMULATED_PROVIDER_TIMEOUT"
        if self.scenario == "oversized_unicode_errors":
            error_message = "😀" * 20000 + '\nUNTRUSTED_ERROR_TAIL_"' * 1000
        cancel = {"cancel_first": 0, "cancel_middle": 33, "cancel_last": 67}.get(self.scenario)
        if cancel == index:
            error_message = "SIMULATED_CANCELLED_BY_USER"
        if self.scenario == "late_cancel_in_oversized_error" and index == 0:
            error_message = "😀" * 20000 + "SIMULATED_CANCELLED_BY_USER"
        if error_message is not None:
            cancelled = "cancel" in error_message.lower()
            self.expected_results.append(dict(step=step, status="cancelled" if cancelled else "error", response_id=None, finish_reason=None, error_preview=error_message[:32]))
            raise RuntimeError(error_message)
        if self.scenario == "raw_response_shapes":
            # Do not interpret, score, repair or execute any of these outputs.
            shapes = [None, {}, {"choices": []}, {"choices": [{"message": {"content": "{broken"}}]},
                      {"choices": [{"message": {"content": "{\"tool\":\"write\",\"path\":\"/proc/NEVER_EXECUTE\",\"content\":\"no\"}", "reasoning": "preserve raw reasoning"}, "finish_reason": "length"}], "usage": {"test_only": True}}]
            response = shapes[index % len(shapes)]
        elif self.scenario == "oversized_unicode_response_metadata":
            response = {"id": "😀" * 20000, "choices": [{"message": {"content": "FORBIDDEN_RAW_CONTENT" * 20000, "reasoning": "FORBIDDEN_RAW_REASONING" * 10000}, "finish_reason": "😀" * 20000}], "usage": {"FORBIDDEN_RAW_USAGE": ["cost_object" * 1000] * 100}}
        else:
            response = {"choices": [{"message": {"content": '{"tool":"read","path":"/proc/catalog/NEVER_EXECUTE.json"}', "reasoning": "SIMULATED_NOT_MODEL_OUTPUT"}, "finish_reason": "stop"}], "usage": {"test_only": True, "fixture_call": index + 1}}
        self.replies.append(copy.deepcopy(response))
        expected = dict(step=step, status="response", response_id=None, finish_reason=None)
        if isinstance(response, dict):
            if isinstance(response.get("id"), str): expected["response_id"] = response["id"][:32]
            choices = response.get("choices")
            if isinstance(choices, list) and choices and isinstance(choices[0], dict) and isinstance(choices[0].get("finish_reason"), str): expected["finish_reason"] = choices[0]["finish_reason"][:16]
        self.expected_results.append(expected)
        return response
    def usage(self):
        self.usage_calls += 1
        raise AssertionError("usage objects must never be fetched/dumped by this diagnostic")
    def answer(self, *args, **kwargs): self.answers.append([args, kwargs]); return {}


def execute(source, host, native, pool):
    stream, out = io.StringIO(), []
    error = None
    started = time.monotonic()
    try:
        if native:
            with pool.checkout(limits=LIMITS) as session:
                session.feed_run(PROXY + source, external_lookup={"host_llm": host.llm, "host_usage": host.usage, "host_answer": host.answer}, print_callback=lambda *a: out.append(str(a[1]) if len(a) > 1 else str(a[0])))
        else:
            with contextlib.redirect_stdout(stream): exec(source, dict(bitgn=host))
    except Exception as exc:
        error = str(exc)
    text = "".join(out) if native else stream.getvalue()
    return text, error, time.monotonic() - started


def main():
    bundle = json.loads((HERE / "fixtures.json").read_text())
    manifest = json.loads((HERE / "manifest.json").read_text())
    inputs = json.loads((HERE / "inputs/semantic-fixtures.json").read_text())
    assert [f["case"] for f in bundle["fixtures"]] == [f["case"] for f in inputs]
    assert len(inputs) == 17
    expected_plan = []
    for repetition in (1, 2):
        for index, fixture in enumerate(bundle["fixtures"]):
            order = ("C", "L") if (index + repetition) % 2 == 1 else ("L", "C")
            for arm in order:
                expected_plan.append(dict(ordinal=len(expected_plan) + 1, case_index=index, case=fixture["case"], repeat=repetition, arm=arm, request_sha256=sha(canonical(fixture["arms"][arm]))))
    assert bundle["plan"] == expected_plan == json.loads((HERE / "call-plan.json").read_text())
    assert len(expected_plan) == 68
    for fixture in bundle["fixtures"]:
        own = [p for p in expected_plan if p["case"] == fixture["case"]]
        assert len(own) == 4 and sum(p["arm"] == "C" for p in own) == 2
        assert [p["arm"] for p in own[:2]] == list(reversed([p["arm"] for p in own[2:]]))
    # Audit diagnostic runner capabilities. It contains no runtime call/task API.
    tree = ast.parse((HERE / "runner.py").read_text())
    attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "bitgn"}
    assert attributes == {"llm", "answer"}
    for form, prefix in (("agent.py", "diagnostic_packed"), ("readable.py", "diagnostic_readable")):
        data = (HERE / form).read_bytes()
        assert sha(data) == manifest[prefix + "_sha256"] and len(data) == manifest[prefix + "_bytes"]
    assert (HERE / "agent.py").stat().st_size <= 65536
    rows = []
    successes = {}
    scenarios = ["success", "provider_error_3", "all_provider_errors", "raw_response_shapes", "cancel_first", "cancel_middle", "cancel_last", "oversized_unicode_response_metadata", "oversized_unicode_errors", "late_cancel_in_oversized_error"]
    with monty.Monty() as pool:
        for form in ("readable.py", "agent.py"):
            for native in (False, True):
                for scenario in scenarios:
                    host = Host(bundle, expected_plan, scenario)
                    output, error, duration = execute((HERE / form).read_text(), host, native, pool)
                    requests = [json.loads(line.split(" ", 1)[1]) for line in output.splitlines() if line.startswith("SKU_DIAGNOSTIC_REQUEST ")]
                    results = [json.loads(line.split(" ", 1)[1]) for line in output.splitlines() if line.startswith("SKU_DIAGNOSTIC_RESULT ")]
                    begins = [line for line in output.splitlines() if line.startswith("SKU_DIAGNOSTIC_BEGIN ")]
                    ends = [line for line in output.splitlines() if line.startswith("SKU_DIAGNOSTIC_END ")]
                    assert len(begins) == 1
                    cancelled = scenario.startswith("cancel_") or scenario == "late_cancel_in_oversized_error"
                    expected_calls = {"cancel_first": 1, "cancel_middle": 34, "cancel_last": 68, "late_cancel_in_oversized_error": 1}.get(scenario, 68)
                    assert len(host.calls) == expected_calls and requests == [dict(ordinal=s["ordinal"]) for s in expected_plan[:expected_calls]], (form, native, scenario, error)
                    assert [r["step"] for r in results] == expected_plan[:expected_calls]
                    if cancelled:
                        assert error and "SIMULATED_CANCELLED_BY_USER" in error
                        assert not host.answers and not ends and host.usage_calls == 0
                    else:
                        assert error is None and len(host.answers) == 1 and len(ends) == 1 and host.usage_calls == 0, (scenario, error)
                        assert host.answers[0][1] == dict(outcome="OUTCOME_NONE_UNSUPPORTED", refs=[])
                        assert "carrier task was not attempted" in host.answers[0][0][0]
                    expected_errors = 68 if scenario in ("all_provider_errors", "oversized_unicode_errors") else int(scenario == "provider_error_3")
                    assert sum(r["status"] == "error" for r in results) == expected_errors
                    assert results == host.expected_results
                    assert all("response" not in r and "error" not in r for r in results)
                    assert all(marker not in output for marker in ("FORBIDDEN_RAW_CONTENT", "FORBIDDEN_RAW_REASONING", "FORBIDDEN_RAW_USAGE", "UNTRUSTED_ERROR_TAIL", "NEVER_EXECUTE", "SIMULATED_NOT_MODEL_OUTPUT"))
                    stdout_bytes = len(output.encode("utf-8"))
                    assert stdout_bytes < 65536, (form, native, scenario, stdout_bytes)
                    # Full logs agree across readable/packed and CPython/native; timings excluded.
                    identity = {"requests": requests, "results": results, "answers": json.loads(json.dumps(host.answers)), "begin": begins, "end": ends}
                    if scenario in successes: assert successes[scenario] == identity, (form, native, scenario, "parity")
                    else: successes[scenario] = identity
                    rows.append(dict(form=form, native=native, scenario=scenario, exact_ordered_logical_calls=len(host.calls), bounded_metadata_records=len(results), preserved_error_statuses=expected_errors, cancelled=cancelled, carrier_answers=len(host.answers), stdout_utf8_bytes=stdout_bytes, seconds=round(duration, 6)))
    report = dict(status="passed offline; NOT SUBMITTED", executions=rows, native_limits=LIMITS, stdout_limit_bytes=65536, max_observed_stdout_bytes=max(r["stdout_utf8_bytes"] for r in rows), total_executions=len(rows), all_68_calls_verified=True, exact_parameter_and_request_order=True, all_17_fixtures_retained=True, counterbalanced_two_repeats=True, readable_packed_native_parity=True, errors_preserved_without_custom_retry=True, raw_outputs_uninterpreted_and_not_logged=True, raw_response_source="immutable llm_response/error trace events; stdout contains metadata only", cancellation_stops_calls_and_carrier_answer=True, allowed_runtime_capabilities=sorted(attributes), usage_calls=0, real_model_calls=0, ecom_actions=0, cost_usd=0, caveats=["Fake cancellation exception validates runner rethrow only; real SDK/host cancellation enforcement is outside this test.", "Fake provider errors test local records; actual transport automatic retries are not simulated.", "No semantic outcome scorer is implemented or run."])
    (HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS: 40 runner executions; 68 exact ordered requests; readable/packed CPython/native parity; bounded stdout including oversized Unicode responses/errors; cancellation; no actions or usage dumps.")


if __name__ == "__main__": main()
