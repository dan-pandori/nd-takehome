"""Reviewer's own textbook72 renaming-class keys (never prints a textbook72 theorem).
key_po: premise-order-invariant, min over the 24 bijections of {P,Q,R,S} of (sorted premise multiset, conclusion).
key_cur: same after uncurrying the conclusion (Γ ⊢ A → B  ~  Γ, A ⊢ B), repeated; key_curneg also unfolds ¬A as A → ⊥.
"""
import itertools
import json
from nd import show, parse_prompt

AT = ["P", "Q", "R", "S"]
PERMS = [dict(zip(AT, p)) for p in itertools.permutations(AT)]


def ren(f, m):
    if isinstance(f, str):
        return m.get(f, f)
    return (f[0],) + tuple(ren(g, m) for g in f[1:])


def key_po(prem, concl):
    best = None
    for m in PERMS:
        k = (tuple(sorted(show(ren(p, m)) for p in prem)), show(ren(concl, m)))
        if best is None or k < best:
            best = k
    return best


def key_set(prem, concl):
    # premises as a SET (duplicates collapse) -- the weakest equality used here
    best = None
    for m in PERMS:
        k = (tuple(sorted(set(show(ren(p, m)) for p in prem))), show(ren(concl, m)))
        if best is None or k < best:
            best = k
    return best


def uncurry(prem, concl, neg=False):
    prem = list(prem)
    while True:
        if isinstance(concl, tuple) and concl[0] == ">":
            prem.append(concl[1])
            concl = concl[2]
        elif neg and isinstance(concl, tuple) and concl[0] == "~":
            prem.append(concl[1])
            concl = "F"
        else:
            return prem, concl


def keys(prem, concl):
    return {"po": key_po(prem, concl), "set": key_set(prem, concl),
            "cur": key_set(*uncurry(prem, concl)), "curneg": key_set(*uncurry(prem, concl, neg=True))}


class TB72:
    def __init__(self, path="../data/bs/textbook72.jsonl"):
        self.K = {"po": set(), "set": set(), "cur": set(), "curneg": set()}
        for r in map(json.loads, open(path)):
            p, c = parse_prompt(r["prompt"])
            for k, v in keys(p, c).items():
                self.K[k].add(v)

    def hits(self, prem, concl):
        return {k for k, v in keys(prem, concl).items() if v in self.K[k]}
