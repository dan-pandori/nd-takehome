"""Reviewer's own Lean re-check harness (peer-rl-review).  Independent of lean_gate.py / nd2lean.py / lean_tok.py.

check(items) with items = [(prompt, body)], body = a one-line tactic text (the env's `lean_text` / guided `accepted` key)
-> list of (ok, reason).  A theorem is accepted iff Lean 4.34.0 reports no error on its line, prints its axioms line,
and the axioms are a subset of {propext, Classical.choice, Quot.sound} (no sorryAx).

nd_to_lean(prompt, nd) renders an ND proof string (spec format, `N1 ... : RULE refs ; ... ; QED`) to a tactic body,
written from the ND rule semantics (premise h<j>, line n<k>), for reads that stored only ND strings.
"""
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fml  # noqa: E402

LEAN = os.path.expanduser("~/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean")
OK_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
CHUNK = 250


def lf(f):
    """formula tuple -> Lean"""
    if f[0] == "a":
        return f[1]
    if f[0] == "F":
        return "False"
    if f[0] == "~":
        return f"( ¬ {lf(f[1])} )"
    o = {"&": "∧", "v": "∨", ">": "→"}[f[0]]
    return f"( {lf(f[1])} {o} {lf(f[2])} )"


def statement(prompt, name):
    prem, concl = fml.parse_prompt(prompt)
    hyps = " ".join(f"( h{j + 1} : {lf(p)} )" for j, p in enumerate(prem))
    return f"theorem {name} ( P Q R S : Prop ) {hyps} : {lf(concl)} := by"


def _run_file(srcs, tag):
    """srcs: list of (stmt_prefix_without_name_fn, body) already formatted lines with placeholder {NAME}"""
    lines = ["set_option linter.unusedVariables false"]
    first = len(lines) + 1  # 1-based line of theorem 0
    for k, (stmt, body) in enumerate(srcs):
        lines.append(stmt.format(NAME=f"t{k}") + " " + body)
        lines.append(f"#print axioms t{k}")
    text = "\n".join(lines) + "\n"
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False, dir="/tmp") as fh:
        fh.write(text)
        path = fh.name
    try:
        p = subprocess.run([LEAN, "-DmaxErrors=100000000", path], capture_output=True, text=True, timeout=1800)
        out = p.stdout + p.stderr
        crashed = False
    except subprocess.TimeoutExpired:
        out, crashed = "", True
    finally:
        os.unlink(path)
    if crashed:
        return None
    base = os.path.basename(path)
    err_lines = set()
    sorry_lines = set()
    for m in re.finditer(re.escape(base) + r":(\d+):\d+: (error|warning): (.*)", out):
        ln = int(m.group(1))
        if m.group(2) == "error":
            err_lines.add(ln)
        elif "sorry" in m.group(3):
            sorry_lines.add(ln)
    axioms = {}
    for m in re.finditer(r"'t(\d+)' depends on axioms: \[([^\]]*)\]", out):
        axioms[int(m.group(1))] = {a.strip() for a in m.group(2).split(",") if a.strip()}
    for m in re.finditer(r"'t(\d+)' does not depend on any axioms", out):
        axioms[int(m.group(1))] = set()
    res = []
    for k in range(len(srcs)):
        tl = first + 2 * k
        if tl in err_lines:
            res.append((False, "error"))
        elif tl in sorry_lines:
            res.append((False, "sorry"))
        elif k not in axioms:
            res.append((False, "no axioms line"))
        elif not axioms[k] <= OK_AXIOMS:
            res.append((False, "axioms " + ",".join(sorted(axioms[k]))))
        elif (tl + 1) in err_lines:
            res.append((False, "error on #print line"))
        else:
            res.append((True, "ok"))
    return res


def _check_srcs(srcs, tag="c", depth=0):
    if not srcs:
        return []
    r = _run_file(srcs, tag)
    if r is not None:
        return r
    if len(srcs) == 1:
        return [(False, "lean crash/timeout")]
    h = len(srcs) // 2
    # renumbering happens inside _run_file, per written file (the recursive-split trap)
    return _check_srcs(srcs[:h], tag, depth + 1) + _check_srcs(srcs[h:], tag, depth + 1)


def check(items, chunk=CHUNK, progress=False):
    srcs = []
    for prompt, body in items:
        stmt = statement(prompt, "{NAME}")
        srcs.append((stmt, body.replace("\n", " ")))
    out = []
    for i in range(0, len(srcs), chunk):
        out += _check_srcs(srcs[i:i + chunk])
        if progress:
            print(f"  lean: {min(i + chunk, len(srcs))}/{len(srcs)}", file=sys.stderr, flush=True)
    return out


# ---------------- ND -> Lean ----------------
LINE = re.compile(r"N(\d+) ((?:\| )*)(.*) : (\S+)((?: N\d+)*)$")


class NDError(Exception):
    pass


def parse_nd(nd):
    lines = []
    for part in nd.split(" ; "):
        part = part.strip()
        if part == "QED":
            break
        m = LINE.match(part)
        if not m:
            raise NDError("unparsed line: " + part)
        k = int(m.group(1))
        depth = m.group(2).count("|")
        f, _ = fml.parse_formula(m.group(3).split())
        rule = m.group(4)
        refs = [int(x[1:]) for x in m.group(5).split()]
        lines.append({"k": k, "d": depth, "f": f, "rule": rule, "refs": refs})
    return lines


