"""Reviewer summary per set: shares (uses / working / primary / curried / sub-types / v0) and by length / depth."""
import gzip
import json
import sys
from collections import Counter, defaultdict

STRATS = ["direct", "and_intro", "cond_proof", "or_intro", "cases", "disj_syll", "neg_intro", "mod_tollens",
          "ex_falso", "contradiction", "dne", "lem", "lemma_reuse"]


def run(name):
    R = [r for r in (json.loads(l) for l in gzip.open(f"out/labels_{name}.jsonl.gz", "rt")) if "uses" in r]
    n = len(R)
    s = {"n": n}
    s["uses"] = {k: sum(k in r["uses"] for r in R) for k in STRATS}
    s["work"] = {k: sum(k in r["work"] for r in R) for k in ("cond_proof", "cases", "neg_intro", "contradiction")}
    s["primary"] = dict(Counter(r["primary"] for r in R))
    s["curried"] = dict(Counter(r["curried"] for r in R))
    s["sub"] = dict(Counter(x for r in R for x in r["sub"]))
    s["v0"] = dict(Counter(x for r in R for x in r["v0"]))
    s["boxfree"] = sum(r["boxfree"] for r in R)
    s["dn_any"] = sum(("contradiction" in r["uses"]) or ("dne" in r["uses"]) for r in R)
    s["negi_any"] = sum(("neg_intro" in r["uses"]) or any(x.startswith("mod_tollens.") for x in r["sub"]) or
                        ("contradiction" in r["uses"] and any(x == "contradiction.sigma" for x in r["sub"])) for r in R)
    bylen = defaultdict(Counter)
    bydep = defaultdict(Counter)
    for r in R:
        L = r["n_kept"]
        lb = str(L) if L <= 12 else "13+"
        d = str(min(r["depth"], 4)) if r["depth"] < 4 else "4+"
        for key, tab in ((lb, bylen), (d, bydep)):
            tab[key]["n"] += 1
            for k in r["uses"]:
                tab[key][k] += 1
            tab[key]["primary:" + r["primary"]] += 1
    s["by_len"] = {k: dict(v) for k, v in bylen.items()}
    s["by_depth"] = {k: dict(v) for k, v in bydep.items()}
    s["mean_lines"] = sum(r["n_kept"] for r in R) / n
    return s


if __name__ == "__main__":
    allr = {}
    for nm in sys.argv[1:]:
        allr[nm] = run(nm)
    json.dump(allr, open("out/summary_all.json", "w"), indent=1, sort_keys=True)
    k = allr.get("k12")
    if k:
        n = k["n"]
        print("K12 DN anywhere", k["dn_any"], f"{100 * k['dn_any'] / n:.2f}%")
        neg = sum(1 for l in gzip.open("out/labels_k12.jsonl.gz", "rt"))
        print("K12 sub-type shares (proof level):")
        for x, v in sorted(k["sub"].items()):
            print(f"   {x:40s} {v:7d} {100 * v / n:6.2f}%")
