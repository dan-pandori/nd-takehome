"""Reviewer's own ND -> Lean renderer and batch Lean 4 checker (proof-strategies review).

render(prem, concl, proof) -> one-line tactic body for `theorem t (P Q R S : Prop) (h1 : ..) .. : G := by <body>`.
check(items) with items = [(prem, concl, body)] -> [(ok, reason)].  Accepted iff Lean 4.34.0 reports no error on the
theorem's line and `#print axioms` lists only {propext, Classical.choice, Quot.sound} (so sorryAx fails).
Files are renumbered per written file (inside the recursion), the trap noted in earlier reviews.
"""
import os
import re
import subprocess
import tempfile
from nd import Proof

LEAN = os.path.expanduser("~/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean")
OK_AX = {"propext", "Classical.choice", "Quot.sound"}


def lf(f):
    if isinstance(f, str):
        return "False" if f == "F" else f
    if f[0] == "~":
        return "(¬ " + lf(f[1]) + ")"
    return "(" + lf(f[1]) + {"&": " ∧ ", "v": " ∨ ", ">": " → "}[f[0]] + lf(f[2]) + ")"


def statement(prem, concl, name):
    hs = " ".join(f"(h{j + 1} : {lf(p)})" for j, p in enumerate(prem))
    return f"theorem {name} (P Q R S : Prop) {hs} : {lf(concl)} := by"


def render(prem, concl, proof, flip=None):
    """flip: optional line index k whose ORI1/ORI2 (or ANDE1/ANDE2) is swapped (negative control)."""
    P = Proof(prem, concl, proof)
    L = P.L
    pr_idx = {}
    n = 0
    for k in P.order:
        if L[k]["rule"] == "PR":
            pr_idx[k] = n + 1
            n += 1

    def term(k):
        x = L[k]
        r, refs = x["rule"], x["refs"]
        v = lambda j: f"n{j}"  # noqa: E731
        if r == "PR":
            return f"h{pr_idx[k]}"
        if r == "R":
            return v(refs[0])
        if r == "ANDI":
            return f"(And.intro {v(refs[0])} {v(refs[1])})"
        if r in ("ANDE1", "ANDE2"):
            rr = r if flip != k else ("ANDE2" if r == "ANDE1" else "ANDE1")
            return f"{v(refs[0])}.{'1' if rr == 'ANDE1' else '2'}"
        if r in ("ORI1", "ORI2"):
            rr = r if flip != k else ("ORI2" if r == "ORI1" else "ORI1")
            return f"(Or.{'inl' if rr == 'ORI1' else 'inr'} {v(refs[0])})"
        if r == "IMPE":
            return f"({v(refs[0])} {v(refs[1])})"
        if r == "NEGE":
            return f"({v(refs[1])} {v(refs[0])})"
        if r == "BOTE":
            if L[refs[0]]["f"] == "F":
                return f"(False.elim {v(refs[0])})"
            # state-env ND decoding of Lean's `n.elim` on n : ¬A (Not.elim : ¬a → a → b): valid in Lean, not ND's BOTE
            return f"(Not.elim {v(refs[0])})"
        if r == "DN":
            return f"(Classical.byContradiction (fun hh => {v(refs[0])} hh))"
        if r in ("IMPI", "NEGI"):
            return box(refs[0], refs[1])
        if r == "ORE":
            j, s1, e1, s2, e2 = refs
            return f"(Or.elim {v(j)} {box(s1, e1)} {box(s2, e2)})"
        raise ValueError("rule " + r)

    def block(ctx, upto=None):
        out = []
        for k in P.order:
            x = L[k]
            if x["ctx"] == ctx and x["rule"] != "AS":
                out.append(f"have n{k} : {lf(x['f'])} := {term(k)}")
            if upto is not None and k == upto:
                break
        return out

    def box(s, e):
        cs = L[s]["ctx"]
        inner = []
        started = False
        for k in P.order:
            if k == s:
                started = True
                continue
            if not started:
                continue
            x = L[k]
            if x["ctx"][: len(cs)] != cs:
                break
            if x["ctx"] == cs and x["rule"] != "AS":
                inner.append(f"have n{k} : {lf(x['f'])} := {term(k)}")
        return f"(fun (n{s} : {lf(L[s]['f'])}) => by {' ; '.join(inner + [f'exact n{e}'])})"

    top = block(())
    return " ; ".join(top + [f"exact n{P.last}"])


def _run(srcs):
    lines = ["set_option linter.unusedVariables false", "set_option maxRecDepth 10000"]
    first = len(lines) + 1
    for k, (st, body) in enumerate(srcs):
        lines.append(st.replace("{NAME}", f"t{k}") + " " + body)
        lines.append(f"#print axioms t{k}")
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False, dir="/tmp", prefix="rvps_") as fh:
        fh.write("\n".join(lines) + "\n")
        path = fh.name
    try:
        p = subprocess.run([LEAN, "-DmaxErrors=100000000", path], capture_output=True, text=True, timeout=3600)
        out = p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        os.unlink(path)
        return None
    os.unlink(path)
    base = re.escape(os.path.basename(path))
    err = set()
    for m in re.finditer(base + r":(\d+):\d+: error", out):
        err.add(int(m.group(1)))
    ax = {}
    for m in re.finditer(r"'t(\d+)' depends on axioms: \[([^\]]*)\]", out):
        ax[int(m.group(1))] = {a.strip() for a in m.group(2).split(",") if a.strip()}
    for m in re.finditer(r"'t(\d+)' does not depend on any axioms", out):
        ax[int(m.group(1))] = set()
    res = []
    for k in range(len(srcs)):
        ln = first + 2 * k
        if ln in err:
            res.append((False, "error"))
        elif k not in ax:
            res.append((False, "no axioms line"))
        elif not ax[k] <= OK_AX:
            res.append((False, "axioms " + ",".join(sorted(ax[k]))))
        elif ln + 1 in err:
            res.append((False, "error on #print"))
        else:
            res.append((True, "ok"))
    return res


def _rec(srcs):
    if not srcs:
        return []
    r = _run(srcs)
    if r is not None:
        return r
    if len(srcs) == 1:
        return [(False, "timeout")]
    h = len(srcs) // 2
    return _rec(srcs[:h]) + _rec(srcs[h:])


def check(items, chunk=300, progress=None):
    srcs = [(statement(p, c, "{NAME}"), body) for (p, c, body) in items]
    out = []
    for i in range(0, len(srcs), chunk):
        out += _rec(srcs[i:i + chunk])
        if progress:
            print(f"  {progress}: {min(i + chunk, len(srcs))}/{len(srcs)}", flush=True)
    return out
