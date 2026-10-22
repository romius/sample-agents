import json

def sdk_call(method, args):
    return bitgn.call(method, args)

def invoke(callback):
    return callback("Exec", {"path": "/bin/id"})

observed = {"purpose": "SDK callback boundary probe; carrier task not attempted"}
try:
    captured = bitgn.call
    observed["method_value_access"] = "allowed"
except Exception as error:
    observed["method_value_access"] = "raised"
    observed["method_value_error"] = str(error)[:160]

direct = bitgn.call("Exec", {"path": "/bin/id"})
wrapped = invoke(sdk_call)
assert isinstance(direct, dict) and isinstance(wrapped, dict)
assert isinstance(direct.get("stdout"), str) and direct["stdout"]
assert wrapped.get("stdout") == direct["stdout"]
observed["direct_call"] = "returned identity stdout"
observed["named_callback"] = "returned identical identity stdout"
print("SDK_CALLBACK_PROBE " + json.dumps(observed))
bitgn.answer("SDK callback probe completed; carrier task not attempted. See trace; grade is not benchmark evidence.", outcome="OUTCOME_NONE_UNSUPPORTED", refs=[])
