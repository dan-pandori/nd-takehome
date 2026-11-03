#!/usr/bin/env python3
"""Per-checkpoint x problem results, unbiased pass@k with problem-bootstrap intervals, and reach.

Inputs: artifacts/olmo_pilot/graded/<job>.jsonl for the jobs listed in olmo_pilot/jobs.csv (job, model, step, phase),
olmo_pilot/problems.jsonl, olmo_pilot/exclusions.csv (pid, reason) if present.
Outputs (olmo_pilot/): results.csv (one row per model x problem), passk.csv, reach.csv, dynamics.csv.

Sample order within (model, problem) is (chunk, i): extension jobs continue the chunk numbering, so "first success"
is the 1-based position of the first correct sample in the order the samples were drawn. pass@k estimates:
k <= n_fixed uses Chen et al.'s unbiased estimator on the fixed-budget samples; k > n_fixed uses the
first-success indicator 1{first success <= k}, which is unbiased for sequential sampling up to the first success
(problems solved in the fixed phase count as 1). It is defined only up to the budget each problem actually received.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

A = Path("artifacts/olmo_pilot")
O = Path("olmo_pilot")
GRADES = ("rl", "ansline", "main")
KSTAR = 128


def passk(n, c, k):
    if k > n:
        return float("nan")
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def load(jobs_csv, grade_dir=A / "graded"):
    jobs = list(csv.DictReader(open(jobs_csv)))
    rows = defaultdict(list)  # (model, pid) -> list of (chunk, i, phase, sample row)
    meta = {}
    for j in jobs:
        if j["phase"] in ("void", "pilot", "probe"):  # void: interrupted, unused; pilot: AIME 2023; probe: RL prompts
            continue
        f = grade_dir / f"{j['job']}.jsonl"
        if not f.exists():
            continue
        meta[j["model"]] = int(j["step"])
        for ln in open(f):
            r = json.loads(ln)
            rows[(j["model"], r["pid"])].append((r["chunk"], r["i"], j["phase"], r))
    for k in rows:
        rows[k].sort(key=lambda t: (t[0], t[1]))
    return rows, meta


def summarize(rows, meta, probs, excl):
    out = []
    for (model, pid), ss in sorted(rows.items(), key=lambda kv: (meta[kv[0][0]], kv[0][1])):
        fixed = [s for s in ss if s[2] == "fixed"]
        rec = {"model": model, "step": meta[model], "pid": pid, "set": probs[pid]["set"],
               "excluded": excl.get(pid, ""), "n_fixed": len(fixed), "attempts": len(ss)}
        for g in GRADES:
            ok = [bool(s[3].get(g)) for s in ss]
            rec[f"succ_{g}"] = sum(ok)
            rec[f"succ_fixed_{g}"] = sum(bool(s[3].get(g)) for s in fixed)
            rec[f"succ_confirm_{g}"] = sum(bool(s[3].get(g)) for s in ss if s[2] == "confirm")
            rec[f"first_{g}"] = (ok.index(True) + 1) if any(ok) else ""
        toks = [s[3]["n_tok"] for s in ss]
        rec["mean_tok"] = round(float(np.mean(toks)), 1)
        rec["sum_tok"] = int(np.sum(toks))
        rec["length_cut"] = sum(s[3]["finish"] == "length" for s in ss)
        out.append(rec)
    return out


def pass_curve(res, model, ks, grade="rl", pids=None):
    """Per-problem pass@k estimates for one model (rows: problems, cols: ks); NaN where undefined."""
    rr = [r for r in res if r["model"] == model and (pids is None or r["pid"] in pids)]
    M = np.full((len(rr), len(ks)), np.nan)
    for a, r in enumerate(rr):
        n, c = r["n_fixed"], r[f"succ_fixed_{grade}"]
        fs = r[f"first_{grade}"]
        for b, k in enumerate(ks):
            if k <= n:
                M[a, b] = passk(n, c, k)
            elif c > 0:
                M[a, b] = 1.0
            elif fs != "" and int(fs) <= k:
                M[a, b] = 1.0          # first success within the first k draws: the indicator is 1 for every k >= it
            elif k <= r["attempts"]:
                M[a, b] = 0.0          # k draws observed, none correct
    return [r["pid"] for r in rr], M


def boot_ci(M, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    n = M.shape[0]
    idx = rng.integers(0, n, size=(B, n))
    means = np.nanmean(M[idx], axis=1)
    return np.nanpercentile(means, 2.5, axis=0), np.nanpercentile(means, 97.5, axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=str(O / "jobs.csv"))
    ap.add_argument("--outdir", default=str(O))
    ap.add_argument("--sets", default="aime2024,aime2025,aime2026")
    ap.add_argument("--kstar", type=int, default=128, help="extension budget reached (strong-reach threshold)")
    args = ap.parse_args()
    global KSTAR
    KSTAR = args.kstar
    probs = {r["pid"]: r for r in (json.loads(ln) for ln in open(O / "problems.jsonl"))}
    excl = {}
    if (O / "exclusions.csv").exists():
        excl = {r["pid"]: r["reason"] for r in csv.DictReader(open(O / "exclusions.csv"))}
    rows, meta = load(args.jobs)
    res = summarize(rows, meta, probs, excl)
    od = Path(args.outdir)
    with open(od / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    sets = set(args.sets.split(","))
    head = {p for p, r in probs.items() if r["set"] in sets and p not in excl}
    models = sorted(meta, key=meta.get)
    ks = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    with open(od / "passk.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "step", "grade", "k", "n_problems", "pass_at_k", "lo95", "hi95"])
        for m in models:
            for g in GRADES:
                pids, M = pass_curve(res, m, ks, g, head)
                if not pids:
                    continue
                lo, hi = boot_ci(M)
                for b, k in enumerate(ks):
                    col = M[:, b]
                    if np.isnan(col).any():
                        continue  # report pass@k only where every headline problem has an estimate
                    w.writerow([m, meta[m], g, k, len(pids), f"{np.mean(col):.4f}", f"{lo[b]:.4f}", f"{hi[b]:.4f}"])
    # Lower bound beyond the fixed budget: problems without samples that far count as unsolved (dead problems were
    # extended for nobody, so this treats every model alike). Rows only where at least one problem was extended.
    with open(od / "passk_lb.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "step", "grade", "k", "n_problems", "pass_at_k", "n_defined"])
        for m in models:
            for g in GRADES:
                pids, M = pass_curve(res, m, ks, g, head)
                if not pids:
                    continue
                max_att = max(r["attempts"] for r in res if r["model"] == m and r["pid"] in head)
                for b, k in enumerate(ks):
                    if k > max_att:
                        break
                    col = M[:, b]
                    nd = int((~np.isnan(col)).sum())
                    if nd == 0 or (k > 1 and not np.isnan(col).any()):
                        if not np.isnan(col).any():
                            w.writerow([m, meta[m], g, k, len(pids), f"{np.mean(col):.4f}", nd])
                        continue
                    w.writerow([m, meta[m], g, k, len(pids), f"{np.nansum(col) / len(col):.4f}", nd])
    print(f"wrote {od/'results.csv'}, {od/'passk.csv'} ({len(res)} model x problem rows, {len(head)} headline problems)")
    reach(res, meta, models, head, od)


def reach(res, meta, models, head, od, base="base"):
    """Reach both ways round, at full budget and at matched k, under each grade; dynamics vs the previous ckpt."""
    by = {(r["model"], r["pid"]): r for r in res}
    rl_models = [m for m in models if m != base]
    k_match = min((by[(m, p)]["n_fixed"] for m in models for p in head if (m, p) in by), default=0)
    rows, dyn = [], []
    for g in GRADES:
        for m in rl_models:
            rch, rev, strong = [], [], []
            for p in sorted(head):
                b, c = by.get((base, p)), by.get((m, p))
                if b is None or c is None:
                    continue
                if c[f"succ_{g}"] >= 1 and b[f"succ_{g}"] == 0:
                    rch.append(p)
                    # strong reach (Part A as amended in Part B): >= 2 correct samples of c including >= 1 fresh
                    # confirmation sample, the base also has no ansline-correct sample, and its budget reached K*
                    if (c[f"succ_{g}"] >= 2 and c[f"succ_confirm_{g}"] >= 1 and b["succ_ansline"] == 0
                            and b["attempts"] >= KSTAR):
                        strong.append(p)
                if b[f"succ_{g}"] >= 1 and c[f"succ_{g}"] == 0:
                    rev.append(p)
            # matched-k expected entries/exits vs base (independent draws => product of unbiased estimates)
            ent = ext = 0.0
            for p in head:
                b, c = by.get((base, p)), by.get((m, p))
                if b is None or c is None:
                    continue
                pb = passk(b["n_fixed"], b[f"succ_fixed_{g}"], k_match)
                pc = passk(c["n_fixed"], c[f"succ_fixed_{g}"], k_match)
                ent += pc * (1 - pb)
                ext += pb * (1 - pc)
            rows.append({"model": m, "step": meta[m], "grade": g, "reach_full": len(rch), "strong_reach": len(strong),
                         "reverse_full": len(rev), f"exp_entries_k{k_match}": round(ent, 3),
                         f"exp_exits_k{k_match}": round(ext, 3), "reach_pids": " ".join(rch),
                         "strong_pids": " ".join(strong), "reverse_pids": " ".join(rev)})
        for a, b_ in zip(rl_models, rl_models[1:]):
            ent = ext = 0.0
            for p in head:
                x, y = by.get((a, p)), by.get((b_, p))
                if x is None or y is None:
                    continue
                px = passk(x["n_fixed"], x[f"succ_fixed_{g}"], k_match)
                py = passk(y["n_fixed"], y[f"succ_fixed_{g}"], k_match)
                ent += py * (1 - px)
                ext += px * (1 - py)
            dyn.append({"from": a, "to": b_, "step": meta[b_], "grade": g, "k": k_match,
                        "exp_entries": round(ent, 3), "exp_exits": round(ext, 3)})
    for name, data in (("reach.csv", rows), ("dynamics.csv", dyn)):
        if data:
            with open(od / name, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                w.writeheader()
                w.writerows(data)
    print(f"wrote reach.csv, dynamics.csv (matched k = {k_match})")


if __name__ == "__main__":
    main()
