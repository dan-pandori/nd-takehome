#!/usr/bin/env python3
"""lit-measures: compute behind every arm (AGENT_POLICY 2026-09-29), derived from the pulled job logs, and written as
results-registry rows (record.py; ND_RUN_ID=lit-measures).  GPU = RTX 3090 (lm2, $0.22/h).

  ND_RUN_ID=lit-measures python3 lm_compute.py [--no_record]   -> artifacts/lit-measures/compute.tsv

M2 cell (arm m2_grid, seed = init seed, labels.data_seed, labels.rep): gpu_seconds = the train log's "saved ... (X s
total" + the eval log's "generated ... in Y s" (the Lean check is CPU); train_steps 6000; train_tokens = the train log's
"useful tokens" (the fast path's packed stream; every step sees the same 6000 x 128 records); gen_tokens are not logged
by eval_set.py (greedy, 5,000 attempts: `attempts`); lean_checks = 5,000 (one per held-out theorem; the strict parser
rejects some before Lean).  M1: 0 GPU (VPS CPU, ~25 min forward passes, 136,755 scored step sequences).  M3: 0 GPU
(files only; pod CPU ~1 min + 2.1 GB download).  The repro runs (arm m2_repro) are listed with their train seconds."""
import glob, os, re, sys
D = 'artifacts/lit-measures/m2'
rows = []
for f in sorted(glob.glob(f'{D}/logs/train_i*.log')):
    c = os.path.basename(f)[6:-4]
    m = re.match(r'i(\d+)_d(\d+)(?:_(r\d+))?$', c); tl = open(f).read()
    s = re.search(r'saved \S+ \(([\d.]+)s total', tl); u = re.search(r'useful tokens (\d+)', tl)
    ev = f'{D}/logs/heldout_{c}.log'; g = re.search(r'generated (\d+) proofs in (\d+)s', open(ev).read()) if os.path.exists(ev) else None
    if not (s and g and os.path.exists(f'{D}/heldout_{c}.json')):
        continue
    rows.append({'arm': 'm2_grid' if not m[3] else 'm2_rep', 'cell': c, 'seed': int(m[1]), 'data_seed': int(m[2]), 'rep': m[3] or '',
                 'gpu_seconds': round(float(s[1]) + float(g[2]), 1), 'train_steps': 6000, 'train_tokens': int(u[1]),
                 'attempts': int(g[1]), 'lean_checks': int(g[1])})
for f in sorted(glob.glob(f'{D}/repro/*.log')):
    s = re.search(r'saved \S+ \(([\d.]+)s total', open(f).read())
    if s and 'nf_' not in f:
        n = 6000 if 'full' in f else 300
        rows.append({'arm': 'm2_repro', 'cell': os.path.basename(f)[:-4], 'seed': 0, 'data_seed': 0, 'rep': '',
                     'gpu_seconds': float(s[1]), 'train_steps': n, 'train_tokens': '', 'attempts': 0, 'lean_checks': 0})
K = ['arm', 'cell', 'seed', 'data_seed', 'rep', 'gpu_seconds', 'train_steps', 'train_tokens', 'attempts', 'lean_checks']
with open('artifacts/lit-measures/compute.tsv', 'w') as o:
    o.write('\t'.join(K) + '\n')
    for r in rows:
        o.write('\t'.join(str(r[k]) for k in K) + '\n')
tot = lambda a, k: sum(r[k] for r in rows if r['arm'] == a and r[k] != '')
for a in ('m2_grid', 'm2_rep', 'm2_repro'):
    print(f"{a:9s} cells {sum(r['arm'] == a for r in rows):3d}  gpu_seconds {tot(a, 'gpu_seconds'):9.0f}  train_steps {tot(a, 'train_steps'):7d}  "
          f"train_tokens {tot(a, 'train_tokens'):.3e}  attempts {tot(a, 'attempts')}  lean_checks {tot(a, 'lean_checks')}")
if '--no_record' not in sys.argv:
    import record
    record.set_config({'script': 'lm_compute.py'}, role='compute')
    for r in rows:
        for k in ('gpu_seconds', 'train_steps', 'train_tokens', 'lean_checks'):
            if r[k] != '':
                record.record(k, r[k], arm=r['arm'], seed=r['seed'], source=f"{D}/logs/train_{r['cell']}.log",
                              gpu='RTX 3090', data_seed=r['data_seed'], rep=r['rep'], cell=r['cell'], round=None)
    record.sync()
