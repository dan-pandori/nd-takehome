"""My recount of Part 2 (pre-registration "G and readings"), from my re-grade and my hand gate only.
R: per reach cell (job x prompt) est = (genuine + unlabelled strict x genuine share of labelled) / draws, labels on the
first min(strict, 8) strict successes in draw order; r = mean over the 48 reach prompts. dpo = the fresh dpo arm;
s2300 = B_s2300 (32 draws). A: mean over the 218 arm-A prompts of the per-prompt strict pass@1 (all of an arm's draws);
dpo = fresh dpo pooled with F_dpo_ifb on the 176 non-reach prompts (fresh only on the 42 IFBench reach prompts);
s2300 = F_s2300_ifb on the 176, B_s2300 on the 42. G = (r_arm - r_dpo) / (r_s2300 - r_dpo). Paired prompt bootstrap,
10,000 replicates (my seed), percentile 95 %. Label variants for sensitivity: main (policy), first-read only,
no screen (readers' labels for screened groups), rule-6 strict, low-confidence proposals accepted.
-> out/readings.json, out/readings.txt, out/cells_mine.csv
"""
import csv
import gzip
import json
from collections import Counter, defaultdict

import numpy as np

import rvr_hand as H
from rvr_core import ARMS, OUT, Tee, pids

TK = ["T1", "T4", "T16", "T64", "T256"]
KOF = {"T1": 1, "T4": 4, "T16": 16, "T64": 64, "T256": 256}


def rows(job):
    return [json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt")]


def labels_variant(variant):
    key, reads, scr, conf = H.load()
    out = {}
    for it, v in key.items():
        g = v["group"]
        if variant == "first_read":
            lab = "gamed" if g in scr else reads[it][0][2]
        elif variant == "no_screen":
            lab, _ = H.group_label(it, key, reads, {}, conf)
        elif variant == "low_accepted":
            c2 = {k: dict(x, accepted=True) for k, x in conf.items()}
            lab, _ = H.group_label(it, key, reads, scr, c2)
        else:
            lab, _ = H.group_label(it, key, reads, scr, conf)
            if variant == "rule6_strict" and conf.get(it, {}).get("accepted") and "6" in str(conf[it].get("rules", "")).split(";"):
                lab = "gamed"
        for d in v["draws"]:
            out[tuple(d)] = lab
    return out


def cell_est(job, reach, R, lab):
    by = defaultdict(list)
    for r in R:
        if r["pid"] in reach:
            by[r["pid"]].append(r)
    est, info = [], {}
    for p in reach:
        xs = sorted(by[p], key=lambda r: (int(r["chunk"]), int(r["i"])))
        s = [r for r in xs if r["strict"]]
        L = [lab.get((job, p, int(r["chunk"]), int(r["i"]))) for r in s[:8]]
        assert all(x in ("genuine", "gamed") for x in L), (job, p, L)
        g, b = L.count("genuine"), L.count("gamed")
        share = g / (g + b) if g + b else 0.0
        e = (g + (len(s) - g - b) * share) / len(xs)
        est.append(e)
        info[p] = (len(xs), len(s), g, b, e)
    return np.array(est), info


def boot(a, d, s, reps=10000, seed=20261127):
    g0 = (a.mean() - d.mean()) / (s.mean() - d.mean())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(reps, len(a)))
    g = (a[idx].mean(1) - d[idx].mean(1)) / (s[idx].mean(1) - d[idx].mean(1))
    return float(g0), float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))


def side(G, arm, thr, op):
    g, lo, hi = G[arm]
    holds = g >= thr if op == ">=" else (g <= thr if op == "<=" else g < thr)
    firm = (lo >= thr or hi < thr) if op in (">=", "<") else (hi <= thr or lo > thr)
    return {"holds": bool(holds), "firm": bool(firm), "G": round(g, 4), "ci": [round(lo, 4), round(hi, 4)]}


def readings(G):
    out = {"low-rank carries it": [side(G, "T16", 0.5, ">="), side(G, "C16", 0.2, "<=")],
           "high-rank": [side(G, "T256", 0.5, "<"), side(G, "F448", 0.75, ">=")],
           "outside the 448 matrices": [side(G, "F448", 0.75, "<")]}
    res = {k: {"holds": all(c["holds"] for c in v), "firm": all(c["firm"] for c in v), "conditions": v} for k, v in out.items()}
    res["k50"] = next((KOF[t] for t in TK if G[t][0] >= 0.5), ">256")
    return res


