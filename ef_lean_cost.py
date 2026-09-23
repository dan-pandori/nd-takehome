#!/usr/bin/env python3
"""Run efficiency, step 3d: is a persistent Lean process/server worth building?

Measures the fixed per-process cost of `lean_check._run` by timing the same texts at several chunk sizes: with
`c` theorems per process the cost is fixed + c*per_theorem, so a chunk sweep identifies both.  Also sweeps the
worker count for the wall-clock the gate actually pays.  Input: the texts of a bench run's token dump.
"""
import os, sys, json, time, gzip, argparse, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lean_check
from lean_check import check, _run
from model import load_ckpt
import lean_free

ap = argparse.ArgumentParser()
ap.add_argument('--tokens', default='artifacts/ef/base_orig_tokens.npz')
ap.add_argument('--ckpt', default='ckpts/ef/stage1_full_seq_s0.pt')
ap.add_argument('--targets', default='artifacts/ef/targets200.jsonl')
ap.add_argument('--k', type=int, default=256)
ap.add_argument('--n', type=int, default=3000)
ap.add_argument('--out', default='artifacts/ef/lean_cost.json')
a = ap.parse_args()

_, tok, _ = load_ckpt(a.ckpt, 'cpu')
tg = [json.loads(l) for l in open(a.targets)]
prompts = [t['prompt'] for t in tg for _ in range(a.k)]
d = np.load(a.tokens, allow_pickle=True)
ids = d['ids']
srcs = []
for i in range(ids.shape[0]):
    tx = tok.decode([int(x) for x in ids[i]])
    if tok.last_text is not None:
        srcs.append(tok.statement(prompts[i]) + ' ' + tok.last_text)
print('texts', len(srcs), flush=True)
random.Random(0).shuffle(srcs)
srcs = srcs[:a.n]

rec = {'n_texts': len(srcs), 'chunk_sweep': [], 'worker_sweep': []}
import tempfile, shutil
wd = tempfile.mkdtemp(prefix='leancost_')
for c in (1, 10, 50, 100, 300, 600, 1200):
    sub = srcs[:min(len(srcs), c * 4)] if c >= 300 else srcs[:min(len(srcs), max(c * 8, 200))]
    t0 = time.time(); proc = 0.0; n = 0
    for i in range(0, len(sub), c):
        r, cpu = _run(sub[i:i + c], wd, f'x{c}_{i}')
        proc += cpu; n += len(r)
    rec['chunk_sweep'].append({'chunk': c, 'n': n, 'proc_s': round(proc, 3), 'proc_s_per_theorem': round(proc / n, 5),
                               'serial_wall_s': round(time.time() - t0, 3)})
    print('chunk', rec['chunk_sweep'][-1], flush=True)
shutil.rmtree(wd, ignore_errors=True)

# fixed cost per process from the two extreme chunk sizes actually measured
pts = {r['chunk']: r['proc_s'] / r['n'] for r in rec['chunk_sweep']}
if 1 in pts and 300 in pts:
    per_thm = pts[300] - (pts[1] - pts[300]) / (300 - 1)
    fixed = pts[1] - per_thm
    rec['fit'] = {'fixed_s_per_process': round(fixed, 4), 'per_theorem_s': round(per_thm, 5),
                  'fixed_share_at_chunk_300': round(fixed / (fixed + 300 * per_thm), 5)}
    print('fit', rec['fit'], flush=True)

for w in (16, 32, 64, 128, 192):
    t0 = time.time()
    res, wall, cpu = check(srcs, workers=w, chunk=300)
    rec['worker_sweep'].append({'workers': w, 'n': len(srcs), 'wall_s': round(wall, 2), 'proc_s': round(cpu, 1),
                                'texts_per_wall_s': round(len(srcs) / wall, 1), 'ok': sum(1 for r in res if r['ok'])})
    print('workers', rec['worker_sweep'][-1], flush=True)

json.dump(rec, open(a.out, 'w'), indent=1)
print('wrote', a.out)
