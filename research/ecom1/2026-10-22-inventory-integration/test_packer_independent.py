"""Independent deterministic packer/removal audit. Does not rebuild candidates.

Run: UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project
 --offline --with python-minifier==3.4.0 --with pydantic-monty==1.2.0
 python test_packer_independent.py
"""
import ast
import base64
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import random
import runpy
import sys

HERE = Path(__file__).resolve().parent
CODEC = runpy.run_path(str(HERE / "lzpack_dp.py"))
RNG = random.Random(10222026)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def oracle_size(data):
    """Enumerate every valid literal and nonoverlapping prior substring.

    This deliberately has no hash table, longest-match finder or bounded window.
    """
    @lru_cache(None)
    def best(i):
        if i == len(data):
            return 0
        options = [1 + size + best(i + size) for size in range(1, min(128, len(data) - i) + 1)]
        for old in range(max(0, i - 65535), i - 3):
            for size in range(4, min(131, len(data) - i, i - old) + 1):
                if data[old:old + size] == data[i:i + size]:
                    options.append(3 + best(i + size))
                else:
                    break
        return min(options)
    return best(0)


def independent_decode(tokens):
    """Strict token parser, separate implementation from production decoder."""
    output = bytearray()
    cursor = 0
    references = []
    while cursor < len(tokens):
        tag = tokens[cursor]
        cursor += 1
        if tag & 128:
            assert cursor + 2 <= len(tokens), "truncated offset"
            distance = int.from_bytes(tokens[cursor:cursor + 2], "big")
            cursor += 2
            size = (tag & 127) + 4
            assert 4 <= size <= 131 and size <= distance <= min(65535, len(output))
            start = len(output) - distance
            # Freeze the copied source: overlapping references cannot pass.
            literal = bytes(output[start:start + size])
            assert len(literal) == size
            references.append([len(output), distance, size])
            output += literal
        else:
            size = tag + 1
            assert cursor + size <= len(tokens), "truncated literal"
            output += tokens[cursor:cursor + size]
            cursor += size
    return bytes(output), references


def runtime_decoder():
    tree = ast.parse(CODEC["STUB"] % "")
    tree.body = tree.body[:-1]  # Do not execute a payload; inspect exact decoder.
    env = {}
    exec(compile(tree, "<exact runtime decoder>", "exec"), env)
    return env["_lz"]


