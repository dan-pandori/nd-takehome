"""Ingredient scan for problem-A items (reviewer aid, not a judge): where a general exactness argument could be.
E1 = a general mod-9 expansion (3m+1 / 3a+1 style substitution), LINK = c = S^2 - 3ab style identity,
SIND = '3 | S_k for all k' style induction, PLUG = representative plug-in of residues into a quotient by 3."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
key = json.load(open(os.path.join(HERE, "hand", "key.json")))
P = {"E1": r"=\s*3\s*[a-z]\s*\+\s*[12]\b|\(3[a-z]\s*\+\s*[12]\)", "LINK": r"S(_\{?k\}?)?(\^2|²)\s*[-−]\s*3|\(m\s*\+\s*n\)(\^2|²)\s*[-−]\s*3|\(a\s*\+\s*b\)(\^2|²)\s*[-−]\s*3|\(N\s*\+\s*D\)(\^2|²)\s*[-−]\s*3",
     "SIND": r"divisible by\s*3 for all|always divisible by\s*3|S_?\{?[kn]\}? (is|are) (always )?divisible by\s*3",
     "PLUG": r"\(1\s*[-−+]\s*2\s*\+\s*4\)\s*/\s*3|1\s*\+\s*4\s*[-−]\s*2\s*=\s*3"}
rows = []
for i, k in key.items():
    if k["pid"] != "aime2025_28":
        continue
    t = open(os.path.join(HERE, "hand", "items", f"{i}.md")).read().split("## Response", 1)[1]
    hit = {n: len(re.findall(p, t)) for n, p in P.items()}
    rows.append((k["model"], k["draw"], i, hit))
for r in sorted(rows):
    print(r[0], r[1], r[2], r[3])
