#!/usr/bin/env python3
"""Per-model x problem results, unbiased pass@k with problem-bootstrap intervals, matched-k dynamics, candidates.

Inputs: artifacts/olmo32/graded/<job>.jsonl for the jobs in olmo32/jobs.csv (job, model, phase, seed, order),
olmo32/problems.jsonl, olmo32/exclusions.csv (pid, reason).
Outputs (olmo32/): results.csv (one row per model x problem), passk.csv, dynamics.csv, candidates_fixed.csv.

Draw order within (model, problem): jobs in their `order` column (the fixed phase first), then (chunk, i). The
"draw" of a success is its 1-based position in that order. Phases: fixed (the matched-k phase), ext (defender
extension), confirm (challenger fresh samples), s0 (Stage 0, AIME 2024, never reported here), void (unused).
pass@k: Chen et al.'s unbiased estimator on the fixed-phase samples; problem bootstrap (10,000 resamples, seed 0).
Expected entries of c at k: sum_p pass@k_c(p) (1 - pass@k_dpo(p)); exits: sum_p (1 - pass@k_c(p)) pass@k_dpo(p)
(independent draws, so the product of unbiased estimates is unbiased).
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

A = Path("artifacts/olmo32")
O = Path("olmo32")
MODELS = ("dpo", "s0100", "s0750", "s2300")
STEP = {"dpo": 0, "s0100": 100, "s0750": 750, "s2300": 2300}
GRADES = ("rl", "final", "main", "doubly")
B = 10000


def passk(n, c, k):
    if k > n:
        return float("nan")
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def credit(r, g):
    return bool(r["rl"] and r["final"]) if g == "doubly" else bool(r.get(g))


def load(jobs_csv=O / "jobs.csv", grade_dir=A / "graded"):
    jobs = [j for j in csv.DictReader(open(jobs_csv)) if j["phase"] not in ("void", "s0")]
    rows = defaultdict(list)  # (model, pid) -> [(order, chunk, i, phase, job, row)]
    for j in jobs:
        f = grade_dir / f"{j['job']}.jsonl"
        if not f.exists():
            continue
        for ln in open(f):
            r = json.loads(ln)
            rows[(j["model"], r["pid"])].append((int(j["order"]), r["chunk"], r["i"], j["phase"], j["job"], r))
    for k in rows:
        rows[k].sort(key=lambda t: t[:3])
    return rows


def summarize(rows, probs, excl):
    out = []
    for model in MODELS:
        for pid in probs:
            ss = rows.get((model, pid), [])
            if not ss:
                continue
            fixed = [s for s in ss if s[3] == "fixed"]
            rec = {"model": model, "step": STEP[model], "pid": pid, "set": probs[pid]["set"],
                   "excluded": excl.get(pid, ""), "n_fixed": len(fixed), "attempts": len(ss),
                   "n_ext": sum(s[3] == "ext" for s in ss), "n_confirm": sum(s[3] == "confirm" for s in ss)}
            for g in GRADES:
                ok = [credit(s[5], g) for s in ss]
                draws = [i + 1 for i, x in enumerate(ok) if x]
                rec[f"succ_{g}"] = len(draws)
                rec[f"succ_fixed_{g}"] = sum(credit(s[5], g) for s in fixed)
                rec[f"first_{g}"] = draws[0] if draws else ""
                rec[f"second_{g}"] = draws[1] if len(draws) > 1 else ""
            toks = [s[5]["n_tok"] for s in ss]
            rec["mean_tok"] = round(float(np.mean(toks)), 1)
            rec["mean_tok_fixed"] = round(float(np.mean([s[5]["n_tok"] for s in fixed])), 1) if fixed else ""
            rec["sum_tok"] = int(np.sum(toks))
            rec["length_cut"] = sum(s[5]["finish"] == "length" for s in ss)
            rec["think_end"] = sum(bool(s[5].get("think_end")) for s in ss)
            out.append(rec)
    return out


def fixed_matrix(res, model, ks, grade, pids):
    by = {r["pid"]: r for r in res if r["model"] == model}
    M = np.full((len(pids), len(ks)), np.nan)
    for a, pid in enumerate(pids):
        r = by.get(pid)
        if r is None:
            continue
        for b, k in enumerate(ks):
            M[a, b] = passk(r["n_fixed"], r[f"succ_fixed_{grade}"], k)
    return M


def boot(stat_rows, seed=0):
    """stat_rows: (n_problems, ...) per-problem values; returns the 2.5 / 97.5 % of the bootstrap mean or sum."""
    rng = np.random.default_rng(seed)
    n = stat_rows.shape[0]
    idx = rng.integers(0, n, size=(B, n))
    return idx


def main():
    probs = {r["pid"]: r for r in (json.loads(ln) for ln in open(O / "problems.jsonl"))}
    excl = {r["pid"]: r["reason"] for r in csv.DictReader(open(O / "exclusions.csv"))} if (O / "exclusions.csv").exists() else {}
    rows = load()
    res = summarize(rows, probs, excl)
    with open(O / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    head = [p for p in probs if p not in excl]
    have = {r["model"] for r in res}
    ks = (1, 2, 4, 8, 16)
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(head), size=(B, len(head)))
    pk_rows, dyn_rows = [], []
    for g in ("rl", "final"):
        mats = {m: fixed_matrix(res, m, ks, g, head) for m in MODELS if m in have}
        for m, M in mats.items():
            for b, k in enumerate(ks):
                col = M[:, b]
                if np.isnan(col).all():
                    continue
                bs = np.nanmean(col[idx], axis=1)
                pk_rows.append({"grade": g, "model": m, "k": k, "n_problems": int((~np.isnan(col)).sum()),
                                "pass_at_k": round(float(np.nanmean(col)), 4),
                                "lo95": round(float(np.percentile(bs, 2.5)), 4),
                                "hi95": round(float(np.percentile(bs, 97.5)), 4)})
        if "dpo" not in mats:
            continue
        for m in mats:
            if m == "dpo":
                continue
            for k in (1, 8):
                b = ks.index(k)
                pc, pd = mats[m][:, b], mats["dpo"][:, b]
                ent, ext = pc * (1 - pd), (1 - pc) * pd
                diff = pc - pd
                row = {"grade": g, "model": m, "k": k, "n_problems": len(head),
                       "pass_diff": round(float(np.mean(diff)), 4),
                       "pass_diff_lo95": round(float(np.percentile(diff[idx].mean(1), 2.5)), 4),
                       "pass_diff_hi95": round(float(np.percentile(diff[idx].mean(1), 97.5)), 4),
                       "exp_entries": round(float(ent.sum()), 3),
                       "entries_lo95": round(float(np.percentile(ent[idx].sum(1), 2.5)), 3),
                       "entries_hi95": round(float(np.percentile(ent[idx].sum(1), 97.5)), 3),
                       "exp_exits": round(float(ext.sum()), 3),
                       "exits_lo95": round(float(np.percentile(ext[idx].sum(1), 2.5)), 3),
                       "exits_hi95": round(float(np.percentile(ext[idx].sum(1), 97.5)), 3)}
                if k == 8:
                    row["obs_entries"] = int(((pc > 0) & (pd == 0)).sum())
                    row["obs_exits"] = int(((pc == 0) & (pd > 0)).sum())
                dyn_rows.append(row)
    for name, rr in (("passk.csv", pk_rows), ("dynamics.csv", dyn_rows)):
        if rr:
            keys = sorted({k for r in rr for k in r}, key=lambda k: list(rr[-1].keys()).index(k) if k in rr[-1] else 99)
            with open(O / name, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=keys)
                w.writeheader()
                w.writerows(rr)
    # fixed-phase candidates (union of the rl and final definitions), all 60 problems, exclusions flagged
    by = {(r["model"], r["pid"]): r for r in res}
    cand = []
    for pid in probs:
        d = by.get(("dpo", pid))
        if d is None:
            continue
        for g in ("rl", "final"):
            rl_solvers = [m for m in MODELS[1:] if (m, pid) in by and by[(m, pid)][f"succ_fixed_{g}"] > 0]
            if d[f"succ_fixed_{g}"] == 0 and rl_solvers:
                cand.append({"pid": pid, "kind": "reach", "grade": g, "challengers": " ".join(rl_solvers),
                             "excluded": excl.get(pid, "")})
            s = by.get(("s2300", pid))
            if s is not None and d[f"succ_fixed_{g}"] > 0 and s[f"succ_fixed_{g}"] == 0:
                cand.append({"pid": pid, "kind": "reverse", "grade": g, "challengers": "dpo",
                             "excluded": excl.get(pid, "")})
    with open(O / "candidates_fixed.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pid", "kind", "grade", "challengers", "excluded"])
        w.writeheader()
        w.writerows(cand)
    print(f"results.csv {len(res)} rows; passk.csv {len(pk_rows)}; dynamics.csv {len(dyn_rows)}; "
          f"candidates_fixed.csv {len(cand)} (headline set {len(head)} of {len(probs)})")


if __name__ == "__main__":
    main()