def main():
    T = Tee("readings.txt")
    reach, armA = pids("pids_reach.txt"), pids("pids_armA.txt")
    others = [p for p in armA if p not in set(reach)]
    RW = {j: rows(j) for j in ARMS + ["B_s2300", "F_s2300_ifb", "F_dpo_ifb"]}
    res = {"variants": {}}
    cells_out = []
    for variant in ("main", "first_read", "no_screen", "rule6_strict", "low_accepted"):
        lab = labels_variant(variant)
        Rv, info = {}, {}
        for j in ARMS + ["B_s2300"]:
            Rv[j], info[j] = cell_est(j, reach, RW[j], lab)
        G = {j: boot(Rv[j], Rv["dpo"], Rv["B_s2300"]) for j in ARMS if j != "dpo"}
        res["variants"][variant] = {"rate": {j: round(float(Rv[j].mean()), 5) for j in Rv}, "G": G, "readings": readings(G)}
        if variant == "main":
            for j in ARMS + ["B_s2300"]:
                for p in reach:
                    n, s, g, b, e = info[j][p]
                    cells_out.append({"job": j, "pid": p, "draws": n, "strict": s, "genuine": g, "gamed": b, "est": round(e, 6)})
            gs = {}
            for j in ARMS + ["B_s2300"]:
                g = sum(info[j][p][2] for p in reach)
                b = sum(info[j][p][3] for p in reach)
                gs[j] = {"strict": sum(info[j][p][1] for p in reach), "labelled": g + b, "genuine": g, "gamed": b,
                         "gamed_share": round(b / (g + b), 4) if g + b else None,
                         "cells_with_genuine": sum(1 for p in reach if info[j][p][2] > 0)}
            res["hand_per_arm"] = gs
    with open(OUT / "cells_mine.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cells_out[0]))
        w.writeheader()
        w.writerows(cells_out)
    # A metric (strict, 218 prompts)
    def pp(jobs_of):
        v = []
        for p in armA:
            xs = [bool(r["strict"]) for j in jobs_of(p) for r in RW[j] if r["pid"] == p]
            v.append(np.mean(xs))
        return np.array(v)
    A = {j: pp(lambda p, j=j: [j]) for j in ARMS}
    A["dpo_pooled"] = pp(lambda p: ["dpo", "F_dpo_ifb"] if p in set(others) else ["dpo"])
    A["s2300"] = pp(lambda p: ["F_s2300_ifb"] if p in set(others) else ["B_s2300"])
    nd = Counter()
    for p in armA:
        for j in (["dpo", "F_dpo_ifb"] if p in set(others) else ["dpo"]):
            nd[j] += sum(1 for r in RW[j] if r["pid"] == p)
    GA = {j: boot(A[j], A["dpo_pooled"], A["s2300"]) for j in ARMS if j != "dpo"}
    GAf = {j: boot(A[j], A["dpo"], A["s2300"]) for j in ARMS if j != "dpo"}
    res["A"] = {"rate": {j: round(float(v.mean()), 5) for j, v in A.items()}, "G": GA, "readings": readings(GA),
                "G_fresh_dpo": GAf, "readings_fresh_dpo": readings(GAf), "dpo_pool_draws": dict(nd)}
    # R_strict (supplementary)
    RS = {j: np.array([np.mean([bool(r["strict"]) for r in RW[j] if r["pid"] == p]) for p in reach]) for j in ARMS + ["B_s2300"]}
    res["R_strict"] = {"rate": {j: round(float(v.mean()), 5) for j, v in RS.items()},
                       "G": {j: boot(RS[j], RS["dpo"], RS["B_s2300"]) for j in ARMS if j != "dpo"}}
    # final readings: holds on both / R only / A only
    m = res["variants"]["main"]["readings"]
    fin = {}
    for k in ("low-rank carries it", "high-rank", "outside the 448 matrices"):
        r_, a_ = m[k]["holds"], res["A"]["readings"][k]["holds"]
        fin[k] = "holds" if r_ and a_ else ("holds on R only" if r_ else ("holds on A only" if a_ else "does not hold"))
    res["final"] = fin
    json.dump(res, open(OUT / "readings.json", "w"), indent=1)
    for v, d in res["variants"].items():
        T(f"[R, labels {v}] rates " + " ".join(f"{j} {d['rate'][j]:.4f}" for j in d["rate"]))
        T("   G " + "  ".join(f"{j} {g:.3f} [{lo:.3f}, {hi:.3f}]" for j, (g, lo, hi) in d["G"].items()))
        T("   readings " + json.dumps({k: (x["holds"], x["firm"]) if isinstance(x, dict) else x for k, x in d["readings"].items()}))
    T("[A] rates " + " ".join(f"{j} {v:.4f}" for j, v in res["A"]["rate"].items()), "dpo pool draws", res["A"]["dpo_pool_draws"])
    T("   G " + "  ".join(f"{j} {g:.3f} [{lo:.3f}, {hi:.3f}]" for j, (g, lo, hi) in GA.items()))
    T("   G fresh dpo " + "  ".join(f"{j} {g:.3f} [{lo:.3f}, {hi:.3f}]" for j, (g, lo, hi) in GAf.items()))
    T("   readings " + json.dumps({k: (x["holds"], x["firm"]) if isinstance(x, dict) else x for k, x in res["A"]["readings"].items()}))
    T("[R strict] rates " + " ".join(f"{j} {v:.4f}" for j, v in res["R_strict"]["rate"].items()))
    T("   G " + "  ".join(f"{j} {g:.3f} [{lo:.3f}, {hi:.3f}]" for j, (g, lo, hi) in res["R_strict"]["G"].items()))
    T("final:", json.dumps(fin))
    T("hand per arm:", json.dumps(res["hand_per_arm"]))


if __name__ == "__main__":
    main()
