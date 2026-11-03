#!/usr/bin/env python3
"""Compute rows for the results registry (AGENT_POLICY "Record the compute behind every arm"), derived from job files.

Per job in olmo_pilot/jobs.csv with a meta file: gpu_seconds = model load + generation wall-clock (meta t_load_s +
t_gen_s; one GPU; labels.gpu from meta), gen_tokens (meta gen_tokens), attempts (samples). No training happens in
this run (train_steps = train_tokens = 0) and no Lean is involved (answers are checked by open-instruct's math
verifier; verifier_checks = samples graded). Likelihood scoring jobs (phase L) are added from their logs.
Writes rows via record.py (ND_RUN_ID=olmo-rlzero-pilot) and prints the per-arm table (arm = model, phase).

Usage: ND_RUN_ID=olmo-rlzero-pilot compute_rows.py [--dry]
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

A = Path("artifacts/olmo_pilot")
O = Path("olmo_pilot")


# Jobs whose meta file is missing: P_base (meta lost with pod orz-a; tokens from its graded file, time estimated at
# F_base's 777 tok/s plus one model load) and the two void step_0100 runs (GPU time from their log timestamps).
EXTRA = {
    "P_base": {"gpu": "NVIDIA A100-SXM4-80GB", "derive": "graded", "tok_per_s": 777.3, "t_load_s": 72.0, "spec_ngram": 4},
    "F_s0100": {"gpu": "NVIDIA A100-SXM4-80GB", "t_gen_s": (54 - 21) * 60, "t_load_s": 72.0, "samples": 0,
                "gen_tokens": 0, "spec_ngram": 4, "note": "void: JOB_START 07:21, pod orz-a lost ~07:54 (host restart)"},
    "F_s0100b": {"gpu": "NVIDIA A100-SXM4-80GB", "t_gen_s": (57 - 0) * 60 - 72, "t_load_s": 72.0, "samples": 0,
                 "gen_tokens": 0, "spec_ngram": 4, "note": "void: JOB_START ~07:58, stopped 08:57 for budget"},
}


def metas():
    out = {}
    for j in csv.DictReader(open(O / "jobs.csv")):
        f = A / "meta" / f"{j['job']}.json"
        if f.exists():
            m = json.loads(open(f).read().strip().splitlines()[-1])
            out[j["job"]] = (j, m)
        elif j["job"] in EXTRA:
            e = dict(EXTRA[j["job"]])
            if e.pop("derive", None) == "graded":
                rows = [json.loads(ln) for ln in open(A / "graded" / f"{j['job']}.jsonl")]
                e["samples"], e["gen_tokens"] = len(rows), sum(r["n_tok"] for r in rows)
                e["t_gen_s"] = e["gen_tokens"] / e.pop("tok_per_s")
                e["note"] = "estimated: meta lost with pod orz-a; tokens from graded file, time at F_base's tok/s"
            out[j["job"]] = (j, e)
    return out


def main():
    dry = "--dry" in sys.argv
    rows = metas()
    agg = defaultdict(lambda: defaultdict(float))
    if not dry:
        sys.path.insert(0, ".")
        import record
    for job, (j, m) in rows.items():
        gs = float(m["t_load_s"]) + float(m["t_gen_s"])
        key = (j["model"], j["phase"])
        agg[key]["gpu_seconds"] += gs
        agg[key]["gen_tokens"] += m["gen_tokens"]
        agg[key]["attempts"] += m["samples"]
        agg[key]["jobs"] += 1
        if not dry:
            lab = dict(arm=j["model"], seed=int(j["seed"]), role="sample", source=f"artifacts/olmo_pilot/meta/{job}.json",
                       phase=j["phase"], job=job, gpu=m["gpu"], n_gpu=1, derived="from job meta (t_load_s + t_gen_s)",
                       spec_ngram=m.get("spec_ngram", 0), note=m.get("note"))
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
