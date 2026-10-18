"""Term size: (1) per-rule formula on the pruned proof, compared per record with the executor's `ts`;
(2) the formula validated against lean_check.py's elaborated-term node count on the reviewer's own Lean renderings."""
import gzip
import json
import random
import sys
from collections import Counter
from nd import parse_prompt, Proof
from cls import A

W = {"IMPE": 1, "NEGE": 1, "ANDE1": 1, "ANDE2": 1, "ANDI": 1, "ORI1": 1, "ORI2": 1, "BOTE": 1, "IMPI": 1, "NEGI": 1,
     "ORE": 3, "DN": 3, "R": 0, "PR": 0, "AS": 0}


def ts(P, pruned=True):
    a = A(P, pruned=pruned)
    return sum(W[P.L[k]["rule"]] for k in a.keep)


def compare(name, fn, field):
    op = gzip.open(fn, "rt") if fn.endswith(".gz") else open(fn)
    T = [json.loads(l) for l in gzip.open(f"../artifacts/ps/labels/{name}.jsonl.gz", "rt")]
    d = Counter()
    tot = []
    for r, t in zip(map(json.loads, op), T):
        if not r.get(field):
            continue
        p, c = parse_prompt(r["prompt"])
        P = Proof(p, c, r[field])
        x = ts(P)
        tot.append(x)
        d["same" if x == t.get("ts") else "diff"] += 1
    tot.sort()
    print(name, dict(d), "median", tot[len(tot) // 2], "mean %.2f" % (sum(tot) / len(tot)), "max", tot[-1])
    return tot


if __name__ == "__main__":
    if sys.argv[1] == "compare":
        res = {}
        for name, fn, field in (("k12", "../data/ps/in/train_k12.jsonl.gz", "proof"),
                                ("cap6", "../data/ps/in/train_depth3_f0_a1.jsonl.gz", "proof"),
                                ("k12ko", "../data/ps/in/train_k12ko.jsonl.gz", "proof"),
                                ("charles_base", "../data/ps/in/charles/charles_base_full.jsonl", "reference_proof"),
                                ("k12_min990", "../data/ps/search/k12_min990.checked.jsonl", "proof"),
                                ("tb_schema_search", "../data/ps/search/tb_schema.checked.jsonl", "proof")):
            t = compare(name, fn, field)
            res[name] = {"n": len(t), "median": t[len(t) // 2], "mean": sum(t) / len(t)}
        json.dump(res, open("out/termsize_formula.json", "w"), indent=1)
    else:
        sys.path.insert(0, "..")
        import lean_check
        from lean import render, statement
        rng = random.Random(5)
        rows = []
        for fn, field, n in (("../data/ps/in/train_k12.jsonl.gz", "proof", 250),
                             ("../data/ps/in/charles/charles_base_full.jsonl", "reference_proof", 50),
                             ("../data/ps/search/tb_schema.checked.jsonl", "proof", 50)):
            op = gzip.open(fn, "rt") if fn.endswith(".gz") else open(fn)
            allr = [json.loads(l) for l in op]
            rows += [(r["prompt"], r[field]) for r in rng.sample(allr, n)]
        srcs, want = [], []
        for prompt, proof in rows:
            p, c = parse_prompt(prompt)
            P = Proof(p, c, proof)
            srcs.append(statement(p, c, "t") + " " + render(p, c, proof))
            want.append(ts(P))
        res, wall, cpu = lean_check.check(srcs, workers=1)
        agree = sum(1 for r, w in zip(res, want) if r["ok"] and r["size"] == w)
        bad = [(r, w) for r, w in zip(res, want) if not (r["ok"] and r["size"] == w)]
        print("lean_check on reviewer renderings:", len(srcs), "ok", sum(r["ok"] for r in res), "size == formula", agree,
              "wall %.0f s" % wall)
        for r, w in bad[:10]:
            print("  mismatch", r, "formula", w)
        json.dump({"n": len(srcs), "ok": sum(r["ok"] for r in res), "agree": agree}, open("out/termsize_leancheck.json", "w"))
