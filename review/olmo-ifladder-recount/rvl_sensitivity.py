"""Sensitivity of my cell outcomes to the reading rule (run olmo-ifladder).

Label maps: final (majority of three, rvl_hand.labels); first read only; pessimistic (an item is genuine only if
every read of it says genuine); and strict (every strict success genuine, no gate). For each map the draw-order walk is
re-run; a walk that reaches an item with no label stops (outcome "unsettled" for that map). Reported per cell type:
elicited / not elicited / unsettled, and the prompts whose outcome differs from the final map.
Also: reader agreement on items with >= 2 reads, by cell, and the checker-disagreement flags.
Writes out/sensitivity.{txt,json}.
"""
import collections
import json

from rvl_core import OUT, Tee, dump
from rvl_hand import CELLS, cells_of, gkey, labels, mech_labels, reads, walk

P = Tee("sensitivity.txt")
lab = labels()
mech = mech_labels()
rd = reads()
grp = collections.defaultdict(list)
for k, rs in rd.items():
    grp[gkey(k)] += rs


def mk(rule):
    out = {}
    for g, rs in grp.items():
        labs = [r[1] for r in rs]
        if rule == "first":
            L = labs[0]
        elif rule == "pessimistic":
            L = "genuine" if all(x == "genuine" for x in labs) else "gamed"
        else:
            L = lab[g]["label"]
        out[g] = {"label": L, "how": rule, "reads": []}
    return out


maps = {"final": mk("final"), "first": mk("first"), "pessimistic": mk("pessimistic")}
res = {}
base = {}
for name, m in maps.items():
    cnt = collections.Counter()
    diff = []
    for c, pid in cells_of():
        w = walk(c, pid, m, mech)
        o = w["outcome"] or "unsettled"
        cnt[(c, o)] += 1
        if name == "final":
            base[(c, pid)] = o
        elif o != base[(c, pid)]:
            diff.append(f"{c}|{pid}: {base[(c, pid)]} -> {o}")
    res[name] = {"counts": {f"{c}|{o}": v for (c, o), v in cnt.items()}, "diff": diff}
    P(f"[{name}] " + "; ".join(f"{c}: E {cnt[(c, 'elicited')]} N {cnt[(c, 'not elicited')]} U {cnt[(c, 'unsettled')]}"
                                 for c in CELLS))
    if diff:
        P(f"    differs from final: {diff}")
# strict map: every strict success genuine
SETS = json.load(open(OUT / "sets.json"))["cells"]
sd = []
for c, pid in cells_of():
    o = "elicited" if SETS[c][pid]["strict"] >= 2 else "not elicited"
    if o != base[(c, pid)]:
        sd.append(f"{c}|{pid}: {base[(c, pid)]} -> {o}")
P(f"[strict, no gate] differs from final on {len(sd)} cells: {sd}")
res["strict_diff"] = sd
# agreement
ag = collections.Counter()
for g, rs in grp.items():
    if len(rs) >= 2:
        c = "SRC" if g[0] == "SRC" else {"g2": "R2/S2", "g3": "R3/S3", "g4": "R4/S4", "gp": "LM/LC"}[g[1]]
        ag[(c, rs[0][1] == rs[1][1])] += 1
P("first-vs-second read agreement by prompt group: " +
  "; ".join(f"{c}: {ag[(c, True)]}/{ag[(c, True)] + ag[(c, False)]}" for c in sorted({k[0] for k in ag})))
res["agreement"] = {f"{k[0]}|{k[1]}": v for k, v in ag.items()}
dump(res, "sensitivity.json")
