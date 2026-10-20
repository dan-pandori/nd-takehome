#!/usr/bin/env python3
"""20,000 K12-Kalmár records drawn with random.Random(seed) -- the replay-only ("anneal") control of Addendum 3.

  python3 kalmar/make_replay.py <seed> [--n 20000] [--src data/kalmar/train_kal_sl.jsonl] [--out data/kalmar/replay20k_s<seed>.jsonl]
"""
import argparse, json, random
ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int)
ap.add_argument('--n', type=int, default=20000)
ap.add_argument('--src', default='data/kalmar/train_kal_sl.jsonl')
ap.add_argument('--out', default=None)
a = ap.parse_args()
lines = [l for l in open(a.src) if l.strip()]
pick = random.Random(a.seed).sample(range(len(lines)), a.n)
out = a.out or f'data/kalmar/replay20k_s{a.seed}.jsonl'
with open(out, 'w') as f:
    for i in pick:
        r = json.loads(lines[i])
        f.write(json.dumps({'prompt': r['prompt'], 'proof': r['proof'], 'n_lines': r['n_lines']}) + '\n')
print(out, len(pick))
