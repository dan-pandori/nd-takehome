#!/usr/bin/env python3
"""Levin's Kt for the whole-proof Python programs (run kalmar-complexity): program bits (DEFLATE) + log2 of the mean
number of Python function calls (sys.setprofile 'call' events) per theorem on the 1,000 test theorems.
-> artifacts/kc/kt_python.json"""
import json, math, os, statistics, sys
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(H, 'programs/python'))
from kalmar_complexity.common import sample_prompts
from ksl_alg import K
from ksl_seq import Q
from ktt_alg import T
from ktt_lean import L
from parse import S
sizes = json.load(open(os.path.join(ROOT, 'artifacts/kc/python_sizes.json')))
calls = {'K-sl algorithm': [], 'K-sl algorithm + lean_seq render': [], 'K-tt algorithm': [], 'K-tt algorithm + Lean render': []}
n = [0]
def prof(frame, ev, arg):
    if ev == 'call': n[0] += 1
for p in sample_prompts(1000):
    P, G = S(p)
    for name, fn in (('K-sl algorithm', lambda: K(P, G)), ('K-sl algorithm + lean_seq render', lambda: Q(K(P, G))),
                     ('K-tt algorithm', lambda: T(P, G)), ('K-tt algorithm + Lean render', lambda: L(T(P, G), P, G))):
        n[0] = 0; sys.setprofile(prof); fn(); sys.setprofile(None); calls[name].append(n[0])
out = {}
for k, v in calls.items():
    m = statistics.mean(v); bits = sizes[k]['deflate_bytes'] * 8
    out[k] = {'deflate_bits': bits, 'mean_calls': m, 'median_calls': statistics.median(v), 'max_calls': max(v),
              'Kt_bits': bits + math.log2(m)}
    print(f"{k:36} bits {bits:6}  calls mean {m:9.0f} max {max(v):8}  Kt {bits + math.log2(m):8.1f}")
json.dump(out, open(os.path.join(ROOT, 'artifacts/kc/kt_python.json'), 'w'), indent=1)
