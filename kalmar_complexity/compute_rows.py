#!/usr/bin/env python3
"""Compute behind every pod arm of run kalmar-complexity, as results-registry rows (AGENT_POLICY, 2026-09-29).

  ND_RUN_ID=kalmar-complexity python3 kalmar_complexity/compute_rows.py            # B2 + B1-snap rows; table -> artifacts/kc/compute_table.md
  ND_RUN_ID=kalmar-complexity python3 kalmar_complexity/compute_rows.py --only b3  # then the B3 rows (appended), once

Derived from the job logs (`artifacts/kc/logs/<job>.log`: START / END UTC = wall seconds on the GPU) and the B2 result
files (training steps and training tokens = the real, unpadded tokens of the batches, summed over the block models).
The B2 / B1-snap scripts did not record rows themselves, so this script writes them afterwards (method stated per row).
GPU: NVIDIA A40 (secure cloud, billed $0.59/h), pods kc-1 / kc-2 / kc-3; several jobs shared one card, and each job's wall
time counts in full (so GPU-seconds over-count the card time when jobs ran side by side).  Generated tokens: 0 (no
sampling in this run).  Lean checks: 0 (no proof is judged; the builder's proofs were Lean-checked by kalmar-pretrain).
Everything else in the run (programs, decision procedure, B1, Q4) ran on the VPS CPU: 0 GPU-seconds.
"""
import datetime, glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault('ND_RUN_ID', 'kalmar-complexity')
import record


def wall(log):
    t = open(log).read()
    a = re.search(r'START (\S+Z)', t); b = re.search(r'END (\S+Z)', t)
    if not (a and b):
        return None
    f = lambda s: datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    return (f(b.group(1)) - f(a.group(1))).total_seconds()


def b3_rows():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'artifacts/kc/b3/*_s*.json'))):
        R = json.load(open(f)); a = R['args']
        log = os.path.join(ROOT, f"artifacts/kc/logs/b3_{a['arm']}_s{a['seed']}.log")
        rows.append((f"B3 {a['arm']} M", a['seed'], wall(log) if os.path.exists(log) else None, R['train']['steps'],
                     R['train']['train_tokens'], os.path.relpath(f, ROOT)))
    return rows


def main():
    only_b3 = '--only' in sys.argv and sys.argv[sys.argv.index('--only') + 1] == 'b3'
    rows = []
    for f in ([] if only_b3 else sorted(glob.glob(os.path.join(ROOT, 'artifacts/kc/b2/*.json')))):
        R = json.load(open(f))
        if 'summary' not in R:
            continue
        a = R['args']; v2 = bool(a.get('patience_steps'))
        job = ('b2v2_' if v2 else 'b2_') + f"{a['task']}_{a['size']}_s{a['seed']}"
        log = os.path.join(ROOT, f'artifacts/kc/logs/{job}.log')
        w = wall(log) if os.path.exists(log) else None
        arm = f"B2 {a['task']} {a['size']}" + (' v2' if v2 else '')
        steps = sum(b.get('steps', 0) for b in R['blocks']); tok = sum(b.get('train_tokens', 0) for b in R['blocks'])
        rows.append((arm, a['seed'], w, steps, tok, os.path.relpath(f, ROOT)))
    snap = os.path.join(ROOT, 'artifacts/kc/logs/snap.log')
    if only_b3:
        rows = b3_rows()
    elif os.path.exists(snap):
        rows.append(('B1-snap (24 checkpoints on tf1200)', None, wall(snap), 0, 0, 'artifacts/kc/b1_snap.json'))
    method = ('derived after the fact from the job log START/END (wall seconds on a shared A40) and the result file; '
              'kalmar_complexity/compute_rows.py')
    with open(os.path.join(ROOT, 'artifacts/kc/compute_table.md'), 'a' if only_b3 else 'w') as out:
        if not only_b3:
            out.write('| arm | seed | GPU-seconds (A40, wall; shared card) | training steps | training tokens | generated tokens | Lean checks | source |\n')
            out.write('|---|---|---|---|---|---|---|---|\n')
        for arm, seed, w, steps, tok, src in rows:
            for m, val in (('gpu_seconds', w), ('train_steps', steps), ('train_tokens', tok), ('gen_tokens', 0),
                           ('lean_checks', 0)):
                if val is not None:
                    record.record(m, val, arm=arm, seed=seed, role='measure', source=src, gpu='NVIDIA A40',
                                  method=method)
            out.write(f"| {arm} | {seed if seed is not None else '—'} | {w:,.0f} | {steps:,} | {tok:,} | 0 | 0 | `{src}` |\n"
                      if w is not None else f"| {arm} | {seed} | — | {steps:,} | {tok:,} | 0 | 0 | `{src}` |\n")
    print(open(os.path.join(ROOT, 'artifacts/kc/compute_table.md')).read())


if __name__ == '__main__':
    main()
