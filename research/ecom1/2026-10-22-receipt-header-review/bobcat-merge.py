"""bobcat TRAIN-2 receipt merge (codex d4228 original-first parse + thingy H1d R6 alphabet + sin_g4 label fix + header tolerance).
usage: python3 merge_patch.py PAYLOAD_IN OUT   (PAYLOAD_IN = TRAIN-1 r2 payload.py d4659r2, sha 736630cc...)
Only the receipt parser DM and the constant C9 change; every other top-level statement is untouched (asserted)."""
import ast, hashlib, sys
src = open(sys.argv[1], encoding="utf-8").read()
def once(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:60]); return s.replace(a, b)
i = src.index("\ndef DM(text):") + 1; j = src.index("\ndef ", i + 5) + 1
old = src[i:j]
assert "C9" in old and "t?otal" in old, "expected TRAIN-1 DM (sin_g4 label fix present)"
new = old
new = once(new, "def DM(text):", "def DM(text,_s=False):")
# (a) header tolerance: OCR damages the layout-C header ('Item t Unit Total' in TRAIN-1 smoke j6b8792be t003)
new = once(new, "else'C'if'ITEM QTY UNIT TOTAL'in H.join(L.split())else A", "else'C'if'UNIT TOTAL'in H.join(L.split())else A")
# (b) codex d4228: row patterns go through _rcp_match (original class first, widened class only on retry)
new = once(new, "B=N.fullmatch('('+C9+R+An+')',G)if J is A else A", "B=_rcp_match('('+C9+R+An+')',G,0,_s)if J is A else A")
new = once(new, "B=N.search('\\\\[[0-9Il]+\\\\] ('+C9+R+An+') (\\\\S+)(?: [^0-9A-Za-z].*)?$',G)", "B=_rcp_match('\\\\[[0-9Il]+\\\\] ('+C9+R+An+') (\\\\S+)(?: [^0-9A-Za-z].*)?$',G,1,_s)")
new = once(new, "B=N.match('(.+?) ('+C9+S+An+S+An+')(?: |$)',G)", "B=_rcp_match('(.+?) ('+C9+S+An+S+An+')(?: |$)',G,2,_s)")
helper = ("def _rcp_match(p,t,m,s):\n for x in((p,p.replace(C9,'[0-9IlSBOZQL|]{1,3}'))if s else(p,)):\n"
          "  r=N.fullmatch(x,t)if m==0 else N.search(x,t)if m==1 else N.match(x,t)\n  if r:return r\n return A\n")
tail = "_rcp_items=DM\ndef DM(text):\n r=_rcp_items(text)\n return r if r is not A else _rcp_items(text,True)\n"
out = src.replace(old, helper + new + tail)
# first pass uses the record's quantity class again; H1d R6's wider class (S,B,O,Z,Q,L) moves to the retry pass
out = once(out, "C9='[0-9IlSBOZQL|]{1,3}'", "C9='[0-9Il|]{1,3}'")
assert not ({"_rcp_match", "_rcp_items"} & {n.id for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Name)})
a = [ast.dump(x) for x in ast.parse(src).body]; b = [ast.dump(x) for x in ast.parse(out).body]
assert len(b) == len(a) + 3
open(sys.argv[2], "w", encoding="utf-8").write(out)
print("out", len(out.encode()), "sha256", hashlib.sha256(out.encode()).hexdigest())
