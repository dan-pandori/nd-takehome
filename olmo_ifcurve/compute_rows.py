#!/usr/bin/env python3
"""Compute rows of run olmo-ifcurve for the results registry (AGENT_POLICY "Record the compute behind every arm"), from
the job metas (artifacts/olmo_ifcurve/meta/<job>.json and <job>_stage0.json; a resumed job appends one JSON line per
run). olmo_ifladder/compute_rows.py adapted. Per job run: gpu_seconds = (t_load_s + t_gen_s) x tp (H200), gen_tokens,
attempts (= samples), verifier_checks (= samples graded), train_steps / train_tokens / lean_checks = 0 (no training,
no Lean: official IFBench / IFEval checkers). Pod time outside jobs (set-up, downloads, idle, the 2026-11-21 orphaned
pods) is not in these rows; podbudget's billed hours and dollars are in numbers.md. Arms: a job's draws split into arm A
(chunk 0, or chunks 0-1 for M8 non-reach prompts) and arm B by draw count in the table, not in the registry rows.

  ND_RUN_ID=olmo-ifcurve python3 olmo_ifcurve/compute_rows.py [--dry]
"""
import csv
import json
import sys
from pathlib import Path

M = Path("artifacts/olmo_ifcurve/meta")


def runs():
    for f in sorted(M.glob("*.json")):
        if f.name.startswith(("pod_env", "pip_freeze", "stage0_projection")) or f.name.endswith(".done"):
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
        rows.append({"meta": f.name, "run": k, "job": m["job"], "ckpt": m["name"], "rev": m["rev"], "seed": m["seed"],
                     "gpu": (m.get("gpus") or ["?"])[0], "tp": tp, "gpu_seconds": round(gs, 1),
                     "gen_tokens": m["gen_tokens"], "attempts": m["samples"], "length_cut": m["length_cut"],
                     "tok_per_s": m["tok_per_s"]})
        if not dry:
            lab = dict(arm=m["name"], seed=int(m["seed"]), role="sample", round=m["job"], job=m["job"], gpu=rows[-1]["gpu"],
                       n_gpu=tp, source=f"artifacts/olmo_ifcurve/meta/{f.name}#{k}", derived="(t_load_s + t_gen_s) x tp")
            record.record("gpu_seconds", round(gs, 1), **lab)
            record.record("gen_tokens", int(m["gen_tokens"]), **lab)
            record.record("attempts", int(m["samples"]), **lab)
            for key in ("train_steps", "train_tokens", "lean_checks"):
                record.record(key, 0, **lab)
            record.record("verifier_checks", int(m["samples"]), **lab)
    if rows:
        with open("olmo_ifcurve/compute.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    tot = {}
    for r in rows:
        t = tot.setdefault(r["ckpt"], [0.0, 0, 0])
        t[0] += r["gpu_seconds"]
        t[1] += r["gen_tokens"]
        t[2] += r["attempts"]
    print("ckpt  GPU-h  gen_Mtok  draws")
    for c, (g, t, a) in sorted(tot.items()):
        print(f"{c:6} {g / 3600:6.2f} {t / 1e6:8.2f} {a:6d}")


if __name__ == "__main__":
    main()
