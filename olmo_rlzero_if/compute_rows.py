#!/usr/bin/env python3
"""Compute rows for the results registry (AGENT_POLICY "Record the compute behind every arm"), derived from job files.

olmo_ifomega/compute_rows.py for run olmo-rlzero-if, with the olmo-ifomega review's fix: samples and generated tokens
are counted from the graded rows (every segment of a resumed job), GPU-seconds summed over every meta line (one per
job segment: (t_load_s + t_gen_s) x tp). GPU type from the meta. No training (train_steps = train_tokens = 0), no Lean
(the official IF checkers judge: verifier_checks = samples graded). Pod time outside jobs (setup, downloads, idle) is
not in these rows; billed pod costs are in numbers.md.
Usage: ND_RUN_ID=olmo-rlzero-if compute_rows.py [--dry] [--only job,job]
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

A, O = Path("artifacts/olmo_rlzero_if"), Path("olmo_rlzero_if")


def main():
    dry = "--dry" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    if not dry:
        sys.path.insert(0, ".")
        import record
    agg = defaultdict(lambda: defaultdict(float))
    for j in csv.DictReader(open(O / "jobs.csv")):
        if only and j["job"] not in only:
            continue
        mf, gf = A / "meta" / f"{j['job']}.json", A / "graded" / f"{j['job']}.jsonl"
        if not mf.exists() or not gf.exists():
            continue
        metas = [json.loads(ln) for ln in open(mf) if ln.strip()]
        gs = sum((float(m["t_load_s"]) + float(m["t_gen_s"])) * int(m.get("tp", 1)) for m in metas)
        rows = [json.loads(ln) for ln in open(gf)]
        tok, n = sum(r["n_tok"] for r in rows), len(rows)
        key = (j["model"], j["phase"])
        for k, v in (("gpu_seconds", gs), ("gen_tokens", tok), ("attempts", n), ("jobs", 1)):
            agg[key][k] += v
        if not dry:
            lab = dict(arm=j["model"], seed=int(j["seed"]), role="sample", source=f"artifacts/olmo_rlzero_if/graded/{j['job']}.jsonl",
                       phase=j["phase"], job=j["job"], gpu=(metas[-1].get("gpus") or ["?"])[0], n_gpu=int(metas[-1].get("tp", 1)),
                       pod=j.get("pod"), derived="gpu_seconds from every meta line; tokens and samples from the graded rows")
            record.record("gpu_seconds", round(gs, 1), **lab)
            record.record("gen_tokens", int(tok), **lab)
            record.record("attempts", int(n), **lab)
            for k in ("train_steps", "train_tokens", "lean_checks"):
                record.record(k, 0, **lab)
            record.record("verifier_checks", int(n), **lab)
    print(f"{'model':8s} {'phase':8s} {'jobs':>4s} {'GPU-h':>7s} {'gen tokens':>12s} {'samples':>8s}")
    for (mo, ph), v in sorted(agg.items()):
        print(f"{mo:8s} {ph:8s} {int(v['jobs']):4d} {v['gpu_seconds'] / 3600:7.2f} {int(v['gen_tokens']):12,d} {int(v['attempts']):8d}")


if __name__ == "__main__":
    main()