def nd_to_lean(prompt, nd):
    prem, concl = fml.parse_prompt(prompt)
    L = parse_nd(nd)
    by_k = {x["k"]: x for x in L}
    # box structure: box = {"as": line, "body": [lines in this box at its depth or nested boxes]}
    top = {"as": None, "d": 0, "items": []}
    stack = [top]
    boxes = {}
    for x in L:
        d = x["d"]
        if x["rule"] == "AS":
            if d < 1:
                raise NDError("AS at depth 0")
            while len(stack) > 1 and stack[-1]["d"] >= d:
                stack.pop()
            if stack[-1]["d"] != d - 1:
                raise NDError("box depth jump")
            b = {"as": x, "d": d, "items": []}
            boxes[x["k"]] = b
            stack[-1]["items"].append(("box", b))
            stack.append(b)
        else:
            while len(stack) > 1 and stack[-1]["d"] > d:
                stack.pop()
            if stack[-1]["d"] != d:
                raise NDError(f"line N{x['k']} at depth {d} outside any open box")
            stack[-1]["items"].append(("line", x))
    used_prem = set()

    def term(x):
        r, refs, f = x["rule"], x["refs"], x["f"]
        n = lambda k: f"n{k}"  # noqa: E731
        if r == "PR":
            for j, p in enumerate(prem):
                if p == f and j not in used_prem:
                    used_prem.add(j)
                    return f"h{j + 1}"
            for j, p in enumerate(prem):
                if p == f:
                    return f"h{j + 1}"
            raise NDError("PR formula not a premise")
        if r == "R":
            return n(refs[0])
        if r == "ANDI":
            return f"⟨ {n(refs[0])} , {n(refs[1])} ⟩"
        if r == "ANDE1":
            return f"{n(refs[0])}.1"
        if r == "ANDE2":
            return f"{n(refs[0])}.2"
        if r in ("IMPE", "NEGE"):
            a, b = refs
            fa, fb = by_k[a]["f"], by_k[b]["f"]
            # function first: the reference whose formula is (other -> ...) or (~ other)
            if (fa[0] == ">" and fa[1] == fb) or (fa[0] == "~" and fa[1] == fb):
                return f"{n(a)} {n(b)}"
            if (fb[0] == ">" and fb[1] == fa) or (fb[0] == "~" and fb[1] == fa):
                return f"{n(b)} {n(a)}"
            return f"{n(a)} {n(b)}"  # leave it to Lean
        if r == "ORI1":
            return f"Or.inl {n(refs[0])}"
        if r == "ORI2":
            return f"Or.inr {n(refs[0])}"
        if r == "DN":
            return f"Classical.byContradiction ( fun hh => {n(refs[0])} hh )"
        if r == "BOTE":
            return f"False.elim {n(refs[0])}"
        if r in ("IMPI", "NEGI"):
            a, c = refs
            if a not in boxes:
                raise NDError("IMPI/NEGI without box")
            return render_fun(boxes[a], c, neg=(r == "NEGI"))
        if r == "ORE":
            j, a1, c1, a2, c2 = refs
            if a1 not in boxes or a2 not in boxes:
                raise NDError("ORE without boxes")
            return f"Or.elim {n(j)} {render_fun(boxes[a1], c1)} {render_fun(boxes[a2], c2)}"
        raise NDError("unknown rule " + r)

    def render_items(items):
        out = []
        for kind, v in items:
            if kind == "line":
                out.append(f"have n{v['k']} : {lf(v['f'])} := {term(v)}")
        return out

    def render_fun(b, c, neg=False):
        a = b["as"]
        inner = render_items(b["items"])
        end = f"exact ( n{c} : False )" if neg else f"exact n{c}"
        return f"( fun ( n{a['k']} : {lf(a['f'])} ) => by {' ; '.join(inner + [end])} )"

    body = render_items(top["items"])
    last = [v for kind, v in top["items"] if kind == "line"]
    if not last:
        raise NDError("no top-level line")
    if last[-1]["f"] != concl:
        raise NDError("last top-level line is not the conclusion")
    return " ; ".join(body + [f"exact n{last[-1]['k']}"])


if __name__ == "__main__":
    # smoke test
    pr = "THM SEQ ( ( P v Q ) > ( Q v P ) ) PRF"
    nd = ("N1 | ( P v Q ) : AS ; N2 | | P : AS ; N3 | | ( Q v P ) : ORI2 N2 ; N4 | | Q : AS ; N5 | | ( Q v P ) : "
          "ORI1 N4 ; N6 | ( Q v P ) : ORE N1 N2 N3 N4 N5 ; N7 ( ( P v Q ) > ( Q v P ) ) : IMPI N1 N6 ; QED")
    b = nd_to_lean(pr, nd)
    print(b)
    print(check([(pr, b), (pr, "sorry"), (pr, b.replace("Or.inr", "Or.inl", 1))]))
