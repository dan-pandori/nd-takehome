#!/usr/bin/env python3
"""Test the hand-golfed Python programs against the builders (run kalmar-complexity).

  python3 kalmar_complexity/programs/python/test_python.py [--n 1000] [--seed 20261020]

For every sampled K12 theorem (kalmar_complexity.common.sample_prompts):
  K-sl:  ksl_nd.R(ksl_alg.K(*parse.S(prompt)))  == kalmar.build(prompt, 'sl')['proof']          (ND text)
         ksl_seq.Q(ksl_alg.K(*parse.S(prompt))) == ' '.join(state_env.canonicalise(prompt, proof)) (lean_seq, canonical)
  K-tt:  ktt_lean.L(ktt_alg.T(P, G), P, G)       == tt_prover.solve(prompt)                       (Lean source)
Then the calibration programs (test_calib.py).
"""
import argparse, os, sys, time
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(H))))
from kalmar_complexity.common import sample_prompts, ref_sl, ref_tt, TEST_SEED
from state_env import canonicalise
from ksl_alg import K
from ksl_nd import R
from ksl_seq import Q
from ktt_alg import T
from ktt_lean import L
from parse import S
import test_calib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=TEST_SEED)
    a = ap.parse_args()
    t0 = time.time()
    ok = {'K-sl ND': 0, 'K-sl lean_seq': 0, 'K-tt Lean': 0}
    for p in sample_prompts(a.n, a.seed):
        P, G = S(p)
        r = ref_sl(p)['proof']
        ok['K-sl ND'] += R(K(P, G)) == r
        ok['K-sl lean_seq'] += Q(K(P, G)) == ' '.join(canonicalise(p, r))
        ok['K-tt Lean'] += L(T(P, G), P, G) == ref_tt(p)
    print(f'theorems {a.n} (seed {a.seed}):', ok, f'{time.time() - t0:.0f}s')
    test_calib.main(seed=a.seed % 1000 + 1)


if __name__ == '__main__':
    main()
