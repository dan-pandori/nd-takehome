#!/usr/bin/env python3
"""Reviewer recount of olmo-novelty Q2 (ProRL's "largest where the start is weakest" correlation), own code.

Spec: preregistration/olmo-novelty.md, "Design — the correlation". Reads counts from olmo_ifomega/results.csv
(fixed phase: dpo 16 draws per prompt, each RL checkpoint 8) and, for a real-split check and a count cross-check,
the per-draw grades of the fixed-phase jobs (bucket olmo-ifomega/artifacts/olmo_ifomega/graded/F_*_{ifb,ife}.jsonl,
sha256 checked against artifacts/MANIFEST.jsonl; --graded DIR).

    python3 review_onv/corr.py --root ~/review/olmo-novelty --graded ~/review/olmo-novelty/scratch_onv/graded

Split design: x = dpo pass@1 on 8 of its 16 draws, y = RL pass@1 (8 draws) - dpo pass@1 on the other 8. With counts
only the 8 drawn for x are a hypergeometric draw from dpo's 16 (exchangeable draws); rho is averaged over partitions.
Spearman = Pearson on average ranks (own ranker, cross-checked against scipy once).
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

NPART = 2000
NBOOT = 2000
MODELS = ("dpo", "s0100", "s0750", "s2300")


def ranks(v):
    v = np.asarray(v, dtype=float)
    order = np.argsort(v, kind="mergesort")
    r = np.empty(len(v))
    sv = v[order]
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and sv[j + 1] == sv[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    rx -= rx.mean()
    ry -= ry.mean()
    d = math.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / d) if d > 0 else float("nan")


def load_counts(root, task, grade):
    """model -> {pid: (succ_fixed, n_fixed)} over non-excluded prompts of task."""
    out = defaultdict(dict)
    for r in csv.DictReader(open(root / "olmo_ifomega" / "results.csv")):
        if r["task"] != task or r["excluded"]:
            continue
        s = r[f"succ_fixed_{grade}"]
        out[r["model"]][r["pid"]] = (int(s), int(r["n_fixed"]))
    return out


def load_draws(gdir, job):
    """pid -> list of (strict, loose) in draw order (chunk, i)."""
    rows = defaultdict(list)
    for ln in open(gdir / f"{job}.jsonl"):
        r = json.loads(ln)
        rows[r["pid"]].append((r["chunk"], r["i"], bool(r["strict"]), bool(r["loose"])))
    return {p: [(a, b) for _, _, a, b in sorted(v)] for p, v in rows.items()}


def arrays(cnt, rl, pids=None):
    pids = sorted(set(cnt["dpo"]) & set(cnt[rl])) if pids is None else pids
    c = np.array([cnt["dpo"][p][0] for p in pids])
    nd = {cnt["dpo"][p][1] for p in pids}
    s = np.array([cnt[rl][p][0] for p in pids])
    nr = {cnt[rl][p][1] for p in pids}
    assert nd == {16} and nr == {8}, (nd, nr)
    return pids, c, s


def split_xy(c, s, rng, k=1):
    a = rng.hypergeometric(c, 16 - c, 8)  # dpo successes among the 8 draws used for x
    b = c - a
    if k == 1:
        return a / 8.0, s / 8.0 - b / 8.0
    # pass@8 on 8 draws is binary
    return (a > 0).astype(float), (s > 0).astype(float) - (b > 0).astype(float)


def split_rho(c, s, rng, k=1, npart=NPART):
    return float(np.mean([spearman(*split_xy(c, s, rng, k)) for _ in range(npart)]))


def boot_ci(c, s, rng, k=1, nboot=NBOOT):
    n = len(c)
    vals = []
    for _ in range(nboot):
        i = rng.integers(0, n, n)
        vals.append(spearman(*split_xy(c[i], s[i], rng, k)))
    vals = np.array(vals)
    vals = vals[~np.isnan(vals)]
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)), len(vals)


def naive_rho(c, s, k=1):
    if k == 1:
        x = c / 16.0
        return spearman(x, s / 8.0 - x)
    x = np.array([1 - math.comb(16 - ci, 8) / math.comb(16, 8) for ci in c])  # unbiased pass@8 from 16
    return spearman(x, (s > 0).astype(float) - x)


def null_rho(c, s, rng, nperm=NPART):
    vals = []
    for _ in range(nperm):
        x, _ = split_xy(c, s, rng)
        b = c - x * 8
        sp = rng.permutation(s)
        vals.append(spearman(x, sp / 8.0 - b / 8.0))
    vals = np.array(vals)
    return float(vals.mean()), float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def bins(c, s, rng, npart=NPART):
    edges = [("zero", lambda x: x == 0), ("(0,.25]", lambda x: (x > 0) & (x <= .25)),
             ("(.25,.5]", lambda x: (x > .25) & (x <= .5)), ("(.5,.75]", lambda x: (x > .5) & (x <= .75)),
             (">.75", lambda x: x > .75)]
    acc = {e: [] for e, _ in edges}
    nn = {e: [] for e, _ in edges}
    for _ in range(npart):
        x, y = split_xy(c, s, rng)
        for e, f in edges:
            m = f(x)
            nn[e].append(m.sum())
            if m.sum():
                acc[e].append(y[m].mean())
    return {e: (float(np.mean(acc[e])) if acc[e] else float("nan"), float(np.mean(nn[e]))) for e, _ in edges}


def per_type(root, cnt, rl, rng, unit="id", k=8, npart=NPART, minp=2):
    probs = {}
    for ln in open(root / "olmo_ifomega" / "problems.jsonl"):
        p = json.loads(ln)
        probs[p["pid"]] = p
    pids, c, s = arrays(cnt, rl)
    groups = defaultdict(list)
    for j, p in enumerate(pids):
        for iid in probs[p]["instruction_id_list"]:
            key = iid if unit == "id" else iid.split(":")[0]
            groups[key].append(j)
    keys = [g for g in sorted(groups) if len(groups[g]) >= minp]
    idx = [np.array(groups[g]) for g in keys]

    def rho_once(cc, ss, rr):
        x, y = split_xy(cc, ss, rr, k)
        return spearman([x[i].mean() for i in idx], [y[i].mean() for i in idx])

    rho = float(np.mean([rho_once(c, s, rng) for _ in range(npart)]))
    # bootstrap over types (ProRL's unit), prompts inside a type kept
    vals = []
    for _ in range(NBOOT):
        pick = rng.integers(0, len(keys), len(keys))
        xs, ys = [], []
        x, y = split_xy(c, s, rng, k)
        for t in pick:
            xs.append(x[idx[t]].mean())
            ys.append(y[idx[t]].mean())
        vals.append(spearman(xs, ys))
    vals = np.array(vals)
    vals = vals[~np.isnan(vals)]
    # naive per-type (shared draws, unbiased pass@k from all 16)
    if k == 8:
        xa = np.array([1 - math.comb(16 - ci, 8) / math.comb(16, 8) for ci in c])
        ya = (s > 0).astype(float) - xa
    else:
        xa = c / 16.0
        ya = s / 8.0 - xa
    nv = spearman([xa[i].mean() for i in idx], [ya[i].mean() for i in idx])
    return dict(n_types=len(keys), n_prompts_in=int(sum(len(i) for i in idx)), rho=rho,
                lo=float(np.percentile(vals, 2.5)), hi=float(np.percentile(vals, 97.5)), naive=nv)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--graded", default=None)
    ap.add_argument("--out", default="review_onv/corr_out.json")
    a = ap.parse_args()
    root = Path(a.root).expanduser()
    res = {}
    rng = np.random.default_rng(20261107)

    # sanity: own ranker vs scipy
    try:
        from scipy.stats import spearmanr
        t = np.random.default_rng(1).integers(0, 5, 200)
        u = np.random.default_rng(2).integers(0, 5, 200)
        assert abs(spearmanr(t, u)[0] - spearman(t, u)) < 1e-12
        res["ranker_check"] = "own spearman == scipy.spearmanr on tied integers"
    except ImportError:
        res["ranker_check"] = "scipy absent"

    for task in ("ifbench", "ifeval"):
        for grade in ("strict", "loose"):
            cnt = load_counts(root, task, grade)
            for rl in ("s2300", "s0750", "s0100"):
                if rl not in cnt or not cnt[rl]:
                    continue
                pids, c, s = arrays(cnt, rl)
                key = f"{task}/{grade}/{rl}"
                r = dict(n=len(pids))
                r["mean_dpo_p1"] = float((c / 16).mean())
                r["mean_rl_p1"] = float((s / 8).mean())
                r["P1_rho"] = split_rho(c, s, rng)
                r["P1_lo"], r["P1_hi"], r["P1_nboot"] = boot_ci(c, s, rng)
                r["naive_rho"] = naive_rho(c, s)
                r["pass8_split_rho"] = split_rho(c, s, rng, k=8)
                r["pass8_lo"], r["pass8_hi"], _ = boot_ci(c, s, rng, k=8)
                r["pass8_naive_rho"] = naive_rho(c, s, k=8)
                m = c >= 1
                r["n_dpo_ge1"] = int(m.sum())
                r["ge1_rho"] = split_rho(c[m], s[m], rng)
                r["ge1_lo"], r["ge1_hi"], _ = boot_ci(c[m], s[m], rng)
                r["null_rho"], r["null_lo"], r["null_hi"] = null_rho(c, s, rng)
                r["bins"] = bins(c, s, rng)
                if task == "ifbench":
                    r["type_id_pass8"] = per_type(root, cnt, rl, rng, "id", 8)
                    r["type_id_pass1"] = per_type(root, cnt, rl, rng, "id", 1)
                    r["type_cat_pass8"] = per_type(root, cnt, rl, rng, "cat", 8)
                res[key] = r
                print(key, json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()
                                       if not isinstance(v, dict)}))
                print("   bins", {k: (round(v[0], 3), round(v[1], 1)) for k, v in r["bins"].items()})
                for t in ("type_id_pass8", "type_id_pass1", "type_cat_pass8"):
                    if t in r:
                        print("  ", t, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r[t].items()})

    if a.graded:
        g = Path(a.graded).expanduser()
        jobs = {"ifbench": {"dpo": "F_dpo_ifb", "s2300": "F_s2300_ifb", "s0750": "F_s0750_ifb", "s0100": "F_s0100_ifb"},
                "ifeval": {"dpo": "F_dpo_ife", "s2300": "F_s2300_ife", "s0750": "F_s0750_ife"}}
        for task, jm in jobs.items():
            draws = {m: load_draws(g, j) for m, j in jm.items()}
            for gi, grade in enumerate(("strict", "loose")):
                cnt = load_counts(root, task, grade)
                bad = 0
                for m in jm:
                    for p, (sc, n) in cnt[m].items():
                        d = draws[m].get(p, [])
                        if len(d) != n or sum(t[gi] for t in d) != sc:
                            bad += 1
                res[f"crosscheck/{task}/{grade}"] = f"{bad} (model, prompt) count mismatches results.csv vs per-draw files"
                print(f"crosscheck {task}/{grade}: {bad} mismatches")
                for rl in [m for m in jm if m != "dpo"]:
                    pids = sorted(cnt["dpo"])
                    out = []
                    for half in (0, 1):
                        xa, yb = [], []
                        for p in pids:
                            d = [t[gi] for t in draws["dpo"][p]]
                            first, second = d[:8], d[8:]
                            xh, oh = (first, second) if half == 0 else (second, first)
                            xa.append(sum(xh) / 8.0)
                            yb.append(sum(t[gi] for t in draws[rl][p]) / 8.0 - sum(oh) / 8.0)
                        out.append(spearman(xa, yb))
                    res[f"realsplit/{task}/{grade}/{rl}"] = out
                    print(f"realsplit {task}/{grade}/{rl}: x=draws1-8 {out[0]:.4f}  x=draws9-16 {out[1]:.4f}")

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
