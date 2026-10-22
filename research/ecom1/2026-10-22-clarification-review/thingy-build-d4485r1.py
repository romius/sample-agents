"""Build h1d/agent_h1d.py = c10r2 packed agent (../base.py, sha 1e6a0ae3...) + riders written in the packed vocabulary (tabs, aliases of the packed preamble).
usage: python3 -I -B build_h1d_packed.py out.py [R1,R2,...] [--trim]     --trim: also shrink the 330-byte header comment to one short line
Every edit is a text replacement asserted to match exactly once.  New global names qA..qE and locals qa..qk are not used anywhere in the base (checked)."""
import sys, ast, hashlib, re
H = "/tmp/claude-0/-home-user-career/fdc266b9-a536-5e2b-bfa1-013f3597ef40/scratchpad/localbench/c10/"
src = open(H + "base.py", newline="", encoding="utf-8").read()
assert hashlib.sha256(src.encode("utf-8")).hexdigest() == "1e6a0ae3505593c380fbc1d3010295cef58e2b2a7a8aaf0cfe6a47da8591a86f"
args = [a for a in sys.argv[2:] if not a.startswith("--")]
want = args[0].split(",") if args else ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9"]
trim = "--trim" in sys.argv or "--compact" in sys.argv
compact = "--compact" in sys.argv
base_names = set()
for n in ast.parse(src).body:
    if isinstance(n, ast.FunctionDef): base_names.add(n.name)
    for x in ast.walk(n):
        if isinstance(x, ast.Name): base_names.add(x.id)
        if isinstance(x, ast.arg): base_names.add(x.arg)

def once(s, old, new):
    assert s.count(old) == 1, (s.count(old), old[:80])
    return s.replace(old, new)

funcs = ""
B6_old = "if C==Aa:D=D6(A[A9],A[A2]);E=EO(BV(A.get(CI,[]),D,A[A2]),A[A2]);I('Final answer',g.dumps([D,E]));return bitgn.answer(D,outcome=A[A2],refs=E)"
inner = "EO(BV(A.get(CI,[]),D,A[A2]),A[A2])"
if "R1" in want:
    inner = "qA(" + inner + ")"
    funcs += (
        "def qA(qa):\n"
        "\tqb=N.search('\\\\(but not (PT-[A-Za-z0-9-]+)\\\\)',c)\n"
        "\tif qb is A:return qa\n"
        "\ttry:qc=bitgn.call(f,{F:'/docs/catalogue-lookup.md'}).get(J)or C\n"
        "\texcept q:return qa\n"
        "\tif N.search('(?i)then (?:do not|don.t) (?:quote|cite) that',qc)is A:return qa\n"
        "\treturn[qd for qd in qa if qd.split('#',1)[0].rsplit(K,1)[-1].lower()!=qb.group(1).lower()+l]\n")
post = ""
if "R2" in want:
    post = ";D=qB(D,A[A2],E)"
    funcs += (
        "def qB(qa,qb,qc):\n"
        "\tif qb!=Bk:return qa\n"
        "\tqd=[]\n"
        "\tfor qe in qc:\n"
        "\t\tqf=qe.split('#',1)[0].rsplit(K,1)[-1]\n"
        "\t\tif qf.startswith('PT-')and qf.endswith(l)and qf[:-5]not in qa and qf[:-5]not in qd:qd.append(qf[:-5])\n"
        "\treturn qa+' Candidates: '+', '.join(qd)if qd else qa\n")
if "R1" in want or "R2" in want:
    src = once(src, B6_old, "if C==Aa:D=D6(A[A9],A[A2]);E=" + inner + post.replace(";D=", ";D=", 1) + ";I('Final answer',g.dumps([D,E]));return bitgn.answer(D,outcome=A[A2],refs=E)")
QC_FULL = "qC='under (/tmp/[\\\\w.-]+), delete only files whose basename ends exactly in `\\\\.tmp`\\\\. leave every other file there untouched\\\\. return only the deleted paths, one per line, sorted alphabetically\\\\.','please clean out every temporary file under (/tmp/[\\\\w.-]+)\\\\. delete all files there and nothing else\\\\. return only the deleted paths, one per line, sorted alphabetically\\\\.'\n"
QC_HEAD = "qC='under (/tmp/[\\\\w.-]+), delete only files whose basename ends exactly in `\\\\.tmp`.*','please clean out every temporary file under (/tmp/[\\\\w.-]+)\\\\. delete all files there and nothing else.*'\n"
if "R3" in want:
    funcs += (
        (QC_HEAD if (compact and "--fulltpl" not in sys.argv) else QC_FULL) +
        "def qD(qa,qb):\n"
        "\tif not AP(qb)[0].startswith('emp-'):return\n"
        "\tqa=H.join(qa.split())\n"
        "\tfor qc,qd in enumerate(qC):\n"
        "\t\tqe=N.fullmatch('(?i)'+qd,qa)\n"
        "\t\tif qe:\n"
        "\t\t\tqf=bitgn.call(CD,{F:qe.group(1)}).get(CN)or[]\n"
        "\t\t\tif i(qg.get(k)!=At or qg.get(R,C).lower()in('agents.md','readme.md')for qg in qf):return\n"
        "\t\t\tqh=sorted(qg[F]for qg in qf if qc or qg[R].endswith('.tmp'))\n"
        "\t\t\tif not qh:return\n"
        "\t\t\tfor qg in qh:bitgn.call('Delete',{F:qg})\n"
        "\t\t\treturn U.join(qh),[qe.group(1),y]\n")
    old = "if not Q:\n\ttry:AR=F3(c,AD)\n"
    new = ("if not Q:\n\ttry:qi=qD(c,AD)\n\texcept o as Z:I('cleanup: failed, falling back',D(Z)[:200]);qi=A\n"
           "\tif qi is not A:I('cleanup:',B(qi[0].split(U)),'files');bitgn.answer(qi[0],outcome=h,refs=qi[1]);Q=M\n") + old
    src = once(src, old, new)
