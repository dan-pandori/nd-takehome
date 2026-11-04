#!/usr/bin/env python3
"""Compute rows for the results registry (AGENT_POLICY "Record the compute behind every arm"), derived from job files.

Per job in olmo32/jobs.csv with a meta file: gpu_seconds = model load + generation wall-clock (meta t_load_s +
t_gen_s) x GPUs (TP 1 on one H200 throughout), labels.gpu from meta, gen_tokens (meta gen_tokens), attempts (samples).
No training happens in this run (train_steps = train_tokens = 0) and no Lean is involved (answers are checked by
open-instruct's math verifier and the final-answer grade; verifier_checks = samples graded). The likelihood job
(phase L) is prompt scoring: gen_tokens 0, its scored tokens in labels. Pod time not spent in a job (setup, downloads,
idle between jobs) is not in these rows; podbudget's billed hours are in numbers.md.
Writes rows via record.py (ND_RUN_ID=olmo-think32b) and prints the per-arm table (arm = model, phase).

Usage: ND_RUN_ID=olmo-think32b compute_rows.py [--dry]
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

A = Path("artifacts/olmo32")
O = Path("olmo32")


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
            lab = dict(arm=j["model"], seed=int(j["seed"]), role="sample", source=f"artifacts/olmo32/meta/{job}.json",
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
