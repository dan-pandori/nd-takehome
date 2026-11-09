#!/usr/bin/env python3
"""Compute rows for the results registry (AGENT_POLICY "Record the compute behind every arm"), from the job metas and the
LoRA training reports. olmo_iffu/compute_rows.py for this run. Sampling jobs (olmo_ifladder/jobs.csv with a meta):
gpu_seconds = (t_load_s + t_gen_s) x tp (H200), gen_tokens, attempts (= samples), verifier_checks (= samples graded).
LoRA training (meta/lora_<arm>.json): gpu_seconds = secs_total (load excluded; it covers base NLL, training, PEFT and
merged NLL, merge and save), train_steps, train_tokens (prompt + response tokens of the steps). No Lean (IF answers:
official IFBench / IFEval checkers). Pod time outside jobs (set-up, downloads, idle) is not in these rows; podbudget's
billed hours and dollars are in numbers.md. Writes rows via record.py (ND_RUN_ID=olmo-ifladder) and prints the per-arm
table. Usage: ND_RUN_ID=olmo-ifladder compute_rows.py [--dry]
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

A = Path("artifacts/olmo_ifladder")
O = Path("olmo_ifladder")


def main():
    dry = "--dry" in sys.argv
    if not dry:
        sys.path.insert(0, ".")
        import record
    agg = defaultdict(lambda: defaultdict(float))
    for j in csv.DictReader(open(O / "jobs.csv")):
        f = A / "meta" / f"{j['job']}.json"
        if not f.exists():
            continue
        m = json.loads(open(f).read().strip().splitlines()[-1])
        tp = int(m.get("tp", 1))
        gs = (float(m["t_load_s"]) + float(m["t_gen_s"])) * tp
        key = (j["arm"], j["model"], j["rung"])
        agg[key]["gpu_seconds"] += gs
        agg[key]["gen_tokens"] += m["gen_tokens"]
        agg[key]["attempts"] += m["samples"]
        agg[key]["jobs"] += 1
        if not dry:
            lab = dict(arm=j["model"], seed=int(j["seed"]), role="sample", round=f"{j['arm']}-r{j['rung']}", job=j["job"],
                       gpu=(m.get("gpus") or ["?"])[0], n_gpu=tp, pod=j["pod"],
                       source=f"artifacts/olmo_ifladder/meta/{j['job']}.json", derived="(t_load_s + t_gen_s) x tp")
            record.record("gpu_seconds", round(gs, 1), **lab)
            record.record("gen_tokens", int(m["gen_tokens"]), **lab)
            record.record("attempts", int(m["samples"]), **lab)
            for k in ("train_steps", "train_tokens", "lean_checks"):
                record.record(k, 0, **lab)
            record.record("verifier_checks", int(m["samples"]), **lab)
    for arm in ("main", "ctrl"):
        f = A / "meta" / f"lora_{arm}.json"
        if not f.exists():
            continue
        m = json.load(open(f))
        key = ("lora-train", f"lora_{arm}", "-")
        agg[key]["gpu_seconds"] += m["secs_total"]
        agg[key]["train_steps"] += m["steps"]
        agg[key]["train_tokens"] += m["train_tokens"]
        agg[key]["jobs"] += 1
        if not dry:
            lab = dict(arm=f"lora_{arm}", seed=m["recipe"]["seed"], role="train", round="lora", job=f"lora_{arm}",
                       gpu=m.get("gpu", "?"), n_gpu=1, pod="ifl-a", source=f"artifacts/olmo_ifladder/meta/lora_{arm}.json",
                       derived="secs_total of the training process (model load excluded)")
            record.record("gpu_seconds", round(m["secs_total"], 1), **lab)
            record.record("train_steps", int(m["steps"]), **lab)
            record.record("train_tokens", int(m["train_tokens"]), **lab)
            for k in ("gen_tokens", "attempts", "lean_checks"):
                record.record(k, 0, **lab)
    print("| arm | model | rung | jobs | samples | generated tokens | train steps | train tokens | GPU-hours (H200) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (a, mo, r), v in sorted(agg.items()):
        print(f"| {a} | {mo} | {r} | {int(v['jobs'])} | {int(v['attempts']):,} | {v['gen_tokens'] / 1e6:.2f} M | "
              f"{int(v['train_steps'])} | {int(v['train_tokens']):,} | {v['gpu_seconds'] / 3600:.2f} |")


if __name__ == "__main__":
    main()
