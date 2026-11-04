#!/usr/bin/env python3
"""Per-model x prompt results, unbiased pass@k with prompt-bootstrap intervals, matched-k dynamics, candidates.

olmo32/analyze.py (run olmo-think32b) generalised to tasks. Inputs: artifacts/olmo_ifomega/graded/<job>.jsonl for the
jobs in olmo_ifomega/jobs.csv (job, model, phase, seed, order, ...), olmo_ifomega/problems.jsonl,
olmo_ifomega/exclusions.csv (pid, reason). Outputs (olmo_ifomega/): results.csv (one row per model x prompt),
passk.csv, dynamics.csv, candidates_fixed.csv.

Grades: IF tasks strict (primary), loose, rlview; OMEGA tasks omega (primary), rl, doubly (= omega and rl).
Draw order within (model, prompt): jobs in their `order` column (the fixed phase first), then (chunk, i); a success's
"draw" is its 1-based position. Phases: fixed, ext (defender extension), confirm (challenger fresh samples), s0
(Stage 0, never reported here), void (unused). pass@k: Chen et al.'s unbiased estimator on the fixed-phase samples;
prompt bootstrap within each task (10,000 resamples, seed 0). Expected entries of c at k: sum_p pass@k_c(p)
(1 - pass@k_dpo(p)); exits: sum_p (1 - pass@k_c(p)) pass@k_dpo(p).
Candidates (fixed phase): reach = dpo 0 / 16 and some RL checkpoint >= 1 / 8; reverse = dpo >= 1 / 16 and s2300 0 / 8;
IF on strict, OMEGA on the union of omega and rl.
"""
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

A = Path("artifacts/olmo_ifomega")
O = Path("olmo_ifomega")
MODELS = ("dpo", "s0100", "s0750", "s2300")
STEP = {"dpo": 0, "s0100": 100, "s0750": 750, "s2300": 2300}
TASKS = ("ifbench", "ifeval", "omega_in", "omega_out")
GRADES = {"ifbench": ("strict", "loose", "rlview"), "ifeval": ("strict", "loose", "rlview"),
          "omega_in": ("omega", "rl", "doubly"), "omega_out": ("omega", "rl", "doubly")}
CAND = {"ifbench": ("strict",), "ifeval": ("strict",), "omega_in": ("omega", "rl"), "omega_out": ("omega", "rl")}
B = 10000


def passk(n, c, k):
    if k > n:
        return float("nan")
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def credit(r, g):
    return bool(r.get(g))


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
        for pid, p in probs.items():
            ss = rows.get((model, pid), [])
            if not ss:
                continue
            fixed = [s for s in ss if s[3] == "fixed"]
            rec = {"model": model, "step": STEP[model], "pid": pid, "task": p["task"], "family": p.get("family", ""),
                   "excluded": excl.get(pid, ""), "n_fixed": len(fixed), "attempts": len(ss),
                   "n_ext": sum(s[3] == "ext" for s in ss), "n_confirm": sum(s[3] == "confirm" for s in ss)}
            for g in ("strict", "loose", "rlview", "omega", "rl", "doubly"):
                if g not in GRADES[p["task"]]:
                    for x in ("succ", "succ_fixed", "first", "second"):
                        rec[f"{x}_{g}"] = ""
                    continue
                ok = [credit(s[5], g) for s in ss]
                draws = [i + 1 for i, x in enumerate(ok) if x]
                rec[f"succ_{g}"] = len(draws)
                rec[f"succ_fixed_{g}"] = sum(credit(s[5], g) for s in fixed)
                rec[f"first_{g}"] = draws[0] if draws else ""
                rec[f"second_{g}"] = draws[1] if len(draws) > 1 else ""
            if p["task"] in ("ifbench", "ifeval"):  # per-constraint successes over the fixed phase, ';'-joined
                per = np.array([s[5]["per"] for s in fixed], dtype=float) if fixed else np.zeros((0, 0))
                rec["per_constraint_fixed"] = ";".join(str(int(x)) for x in per.sum(0)) if len(per) else ""
            else:
                rec["per_constraint_fixed"] = ""
            toks = [s[5]["n_tok"] for s in ss]
            rec["mean_tok"] = round(float(np.mean(toks)), 1)
            rec["mean_tok_fixed"] = round(float(np.mean([s[5]["n_tok"] for s in fixed])), 1) if fixed else ""
            rec["sum_tok"] = int(np.sum(toks))
            rec["length_cut"] = sum(s[5]["finish"] == "length" for s in ss)
            rec["length_cut_fixed"] = sum(s[5]["finish"] == "length" for s in fixed)
            rec["think_end"] = sum(bool(s[5].get("think_end")) for s in ss)
            out.append(rec)
    return out


def fixed_matrix(res, model, k, grade, pids):
    by = {r["pid"]: r for r in res if r["model"] == model}
    v = np.full(len(pids), np.nan)
    for a, pid in enumerate(pids):
        r = by.get(pid)
        if r is not None and r["n_fixed"]:
            v[a] = passk(r["n_fixed"], r[f"succ_fixed_{grade}"], k)
    return v


