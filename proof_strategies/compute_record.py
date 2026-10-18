#!/usr/bin/env python3
"""Compute record of run proof-strategies (AGENT_POLICY: GPU-seconds + type, generated tokens, training steps / tokens,
Lean checks), as results-registry rows.  No model was trained or sampled.  One pod (ps-c0, RTX 3090, $0.50/h, 0.1958 h
billed per podrm, 2026-10-18 19:16–19:28 UTC) ran six CPU search jobs (its GPU idle); everything else ran on the VPS.
Sources: artifacts/ps/pod_logs/ps_j*.log (each job's last line), the Lean-check counts in log.md.

  ND_RUN_ID=proof-strategies python3 proof_strategies/compute_record.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import record                                   # noqa: E402

JOBS = {  # job: (log, Lean checks on the VPS of its outputs)
    'J1_search_tb_schema': ('ps_j1.log', 1610), 'J2_search_textbook72': ('ps_j2.log', 58), 'J3_search_k12_min990': ('ps_j3.log', 990),
    'J4_necessity_k12_594': ('ps_j4.log', 2880), 'J5_necessity_charles_187': ('ps_j5.log', 514), 'J6_necessity_textbook72': ('ps_j6.log', 216)}


def main():
    record.set_config({'pod': 'ps-c0', 'gpu': 'NVIDIA GeForce RTX 3090', 'billed_h': 0.1958, 'usd': 0.10}, role='analysis')
    rows = []
    for job, (log, lean) in JOBS.items():
        last = json.loads(open(f'artifacts/ps/pod_logs/{log}').read().strip().splitlines()[-1])
        cpu = last.get('cpu_s')
        for metric, val in (('gpu_seconds', 0), ('gen_tokens', 0), ('train_steps', 0), ('train_tokens', 0), ('lean_checks', lean),
                            ('wall_seconds', last['wall_s'])) + ((('cpu_seconds', cpu),) if cpu is not None else ()):
            record.record(metric, val, arm=job, source=f'artifacts/ps/pod_logs/{log}', gpu_type='NVIDIA GeForce RTX 3090 (idle; CPU job)')
        rows.append((job, last['wall_s'], cpu, lean))
    record.record('pod_seconds', round(0.1958 * 3600), arm='pod_ps-c0', source='podrm output, log.md 2026-10-18', gpu_type='NVIDIA GeForce RTX 3090', usd=0.10)
    for r in rows:
        print(r)


if __name__ == '__main__':
    main()
