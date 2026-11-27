"""Agreement of my hand-gate labels with (a) the executor's (olmo_lowrank/handcheck.csv final labels + its screen
hand/screen.csv + identity inheritance on (pid, sha1 of the whitespace-collapsed answer)[:16], re-implemented here) on
every deciding draw of my scope, and (b) olmo-ifcurve's final labels on the B_s2300 draws (olmo_ifcurve/handcheck.csv).
-> out/agree.json, out/agree.txt"""
import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict

import rvr_hand as H
from rvr_core import ART, OUT, RAW, Tee


def akey(a):
    return hashlib.sha1(re.sub(r"\s+", " ", a or "").strip().encode()).hexdigest()[:16]


def main():
    T = Tee("agree.txt")
    key, reads, scr, conf = H.load()
    mine = {}
    for it, v in key.items():
        lab, how = H.group_label(it, key, reads, scr, conf)
        for d in v["draws"]:
            mine[tuple(d)] = (lab, how, it)
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
            inh[(k[1], akey(A[k]))].add("gamed")
    def ex_of(k):
        if k in ex_scr:
            return "gamed", "screen"
        if k in ex_lab:
            return ex_lab[k], "read"
        s = inh.get((k[1], akey(A[k])))
        if s and len(s) == 1:
            return next(iter(s)), "inherited"
        return None, "none" if not s else "conflict"
    res = {"per_job": {}, "disagree": []}
    tot = Counter()
    for job in ["T1", "T4", "T16", "T64", "T256", "F448", "C16", "B_s2300"]:
        c = Counter()
        for k, (lab, how, it) in mine.items():
            if k[0] != job:
                continue
            el, eh = ex_of(k)
            if el is None:
                c["executor_unlabelled"] += 1
                continue
            c["n"] += 1
            c["agree"] += el == lab
            c[f"mine_{lab}_exec_{el}"] += 1
            if el != lab:
                res["disagree"].append({"job": job, "pid": k[1], "chunk": k[2], "i": k[3], "mine": lab, "mine_how": how,
                                        "item": it, "exec": el, "exec_how": eh})
        res["per_job"][job] = dict(c)
        tot.update(c)
        T(f"{job:8s} n {c['n']:4d} agree {c['agree']:4d} ({c['agree'] / max(1, c['n']):.3f}) | mine genuine/exec gamed "
          f"{c['mine_genuine_exec_gamed']:3d}  mine gamed/exec genuine {c['mine_gamed_exec_genuine']:3d}  exec unlabelled {c['executor_unlabelled']}")
    res["total"] = dict(tot)
    T(f"TOTAL n {tot['n']} agree {tot['agree']} ({tot['agree'] / tot['n']:.3f}); mine genuine/exec gamed {tot['mine_genuine_exec_gamed']}, "
      f"mine gamed/exec genuine {tot['mine_gamed_exec_genuine']}")
    T("disagreements by prompt:", Counter(d["pid"] for d in res["disagree"]).most_common(15))
    T("disagreements by my label source:", Counter(d["mine_how"] for d in res["disagree"]))
    # (b) olmo-ifcurve's final labels on B_s2300 draws
    ic = {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])): r["final_label"]
          for r in csv.DictReader(open(RAW / "olmo_ifcurve" / "handcheck.csv")) if r.get("final_label") in ("genuine", "gamed")}
    jobs_ic = Counter(k[0] for k in ic)
    c = Counter()
    for k, (lab, how, it) in mine.items():
        if k[0] != "B_s2300":
            continue
        o = ic.get(("B_s2300", k[1], k[2], k[3]))
        if o is None:
            continue
        c["n"] += 1
        c["agree"] += o == lab
        c[f"mine_{lab}_ifcurve_{o}"] += 1
    res["ifcurve_B_s2300"] = dict(c)
    T(f"olmo-ifcurve final labels on B_s2300 draws (jobs in its table: {dict(jobs_ic)}): {dict(c)}")
    json.dump(res, open(OUT / "agree.json", "w"), indent=1)


if __name__ == "__main__":
    main()
