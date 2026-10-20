#!/usr/bin/env python3
"""Check policy.py against the builder on every state the algorithm visits (run kalmar-complexity).

  python3 kalmar_complexity/programs/policy/test_policy.py [--n 1000] [--seed 20261020]

For each sampled K12 theorem: `kalmar.build(prompt, 'sl')` -> `state_env.decompose` (canonical names) -> for every
state, policy(state) must equal the builder's action token for token, and its step tag the builder's tag.
"""
import argparse, collections, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from kalmar_complexity.common import sample_prompts, sl_steps, TEST_SEED
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from policy import policy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=TEST_SEED)
    ap.add_argument('--show', type=int, default=3)
    a = ap.parse_args()
    t0 = time.time()
    ps = sample_prompts(a.n, a.seed)
    n_states = n_ok = n_tag = 0
    bad_thm = 0
    bytag = collections.Counter()
    shown = 0
    for p in ps:
        ok_thm = True
        for st, act, tag, d in sl_steps(p):
            n_states += 1
            bytag[tag] += 1
            try:
                got, gt = policy(st)
            except Exception as e:
                got, gt = [f'<{type(e).__name__}: {e}>'], None
            if got == act:
                n_ok += 1
                n_tag += gt == tag
            else:
                ok_thm = False
                if shown < a.show:
                    shown += 1
                    print('MISMATCH', p, '\n  state ', ' '.join(st), '\n  want  ', ' '.join(act), tag,
                          '\n  got   ', ' '.join(got), gt)
        bad_thm += not ok_thm
    print(f'theorems {len(ps)} (seed {a.seed}), all states exact: {len(ps) - bad_thm}; states {n_states:,}, '
          f'actions exact {n_ok:,}, tags exact {n_tag:,}; {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
