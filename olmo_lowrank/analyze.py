#!/usr/bin/env python3
"""Part 2 analysis of run olmo-lowrank (VPS side; numpy). Pre-registration: "G and readings".

Inputs: row caches (cells.py rows) of the 8 arms and the stored endpoint jobs; olmo_lowrank/hand_cells.csv (hand.py
cells: per reach cell the estimated genuine rate).
  R (primary): the 48 reach prompts' estimated genuine rate. dpo = this run's fresh dpo arm; s2300 = olmo-ifcurve's
     B_s2300 (32 draws per prompt) re-gated here.
  A: the 218 arm-A prompts' strict pass@1 (mean over prompts of the per-prompt mean over that arm's draws). dpo =
     the fresh arm pooled with olmo-ifomega's F_dpo_ifb on the 176 non-reach prompts (robustness: fresh only);
     s2300 = F_s2300_ifb on the 176 non-reach prompts, B_s2300 on the 42 IFBench reach prompts.
G(arm) = (r_arm - r_dpo) / (r_s2300 - r_dpo); paired prompt bootstrap (every arm and both endpoints resampled on the
same prompts), 10,000 replicates, percentile 95 %.

  analyze.py [--reps 10000]  -> olmo_lowrank/results.csv (per arm and metric), olmo_lowrank/summary.json (readings)
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells  # noqa: E402

ARMS = cells.ARMS
TK = ["T1", "T4", "T16", "T64", "T256"]
K_OF = {"T1": 1, "T4": 4, "T16": 16, "T64": 64, "T256": 256}


def per_prompt_strict(jobs_by_pid):
    """{pid: [jobs]} -> {pid: (mean strict, draws)} pooling the listed jobs' draws on that prompt."""
    out = {}
    for pid, jobs in jobs_by_pid.items():
        xs = [x["strict"] for j in jobs for x in cells.by_pid(j).get(pid, [])]
        out[pid] = (float(np.mean(xs)) if xs else np.nan, len(xs))
    return out


def boot_G(arm_v, d_v, s_v, reps, seed):
    """arm_v, d_v, s_v: per-prompt arrays (same prompt order). -> point G, (lo, hi), bootstrap array."""
    P = len(arm_v)
    g0 = (arm_v.mean() - d_v.mean()) / (s_v.mean() - d_v.mean())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, P, size=(reps, P))
    a, d, s = arm_v[idx].mean(1), d_v[idx].mean(1), s_v[idx].mean(1)
    g = (a - d) / (s - d)
    return float(g0), (float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))), g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10000)
    a = ap.parse_args()
    reach, others = cells.reach(), cells.others()
    armA = cells.armA()
    ifb_reach = [p for p in reach if p in set(armA)]
    hc = {(r["job"], r["pid"]): r for r in csv.DictReader(open("olmo_lowrank/hand_cells.csv"))}
    have = [j for j in ARMS if cells.rows(j)]
    res, boots = [], {}
    # ---- R: reach genuine
    R = {}
    for j in have + ["B_s2300"]:
        v = [hc.get((j, p), {}).get("est_genuine_rate", "") for p in reach]
        if all(x != "" for x in v):
            R[j] = np.array([float(x) for x in v])
    # ---- A: 218 strict
    A = {}
    for j in have:
        pp = per_prompt_strict({p: [j] for p in armA})
        A[j] = np.array([pp[p][0] for p in armA])
    dpo_pool = per_prompt_strict({p: (["dpo", "F_dpo_ifb"] if p in set(others) else ["dpo"]) for p in armA})
    A["dpo_pooled"] = np.array([dpo_pool[p][0] for p in armA])
    s_pp = per_prompt_strict({p: (["F_s2300_ifb"] if p in set(others) else ["B_s2300"]) for p in armA})
    A["s2300"] = np.array([s_pp[p][0] for p in armA])
    # reach strict (supplementary)
    RS = {j: np.array([per_prompt_strict({p: [j]})[p][0] for p in reach]) for j in have + ["B_s2300"]}
    seed = 4949
    for metric, V, dkey, skey in (("R", R, "dpo", "B_s2300"), ("A", A, "dpo_pooled", "s2300"),
                                  ("A_fresh_dpo", A, "dpo", "s2300"), ("R_strict", RS, "dpo", "B_s2300")):
        if dkey not in V or skey not in V:
            continue
        for j in [x for x in have if x != "dpo"]:
            if j not in V:
                continue
            g, ci, gb = boot_G(V[j], V[dkey], V[skey], a.reps, seed)
            boots[(metric, j)] = gb
            res.append({"metric": metric, "arm": j, "rate": round(float(np.nanmean(V[j])), 4),
                        "dpo": round(float(V[dkey].mean()), 4), "s2300": round(float(V[skey].mean()), 4),
                        "G": round(g, 4), "G_lo": round(ci[0], 4), "G_hi": round(ci[1], 4), "prompts": len(V[j])})
    with open("olmo_lowrank/results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0]))
        w.writeheader()
        w.writerows(res)
    G = {(r["metric"], r["arm"]): r for r in res}

    def side(metric, arm, thr, op):
        r = G.get((metric, arm))
        if r is None:
            return None
        hold = (r["G"] >= thr) if op == ">=" else (r["G"] <= thr) if op == "<=" else (r["G"] < thr)
        firm = (r["G_lo"] >= thr or r["G_hi"] < thr) if op in (">=", "<") else (r["G_hi"] <= thr or r["G_lo"] > thr)
        return {"holds": bool(hold), "firm": bool(firm), "G": r["G"], "ci": [r["G_lo"], r["G_hi"]]}
    readings = {}
    for metric in ("R", "A"):
        rd = {}
        c1 = [side(metric, "T16", 0.5, ">="), side(metric, "C16", 0.2, "<=")]
        c2 = [side(metric, "T256", 0.5, "<"), side(metric, "F448", 0.75, ">=")]
        c3 = [side(metric, "F448", 0.75, "<")]
        for name, cs in (("low-rank carries it", c1), ("high-rank", c2), ("outside the 448 matrices", c3)):
            if any(c is None for c in cs):
                rd[name] = None
                continue
            rd[name] = {"holds": all(c["holds"] for c in cs), "firm": all(c["firm"] for c in cs), "conditions": cs}
        k50 = next((K_OF[t] for t in TK if (metric, t) in G and G[(metric, t)]["G"] >= 0.5), ">256")
        rd["k50"] = k50
        readings[metric] = rd
    final = {}
    for name in ("low-rank carries it", "high-rank", "outside the 448 matrices"):
        r_, a_ = readings["R"].get(name), readings["A"].get(name)
        if r_ is None or a_ is None:
            final[name] = None
        else:
            final[name] = ("holds" if r_["holds"] and a_["holds"] else "holds on R only" if r_["holds"] else
                           "holds on A only" if a_["holds"] else "does not hold")
    summ = {"readings": readings, "final": final, "results": res,
            "n_prompts": {"reach": len(reach), "armA": len(armA), "ifbench_reach": len(ifb_reach)}}
    json.dump(summ, open("olmo_lowrank/summary.json", "w"), indent=1)
    print("metric      arm   rate    G     95% CI")
    for r in res:
        print(f"{r['metric']:11s} {r['arm']:5s} {r['rate']:.3f} {r['G']:6.3f} [{r['G_lo']:.3f}, {r['G_hi']:.3f}]")
    print(json.dumps(final, indent=1))
    print("k50:", {m: readings[m]["k50"] for m in readings})


if __name__ == "__main__":
    main()
