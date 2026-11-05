#!/usr/bin/env python3
"""Compute rows for the results registry (AGENT_POLICY "Record the compute behind every arm"), derived from job files.

olmo32/compute_rows.py for this run. Per job in olmo_ifomega/jobs.csv with a meta file: gpu_seconds = model load +
generation wall-clock (meta t_load_s + t_gen_s) x GPUs (meta tp; one H200 for every evaluation job, 2 x A100 for
Stage 0's s0_s2300), labels.gpu from meta, gen_tokens (meta gen_tokens), attempts (samples). No training happens in
this run (train_steps = train_tokens = 0) and no Lean is involved (IF answers are checked by the official IFBench /
IFEval checkers, OMEGA answers by OLMES's exact match and open-instruct's math verifier: verifier_checks = samples
graded). Pod time not spent in a job (setup, downloads, contamination scans, idle between jobs) is not in these rows;
podbudget's billed hours are in numbers.md. Stage-0 jobs have no meta of the final format: their rows come from
stage0_summary.json (generation seconds and tokens as measured when they were stopped at the $8 cap).
Writes rows via record.py (ND_RUN_ID=olmo-ifomega) and prints the per-arm table (arm = model, phase).

Usage: ND_RUN_ID=olmo-ifomega compute_rows.py [--dry]
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

A = Path("artifacts/olmo_ifomega")
O = Path("olmo_ifomega")


def metas():
    out = {}
    for j in csv.DictReader(open(O / "jobs.csv")):
        f = A / "meta" / f"{j['job']}.json"
        if f.exists():
            m = json.loads(open(f).read().strip().splitlines()[-1])
            out[j["job"]] = (j, m)
    return out


def main():
    dry = "--dry" in sys.argv
    rows = metas()
    agg = defaultdict(lambda: defaultdict(float))
    if not dry:
        sys.path.insert(0, ".")
        import record
    for job, (j, m) in rows.items():
        gs = (float(m["t_load_s"]) + float(m["t_gen_s"])) * int(m.get("tp", 1))
        key = (j["model"], j["phase"])
        agg[key]["gpu_seconds"] += gs
        agg[key]["gen_tokens"] += m["gen_tokens"]
        agg[key]["attempts"] += m["samples"]
        agg[key]["jobs"] += 1
        if not dry:
            lab = dict(arm=j["model"], seed=int(j["seed"]), role="sample", source=f"artifacts/olmo_ifomega/meta/{job}.json",
                       phase=j["phase"], job=job, gpu=(m.get("gpus") or [m.get("gpu")])[0], n_gpu=int(m.get("tp", 1)),
                       pod=j.get("pod"), derived="from job meta ((t_load_s + t_gen_s) x tp)", note=m.get("note"))
            record.record("gpu_seconds", round(gs, 1), **lab)
            record.record("gen_tokens", int(m["gen_tokens"]), **lab)
            record.record("attempts", int(m["samples"]), **lab)
            record.record("train_steps", 0, **lab)
            record.record("train_tokens", 0, **lab)
            record.record("lean_checks", 0, **lab)
            record.record("verifier_checks", int(m["samples"]), **lab)
    print(f"{'model':10s} {'phase':10s} {'jobs':>4s} {'GPU-h':>7s} {'gen tokens':>12s} {'samples':>8s}")
    for (mo, ph), v in sorted(agg.items()):
        print(f"{mo:10s} {ph:10s} {int(v['jobs']):4d} {v['gpu_seconds'] / 3600:7.2f} {int(v['gen_tokens']):12,d} "
              f"{int(v['attempts']):8d}")


if __name__ == "__main__":
    main()