def packer_checks():
    runtime = runtime_decoder()
    exhaustive = 0
    for size in range(13):
        for seq in itertools.product(range(2), repeat=size):
            data = bytes(seq)
            encoded = CODEC["encode"](data)
            assert len(encoded) == oracle_size(data), [data.hex(), len(encoded)]
            assert independent_decode(encoded)[0] == data
            exhaustive += 1
    small = 0
    for _ in range(350):
        data = bytes(RNG.randrange(RNG.choice([2, 3, 5, 16, 256])) for _ in range(RNG.randrange(1, 65)))
        encoded = CODEC["encode"](data)
        assert len(encoded) == oracle_size(data)
        small += 1

    vectors = [b"", bytes(range(256)), b"\x00" * 4096, b"abcd" * 1000, b"abaabb" * 700]
    for size in [1, 3, 4, 7, 8, 127, 128, 129, 130, 131, 132, 255, 256, 257, 4096, 65535, 65536]:
        vectors.extend([RNG.randbytes(size), (b"abcdefgh" * (size // 8 + 1))[:size]])
    # A unique old reference sits exactly on the uint16 boundary, then just beyond.
    prefix = RNG.randbytes(65535)
    vectors.extend([prefix + prefix[:131], prefix + b"z" + prefix[:131]])
    vectors.extend(RNG.randbytes(RNG.randrange(1, 2049)) for _ in range(120))
    reference_count = 0
    exact_boundary = False
    for data in vectors:
        encoded = CODEC["encode"](data)
        result, refs = independent_decode(encoded)
        assert result == data == CODEC["decode"](encoded)
        assert runtime(base64.b85encode(encoded).decode()).encode("latin1") == data
        assert encoded == CODEC["encode"](data), "nondeterministic output"
        reference_count += len(refs)
        exact_boundary |= any(distance == 65535 for _, distance, _ in refs)
    assert exact_boundary
    # Generated agent is checked without executing the agent.
    packed = (HERE / "agent.py").read_bytes()
    prepack = (HERE / "prepack.py").read_bytes()
    payload = ast.parse(packed).body[-1].value.args[0].args[0].value
    encoded = base64.b85decode(payload)
    assert independent_decode(encoded)[0] == prepack == CODEC["decode"](encoded)
    assert runtime(payload).encode("ascii") == prepack
    return {"exhaustive_binary_strings_0_to_12": exhaustive, "random_small_oracle_cases": small,
            "roundtrip_vectors": len(vectors), "validated_nonoverlapping_references": reference_count,
            "exact_65535_offset_observed": exact_boundary,
            "agent_sha256": digest(packed), "prepack_sha256": digest(prepack),
            "artifact_decodes_exactly": True,
            "optimality_limit": "Minimum encoded token BYTES for all matches in small exhaustive cases. Production search is candidate-bounded; no global optimality claim for large inputs."}


def definition_checks():
    build_tree = ast.parse((HERE / "build.py").read_text())
    inert = next(n for n in build_tree.body if isinstance(n, ast.FunctionDef) and n.name == "inert_definition")
    build = next(n for n in build_tree.body if isinstance(n, ast.FunctionDef) and n.name == "build")
    loop = next(n for n in build.body if isinstance(n, ast.For) and isinstance(n.target, ast.Name) and n.target.id == "name")
    checker = {}
    exec(compile(ast.Module(body=[inert], type_ignores=[]), "<exact inert_definition>", "exec"), checker)
    exact_loop_body = compile(ast.Module(body=loop.body, type_ignores=[]), "<exact overwrite checker>", "exec")

    def accepted_and_removed(source, name):
        nodes = ast.parse(source).body
        env = dict(checker, ast=ast, nodes=nodes, name=name, removed=[])
        exec(exact_loop_body, env)
        removed = env["removed"]
        return ast.Module(body=[n for n in nodes if n not in removed], type_ignores=[])

    donor = (HERE.parent / "2026-10-22-inventory-review/upstream/d4012r1").read_text()
    engine = donor[donor.index("IX_POLICIES="):donor.index("IX_RESULT=")]
    original = ast.parse(engine)
    removed = ast.parse(engine)
    evidence = []
    for name in ["ix_request", "ix_policy_key"]:
        definitions = [(i, n) for i, n in enumerate(original.body) if isinstance(n, ast.FunctionDef) and n.name == name]
        first, second = definitions
        # Stronger fixed-source evidence: EVERY function (including replacement)
        # has only literal defaults; nonfunctions are imports/literals.
        for node in original.body[first[0]:second[0] + 1]:
            if isinstance(node, ast.FunctionDef):
                assert not node.decorator_list
                for default in node.args.defaults + [x for x in node.args.kw_defaults if x is not None]:
                    ast.literal_eval(default)
                assert node.returns is None and not node.type_params
                args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                args += [a for a in [node.args.vararg, node.args.kwarg] if a]
                assert all(a.annotation is None for a in args)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                assert all(a.name in {"re", "json"} for a in node.names)
            elif isinstance(node, ast.Expr):
                assert isinstance(node.value, ast.Constant)
            elif isinstance(node, ast.Assign):
                ast.literal_eval(node.value)
            else:
                raise AssertionError(ast.dump(node))
        removed = accepted_and_removed(ast.unparse(removed), name)
        evidence.append({"name": name, "first_line": first[1].lineno, "replacement_line": second[1].lineno,
                         "no_eager_capture_or_nonliteral_definition_time_expression_in_fixed_interval": True})
    a, b = {}, {}
    exec(compile(original, "<original donor engine>", "exec"), a)
    exec(compile(removed, "<stripped donor engine>", "exec"), b)
    for name in ["ix_request", "ix_policy_key"]:
        assert a[name].__code__.co_code == b[name].__code__.co_code
    for text in list(a["IX_POLICIES"].values()) + ["x", "  mixed\n whitespace\t", ""]:
        assert a["ix_policy_key"](text) == b["ix_policy_key"](text)
    examples = ["", "show me inventory", "Create an inventory CSV export at /exports/check.csv for PowerTools at Linz Hafen. Include `family_id` `fam-fresh` and use exactly these columns: `SKU,2026-10-22`. Return only the export path."]
    for text in examples:
        assert a["ix_request"](text) == b["ix_request"](text)

    parent = (HERE.parent / "2026-10-22-clarification-integration/readable.py").read_bytes()
    assert digest(parent) == "e0825037ed9c8993df78ee122e084e34a35507ddab7559dc0cc575358b0b1e44"
    tree = ast.parse(parent)
    cleanup = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "i2c_cleanup"]
    assert len(cleanup) == 1
    checker["inert_definition"](cleanup[0])
    assert not any(isinstance(n, ast.Name) and n.id == "i2c_cleanup" for n in ast.walk(tree))
    assert not any(isinstance(n, ast.Constant) and isinstance(n.value, str) and "i2c_cleanup" in n.value for n in ast.walk(tree))
    dynamic_names = {"vars", "globals", "locals", "eval", "exec", "getattr", "setattr", "compile", "__import__"}
    dynamic_calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call) and
                     ((isinstance(n.func, ast.Name) and n.func.id in dynamic_names) or
                      (isinstance(n.func, ast.Attribute) and n.func.attr in {"__getattribute__", "__dict__", "__globals__"}))]
    assert not dynamic_calls, dynamic_calls

    gaps = []
    fixtures = {
        "replacement_default_captures_previous_definition": "def victim(): return 'old'\ndef victim(saved=victim): return saved()\nresult=victim()\n",
        "intervening_indirect_capture": "def victim(): return 'old'\ndef capture(): return victim\nsaved=capture()\ndef victim(): return 'new'\nresult=saved()\n",
    }
    for label, source in fixtures.items():
        transformed = accepted_and_removed(source, "victim")
        env = {}
        exec(source, env)
        try:
            after = {}
            exec(compile(transformed, "<synthetic deletion>", "exec"), after)
            outcome = after["result"]
        except Exception as exc:
            outcome = type(exc).__name__
        assert outcome != env["result"]
        gaps.append({"issue": label, "exact_build_checker_accepts": True, "before": env["result"], "after": outcome,
                     "present_in_pinned_sources": False})
    varargs = ast.parse("def f(*args: int, **kwargs: str): pass").body[0]
    checker["inert_definition"](varargs)
    gaps.append({"issue": "inert_definition_omits_vararg_and_kwarg_annotations", "exact_build_checker_accepts": True,
                 "present_in_pinned_sources": False, "note": "Python 3.14 annotations are lazy; this alone is not an eager side-effect proof."})
    return {"fixed_source_removals_supported": True, "overwritten_definition_evidence": evidence,
            "parent_cleanup_definition_count": 1, "parent_cleanup_direct_or_string_references": 0,
            "fixed_parent_dynamic_namespace_calls": dynamic_calls,
            "parent_readable_sha256": digest(parent), "donor_sha256": digest(donor.encode()),
            "generalized_proof_weaknesses": gaps,
            "scope": "Pinned-source audit, not a general dead-code elimination proof. Fresh adversarial examples expose limits of build assertions without demonstrating a defect in this candidate."}


def monty_checks():
    import pydantic_monty as m
    sources = ["print('PACKER_OK')\n", "x='abcd'*300\nprint(len(x))\n",
               "x=list(range(256))\nprint(sum(x))\n", "def f(x):\n return x+1\nprint(f(41))\n"]
    results = []
    with m.Monty() as pool:
        for source in sources:
            outs = []
            for code in [source, CODEC["pack"](source)]:
                out = []
                with pool.checkout() as runtime:
                    runtime.feed_run(code, print_callback=lambda *args: out.append(args))
                outs.append(out)
            assert outs[0] == outs[1], outs
            results.append({"source_sha256": digest(source.encode()), "exact_print_events_equal": True})
    return results


def main():
    inputs = ["lzpack_dp.py", "build.py", "agent.py", "prepack.py"]
    input_hashes = {name: digest((HERE / name).read_bytes()) for name in inputs}
    result = {"python": sys.version, "status": "passed", "seed": 10222026,
              "packer": packer_checks(), "removal": definition_checks(), "native_monty": monty_checks()}
    assert input_hashes == {name: digest((HERE / name).read_bytes()) for name in inputs}, "inputs changed during audit"
    result["input_sha256"] = input_hashes
    target = HERE / "test_packer_independent_results.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
