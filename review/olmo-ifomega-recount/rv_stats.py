"""pass@k with prompt-bootstrap intervals, matched-k entries / exits, candidates, the non-hand verdicts and lengths,
from my cell draws (~/review/oif_rv/draws.json, written by rv_cells.py). Output: out/stats.json, out/stats.txt.

Definitions (pre-registration, Design + Verdict; my own code):
  fixed phase: dpo 16, RL checkpoints 8 per prompt (the F_* jobs). pass@k unbiased (Chen et al.), k <= n.
  candidates under grade G: reach R_G: dpo 0/16 and some RL checkpoint >= 1/8; reverse V_G: dpo >= 1/16, s2300 0/8.
  confirmed(model, pid, G): >= 2 G-successes within the model's first 256 draws on pid, >= 1 of them drawn after the
    prompt became a candidate (= outside the fixed phase); for the defender every success qualifies.
  verdict under G (task): Reach if >= 3 non-excluded prompts in R_G where s2300 is confirmed and dpo has 0 G-successes
    within 256; No reach at 256 if every R_G prompt is dpo-confirmed (>= 2 within 256) or dissolved (no RL checkpoint
    confirmed within 256); else Inconclusive. Reverse prompts are reported by the same rule."""
import csv
import json
import math
import os
import random
from collections import Counter, defaultdict

import rv_core as C

MODELS = ("dpo", "s0100", "s0750", "s2300")
RL = ("s0100", "s0750", "s2300")


def passk(n, c, k):
    if k > n:
        return None
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def excluded():
    fn = os.path.join(C.WS, "olmo_ifomega", "exclusions.csv")
    return {r["pid"] for r in csv.DictReader(open(fn))}


def load():
    d = json.load(open(os.path.join(C.BIG, "draws.json")))
    cells = {}
    for k, v in d.items():
        m, p = k.split("|", 1)
        cells[(m, p)] = v
    return cells


def model_draws(cells, m, p, g):
    c = cells.get((m, p))
    if c is None:
        return None
    fl, fx = c["g"][g][:256], c["fixed"][:256]
    fresh = sum(1 for x, y in zip(fl, fx) if x and not y)
    conf = sum(fl) >= 2 and fresh >= 1
    return {"n": len(fl), "succ": sum(fl), "fresh": fresh, "confirmed": conf, "complete": conf or len(fl) >= 256,
            "first2": [j + 1 for j, x in enumerate(fl) if x][:2]}


def r_fate(cells, p, g, fixed):
    """Fate of a reach candidate under grade g (draws within 256 per model).
    reach: s2300 confirmed and dpo 0 successes in a full 256; dpo_resolved: dpo >= 2 successes within 256;
    dissolved: neither, and every challenger (s2300 and each RL checkpoint with >= 1/8) is complete and unconfirmed;
    open_*: anything else, by reason."""
    d = model_draws(cells, "dpo", p, g)
    ch = ["s2300"] + [m for m in ("s0100", "s0750") if m in fixed and p in fixed[m] and fixed[m][p][1] > 0]
    rl = {m: model_draws(cells, m, p, g) for m in RL if (m, p) in cells}
    s = rl.get("s2300")
    if d["succ"] >= 2:
        status = "dpo_resolved"
    elif s and s["confirmed"] and d["succ"] == 0 and d["n"] >= 256:
        status = "reach"
    elif all(m in rl and rl[m]["complete"] and not rl[m]["confirmed"] for m in ch):
        status = "dissolved" if (d["n"] >= 256 or d["succ"] == 0) else "open_dpo_incomplete"
    elif d["n"] < 256:
        status = "open_dpo_incomplete"
    elif d["succ"] == 1:
        status = "open_dpo_one_success" if (s and s["confirmed"]) else "open_dpo_one_success_challenger_unconfirmed"
    else:
        status = "open_challenger_incomplete"
    return {"status": status, "dpo": d, "rl": rl, "challengers": ch}