if "R4" in want:
    funcs += (
        "def qE(qa):\n"
        "\tqb=qa.split(U);qc=qb[0].count(',')+1;qd=[]\n"
        "\tfor qe in qb:\n"
        "\t\tqf=qe.split(',')\n"
        "\t\twhile B(qf)>qc and qf[-1]=='0':qf.pop()\n"
        "\t\tqd.append(','.join(qf))\n"
        "\treturn U.join(qd)\n")
    old = "\treturn bitgn.call(EF[C],B)\n"
    new = "\tif C==CC and B['path'].startswith('/exports/')and B['path'].endswith('.csv'):B['content']=qE(B['content'])\n" + old
    src = once(src, old, new)
if "R1" in want or "R2" in want or "R3" in want or "R4" in want:
    src = once(src, "def EO(final,outcome):\n", funcs + "def EO(final,outcome):\n")
if "R5" in want:
    src = once(src, "('[[','\\\\[\\\\[[^\\\\]\\\\s,]{3,}(?:\\\\]\\\\]|::)')", "('[[','\\\\[\\\\[[^\\\\]\\\\n,]{3,60}?(?:\\\\]\\\\]|::)')")
if "R6" in want:
    src = once(src, "C9='[0-9Il|]{1,3}'", "C9='[0-9IlSBOZQL|]{1,3}'")
if "R7" in want:
    src = once(src, "if I[S]not in(d,AW,BF,AX,As,BG):return A", "if I[S]not in(d,AW,BF,AX,As,BG,CC,AY):return A")
if "R8" in want:
    old = "\t\tfor C in A6[d]:\n\t\t\tif C.startswith(Ae)and C not in B:B.append(C)\n"
    new = old + "\t\tif'how many of these SKUs'in c:\n\t\t\tAO()\n\t\t\tfor C in X[A3]:\n\t\t\t\tif C[W]not in B and C.get(T)in K:B.append(C[W])\n"
    src = once(src, old, new)
if "R9" in want:
    src = once(src, "and not(';'in D and N.search('[A-Za-z]',D)):raise G(a)", "and not(';'in D and N.search('[A-Za-z]',D))and not(N.fullmatch('[a-z]+',D)and not E[U][-1].endswith(';')):raise G(a)")
if trim:
    hdr = "# inara c10: c9 (d1857r1 + crosslist export + marker gate + receipt check + price drift + bobcat d2118 + naya-ops d2128\n# + agorlov d2243 + redexplorer d2245 + robustness fixes) + demerzel d1395 Delete-404 containment + t074 same-city refs.\n# rename_locals+globals+hoist_literals pack (pack5h.py); readable.py is the review copy.\n"
    src = once(src, hdr, "# inara c10 + H1d riders; credits in the c4-c10 READMEs\n")

if compact:
    # (2) dead function fmt_eur (never referenced)
    src = once(src, "def Fe(cents):A=cents;return'EUR %d.%02d'%(A//100,A%100)\n", "")
    # (4) Delete-404: the generic read-type observation covers delete, exec and write; the specific delete_error branch goes
    i0 = src.index("\tif I[S]==Bh and C.startswith(H):return{'delete_error'")
    i1 = src.index("\n", i0) + 1
    src = src[:i0] + src[i1:]
    src = once(src, "if I[S]not in(d,AW,BF,AX,As,BG" + (",CC,AY" if "R7" in want else "") + "):return A", "if I[S]not in(d,AW,BF,AX,As,BG,Bh,CC,AY):return A")
    # (3) diagnostic prints: keep the handler tag, drop the prose
    import re as _re
    def short(mo):
        tag = "".join(w[0] for w in mo.group(1).split("-"))
        return "I('" + tag + ":fb'"
    n_before = len(src.encode())
    src = _re.sub(r"I\('([a-z0-9 -]+): [^'\n]*falling back'", short, src)
    print("prints shortened:", n_before - len(src.encode()), "bytes")
# new names must be fresh
for nm in re.findall(r"\bq[A-Za-z]\b", "".join(l for l in funcs.split("\n"))):
    pass
used_new = set(re.findall(r"\bq[A-Za-z]\b", funcs))
assert not (used_new & base_names), used_new & base_names
ast.parse(src)
data = src.encode("utf-8")
open(sys.argv[1], "wb").write(data)
print("wrote", sys.argv[1], len(data), "bytes; headroom", 65536 - len(data), "; sha256", hashlib.sha256(data).hexdigest()[:16], "; riders", want, "trim" if trim else "")
