"""inara: pack the readable candidate under the 64 KiB source limit.

pack:  python pack3.py readable.py header.txt agent.py
check: python pack3.py --check agent.py readable.py   (re-packs; requires byte equality and size <= 65536)
python-minifier 3.4.0 with rename_locals, rename_globals AND remove_literal_statements (docstrings) (preserve_globals=["bitgn"]); every other
transform off. Function names, globals and locals become short names; strings, prompts, literals and
control flow are unchanged. Monty supports the emitted `import json as K` and `global` forms.
"""
import sys, hashlib
import python_minifier as pm
from python_minifier import RemoveAnnotationsOptions as RA
def mini(src):
    return pm.minify(src, remove_annotations=RA(False, False, False, False), remove_pass=False,
        remove_literal_statements=True, combine_imports=False, hoist_literals=True,
        rename_locals=True, rename_globals=True, preserve_globals=["bitgn"], remove_object_base=False,
        convert_posargs_to_args=False, remove_asserts=False, remove_debug=False,
        remove_explicit_return_none=False, remove_builtin_exception_brackets=False,
        constant_folding=False, prefer_single_line=False, remove_dead_branches=False)
if __name__ == "__main__":
    if sys.argv[1] == "--check":
        a = open(sys.argv[2], "rb").read(); lines = a.decode().split("\n"); n = 0
        while lines[n].startswith("#"): n += 1
        header = "\n".join(lines[:n]) + "\n"
        b = (header + mini(open(sys.argv[3], encoding="utf-8").read())).encode()
        print(len(a), hashlib.sha256(a).hexdigest(), "| re-pack equal:", a == b, "| <= 65536:", len(a) <= 65536)
        sys.exit(0 if a == b and len(a) <= 65536 else 1)
    out = open(sys.argv[2], encoding="utf-8").read() + mini(open(sys.argv[1], encoding="utf-8").read())
    open(sys.argv[3], "w", encoding="utf-8").write(out)
    print(len(out.encode()), hashlib.sha256(out.encode()).hexdigest())
