#!/usr/bin/env python3
"""Build the support-curves theorem set: a fixed, stratified draw from data/ladder/transfer.jsonl.

  python3 sc_theorems.py --out data/sc/theorems.jsonl

transfer.jsonl holds 2,285 theorems never trained on, each labelled with `L_true` (minlen.py).  Under Lean
`L_true` is an UPPER BOUND on the minimal proof length: it is the shortest ND proof, and Lean accepts proofs
that skip steps ND's rule format demands.  The pool's L_true histogram is 7:300 8:300 9:1010 10:451 11:99
12:102 13:13 14:10 -- there is no theorem below L_true 7, so the run brief's "25 each at L_true 4-6 anchors"
is not available; the 7/8 bins are the anchors instead.

Draw: 60 per bin at L_true 7..12 (over-sampling the long bins, which hold 99 and 102 theorems) and EVERY
theorem at L_true >= 13.  383 theorems.  Deterministic: sorted by name, then random.Random(SEED).sample.
"""
import argparse, json, os, random, collections

SEED = 20260927
PER_BIN = {7: 60, 8: 60, 9: 60, 10: 60, 11: 60, 12: 60}   # L_true >= 13: take all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inp', default='data/ladder/transfer.jsonl')
    ap.add_argument('--out', default='data/sc/theorems.jsonl')
    a = ap.parse_args()
    by = collections.defaultdict(list)
    for l in open(a.inp):
        if l.strip():
            r = json.loads(l)
            by[r['L_true']].append(r)
    rng = random.Random(SEED)
    picked = []
    for L in sorted(by):
        pool = sorted(by[L], key=lambda r: r['name'])
        n = PER_BIN.get(L, len(pool)) if L < 13 else len(pool)
        n = min(n, len(pool))
        picked += rng.sample(pool, n) if n < len(pool) else pool
    picked.sort(key=lambda r: (r['L_true'], r['name']))
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, 'w') as f:
        for r in picked:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    h = collections.Counter(r['L_true'] for r in picked)
    print(f'{len(picked)} theorems -> {a.out}')
    print('L_true histogram:', ' '.join(f'{k}:{v}' for k, v in sorted(h.items())))
    print('schemata:', len({r.get('schema') for r in picked}), ' textbook:', sum(1 for r in picked if r.get('source') == 'textbook'))


if __name__ == '__main__':
    main()
