#!/usr/bin/env python3
"""capability-defs Part 3 (J8): the elicitation share by rl-from-ckpt start.

  python3 capability_defs/analysis/cd_j8.py   -> out/j8.txt (stdout), out/j8.json

For seed s and start S (p1600 / p5000 / p12000 / p16000; pend from J1 / the bracket), the theorems the ladder from S
solves at r8 (x0 or x1) that S fails (0 / 512).  For each, LB_S(t) = log sum over known proofs of pi_S(y) at T 0.8 with
each term at its stage-1 bound (b0 - ln 33; for pend the exact 33-base terms where J1 stage 2 scored them).
Share certified elicited at K = 2e4 (K_eval-set scale), 3.5e6 (K_total scale) and 777 (K_per scale), the same K for every
start (the rfc ladders' compute is within ~1.25x of trajectory's).  Also: share of those theorems the replay-only control
from the same start (rl-from-ckpt c<s>_<S>_r8) solves at k 256 (x0 or x1).
"""
import collections, glob, gzip, json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R
from cd_bracket import lse, LN33

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
KS = {'K_per~777': 777, 'K_eval-set~2e4': 2e4, 'K_total~3.5e6': 3.5e6}


def main():
    sets = json.load(open(f'{ROOT}/artifacts/cd/j8/sets.json'))
    res = {}
    for s in (0, 1, 2):
        terms = collections.defaultdict(lambda: collections.defaultdict(list))   # name -> label -> [b0 - ln33]
        for p in sorted(glob.glob(f'{ROOT}/artifacts/cd/j8/b1_s{s}_p*/compact.jsonl.gz')):
            for l in gzip.open(p, 'rt'):
                r = json.loads(l)
                if r['replay_ok']:
                    for lab, v in r['sc'].items():
                        terms[r['name']][lab].append(v[2] - LN33)
        if not terms:
            print(f's{s}: no J8 results yet'); continue
        row = {}
        for st, new in sets[str(s)].items():
            lab = f's{s}_{st}'
            lbs = [lse(terms[n][lab]) if terms[n][lab] else -math.inf for n in new]
            # replay-only control from the same start
            ctrl = set()
            for x in (0, 1):
                for pool in R.POOLS:
                    f = f'{R.OA}/rl-from-ckpt/c{s}_{st}_r8__{pool}_x{x}.jsonl.gz'
                    if os.path.exists(f):
                        for l in gzip.open(f, 'rt'):
                            r = json.loads(l)
                            if r['n_ok'] > 0:
                                ctrl.add(r['name'])
            row[st] = {'n_new': len(new), 'scored': sum(1 for n in new if terms[n][lab]),
                       **{k: sum(1 for v in lbs if v >= -math.log(K)) / max(1, len(new)) for k, K in KS.items()},
                       'median_LB': float(np.median(lbs)) if lbs else None,
                       'ctrl_solves_share': len(ctrl & set(new)) / max(1, len(new))}
        res[s] = row
        print(f's{s}:')
        for st in ('p1600', 'p5000', 'p12000', 'p16000'):
            v = row[st]
            print(f"  start {st:6s}: ladder's new solves {v['n_new']:3d} (scored {v['scored']}); certified elicited at "
                  + ', '.join(f"{k} {v[k]:.2f}" for k in KS) + f"; median LB {v['median_LB']:.1f} nats; "
                  f"replay-only control from the same start solves {v['ctrl_solves_share']:.2f}")
    json.dump(res, open(f'{OUT}/j8.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
