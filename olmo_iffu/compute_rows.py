#!/usr/bin/env python3
"""Compute rows for the results registry (AGENT_POLICY "Record the compute behind every arm"), from the job metas.
olmo_ifomega/compute_rows.py for this run. Per job in olmo_iffu/jobs.csv with a meta file: gpu_seconds = (t_load_s +
t_gen_s) x tp (H200s; meta gpus), gen_tokens, attempts (= samples). No training (train_steps = train_tokens = 0); no
Lean (IF answers: official IFBench / IFEval checkers; OMEGA: OLMES exact match + open-instruct's MathVerifier:
verifier_checks = samples graded). Pod time outside jobs (set-up, downloads, idle, hand-gate waits) is not in these
rows; podbudget's billed hours and dollars are in numbers.md. Writes rows via record.py (ND_RUN_ID=olmo-iffu) and
prints the per-test table. Usage: ND_RUN_ID=olmo-iffu compute_rows.py [--dry] [--only job,job]
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

A = Path("artifacts/olmo_iffu")
O = Path("olmo_iffu")


def main():
    dry = "--dry" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    if not dry:
        sys.path.insert(0, ".")
        import record
    agg = defaultdict(lambda: defaultdict(float))
    for j in csv.DictReader(open(O / "jobs.csv")):
        f = A / "meta" / f"{j['job']}.json"
        if not f.exists() or (only and j["job"] not in only):
            continue
        m = json.loads(open(f).read().strip().splitlines()[-1])
        tp = int(m.get("tp", 1))
        gs = (float(m["t_load_s"]) + float(m["t_gen_s"])) * tp
        key = (j["test"], j["model"])
        agg[key]["gpu_seconds"] += gs
        agg[key]["gen_tokens"] += m["gen_tokens"]
        agg[key]["attempts"] += m["samples"]
        agg[key]["jobs"] += 1
        if not dry:
            lab = dict(arm=j["model"], seed=int(j["seed"]), role="sample", round=j["test"], job=j["job"],
                       gpu=(m.get("gpus") or ["?"])[0], n_gpu=tp, pod=j["pod"],
                       source=f"artifacts/olmo_iffu/meta/{j['job']}.json", derived="(t_load_s + t_gen_s) x tp")
            record.record("gpu_seconds", round(gs, 1), **lab)
            record.record("gen_tokens", int(m["gen_tokens"]), **lab)
            record.record("attempts", int(m["samples"]), **lab)
            for k in ("train_steps", "train_tokens", "lean_checks"):
                record.record(k, 0, **lab)
            record.record("verifier_checks", int(m["samples"]), **lab)
    print("| test | model | jobs | samples | generated tokens | GPU-hours (H200) |")
    print("|---|---|---|---|---|---|")
    for (t, mo), v in sorted(agg.items()):
        print(f"| {t} | {mo} | {int(v['jobs'])} | {int(v['attempts']):,} | {v['gen_tokens'] / 1e6:.2f} M | {v['gpu_seconds'] / 3600:.2f} |")


if __name__ == "__main__":
    main()
