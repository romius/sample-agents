"""Independent Huffman review; writes only independent_review_results.json.

UV_CACHE_DIR=/tmp/ecom1-uv-cache uv run --python 3.14 --no-project --offline
 --with pydantic-monty==1.2.0 python independent_review.py
"""
import ast
import base64
import collections
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import random
import runpy
import sys

HERE = Path(__file__).resolve().parent
PACK = runpy.run_path(str(HERE / "pack.py"))
SEED = 2026102203


def sha(data):
    return hashlib.sha256(data).hexdigest()


def increment(bits):
    chars = list(bits)
    while chars and chars[-1] == "1":
        chars.pop()
    if not chars:
        raise ValueError("oversubscribed code lengths")
    return "".join(chars[:-1]) + "1" + "0" * (len(bits) - len(chars))


def independent_decode(data):
    """Canonical words constructed as binary strings, then trie-walk payload."""
    if len(data) < 260:
        raise ValueError("short header")
    count = sum(data[i] * 256 ** (3 - i) for i in range(4))
    ordered = sorted((width, symbol) for symbol, width in enumerate(data[4:260]) if width)
    root = {}
    word = None
    for width, symbol in ordered:
        word = "0" * width if word is None else increment(word) + "0" * (width - len(word))
        node = root
        for bit in word:
            if "symbol" in node:
                raise ValueError("prefix collision")
            node = node.setdefault(bit, {})
        if node:
            raise ValueError("duplicate/prefix code")
        node["symbol"] = symbol
    if count == 0:
        if len(data) != 260:
            raise ValueError("empty with payload")
        return b""
    if not root:
        raise ValueError("empty codebook")
    bits = "".join(format(b, "08b") for b in data[260:])
    result = bytearray()
    node = root
    for index, bit in enumerate(bits):
        if bit not in node:
            raise ValueError("unknown code")
        node = node[bit]
        if "symbol" in node:
            result.append(node["symbol"])
            node = root
            if len(result) == count:
                remaining = bits[index + 1:]
                if len(remaining) >= 8 or "1" in remaining:
                    raise ValueError("noncanonical trailing bits")
                return bytes(result)
    raise ValueError("incomplete data")


@lru_cache(None)
def optimal_merge_cost(weights):
    """Brute force every pairwise tree merge, independent of greedy heap."""
    if len(weights) == 1:
        return 0
    return min(weights[i] + weights[j] + optimal_merge_cost(tuple(sorted(
        [x for k, x in enumerate(weights) if k not in (i, j)] + [weights[i] + weights[j]])))
        for i in range(len(weights)) for j in range(i + 1, len(weights)))


def runtime_huffman_source():
    # Exact runtime prefix, before the unchanged LZ decoder. This permits testing
    # arbitrary token bytes independently from whether they are valid LZ.
    prefix = PACK["HUFFMAN"].split(" o=[];i=0;n=len(t)")[0]
    return "import base64\ndef unpack(s):\n" + prefix + "\n return t\n"


def codec_tests():
    rng = random.Random(SEED)
    vectors = [b"", bytes(range(256)), bytes(range(255, -1, -1)) * 5]
    vectors += [bytes([symbol]) * size for symbol in range(256) for size in (7, 9)]
    vectors += [b"x" * size for size in range(1, 17)]
    vectors += [rng.randbytes(size) for size in [2, 3, 4, 15, 16, 17, 255, 256, 257, 4096, 65535, 65536]]
    vectors += [bytes(rng.randrange(alphabet) for _ in range(size))
                for alphabet in (2, 3, 5, 11, 57) for size in (1, 8, 17, 126, 300)]
    fib = [1, 1]
    for _ in range(18):
        fib.append(sum(fib[-2:]))
    vectors.append(b"".join(bytes([i]) * n for i, n in enumerate(fib)))
    runtime = {}
    exec(runtime_huffman_source(), runtime)
    max_width = 0
    for data in vectors:
        encoded = PACK["huffman_encode"](data)
        assert independent_decode(encoded) == PACK["huffman_decode"](encoded) == data
        assert bytes(runtime["unpack"](base64.b85encode(encoded).decode())) == data
        assert encoded == PACK["huffman_encode"](data)
        max_width = max(max_width, max(encoded[4:260]))
    exhaustive = 0
    for size in range(9):
        for seq in itertools.product(range(3), repeat=size):
            data = bytes(seq)
            assert independent_decode(PACK["huffman_encode"](data)) == data
            exhaustive += 1
    optimal = 0
    for weights in itertools.product(range(1, 5), repeat=4):
        data = b"".join(bytes([i]) * n for i, n in enumerate(weights))
        lengths = PACK["lengths_for"](data)
        assert sum(weights[i] * lengths[i] for i in range(4)) == optimal_merge_cost(tuple(sorted(weights)))
        optimal += 1
    class OverLimit:
        def __len__(self):
            return 2 ** 32
    try:
        PACK["huffman_encode"](OverLimit())
    except ValueError as exc:
        assert str(exc) == "token length"
    else:
        raise AssertionError("uint32 count overflow accepted")
    return {"roundtrip_vectors": len(vectors), "exhaustive_ternary_strings": exhaustive,
            "brute_force_tree_optimality_cases": optimal, "max_generated_code_width": max_width,
            "uint32_size_guard": "rejects 2**32 before iteration",
            "empty_stream": "260-byte header, zero count, zero code lengths, no payload",
            "single_symbol": "one-bit zero code; all 256 symbols and all padding residues tested"}, vectors


