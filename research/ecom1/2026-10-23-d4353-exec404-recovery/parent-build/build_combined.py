"""Compose pinned d4236r1/d4237r1 with conservative receipt OCR recovery."""
import ast
import base64
import hashlib
import json
from pathlib import Path

import lzpack

ROOT = Path(__file__).resolve().parent
PARENT_READABLE_SHA = "1e82675e913792454530e1e67568ea1afc3d27326bbdd7bf1cfa37d567f1d179"
PARENT_PACKED_SHA = "2ef447520d2c17d8956426a17882a99e5cf59ee95e750b4afa4a784642f6d446"

HELPER = '''def _receipt_match(pattern, text, mode, recover):
  patterns = (pattern, pattern.replace(RCP_QTY, "[0-9Il|S]{1,3}")) if recover else (pattern,)
  for candidate in patterns:
    match = re.fullmatch(candidate, text) if mode == 0 else re.search(candidate, text) if mode == 1 else re.match(candidate, text)
    if match:
      return match
  return None


'''
WRAPPER = '''

_receipt_original_items = rcp_items


def rcp_items(text):
  original = _receipt_original_items(text)
  return original if original is not None else _receipt_original_items(text, True)
'''


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def ast_key(text):
    return ast.dump(ast.parse(text), include_attributes=False)


def apply_receipt_fix(source):
    assert source.count("def rcp_items(text):") == 1
    assert "_receipt_original_items" not in source
    start = source.index("def rcp_items(text):")
    end = source.index("\ndef rcp_product(", start)
    block = source[start:end].replace(
        "def rcp_items(text):", "def rcp_items(text, _ocr_quantity=False):", 1
    )
    lines = block.splitlines()
    counts = [0, 0, 0]
    for i, line in enumerate(lines):
        for mode, method in enumerate(("fullmatch", "search", "match")):
            anchor = "head = re." + method + "("
            if anchor in line and "RCP_QTY" in line:
                lines[i] = line.replace(anchor, "head = _receipt_match(").replace(
                    ", line)", ", line, " + str(mode) + ", _ocr_quantity)"
                )
                counts[mode] += 1
    assert counts == [1, 1, 1], counts
    result = source[:start] + HELPER + "\n".join(lines) + WRAPPER + source[end:]
    ast.parse(result)
    return result


def verify_unchanged_nodes(parent, candidate):
    old = ast.parse(parent).body
    new = ast.parse(candidate).body
    original_parser = next(n for n in old if isinstance(n, ast.FunctionDef) and n.name == "rcp_items")
    retained = []
    edited_parser_count = 0
    for node in new:
        if isinstance(node, ast.FunctionDef) and node.name == "_receipt_match":
            continue
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "_receipt_original_items" for t in node.targets
        ):
            continue
        if isinstance(node, ast.FunctionDef) and node.name == "rcp_items":
            if len(node.args.args) == 1:
                continue
            edited_parser_count += 1
            retained.append(original_parser)
        else:
            retained.append(node)
    assert edited_parser_count == 1
    assert [ast.dump(n) for n in retained] == [ast.dump(n) for n in old]
    old_i2c = {n.name: ast.dump(n) for n in old if isinstance(n, ast.FunctionDef) and n.name.startswith("i2c_")}
    new_i2c = {n.name: ast.dump(n) for n in new if isinstance(n, ast.FunctionDef) and n.name.startswith("i2c_")}
    assert old_i2c == new_i2c
    return len(old_i2c)


def main():
    readable = (ROOT / "parent_readable.py").read_text()
    packed = (ROOT / "parent_agent.py").read_text()
    assert sha(readable) == PARENT_READABLE_SHA
    assert sha(packed) == PARENT_PACKED_SHA
    tree = ast.parse(packed)
    payload = tree.body[-1].value.args[0].args[0].value
    decoded = lzpack.decode(base64.b85decode(payload)).decode("latin-1")
    assert ast_key(decoded) == ast_key(readable)
    assert lzpack.pack(decoded, lazy=True) == packed, "parent packing must reproduce exactly"

    combined_readable = apply_receipt_fix(readable)
    combined_payload = apply_receipt_fix(decoded)
    unchanged_i2c = verify_unchanged_nodes(readable, combined_readable)
    assert ast_key(combined_payload) == ast_key(combined_readable)
    combined_packed = lzpack.pack(combined_payload, lazy=True)
    assert len(combined_packed.encode()) <= 65536
    new_payload = ast.parse(combined_packed).body[-1].value.args[0].args[0].value
    unpacked = lzpack.decode(base64.b85decode(new_payload)).decode("latin-1")
    assert ast_key(unpacked) == ast_key(combined_readable)

    (ROOT / "readable.py").write_text(combined_readable)
    (ROOT / "agent.py").write_text(combined_packed)
    (ROOT / "decoded.py").write_text(unpacked)
    receipt = {
        "parent_packed": "d4236r1", "parent_packed_sha256": sha(packed),
        "parent_readable": "d4237r1", "parent_readable_sha256": sha(readable),
        "receipt_donor": "d4228r1 (same original-first receipt and row logic, readable names)",
        "readable_bytes": len(combined_readable.encode()),
        "packed_bytes": len(combined_packed.encode()),
        "packed_headroom": 65536-len(combined_packed.encode()),
        "readable_sha256": sha(combined_readable), "packed_sha256": sha(combined_packed),
        "unchanged_i2c_functions": unchanged_i2c,
        "all_other_parent_top_level_nodes_unchanged": True,
        "parent_packing_reproduced_exactly": True,
        "decoded_ast_identical_to_readable": True,
        "packer": "d3268r2 lazy; identical token format to parent",
    }
    (ROOT / "build-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
