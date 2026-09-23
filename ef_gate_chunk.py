#!/usr/bin/env python3
"""Run efficiency, step 3d: what chunk size should the Lean gate use?  Runs the real gate workload (the distinct
texts of a bench run) through lean_check.check at several (chunk, workers) settings.  Writes artifacts/ef/gate_chunk.json."""
import os, sys, json, time, argparse
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import load_ckpt
from lean_check import check
import lean_free

ap = argparse.ArgumentParser()
ap.add_argument('--tokens', default='artifacts/ef/base_rr_tokens.npz')
ap.add_argument('--targets', default='artifacts/ef/targets200.jsonl')
ap.add_argument('--k', type=int, default=256)
ap.add_argument('--out', default='artifacts/ef/gate_chunk.json')
a = ap.parse_args()
_, tok, _ = load_ckpt('ckpts/ef/stage1_full_seq_s0.pt', 'cpu')
tg = [json.loads(l) for l in open(a.targets)]
prompts = [t['prompt'] for t in tg for _ in range(a.k)]
d = np.load(a.tokens, allow_pickle=True)
ids = d['ids']
keys = {}
for i in range(ids.shape[0]):
    tok.decode([int(x) for x in ids[i]])
    if tok.last_text is not None:
        keys.setdefault((prompts[i], lean_free.canonical(tok.last_text)), tok.last_text)
srcs = [tok.statement(p) + ' ' + t for (p, _), t in keys.items()]
print('distinct texts', len(srcs), flush=True)
rec = {'n': len(srcs), 'runs': []}
for workers, chunk in [(64, 120), (64, 300), (64, 600), (64, 1200), (26, 300), (16, 480), (12, 640), (8, 960), (128, 300)]:
    res, wall, cpu = check(srcs, workers=workers, chunk=chunk)
    n_ok = sum(1 for r in res if r['ok'])
    rec['runs'].append({'workers': workers, 'chunk': chunk, 'processes': -(-len(srcs) // chunk),
                        'wall_s': round(wall, 2), 'proc_s': round(cpu, 1), 'accepted': n_ok,
                        'texts_per_wall_s': round(len(srcs) / wall, 1)})
    print(rec['runs'][-1], flush=True)
oks = set(r['accepted'] for r in rec['runs'])
rec['accepted_identical_across_settings'] = (len(oks) == 1)
rec['accepted'] = sorted(oks)
json.dump(rec, open(a.out, 'w'), indent=1)
print('accepted identical across settings:', rec['accepted_identical_across_settings'], rec['accepted'])