def write(name, rr):
    if not rr:
        return
    keys = []
    for r in rr:
        keys += [k for k in r if k not in keys]
    with open(O / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rr)


def main():
    probs = {r["pid"]: r for r in (json.loads(ln) for ln in open(O / "problems.jsonl"))}
    excl = {r["pid"]: r["reason"] for r in csv.DictReader(open(O / "exclusions.csv"))} \
        if (O / "exclusions.csv").exists() else {}
    rows = load()
    res = summarize(rows, probs, excl)
    write("results.csv", res)
    have = {r["model"] for r in res}
    pk_rows, dyn_rows, cand = [], [], []
    for task in TASKS:
        head = [p for p in probs if probs[p]["task"] == task and p not in excl
                and any(r["pid"] == p and r["model"] == "dpo" for r in res)]
        if not head:
            continue
        idx = np.random.default_rng(0).integers(0, len(head), size=(B, len(head)))
        for g in GRADES[task]:
            vec = {m: {k: fixed_matrix(res, m, k, g, head) for k in (1, 2, 4, 8, 16)} for m in MODELS if m in have}
            for m in vec:
                for k, col in vec[m].items():
                    if np.isnan(col).all():
                        continue
                    bs = np.nanmean(col[idx], axis=1)
                    pk_rows.append({"task": task, "grade": g, "model": m, "k": k,
                                    "n_prompts": int((~np.isnan(col)).sum()),
                                    "pass_at_k": round(float(np.nanmean(col)), 4),
                                    "lo95": round(float(np.nanpercentile(bs, 2.5)), 4),
                                    "hi95": round(float(np.nanpercentile(bs, 97.5)), 4)})
            if "dpo" not in vec:
                continue
            for m in vec:
                if m == "dpo":
                    continue
                for k in (1, 8):
                    pc, pd = vec[m][k], vec["dpo"][k]
                    ok = ~np.isnan(pc) & ~np.isnan(pd)
                    if not ok.any():
                        continue
                    ent, ext, diff = pc * (1 - pd), (1 - pc) * pd, pc - pd
                    ent, ext, diff = (np.where(ok, x, 0.0) for x in (ent, ext, diff))
                    n = int(ok.sum())
                    row = {"task": task, "grade": g, "model": m, "k": k, "n_prompts": n,
                           "pass_diff": round(float(diff.sum() / n), 4),
                           "pass_diff_lo95": round(float(np.percentile(diff[idx].sum(1) / ok[idx].sum(1), 2.5)), 4),
                           "pass_diff_hi95": round(float(np.percentile(diff[idx].sum(1) / ok[idx].sum(1), 97.5)), 4),
                           "exp_entries": round(float(ent.sum()), 3),
                           "entries_lo95": round(float(np.percentile(ent[idx].sum(1), 2.5)), 3),
                           "entries_hi95": round(float(np.percentile(ent[idx].sum(1), 97.5)), 3),
                           "exp_exits": round(float(ext.sum()), 3),
                           "exits_lo95": round(float(np.percentile(ext[idx].sum(1), 2.5)), 3),
                           "exits_hi95": round(float(np.percentile(ext[idx].sum(1), 97.5)), 3)}
                    if k == 8:
                        row["obs_entries"] = int(((pc > 0) & (pd == 0) & ok).sum())
                        row["obs_exits"] = int(((pc == 0) & (pd > 0) & ok).sum())
                    dyn_rows.append(row)
        by = {(r["model"], r["pid"]): r for r in res}
        for pid in [p for p in probs if probs[p]["task"] == task]:
            d = by.get(("dpo", pid))
            if d is None or not d["n_fixed"]:
                continue
            for g in CAND[task]:
                solvers = [m for m in MODELS[1:] if (m, pid) in by and by[(m, pid)][f"succ_fixed_{g}"]]
                if d[f"succ_fixed_{g}"] == 0 and solvers:
                    cand.append({"task": task, "pid": pid, "kind": "reach", "grade": g, "challengers": " ".join(solvers),
                                 "excluded": excl.get(pid, "")})
                s = by.get(("s2300", pid))
                if s is not None and s["n_fixed"] and d[f"succ_fixed_{g}"] > 0 and s[f"succ_fixed_{g}"] == 0:
                    cand.append({"task": task, "pid": pid, "kind": "reverse", "grade": g, "challengers": "dpo",
                                 "excluded": excl.get(pid, "")})
    write("passk.csv", pk_rows)
    write("dynamics.csv", dyn_rows)
    with open(O / "candidates_fixed.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["task", "pid", "kind", "grade", "challengers", "excluded"])
        w.writeheader()
        w.writerows(cand)
    print(f"results.csv {len(res)} rows; passk.csv {len(pk_rows)}; dynamics.csv {len(dyn_rows)}; "
          f"candidates_fixed.csv {len(cand)}", file=sys.stderr)


if __name__ == "__main__":
    main()
