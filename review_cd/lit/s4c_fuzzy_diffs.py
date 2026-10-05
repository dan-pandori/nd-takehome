"""Token-level diffs for every fuzzy (non-exact, non-alnum) fragment match among V rows, so that markup-only
differences (Greek letters, \\leq, \\times, \\sim ...) can be told apart from wording changes. Writes s4c_fuzzy_diffs.txt."""
import difflib
import json
import re

import s4_reverify as M
from common import OUT

ledger = json.load(open(f"{OUT}/s2_claims.json"))
V = [r for r in ledger if r["cls"] == "V"]
srcs = {}
out = []
# tokens that are pure math-markup renderings
MARKUP = set("""alpha beta gamma delta epsilon varepsilon theta vartheta lambda mu nu pi rho sigma tau phi varphi chi psi
omega gamma delta theta lambda xi top leq geq neq sim approx times cdot prime ldots dots infty mathcal mathbb mathtt
mathsf textsc displaystyle frac sum log exp left right operatorname tfrac dfrac lvert rvert mid in to rightarrow
leftarrow propto equiv hat widehat tilde bar ell partial nabla int prod circ odot star ast""".split())
n_rows = 0
summary = []
for r in V:
    files = M.find_source(r["pid"])
    if not files:
        continue
    for f in M.fragments(r["claim"]):
        best = None
        for fn in files:
            if fn not in srcs:
                srcs[fn] = M.Source(fn)
            got = srcs[fn].search(f)
            if got[0] in ("exact", "exact(dehyph)", "alnum"):
                best = None
                break
            if got[0].startswith("fuzzy"):
                sc = float(got[0][5:])
                if best is None or sc > best[0]:
                    best = (sc, got[2], fn)
        if best is None:
            continue
        q = re.findall(r"[a-z0-9]+", M.norm(f))
        w = best[1].split()
        ops = difflib.SequenceMatcher(None, q, w, autojunk=False).get_opcodes()
        diffs = []
        for tag, i1, i2, j1, j2 in ops:
            if tag == "equal":
                continue
            diffs.append((tag, " ".join(q[i1:i2]), " ".join(w[j1:j2])))
        # trailing window extension (window longer than quote) is not a difference
        while diffs and diffs[-1][0] == "insert" and ops[-1][0] == "insert":
            diffs.pop()
            break
        # a difference is 'markup-only' if every token involved on the source side is markup / a lone letter or digit,
        # and the quote side holds only short symbol-derived tokens
        def markup_only(d):
            src_t = d[2].split()
            q_t = d[1].split()
            return all(t in MARKUP or len(t) <= 2 for t in src_t) and all(len(t) <= 2 or t in MARKUP for t in q_t)
        kind = "markup-only" if all(markup_only(d) for d in diffs) else "WORDING?"
        n_rows += 1
        summary.append(kind)
        out.append(f"{r['reader']} #{r['n']} {r['pid'][:30]} score={best[0]:.2f} [{kind}] {diffs}")
out.insert(0, f"fuzzy fragment matches: {len(summary)}; markup-only: {summary.count('markup-only')}; "
              f"flagged for wording: {summary.count('WORDING?')}")
open(f"{OUT}/s4c_fuzzy_diffs.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
