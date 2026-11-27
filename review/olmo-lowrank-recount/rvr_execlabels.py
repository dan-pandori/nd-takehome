"""My cell walk and G (rvr_readings.py) with the EXECUTOR's labels (rvr_agree.py's re-implementation of its label
lookup) instead of mine, on the same draws: isolates the label standard from the arithmetic. -> out/readings_execlabels.json"""
import json

import numpy as np

import rvr_agree as AG
import rvr_readings as RD
from rvr_core import ARMS, OUT, Tee, pids


def main():
    T = Tee("readings_execlabels.txt")
    import csv, gzip, hashlib, re
    from collections import defaultdict
    from rvr_core import ART, RAW
    with gzip.open(OUT / "answers_scope.json.gz", "rt") as f:
        A = {tuple(json.loads(k)): v for k, v in json.load(f).items()}
    ex_items = list(csv.DictReader(open(RAW / "olmo_lowrank" / "handcheck.csv")))
    ex_scr = {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])) for r in csv.DictReader(open(ART / "hand" / "screen.csv"))}
    ex_lab, inh = {}, defaultdict(set)
    for r in ex_items:
        k = (r["job"], r["pid"], int(r["chunk"]), int(r["i"]))
        if r["final_label"] in ("genuine", "gamed"):
            ex_lab[k] = r["final_label"]
            inh[(r["pid"], r["ans_key"])].add(r["final_label"])
    for k in ex_scr:
        if k in A:
            inh[(k[1], AG.akey(A[k]))].add("gamed")
    lab = {}
    for k in A:
        if k in ex_scr:
            lab[k] = "gamed"
        elif k in ex_lab:
            lab[k] = ex_lab[k]
        else:
            s = inh.get((k[1], AG.akey(A[k])))
            lab[k] = next(iter(s)) if s and len(s) == 1 else None
    reach = pids("pids_reach.txt")
    Rv = {j: RD.cell_est(j, reach, RD.rows(j), lab)[0] for j in ARMS + ["B_s2300"]}
    G = {j: RD.boot(Rv[j], Rv["dpo"], Rv["B_s2300"]) for j in ARMS if j != "dpo"}
    out = {"rate": {j: round(float(v.mean()), 5) for j, v in Rv.items()}, "G": G, "readings": RD.readings(G)}
    json.dump(out, open(OUT / "readings_execlabels.json", "w"), indent=1)
    T("[R, executor labels, my walk] rates " + " ".join(f"{j} {v:.4f}" for j, v in out["rate"].items()))
    T("   G " + "  ".join(f"{j} {g:.3f} [{lo:.3f}, {hi:.3f}]" for j, (g, lo, hi) in G.items()))
    T("   readings " + json.dumps({k: (x["holds"], x["firm"]) if isinstance(x, dict) else x for k, x in out["readings"].items()}))


if __name__ == "__main__":
    main()
