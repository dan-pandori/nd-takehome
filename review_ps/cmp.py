"""Per-record comparison of reviewer labels with the executor's artifacts/ps/labels/<set>.jsonl.gz."""
import gzip
import json
import sys
from collections import Counter

STRATS = ["direct", "and_intro", "cond_proof", "or_intro", "cases", "disj_syll", "neg_intro", "mod_tollens",
          "ex_falso", "contradiction", "dne", "lem", "lemma_reuse"]
WORKSUB = {"cond_proof": "cond_proof.working", "cases": "cases.genuine", "neg_intro": "neg_intro.working",
           "contradiction": "contradiction.working"}


def main(mine, theirs, show=3):
    M = [json.loads(l) for l in gzip.open(f"out/labels_{mine}.jsonl.gz", "rt")]
    T = [json.loads(l) for l in gzip.open(f"../artifacts/ps/labels/{theirs}.jsonl.gz", "rt")]
    print(f"== {mine} vs executor {theirs}: mine {len(M)} rows, theirs {len(T)} rows")
    Ti = {t["i"]: t for t in T}
    diff = Counter()
    ex = {}
    n = 0
    for m in M:
        t = Ti.get(m["i"])
        if t is None or "uses" not in m or "u" not in t:
            diff["missing/skip " + str(("uses" in m, t is not None and "u" in t))] += 1
            continue
        n += 1
        mu, tu = set(m["uses"]), set(t["u"])
        for s in STRATS:
            if (s in mu) != (s in tu):
                k = f"uses {s} mine={s in mu}"
                diff[k] += 1
                ex.setdefault(k, []).append(m["i"])
        tw = set(t.get("sub", []))
        for s, w in WORKSUB.items():
            a, b = s in m["work"], w in tw
            if a != b:
                k = f"work {s} mine={a}"
                diff[k] += 1
                ex.setdefault(k, []).append(m["i"])
        if m["primary"] != t["pri"]:
            k = f"primary {m['primary']}->{t['pri']}"
            diff[k] += 1
            ex.setdefault(k, []).append(m["i"])
        if m["curried"] != t["pric"]:
            k = f"curried {m['curried']}->{t['pric']}"
            diff[k] += 1
            ex.setdefault(k, []).append(m["i"])
        if m["boxfree"] != t["box_free"]:
            diff["boxfree"] += 1
        # sub-types (theirs use 'strategy.sub'; compare the shared vocabulary)
        ROUTES = {"immediate", "mt", "or_weaken", "and_elim", "and_intro", "imp_hyp", "cases", "self", "mixed",
                  "vacuous", "other"}
        ms = set()
        for s in m["sub"]:
            a, b = s.split(".", 1)
            if a == "contradiction" and b in ROUTES:
                ms.add("contradiction.route_" + b)
                if b == "vacuous":
                    ms.add(s)  # kind 'vacuous' has the same name
            elif b in ("vac", "v0_vacuous", "v0_ds", "dn_lem", "sigma"):
                continue
            else:
                ms.add(s)
        for s in tw | ms:
            if (s in ms) != (s in tw):
                k = f"sub {s} mine={s in ms}"
                diff[k] += 1
                ex.setdefault(k, []).append(m["i"])
    print("compared", n)
    for k, v in sorted(diff.items(), key=lambda kv: -kv[1]):
        print(f"  {v:7d}  {k}   e.g. {ex.get(k, [])[:show]}")
    if not diff:
        print("  identical on uses / working / primary / curried / boxfree / shared sub-types")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