def malformed_tests():
    one = PACK["huffman_encode"](b"A")
    extra = one + b"\x00"
    nonzero_padding = one[:-1] + bytes([one[-1] | 1])
    truncated = PACK["huffman_encode"](bytes(range(16)))[:-1]
    over = bytearray(261)
    over[3] = 1
    over[4:7] = b"\x01\x01\x01"
    unknown = bytearray(one)
    unknown[-1] = 128
    fixtures = {"extra_byte": extra, "nonzero_padding": nonzero_padding,
                "truncated_payload": truncated, "oversubscribed_codebook": bytes(over),
                "unknown_code": bytes(unknown), "short_header": b"abc"}
    env = {}
    exec(runtime_huffman_source(), env)
    results = []
    for label, data in fixtures.items():
        for decoder in (independent_decode, PACK["huffman_decode"]):
            try:
                decoder(data)
            except ValueError:
                pass
            else:
                raise AssertionError((label, "strict decoder accepted"))
        try:
            out = env["unpack"](base64.b85encode(data).decode())
            behavior = {"returned_token_count": len(out), "returned_tokens": out[:20]}
        except Exception as exc:
            behavior = {"exception": type(exc).__name__}
        results.append({"case": label, "strict_decoders_reject": True, "runtime_behavior": behavior})
    return results


def native_tests(vectors):
    import pydantic_monty as m
    selected = [b"", b"A", b"A" * 8, b"A" * 9, bytes(range(256)), b"z" * 65536, vectors[-1]]
    payloads = [base64.b85encode(PACK["huffman_encode"](data)).decode() for data in selected]
    program = runtime_huffman_source() + "\nfor payload,want in zip(payloads,expected):\n value=unpack(payload)\n print(len(value),value==want)\n"
    output = []
    with m.Monty() as engine:
        with engine.checkout() as session:
            session.feed_run(program, inputs={"payloads": payloads, "expected": [list(data) for data in selected]},
                             print_callback=lambda *args: output.append(args))
    text = "".join(str(item[1]) if len(item) > 1 else str(item[0]) for item in output)
    assert text == "".join(f"{len(data)} True\n" for data in selected), text
    return {"exact_token_vector_comparisons": len(selected), "includes_empty_single_symbol_uint32_count_and_depth19": True}


def artifact_tests():
    specs = {"inventory-packed.py": HERE.parent / "2026-10-22-inventory-integration/prepack.py",
             "sku-definition-only-packed.py": HERE.parent / "2026-10-22-sku-evidence-review/size-only-prepack.py"}
    results = []
    for filename, expected_path in specs.items():
        source = (HERE / filename).read_bytes()
        tree = ast.parse(source)
        payload = tree.body[-1].value.args[0].args[0].value
        raw = base64.b85decode(payload)
        tokens = independent_decode(raw)
        expected = expected_path.read_bytes()
        assert PACK["codec"]["decode"](tokens) == expected
        env = {}
        exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), filename, "exec"), env)
        assert env["_lz"](payload).encode("ascii") == expected
        # Exact old LZ loop is retained after the Huffman-only prefix.
        old_function = next(n for n in ast.parse(PACK["codec"]["STUB"] % "").body if isinstance(n, ast.FunctionDef))
        new_function = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
        old_loop = next(n for n in old_function.body if isinstance(n, ast.While))
        new_loop = next(n for n in new_function.body if isinstance(n, ast.While))
        assert ast.dump(old_loop) == ast.dump(new_loop)
        widths = collections.Counter(raw[4:260])
        results.append({"artifact": filename, "sha256": sha(source), "bytes": len(source),
                        "expected_prepack_sha256": sha(expected), "token_count": len(tokens),
                        "code_length_counts": dict(sorted(widths.items())),
                        "independent_exact_roundtrip": True, "unchanged_lz_loop_ast": True})
    return results


def main():
    names = ["pack.py", "inventory-packed.py", "sku-definition-only-packed.py"]
    fingerprints = {name: sha((HERE / name).read_bytes()) for name in names}
    codec, vectors = codec_tests()
    result = {"status": "passed", "python": sys.version, "seed": SEED,
              "initial_compatibility_finding": "Parent's native test found int.from_bytes unsupported in Monty; reviewed version uses manual four-byte arithmetic. No submitted artifact changed.",
              "codec": codec, "malformed_inputs": malformed_tests(), "native": native_tests(vectors),
              "artifacts": artifact_tests(), "input_sha256": fingerprints,
              "scope": "Exact generated payloads decode safely in tested runtime. Runtime is intentionally permissive, not a validator for untrusted or corrupted Huffman streams. Strict build decoder plus exact original-byte equality is required. No paid run or whole-agent behavior claim."}
    assert fingerprints == {name: sha((HERE / name).read_bytes()) for name in names}, "review inputs changed"
    (HERE / "independent_review_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
