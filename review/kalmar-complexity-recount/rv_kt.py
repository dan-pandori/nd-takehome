#!/usr/bin/env python3
"""Levin's Kt for the golfed whole-proof programs on my fresh sample: DEFLATE bits (my count) + log2 mean Python calls
(sys.setprofile 'call' events) per theorem; also proof lines / actions of the builder's proofs on the same sample."""
import json, math, os, random, statistics, sys
HERE = os.path.dirname(os.path.abspath(__file__)); WS = os.path.expanduser('~/review/kalmar-complexity')
sys.path.insert(0, WS); sys.path.insert(0, os.path.join(WS, 'kalmar')); sys.path.insert(0, os.path.join(WS, 'kalmar_complexity/programs/python'))
from ksl_alg import K; from ksl_seq import Q; from ktt_alg import T; from ktt_lean import L; from parse import S
import kalmar
sz = json.load(open(os.path.join(HERE, 'out/python_sizes.json')))
ps = [json.loads(l)['prompt'] for l in open(os.path.join(WS, 'data/kh/train_k12.jsonl'))]
idx = sorted(random.Random(271828).sample(range(len(ps)), 1000))
calls = {k: [] for k in ('K-sl algorithm', 'K-sl alg + lean_seq render', 'K-tt algorithm', 'K-tt alg + Lean render')}
n = [0]
def prof(f, e, a):
    if e == 'call': n[0] += 1
lines, acts = [], []
for i in idx:
    p = ps[i]; P, G = S(p)
    for k, fn in (('K-sl algorithm', lambda: K(P, G)), ('K-sl alg + lean_seq render', lambda: Q(K(P, G))),
                  ('K-tt algorithm', lambda: T(P, G)), ('K-tt alg + Lean render', lambda: L(T(P, G), P, G))):
        n[0] = 0; sys.setprofile(prof); fn(); sys.setprofile(None); calls[k].append(n[0])
    r = kalmar.build(p, 'sl'); lines.append(r['n_lines']); acts.append(r['n_actions'])
out = {}
for k, v in calls.items():
    bits = sz[k]['deflate'] * 8; m = statistics.mean(v)
    out[k] = {'deflate_bits': bits, 'mean_calls': m, 'max_calls': max(v), 'Kt_bits': bits + math.log2(m)}
    print(k, out[k])
out['builder_sl_sample'] = {'lines_mean': statistics.mean(lines), 'lines_median': statistics.median(lines), 'lines_max': max(lines),
                            'actions_mean': statistics.mean(acts), 'actions_max': max(acts)}
print(out['builder_sl_sample'])
json.dump(out, open(os.path.join(HERE, 'out/kt.json'), 'w'), indent=1)
