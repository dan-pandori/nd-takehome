"""DN steps that cite (after R) an ASSUMPTION whose ¬¬G is not a subformula of the theorem (a double negation the proof
introduced itself as a box hypothesis), by the kind of box: ∨E case, →I, ¬I. In pruned proofs.
usage: python3 dn_on_hyp.py <name> <file> <proof_field>"""
import gzip
import json
import sys
from collections import Counter
from nd import parse_prompt, Proof
from cls import A

name, fn, field = sys.argv[1], sys.argv[2], sys.argv[3]
op = gzip.open(fn, "rt") if fn.endswith(".gz") else open(fn)
recs = Counter()
kinds = Counter()
ex = {}
n = 0
for i, line in enumerate(op):
    r = json.loads(line)
    pr = r.get(field)
    if not pr or " : DN " not in pr:
        continue
    n += 1
    p, c = parse_prompt(r["prompt"])
    P = Proof(p, c, pr)
    a = A(P)
    box_kind = {}
    for k in a.keep:
        x = P.L[k]
        if x["rule"] in ("IMPI", "NEGI"):
            box_kind[x["refs"][0]] = x["rule"]
        elif x["rule"] == "ORE":
            j, s1, e1, s2, e2 = x["refs"]
            jr = P.L[a.o(j)]["rule"]
            box_kind[s1] = box_kind[s2] = "ORE_case(j:" + ("PR" if jr == "PR" else "AS" if jr == "AS" else "ORI" if jr in ("ORI1", "ORI2") else "derived") + ")"
    hit = set()
    for k in a.keep:
        x = P.L[k]
        if x["rule"] != "DN":
            continue
        cc = a.o(x["refs"][0])
        if P.L[cc]["rule"] != "AS":
            continue
        if ("~", ("~", x["f"])) in a.sub:
            continue
        kd = box_kind.get(cc, "?")
        kinds[kd] += 1
        hit.add(kd)
    for kd in hit:
        recs[kd] += 1
        ex.setdefault(kd, i)
    if hit:
        recs["ANY"] += 1
out = {"set": name, "records_with_DN": n, "records_by_box_kind": dict(recs), "instances_by_box_kind": dict(kinds), "example_index": ex}
json.dump(out, open(f"out/dn_on_hyp_{name}.json", "w"), indent=1)
print(json.dumps(out))
