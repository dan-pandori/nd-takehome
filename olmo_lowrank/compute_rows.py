#!/usr/bin/env python3
"""Compute rows of run olmo-lowrank for the results registry (AGENT_POLICY "Record the compute behind every arm").
Sampling: per job run (artifacts/olmo_lowrank/meta/<arm>.json, <arm>_stage0.json): gpu_seconds = (t_load_s + t_gen_s)
x tp on one H200, gen_tokens, attempts (= samples), verifier_checks (= samples graded by the official IFBench / IFEval
checkers); train_steps / train_tokens / lean_checks = 0 (no training, no Lean). Part 1 / adapters: GPU-seconds of the
spectra jobs (summary.json wall_s, download waits included) and of the adapter SVD (factors/norms.csv seconds,
logged in stage0). Pod time outside jobs (set-up, downloads before a job, idle) is not in these rows; podbudget's
billed hours and dollars are in numbers.md.

  ND_RUN_ID=olmo-lowrank python3 olmo_lowrank/compute_rows.py [--dry]
"""
import csv
import json
import sys
from pathlib import Path

M = Path("artifacts/olmo_lowrank/meta")
S = Path("artifacts/olmo_lowrank/spectra")


def runs():
    for f in sorted(M.glob("*.json")):
        if f.name.startswith(("pod_env", "pip_freeze", "f448_check", "gpu_")) or f.name.endswith(".done"):
            continue
        for k, ln in enumerate(open(f).read().strip().splitlines()):
            try:
                m = json.loads(ln)
            except json.JSONDecodeError:
                continue
            if "gen_tokens" in m:
                yield f, k, m


def main():
    dry = "--dry" in sys.argv
    if not dry:
        sys.path.insert(0, ".")
        import record
    rows = []
    for f, k, m in runs():
        tp = int(m.get("tp", 1))
        gs = (float(m["t_load_s"]) + float(m["t_gen_s"])) * tp
        arm = m["job"]
        rows.append({"meta": f.name, "run": k, "job": arm, "model": m["name"], "seed": m["seed"], "gpu": "NVIDIA H200",
                     "tp": tp, "gpu_seconds": round(gs, 1), "gen_tokens": m["gen_tokens"], "attempts": m["samples"],
                     "length_cut": m["length_cut"], "tok_per_s": m["tok_per_s"]})
        if not dry:
            lab = dict(arm=arm, seed=int(m["seed"]), role="sample", round=arm, job=arm, gpu="NVIDIA H200", n_gpu=tp,
                       source=f"artifacts/olmo_lowrank/meta/{f.name}#{k}", derived="(t_load_s + t_gen_s) x tp")
            record.record("gpu_seconds", round(gs, 1), **lab)
            record.record("gen_tokens", int(m["gen_tokens"]), **lab)
            record.record("attempts", int(m["samples"]), **lab)
            for key in ("train_steps", "train_tokens", "lean_checks"):
                record.record(key, 0, **lab)
            record.record("verifier_checks", int(m["samples"]), **lab)
    for j in ("R32", "S32", "R7"):
        p = S / j / "summary.json"
        if p.exists():
            sm = json.load(open(p))
            rows.append({"meta": str(p), "run": 0, "job": f"spectra_{j}", "model": j, "seed": "", "gpu": sm.get("gpu", ""),
                         "tp": 1, "gpu_seconds": sm.get("wall_s", ""), "gen_tokens": 0, "attempts": 0, "length_cut": "",
                         "tok_per_s": ""})
            if not dry and sm.get("wall_s"):
                record.record("gpu_seconds", float(sm["wall_s"]), arm=f"spectra_{j}", seed=0, role="analysis",
                              round=j, job=f"spectra_{j}", gpu=sm.get("gpu", ""), n_gpu=1, source=str(p),
                              derived="summary.json wall_s (downloads overlapped)")
    p = Path("artifacts/olmo_lowrank/stage0/N2300_norms.csv")
    if p.exists():
        sec = sum(float(r["seconds"]) for r in csv.DictReader(open(p)))
        rows.append({"meta": str(p), "run": 0, "job": "adapters_svd", "model": "N2300", "seed": "", "gpu": "NVIDIA H200",
                     "tp": 1, "gpu_seconds": round(sec, 1), "gen_tokens": 0, "attempts": 0, "length_cut": "", "tok_per_s": ""})
        if not dry:
            record.record("gpu_seconds", round(sec, 1), arm="adapters_svd", seed=0, role="analysis", round="adapters",
                          job="adapters_svd", gpu="NVIDIA H200", n_gpu=1, source=str(p), derived="sum of per-matrix SVD seconds")
    if rows:
        with open("olmo_lowrank/compute.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    tot = {}
    for r in rows:
        t = tot.setdefault(r["job"], [0.0, 0, 0])
        t[0] += float(r["gpu_seconds"] or 0)
        t[1] += int(r["gen_tokens"] or 0)
        t[2] += int(r["attempts"] or 0)
    for j, (g, t, a) in sorted(tot.items()):
        print(f"{j:14s} gpu_s {g:9.1f} gen_tokens {t:10d} attempts {a:6d}")


if __name__ == "__main__":
    main()
