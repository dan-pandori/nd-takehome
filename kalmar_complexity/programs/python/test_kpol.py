#!/usr/bin/env python3
"""Test the hand-golfed per-step policy kpol.A (state tokens -> action tokens) on every state of the sampled theorems
against the builder's action (run kalmar-complexity).  python3 kalmar_complexity/programs/python/test_kpol.py [--n] [--seed]"""
import argparse, os, sys, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(H))))
from kalmar_complexity.common import sample_prompts, sl_steps, TEST_SEED
from kpol import A
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=1000); ap.add_argument('--seed', type=int, default=TEST_SEED)
a = ap.parse_args(); ok = tot = 0; t0 = time.time()
for p in sample_prompts(a.n, a.seed):
    for st, act, tag, d in sl_steps(p):
        tot += 1; ok += ' '.join(A(st)) == ' '.join(act)
print(f'theorems {a.n} (seed {a.seed}): states {tot:,}, exact {ok:,}; {time.time() - t0:.0f}s')
