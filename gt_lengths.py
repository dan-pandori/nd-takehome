#!/usr/bin/env python3
"""gt_lengths.py -- proof length of accepted proofs per arm, in written lines and elaborated Lean term size.

  python3 gt_lengths.py [--eval artifacts/gt/eval] [--workers 2] > artifacts/gt/lengths_stdout.txt

Per (model, seed, arm) and theorem: the shortest accepted proof (fewest written lines = `have` + `exact` actions,
then fewest characters).  Its elaborated term size comes from `lean_check.check` (inference nodes of the elaborated
value; proof counted only if lean_check accepts it).  Compared on the theorems every arm of that model-seed solved
(paired), and reported on all solved theorems.  Output: artifacts/gt/lengths.json.
"""
import argparse, collections, glob, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from lean_tok import prompt_tokens


def lines(text):
    w = text.split()
    return w.count('have') + w.count('exact')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--eval', default='artifacts/gt/eval')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--out', default='artifacts/gt/lengths.json')
    a = ap.parse_args()
    from lean_check import check
    best = {}
    for fn in sorted(glob.glob(os.path.join(a.eval, '*.rows.jsonl.gz'))):
        m, s, arm = os.path.basename(fn).replace('.rows.jsonl.gz', '').split('_')
        for r in (json.loads(l) for l in gzip.open(fn, 'rt')):
            if r['accepted']:
                t = min(r['accepted'], key=lambda x: (lines(x), len(x)))
                best[(m, s, arm, r['prompt'])] = t
    keys = list(best)
    srcs = [' '.join(prompt_tokens(k[3])) + ' ' + best[k] for k in keys]
    res, wall, proc = check(srcs, workers=a.workers)
    size = {k: (r['size'] if r['ok'] else None) for k, r in zip(keys, res)}
    print(f'lean_check: {len(srcs)} shortest proofs, {sum(1 for r in res if not r["ok"])} rejected by lean_check, '
          f'{wall:.0f} s wall')
    by = collections.defaultdict(dict)
    for (m, s, arm, p), t in best.items():
        by[(m, s)].setdefault(arm, {})[p] = (lines(t), size[(m, s, arm, p)])
    out = {}
    print('model seed arm | solved | paired n | lines mean (paired) | term size mean (paired) | lines median (all) | size median (all)')
    for (m, s), arms in sorted(by.items()):
        common = set.intersection(*[set(v) for v in arms.values()]) if len(arms) > 1 else set()
        for arm, d in sorted(arms.items()):
            pl = [d[p][0] for p in common]; ps = [d[p][1] for p in common if d[p][1] is not None]
            al = [v[0] for v in d.values()]; az = [v[1] for v in d.values() if v[1] is not None]
            out[f'{m}_{s}_{arm}'] = dict(solved=len(d), paired=len(common), lines_paired_mean=float(np.mean(pl)) if pl else None,
                                        size_paired_mean=float(np.mean(ps)) if ps else None,
                                        lines_median=float(np.median(al)), size_median=float(np.median(az)) if az else None)
            o = out[f'{m}_{s}_{arm}']
            print(f"{m} {s} {arm} | {o['solved']} | {o['paired']} | {o['lines_paired_mean']} | {o['size_paired_mean']} | "
                  f"{o['lines_median']} | {o['size_median']}")
    json.dump(dict(rows=out, lean_check_rejected=sum(1 for r in res if not r['ok']), n=len(srcs)), open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
