#!/usr/bin/env python3
"""(features, template) rows for every state of the sampled theorems; checks that the template is a function of the
features.  python3 kalmar_complexity/programs/dtree/build_rows.py [--n 1000] [--seed 20261020] --out rows.json"""
import argparse, collections, json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(H))))
from kalmar_complexity.common import sample_prompts, sl_steps, TEST_SEED
from features import features, label, FEATS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=TEST_SEED)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    cnt = collections.Counter()
    for p in sample_prompts(a.n, a.seed):
        for st, act, tag, d in sl_steps(p):
            F = features(st)
            cnt[(tuple(str(F[k]) for k in FEATS), label(tag, act))] += 1
    by = collections.defaultdict(dict)
    for (x, y), c in cnt.items():
        by[x][y] = c
    conflicts = {x: ys for x, ys in by.items() if len(ys) > 1}
    rows = [{'x': list(x), 'y': y, 'n': c} for (x, y), c in sorted(cnt.items())]
    json.dump({'feats': FEATS, 'n_theorems': a.n, 'seed': a.seed, 'rows': rows,
               'conflicts': [[list(x), ys] for x, ys in conflicts.items()]}, open(a.out, 'w'), indent=0)
    print(f'states {sum(cnt.values()):,}, distinct feature vectors {len(by)}, labels {len({y for _, y in cnt})}, '
          f'conflicting vectors {len(conflicts)}')
    for x, ys in list(conflicts.items())[:5]:
        print('  CONFLICT', dict(zip(FEATS, x)), ys)


if __name__ == '__main__':
    main()