def v_fate(cells, p, g):
    """Fate of a reverse candidate: reverse = dpo confirmed and s2300 0 in a full 256; s2300_resolved = s2300 >= 2."""
    s = model_draws(cells, "s2300", p, g)
    d = model_draws(cells, "dpo", p, g)
    if s["succ"] >= 2:
        status = "s2300_resolved"
    elif d["confirmed"] and s["succ"] == 0 and s["n"] >= 256:
        status = "reverse"
    elif d["complete"] and not d["confirmed"] and (s["n"] >= 256 or s["succ"] == 0):
        status = "dissolved"
    else:
        status = "open"
    return {"status": status, "s2300": s, "dpo": d}


def boot(vals_by_pid, fn, B=10000, seed=1):
    pids = sorted(vals_by_pid)
    rnd = random.Random(seed)
    est = fn([vals_by_pid[p] for p in pids])
    bs = []
    for _ in range(B):
        s = [vals_by_pid[pids[rnd.randrange(len(pids))]] for _ in pids]
        bs.append(fn(s))
    bs.sort()
    return est, bs[int(0.025 * B)], bs[int(0.975 * B) - 1]


def main(B=10000):
    cells = load()
    P = C.load_problems()
    EX = excluded()
    out = {"excluded_n": len(EX)}
    txt = []
    tasks = ("ifbench", "ifeval", "omega_out", "omega_in")
    for task in tasks:
        pids_all = sorted(p for p, r in P.items() if r["task"] == task)
        for setname, pids in (("headline", [p for p in pids_all if p not in EX]), ("all", pids_all)):
            if setname == "all" and task != "ifbench":
                continue
            grades = ("strict", "loose", "rlview") if task.startswith("if") else ("omega", "rl", "doubly", "own")
            res = {"n_prompts": len(pids)}
            for g in grades:
                gres = {}
                fixed = {}
                for m in MODELS:
                    have = [p for p in pids if (m, p) in cells and sum(cells[(m, p)]["fixed"]) > 0]
                    if not have:
                        continue
                    nc = {}
                    for p in have:
                        c = cells[(m, p)]
                        nf = sum(c["fixed"])
                        nc[p] = (nf, sum(c["g"][g][:nf]))
                    fixed[m] = nc
                    ks = (1, 2, 4, 8, 16) if m == "dpo" else (1, 2, 4, 8)
                    row = {"n_prompts": len(have), "n_samples": sum(v[0] for v in nc.values())}
                    for k in ks:
                        vals = {p: passk(n, c_, k) for p, (n, c_) in nc.items()}
                        if any(v is None for v in vals.values()):
                            continue
                        est, lo, hi = boot(vals, lambda s: sum(s) / len(s), B=B if k in (1, 8) else 2000)
                        row[f"pass@{k}"] = [round(est, 4), round(lo, 4), round(hi, 4)]
                    gres[m] = row
                # matched-k entries / exits vs dpo (k = 8)
                ee = {}
                for m in RL:
                    if m not in fixed or "dpo" not in fixed:
                        continue
                    common = [p for p in fixed[m] if p in fixed["dpo"]]
                    vals = {p: (passk(*fixed[m][p], 8), passk(*fixed["dpo"][p], 8)) for p in common}
                    est_e = boot(vals, lambda s: sum(a * (1 - b) for a, b in s), B=2000)
                    est_x = boot(vals, lambda s: sum((1 - a) * b for a, b in s), B=2000)
                    # observed sets at matched k = 8: dpo's first 8 draws vs the checkpoint's 8
                    ent, ext = [], []
                    ent16, ext16 = [], []
                    for p in common:
                        cm, cd = cells[(m, p)], cells[("dpo", p)]
                        s_m = sum(cm["g"][g][:8])
                        s_d8 = sum(cd["g"][g][:8])
                        s_d16 = sum(cd["g"][g][:16])
                        if s_m > 0 and s_d8 == 0:
                            ent.append(p)
                        if s_m == 0 and s_d8 > 0:
                            ext.append(p)
                        if s_m > 0 and s_d16 == 0:
                            ent16.append(p)
                        if s_m == 0 and s_d16 > 0:
                            ext16.append(p)
                    ee[m] = {"expected_entries": [round(x, 2) for x in est_e],
                             "expected_exits": [round(x, 2) for x in est_x],
                             "observed_entries_k8": len(ent), "observed_exits_k8": len(ext),
                             "observed_entries_vs_dpo16": len(ent16), "observed_exits_vs_dpo16": len(ext16)}
                gres["entries_exits_k8"] = ee
                # candidates
                if "dpo" in fixed:
                    R = sorted(p for p in pids if p in fixed["dpo"] and fixed["dpo"][p][1] == 0
                               and any(m in fixed and p in fixed[m] and fixed[m][p][1] > 0 for m in RL))
                    V = sorted(p for p in pids if p in fixed["dpo"] and fixed["dpo"][p][1] > 0
                               and "s2300" in fixed and p in fixed["s2300"] and fixed["s2300"][p][1] == 0)
                    gres["R"] = R
                    gres["V"] = V
                    fate = {}
                    for p in R:
                        fate[p] = r_fate(cells, p, g, fixed)
                    gres["R_fate"] = fate
                    vf = {p: v_fate(cells, p, g) for p in V}
                    gres["V_fate"] = vf
                    st = Counter(f["status"] for f in fate.values())
                    nreach = st["reach"]
                    if nreach >= 3:
                        verdict = "Reach"
                    elif all(f["status"] in ("dpo_resolved", "dissolved") for f in fate.values()):
                        verdict = "No reach at 256"
                    else:
                        verdict = "Inconclusive"
                    gres["verdict"] = {"verdict": verdict, "n_reach": nreach, "status_counts": dict(st),
                                       "by_status": {s: sorted(p for p, f in fate.items() if f["status"] == s)
                                                     for s in st},
                                       "reverse_status": dict(Counter(f["status"] for f in vf.values())),
                                       "reverse_by_status": {s: sorted(p for p, f in vf.items() if f["status"] == s)
                                                             for s in {f["status"] for f in vf.values()}}}
                res[g] = gres
            # lengths (fixed phase): mean tokens, cut share, </think> share
            L = {}
            for m in MODELS:
                ns, cut, te, n = 0, 0, 0, 0
                for p in pids:
                    if (m, p) not in cells:
                        continue
                    c = cells[(m, p)]
                    for j, fx in enumerate(c["fixed"]):
                        if fx:
                            n += 1
                            ns += c["n_tok"][j]
                            cut += c["finish"][j] == "length"
                            te += c["think_end"][j]
                if n:
                    L[m] = {"samples": n, "mean_tok": round(ns / n), "cut_share": round(cut / n, 4),
                            "think_end_share": round(te / n, 4)}
            res["lengths_fixed"] = L
            out[f"{task}|{setname}"] = res
            txt.append(f"== {task} [{setname}] n={len(pids)}")
            for g in grades:
                gr = res[g]
                for m in MODELS:
                    if m in gr:
                        txt.append(f"  {g:7s} {m:6s} " + " ".join(f"{k}={v}" for k, v in gr[m].items()))
                if "verdict" in gr:
                    v = gr["verdict"]
                    txt.append(f"  {g:7s} |R|={len(gr['R'])} |V|={len(gr['V'])} verdict={v['verdict']} R:{v['status_counts']}"
                               f" V:{v['reverse_status']}")
                for m, e in gr.get("entries_exits_k8", {}).items():
                    txt.append(f"  {g:7s} {m} entries/exits k8: {e}")
            for m, l in L.items():
                txt.append(f"  len {m}: {l}")
    json.dump(out, open(os.path.join(C.OUT, "stats.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "stats.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    import sys
    main(B=int(sys.argv[1]) if len(sys.argv) > 1 else 10000)
