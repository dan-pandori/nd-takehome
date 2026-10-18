"""Aggregate reviewer labels of one set: shares of uses / working / primary / curried / sub-types / v0."""
import gzip
import json
import sys
from collections import Counter

STRATS = ["direct", "and_intro", "cond_proof", "or_intro", "cases", "disj_syll", "neg_intro", "mod_tollens",
          "ex_falso", "contradiction", "dne", "lem", "lemma_reuse"]


def load(name):
    return [json.loads(l) for l in gzip.open(f"out/labels_{name}.jsonl.gz", "rt")]


def agg(name, rows=None, quiet=False):
    rows = rows if rows is not None else load(name)
    R = [r for r in rows if "uses" in r]
    n = len(R)
    skip = Counter(r.get("skip") for r in rows if "uses" not in r)
    res = {"set": name, "n_rows": len(rows), "n": n, "skip": dict(skip),
           "ndok": sum(r["ndok"] for r in R)}
    uses = Counter(s for r in R for s in r["uses"])
    work = Counter(s for r in R for s in r["work"])
    prim = Counter(r["primary"] for r in R)
    cur = Counter(r["curried"] for r in R)
    sub = Counter(s for r in R for s in r["sub"])
    v0 = Counter(s for r in R for s in r["v0"])
    res.update(uses=dict(uses), work=dict(work), primary=dict(prim), curried=dict(cur), sub=dict(sub), v0=dict(v0),
               boxfree=sum(r["boxfree"] for r in R), sigma=sum(r["sigma"] for r in R),
               sigma_strict=sum(r["sigma_strict"] for r in R), sigma_plus=sum(r["sigma_plus"] for r in R),
               w_sigma=sum(r["w_sigma"] for r in R),
               dead_only=sum(1 for r in R if set(r["w_uses"]) - set(r["uses"])),
               dead_lines=sum(1 for r in R if r["n_kept"] < r["n_lines"]))
    if not quiet:
        pc = lambda c: f"{c:7d} {100.0 * c / n:6.2f}%"  # noqa: E731
        print(f"== {name}: rows {len(rows)} classified {n} skip {dict(skip)} ndcheck-ok {res['ndok']}")
        print("strategy        uses            working         primary         curried        v0")
        for s in STRATS:
            print(f"{s:14s} {pc(uses[s])}  {pc(work[s]) if s in ('cond_proof','cases','neg_intro','contradiction') else ' ' * 15}"
                  f" {pc(prim[s])} {pc(cur[s])}  {pc(v0[s]) if s in v0 else ''}")
        for k in sorted(set(prim) | set(cur)):
            if k not in STRATS:
                print(f"{k:14s} {'':15s}  {'':15s} {pc(prim[k])} {pc(cur[k])}")
        print("boxfree", pc(res["boxfree"]), "| v0 vacuous discharge", pc(v0["vacuous"]),
              "| sigma(after R, pruned)", res["sigma"], "strict", res["sigma_strict"], "plus", res["sigma_plus"],
              "| sigma written", res["w_sigma"])
        print("records with dead lines", pc(res["dead_lines"]), "| strategy only in dead lines", pc(res["dead_only"]))
    return res


if __name__ == "__main__":
    for nm in sys.argv[1:]:
        r = agg(nm)
        json.dump(r, open(f"out/agg_{nm}.json", "w"), indent=1, sort_keys=True)
