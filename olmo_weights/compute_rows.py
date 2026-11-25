#!/usr/bin/env python3
"""Compute rows for the results registry (AGENT_POLICY "Record the compute behind every arm") for olmo-weights.

One arm per job (manifest/jobs.json). Per job, from artifacts/olmo_weights/stats/<job>/summary.json (every engine run
of the job, including failed tries that were resumed) and files.csv:
  gpu_seconds   = the engine's wall seconds on its pod (1 x NVIDIA A40, secure, billed $0.59/h); the pod ran one job
                  at a time, so this is the job's share of pod time (setup, transfers between jobs and idle are not in
                  it; podbudget's billed hours are in numbers.md)
  gen_tokens 0, train_steps 0, train_tokens 0, lean_checks 0 (no generation, training or Lean in this run)
  bytes_downloaded, files_verified (sha256 checked against the manifest), checkpoints (members)
Writes rows via record.py (ND_RUN_ID=olmo-weights) unless --dry, and prints the per-arm table (markdown).
Usage: ND_RUN_ID=olmo-weights python3 olmo_weights/compute_rows.py [--dry]
"""
import csv, json, os, sys

S = "artifacts/olmo_weights/stats"
J = json.load(open("olmo_weights/manifest/jobs.json"))
POD = {"b32_s1": "ow-a", "p32_rl": "ow-b", "b32_s2": "ow-c", "b32_s3": "ow-c", "p32_sft": "ow-f", "b7_s1": "ow-d",
       "b7_s2": "ow-d", "b7_s3": "ow-e", "p7_sft": "ow-e", "p7_rl": "ow-e", "z7_if": "ow-e", "z7_math": "ow-e",
       "z7_code": "ow-e"}


def main():
    dry = "--dry" in sys.argv
    if not dry:
        sys.path.insert(0, ".")
        import record
    rows = []
    for job in J:
        p = os.path.join(S, job, "summary.json")
        if not os.path.exists(p):
            continue
        runs = json.load(open(p))["runs"]
        wall = sum(r["wall_s"] for r in runs)
        comp = sum(r["compute_s"] for r in runs)
        dl = sum(r["downloaded_bytes"] for r in runs)
        nf = 0
        fp = os.path.join(S, job, "files.csv")
        if os.path.exists(fp):
            nf = sum(1 for r in csv.reader(open(fp)) if len(r) > 6 and r[6] == "ok")
        row = dict(job=job, pod=POD.get(job, "?"), runs=len(runs), gpu_seconds=round(wall, 1), compute_seconds=round(comp, 1),
                   bytes_downloaded=dl, files_verified=nf, checkpoints=len(J[job]["members"]),
                   dollars=round(wall / 3600 * 0.59, 2))
        rows.append(row)
        if not dry:
            lab = dict(arm=job, seed=0, role="stats", job=job, gpu="NVIDIA A40", n_gpu=1, pod=row["pod"],
                       source=f"artifacts/olmo_weights/stats/{job}/summary.json", derived="sum of engine wall_s over runs")
            record.record("gpu_seconds", row["gpu_seconds"], **lab)
            for k in ("gen_tokens", "train_steps", "train_tokens", "lean_checks"):
                record.record(k, 0, **lab)
            record.record("bytes_downloaded", dl, **lab)
            record.record("files_verified", nf, **lab)
    print("| job | pod | checkpoints | engine runs | GPU-seconds (A40) | of which compute | TB downloaded | files sha256-checked | ≈ $ |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['job']} | {r['pod']} | {r['checkpoints']} | {r['runs']} | {r['gpu_seconds']:,.0f} | {r['compute_seconds']:,.0f} | "
              f"{r['bytes_downloaded'] / 1e12:.2f} | {r['files_verified']} | {r['dollars']:.2f} |")
    tot = dict(g=sum(r["gpu_seconds"] for r in rows), b=sum(r["bytes_downloaded"] for r in rows),
               f=sum(r["files_verified"] for r in rows), d=sum(r["dollars"] for r in rows))
    print(f"| **total** | | | | {tot['g']:,.0f} | | {tot['b'] / 1e12:.2f} | {tot['f']} | {tot['d']:.2f} |")


if __name__ == "__main__":
    main()
