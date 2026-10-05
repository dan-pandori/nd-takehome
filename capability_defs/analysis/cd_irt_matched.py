#!/usr/bin/env python3
"""capability-defs Part 3: the IRT card's created set against an ability-matched placebo (critic's design, re-derived).

  python3 capability_defs/analysis/cd_irt_matched.py > capability_defs/analysis/out/irt_matched.txt

For each start checkpoint S in (p1600, p5000, p12000, p16000, pend) and each seed:
  1. calibrate the 2PL items on pretraining checkpoints p0 ... S only (pooled draws x0 + x1);
  2. project, with items fixed: the pretraining continuation (every later pretraining checkpoint), EI from S
     (rl-from-ckpt ladders s<s>_<S>_r{2,4,8}; trajectory r1-r8 when S = pend), and the replay-only control from S
     (c<s>_<S>_r8);
  3. for each projected examinee: delta-theta = theta - theta(S) and "created" = DIF+ items (tail < 1e-3 and log-odds
     residual > ln 10) that S itself fails (0 of its pooled attempts).
Prints created counts and the created rate per base-failed item that the examinee solves at p-hat >= 0.05, so arms can
be compared at matched delta-theta.  Reuses cd_irt.fit.
"""
import gzip, json, math, os, sys
import numpy as np
from scipy.special import expit
from scipy.stats import binom

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R
from cd_irt import fit

PTORDER = [c for c in R.CKS if c.startswith('p')]


def counts_for(items, s, label):
    """pooled x0 + x1 counts for one examinee label: a trajectory checkpoint, 'rfc:<stem>' for rl-from-ckpt reads."""
    c = np.zeros(len(items)); n = np.zeros(len(items)); have = False
    if label.startswith('rfc:'):
        stem = label[4:]
        for x in (0, 1):
            for pool in R.POOLS:
                f = f'{R.OA}/rl-from-ckpt/{stem}__{pool}_x{x}.jsonl.gz'
                if os.path.exists(f):
                    for line in gzip.open(f, 'rt'):
                        r = json.loads(line); j = items.index(r['name'])
                        c[j] += r['n_ok']; n[j] += r['n_tried']; have = True
    else:
        for x in (0, 1):
            d = R.counts(12, s, label, x)
            if d:
                for j, nm in enumerate(items):
                    if nm in d:
                        c[j] += d[nm][0]; n[j] += d[nm][1]; have = True
    return (c, n) if have else (None, None)


def main():
    items = R.all_names()
    print('created = DIF+ (tail < 1e-3, log-odds residual > ln 10) and the start checkpoint 0 / 512; rate = created / '
          '(start-failed items the examinee solves at p-hat >= 0.05)')
    for start in ('p1600', 'p5000', 'p12000', 'p16000', 'pend'):
        upto = PTORDER[:PTORDER.index(start) + 1]
        print(f'\n=== calibration through {start} ===')
        for s in R.SEEDS:
            cal = [counts_for(items, s2, ck) for s2 in R.SEEDS for ck in upto]
            C = np.array([c for c, n in cal if c is not None]); N = np.array([n for c, n in cal if c is not None])
            t, a, b, r = fit(C, N)
            c0, n0 = counts_for(items, s, start)
            t0, _, _, _ = fit(c0[None], n0[None], fix_items=True, a0=a, b0=b)
            later = [ck for ck in PTORDER[PTORDER.index(start) + 1:]]
            arms = [(f'PT {ck}', ck) for ck in later]
            if start == 'pend':
                arms += [(f'EI {r_}', r_) for r_ in ('r1', 'r2', 'r4', 'r8')]
                arms += [('replay r8', f'rfc:c{s}_pend_r8')]
            else:
                arms += [(f'EI r{r_}', f'rfc:s{s}_{start}_r{r_}') for r_ in (2, 4, 8)]
                arms += [('replay r8', f'rfc:c{s}_{start}_r8')]
            rows = []
            for lab, key in arms:
                c, n = counts_for(items, s, key)
                if c is None:
                    continue
                th, _, _, _ = fit(c[None], n[None], fix_items=True, a0=a, b0=b)
                pp = expit(a * (th[0] - b))
                tail = binom.sf(c - 1, n.astype(int), pp)
                res = np.log((c + .5) / (n - c + .5)) - np.log(pp / (1 - pp))
                difp = (n > 0) & (tail < 1e-3) & (res > math.log(10))
                failed = c0 == 0
                solved = (n > 0) & (c / np.maximum(n, 1) >= 0.05)
                created = int((difp & failed).sum()); denom = int((failed & solved).sum())
                rows.append(f'{lab} dθ {th[0] - t0[0]:+.2f} created {created} rate {created / denom if denom else float("nan"):.2f}')
            print(f'  s{s}: ' + ' | '.join(rows))


if __name__ == '__main__':
    main()
