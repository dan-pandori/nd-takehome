#!/usr/bin/env python3
"""Compute rows for the results registry (AGENT_POLICY "Record the compute behind every arm"), run olmo-answeronly (olmo_transplant/compute_rows.py with this run's jobs and a ckpt label).

Per job (meta/<job>.json, last line): gpu_seconds = (t_load_s + t_gen_s [+ phase times for F]) x tp on one H200.
A job mixes conditions, so per condition (arm = writer:cond) the rows carry exact counts from the samples file --
samples (attempts), generated tokens, input tokens (prompt + supplied prefix, once per request; most of it is read from
the prefix cache), checker calls (= samples graded) -- and gpu_seconds apportioned by the condition's share of the
job's generated tokens (derived="apportioned by gen_tokens"). No training (train_steps = train_tokens = 0); no Lean
(the IFBench official checker; lean_checks = 0). Pod time outside jobs (set-up, downloads, idle) is not in these rows;
podbudget's billed hours and dollars are in numbers.md.
Usage: ND_RUN_ID=olmo-answeronly compute_rows.py [--dry]
"""
import collections
import gzip
import json
import os
import sys

A = "artifacts/olmo_answeronly"
JOBS = {"R_dpo": ("oa-1", 8201), "R_s2300": ("oa-1", 8202), "C_dpo": ("oa-1", 8211), "C_s2300": ("oa-1", 8212),
        "L2_dpo": ("oa-1", 8222), "L1_lora": ("oa-1", 8221), "L3_lora": ("oa-1", 8223)}
CKPT = {"dpo": "allenai/Olmo-3-32B-Think-DPO@97604023 (32B bf16)", "s2300": "allenai/Olmo-3.1-32B-Think@97ade57a (step_2300, 32B bf16)",
        "lora_main": "dpo + olmo-ifladder lora/main r16 (sha256 9921a760)"}


def main():
    dry = "--dry" in sys.argv
    if not dry:
        sys.path.insert(0, ".")
        import record
    print("| job | arm (writer:cond) | requests | samples | generated tokens | input tokens | GPU-h (apportioned) |")
    print("|---|---|---|---|---|---|---|")
    tot = collections.Counter()
    for job, (pod, seed) in JOBS.items():
        mf = f"{A}/meta/{job}.json"
        if not os.path.exists(mf):
            continue
        metas = [json.loads(l) for l in open(mf) if l.strip()]
        gs = sum(float(m.get("t_load_s", 0)) + float(m.get("t_gen_s", 0)) + float(m.get("t_phase1_s", 0)) +
                 float(m.get("t_phase2_s", 0)) for m in metas) * int(metas[-1].get("tp", 1))
        agg = collections.defaultdict(collections.Counter)
        seen = set()
        with gzip.open(f"{A}/samples/{job}.jsonl.gz", "rt") as f:
            for ln in f:
                r = json.loads(ln)
                arm = f"{r['writer']}:{r['cond']}"
                a = agg[arm]
                a["samples"] += 1
                a["gen_tokens"] += r["n_tok"] + (r.get("think_n_tok", 0) if r["cond"] == "F" else 0)
                rid = r.get("rid", f"{r['pid']}|{r['cond']}{r.get('cut')}|{r['i']}")
                if rid not in seen or r["cond"] == "F":
                    seen.add(rid)
                    a["requests"] += 1
                    a["input_tokens"] += r["prompt_len"] + r["prefix_len"]
        gen_all = sum(a["gen_tokens"] for a in agg.values())
        for arm, a in sorted(agg.items()):
            share = gs * a["gen_tokens"] / gen_all if gen_all else 0
            tot["gpu_s"] += share
            tot["gen"] += a["gen_tokens"]
            tot["samples"] += a["samples"]
            print(f"| {job} | {arm} | {a['requests']:,} | {a['samples']:,} | {a['gen_tokens'] / 1e6:.2f} M | "
                  f"{a['input_tokens'] / 1e6:.2f} M | {share / 3600:.2f} |")
            if not dry:
                lab = dict(arm=arm, ckpt=CKPT[arm.split(":")[0]], seed=seed, role="sample", round=job, job=job, gpu=(metas[-1].get("gpus") or ["?"])[0],
                           n_gpu=1, pod=pod, source=f"{A}/meta/{job}.json + {A}/samples/{job}.jsonl.gz",
                           derived="gpu_seconds apportioned by gen_tokens within the job; counts exact")
                record.record("gpu_seconds", round(share, 1), **lab)
                record.record("gen_tokens", int(a["gen_tokens"]), **lab)
                record.record("attempts", int(a["samples"]), **lab)
                record.record("input_tokens", int(a["input_tokens"]), **lab)
                for k in ("train_steps", "train_tokens", "lean_checks"):
                    record.record(k, 0, **lab)
                record.record("verifier_checks", int(a["samples"]), **lab)
    print(f"\nall jobs: {tot['samples']:,} samples, {tot['gen'] / 1e6:.2f} M generated tokens, "
          f"{tot['gpu_s'] / 3600:.2f} H200-hours in jobs")


if __name__ == "__main__":
    main()
