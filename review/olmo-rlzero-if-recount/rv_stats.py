"""Fixed-phase pass@k with prompt-bootstrap intervals, lengths, candidates, every candidate's fate at 256 under strict
and loose, the strict verdict per task, reverse prompts, matched-k entries / exits and the extension audit -- all from
my own cells (rv_cells.py). Output: out/stats.json, out/stats.txt"""
import json
import os
from collections import Counter, defaultdict
from math import comb

import numpy as np

import rv_core as C
from rv_cells import EXCL, sets

RL = ("s0100", "s0500", "main")
lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def passk(n, c, k):
    if n < k:
        return float("nan")
    return 1.0 - comb(n - c, k) / comb(n, k)


def boot(vals, B=10000, seed=0):
    v = np.asarray(vals, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(v), size=(B, len(v)))
    m = v[idx].mean(axis=1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def fixed(cell):
    return [d for d in cell if d[0].startswith("F_")]


def fate(cells, model, pid, g, fresh_jobs):
    """Draws within 256, successes under grade g (3 strict, 4 loose), positions, fresh successes."""
    d = cells.get(model, {}).get(pid, [])[:256]
    pos = [k for k, x in enumerate(d) if x[g]]
    fresh = [k for k in pos if d[k][0].split("_")[0] in fresh_jobs]
    return {"n": len(d), "succ": len(pos), "pos": pos[:6], "fresh": len(fresh),
            "jobs": dict(Counter(x[0] for x in d))}


def main():
    P = C.load_problems()
    cells = json.load(open(os.path.join(C.OUT, "cells.json")))
    S = sets(P)
    res = {"passk": {}, "lengths": {}, "cands": {}, "verdict": {}, "reverse": {}, "entries": {}}
    # ------------------------------------------------ fixed phase pass@k
    say("== fixed-phase pass@k (strict / loose), prompt bootstrap 95 % (10,000)")
    for sname, pids in S.items():
        for m in ("base", "s0100", "s0500", "main"):
            for gi, gname in ((3, "strict"), (4, "loose")):
                row = {}
                for k in (1, 2, 4, 8, 16):
                    vals = []
                    for p in pids:
                        f = fixed(cells[m].get(p, []))
                        vals.append(passk(len(f), sum(x[gi] for x in f), k))
                    if any(np.isnan(vals)):
                        continue
                    row[k] = boot(vals)
                res["passk"][f"{sname}|{m}|{gname}"] = row
                say(f"{sname:15s} {m:6s} {gname:6s} " + "  ".join(
                    f"@{k} {v[0]:.3f} [{v[1]:.3f},{v[2]:.3f}]" for k, v in row.items()))
    # ------------------------------------------------ lengths (fixed phase)
    say("== fixed-phase lengths: mean / median tokens, cut at 16,384, '</think>' share, t1 != strict")
    for task in ("ifbench", "ifeval"):
        for m in ("base", "s0100", "s0500", "main"):
            ds = [x for p, c in cells[m].items() if P[p]["task"] == task for x in fixed(c)]
            nt = np.array([x[5] for x in ds])
            cut = sum(x[6] == "length" for x in ds)
            te = sum(bool(x[8]) for x in ds)
            t1d = sum(1 for x in ds if x[7] is not None and bool(x[7]) != bool(x[3]))
            t1w = sum(1 for x in ds if x[7] and not x[3])
            res["lengths"][f"{task}|{m}"] = {"n": len(ds), "mean": float(nt.mean()), "median": float(np.median(nt)),
                                             "cut": cut, "think_end": te, "t1_differs": t1d, "t1_only": t1w}
            say(f"{task:8s} {m:6s} n {len(ds):5d} mean {nt.mean():7.1f} median {np.median(nt):6.0f} cut {cut:4d} "
                f"({cut / len(ds):.3%}) </think> {te:4d} t1!=strict {t1d} (t1-only successes {t1w})")
    # ------------------------------------------------ candidates and fates
    for task, sname in (("ifbench", "ifbench_all300"), ("ifeval", "ifeval_all150")):
        R, V = [], []
        for p in S[sname]:
            fb = fixed(cells["base"].get(p, []))
            bs = sum(x[3] for x in fb)
            rl = {m: sum(x[3] for x in fixed(cells[m].get(p, []))) for m in RL}
            if bs == 0 and any(rl.values()):
                R.append(p)
            if bs >= 1 and rl["main"] == 0:
                V.append(p)
        Rl, Vl = [], []
        for p in S[sname]:
            fb = fixed(cells["base"].get(p, []))
            bs = sum(x[4] for x in fb)
            rl = {m: sum(x[4] for x in fixed(cells[m].get(p, []))) for m in RL}
            if bs == 0 and any(rl.values()):
                Rl.append(p)
            if bs >= 1 and rl["main"] == 0:
                Vl.append(p)
        fates = {}
        for p in R:
            fm = fate(cells, "main", p, 3, ("C1",))
            fb = fate(cells, "base", p, 3, ("E1", "E2", "E3", "E4", "C1"))
            rl8 = {m: sum(x[3] for x in fixed(cells[m].get(p, []))) for m in RL}
            main_conf = fm["succ"] >= 2 and fm["fresh"] >= 1
            if fb["succ"] >= 2:
                st = "resolved"
            elif not main_conf:
                st = "dissolved" if fm["n"] >= 256 else "open-main"
            elif fb["succ"] == 0 and fb["n"] >= 256:
                st = "REACH"
            elif fb["succ"] == 1 and fb["n"] >= 256:
                st = "base-1-at-256"
            else:
                st = "open"
            fates[p] = {"state": st, "main": fm, "base": fb, "rl_fixed": rl8, "excluded": p in EXCL}
        rev = {}
        for p in V:
            fm = fate(cells, "main", p, 3, ("C1",))
            fb = fate(cells, "base", p, 3, ("C1",))
            rev[p] = {"main": fm, "base": fb,
                      "state": ("REVERSE" if fm["succ"] == 0 and fm["n"] >= 256 and fb["succ"] >= 2 and fb["fresh"] >= 1
                                else "main-solves" if fm["succ"] >= 1 else "open")}
        res["cands"][task] = {"R": R, "V": V, "R_loose": Rl, "V_loose": Vl, "fates": fates}
        res["reverse"][task] = rev
        cnt = Counter(f["state"] for p, f in fates.items() if p not in EXCL)
        nreach = cnt["REACH"]
        if nreach >= 3:
            verdict = "Reach"
        elif all(f["state"] in ("resolved", "dissolved") for p, f in fates.items() if p not in EXCL):
            verdict = "No reach at 256"
        else:
            verdict = "Inconclusive"
        res["verdict"][task] = {"strict": verdict, "states": dict(cnt),
                                "reach_pids": sorted(p for p, f in fates.items() if f["state"] == "REACH")}
        say(f"== {task}: R {len(R)} (excluded among them {len([p for p in R if p in EXCL])}) V {len(V)} | loose: R "
            f"{len(Rl)} V {len(Vl)}")
        say(f"   R by RL checkpoint with >= 1/8 (fixed): " + str({m: sum(1 for p in R if fates[p]['rl_fixed'][m]) for m in RL}))
        say(f"   states (non-excluded): {dict(cnt)} -> strict verdict: {verdict}")
        say(f"   strict reach prompts: {res['verdict'][task]['reach_pids']}")
        say(f"   base draws on R: " + str(Counter(min(f['base']['n'], 256) for f in fates.values()).most_common(12)))
        say(f"   main draws on R: " + str(Counter(f['main']['n'] for f in fates.values())))
        say(f"   reverse states: {dict(Counter(v['state'] for v in rev.values()))}; reverse prompts: "
            f"{sorted(p for p, v in rev.items() if v['state'] == 'REVERSE')}")
    # ------------------------------------------------ matched-k entries / exits (fixed phase, k = 8)
    say("== matched-k (k = 8) expected entries sum pass@8_c (1 - pass@8_base) and exits, fixed phase")
    for sname in ("ifbench_h297", "ifeval_all150"):
        for m in RL:
            ent = ext = 0.0
            for p in S[sname]:
                fb = fixed(cells["base"][p]); fc = fixed(cells[m][p])
                pb = passk(len(fb), sum(x[3] for x in fb), 8); pc = passk(len(fc), sum(x[3] for x in fc), 8)
                ent += pc * (1 - pb); ext += pb * (1 - pc)
            res["entries"][f"{sname}|{m}"] = {"entries": ent, "exits": ext}
            say(f"{sname:15s} {m:6s} entries {ent:6.2f} exits {ext:6.2f}")
    json.dump(res, open(os.path.join(C.OUT, "stats.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "stats.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
