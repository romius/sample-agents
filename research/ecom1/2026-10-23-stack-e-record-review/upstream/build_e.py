"""build_e.py — candidate E = bobcat d3756r1 (i2c14 + receipt v2 + two-match "but not" gate, on record d2499r1)
with i2c_xparse replaced by inara's crosslist_parse_ocr (c11 r2 readable d3585 L1642-1763, verbatim), as agreed
between bobcat (d3770) and inara (d3773). Only the parser changes; i2c_crosslist's matching, rendering and write stay.

  python3 build/build_e.py agents/bobcat-d3756r1.py build/inara-c11-readable.py build/E_readable.py build/E_agent.py
Packing reproduces bobcat's format (LZ tokens + base85, decoded by the same _lz header); the script asserts that
unpacking E_agent.py gives E_readable.py byte for byte, that both parse, and that the packed file fits 65,536 B.
"""
import ast, base64, sys

packed_in, inara_src, out_readable, out_agent = sys.argv[1:5]


def unpack(packed):
    g = {}
    exec(packed.replace("exec(_lz(", "_OUT=(_lz(", 1), g)
    return g["_OUT"]


def cut_def(src, name):
    a = src.index("\ndef %s(" % name) + 1
    b = src.index("\ndef ", a + 5) + 1
    return src[:a] + src[b:], src[a:b]


def take_def(src, name):
    a = src.index("\ndef %s(" % name) + 1
    b = a + 5
    while True:  # end at the next top-level statement
        b = src.index("\n", b) + 1
        if b >= len(src) or (src[b] not in " \t\n#"):
            return src[a:b]


packed = open(packed_in).read()
header = packed[:packed.index('exec(_lz("')]
src = unpack(packed)
inara = open(inara_src).read()

# 1. insert inara's parser verbatim (plus `import re` and the two helpers it calls) before i2c_crosslist
block = "import re\n\n# inara crosslist_parse_ocr (c11 r2 d3585, verbatim; credit inara, lom d246, sin_g4, hyrotina, bobcat d1488r6)\n"
block += "".join(take_def(inara, n) for n in ("crosslist_text", "crosslist_uint", "crosslist_parse_ocr"))
anchor = "def i2c_crosslist(ins):"
assert src.count(anchor) == 1
src = src.replace(anchor, block + "\n" + anchor, 1)

# 2. call it; any doubt (ValueError) declines exactly as i2c_xparse returning None did; map inara's keys to i2c's
old = '''    parsed = i2c_xparse(i2c_doc(up))
    if parsed is None:
        return None
'''
new = '''    try:
        parsed = crosslist_parse_ocr(i2c_doc(up))
    except (ValueError, TypeError):
        return None
    for it in parsed["lines"]:
        it["code"], it["qty"] = it["competitor_code"], it["requested_qty"]
'''
assert src.count(old) == 1
src = src.replace(old, new, 1)

# 3. drop bobcat's OCR parser and its private helpers, now called nowhere
for name in ("i2c_xparse", "i2c_xclean", "i2c_xjunk", "i2c_xcode", "i2c_xint_after"):
    src, _ = cut_def(src, name)
    assert name + "(" not in src, name
ast.parse(src)
src.encode("ascii")  # bobcat's _lz decoder maps bytes 1:1 to chr(); the source must stay ASCII


def lz(data):
    """LZ in _lz's format: c<128 -> literal run of c+1 bytes; c>=128 -> copy c-124 (4..131) bytes from
    distance d (2 bytes, big-endian, 4..65535) back in the output; length <= d because _lz copies o[p:p+len].
    Optimal parse (shortest encoding) by dynamic programming over match candidates."""
    n = len(data)
    index, cands = {}, [None] * n
    for i in range(n):
        best = []  # (longest match length, distance) per earlier occurrence
        if i + 4 <= n:
            for p in reversed(index.get(data[i:i + 4], [])[-256:]):
                d = i - p
                if d > 65535:
                    break
                if d < 4:
                    continue
                k = 4
                lim = min(131, d, n - i)
                while k < lim and data[p + k] == data[i + k]:
                    k += 1
                best.append((k, d))
        index.setdefault(data[i:i + 4], []).append(i)
        cands[i] = best
    INF = float("inf")
    cost = [INF] * (n + 1)
    step = [None] * (n + 1)
    cost[n] = 0
    for i in range(n - 1, -1, -1):
        # literal runs of 1..128 bytes
        for L in range(1, min(128, n - i) + 1):
            c = 1 + L + cost[i + L]
            if c < cost[i]:
                cost[i], step[i] = c, ("lit", L)
        for k, d in cands[i]:
            for L in range(4, k + 1):
                c = 3 + cost[i + L]
                if c < cost[i]:
                    cost[i], step[i] = c, ("m", L, d)
    out, i = bytearray(), 0
    while i < n:
        s = step[i]
        if s[0] == "lit":
            out.append(s[1] - 1)
            out.extend(data[i:i + s[1]])
            i += s[1]
        else:
            out.append(s[1] + 124)
            out.extend((s[2] >> 8, s[2] & 255))
            i += s[1]
    return bytes(out)


blob = base64.b85encode(lz(src.encode("ascii"))).decode()
agent = header + 'exec(_lz("' + blob + '"))\n'
assert unpack(agent) == src, "round trip"
ast.parse(agent)
open(out_readable, "w").write(src)
open(out_agent, "w").write(agent)
size = len(agent.encode())
assert size <= 65536, size
import hashlib
print("readable", len(src), "B; agent", size, "B; sha256", hashlib.sha256(agent.encode()).hexdigest())
