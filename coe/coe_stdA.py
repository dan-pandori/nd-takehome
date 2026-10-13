#!/usr/bin/env python3
"""create-or-elicit: compute-matched reach on the 322 (textbook72 scoring only + holdout250), standard A, per new seed at
K = K_train(16).  RL solves = r16 plain k 256 (x0).  Base: pend's 512 read attempts (x0 + x1); on every theorem r16 solves
and the base failed in those 512, coe_bigk's large-k attempts (`stdA_<arm>_s<S>`, up to K, stopping at 10 successes).
Within reach at K: p-hat >= 1 / K (the base's 512-attempt successes count as within reach).  Not reached: 0 successes in
>= K attempts.  Found below the budget: >= 1 success but p-hat < 1 / K.  Delta_cov = RL solves - base within reach.

  python3 coe/coe_stdA.py --out artifacts/coe/stdA.json
"""
import argparse, gzip, json, os
from scipy.stats import beta


def solved(tag):
    fn = f'artifacts/coe/eval/{tag}.jsonl.gz'
    if not os.path.exists(fn):
        return None
    return {json.loads(l)['name']: json.loads(l) for l in gzip.open(fn, 'rt')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    r322 = [json.loads(l)['name'] for l in open('data/coe/r322.jsonl')]
    res = {}
    print('| seed | K_train(16) | r16 solves (of 322) | base within reach at K | Δ_cov | compute-matched set (r16 solves, base not within reach) | of which 0 successes in ≥ K | found below 1/K | undetermined |')
    print('|---|---|---|---|---|---|---|---|---|')
    for arm, seeds in (('full', (3, 4, 5)), ('ko', range(6)), ('dose1', range(3))):
        for s in seeds:
            N = f'{arm}_s{s}'
            kf = f'artifacts/coe/budget/k_{N}.json'
            r16, p0, p1 = solved(f'r16_{N}_x0'), solved(f'pend_{N}_x0'), solved(f'pend_{N}_x1')
            big = f'artifacts/coe/large/stdA_{N}.json'
            if None in (r16, p0, p1) or not os.path.exists(kf) or not os.path.exists(big):
                continue
            K = json.load(open(kf))['K_train16']
            bt = json.load(open(big))['theorems']
            rl = [n for n in r322 if r16[n]['solved']]
            base512 = {n for n in r322 if p0[n]['solved'] or p1[n]['solved']}
            reach, notr, below, und, cm = set(base512), [], [], [], []
            for n in r322:
                if n in base512:
                    continue
                c = p0[n]['n_ok'] + p1[n]['n_ok'] + (bt[n]['ok'] if n in bt else 0)
                m = p0[n]['n_tried'] + p1[n]['n_tried'] + (bt[n]['tried'] if n in bt else 0)
                if c / m >= 1 / K:
                    reach.add(n)
                elif n in bt or m >= K:
                    if r16[n]['solved']:
                        cm.append(n)
                        (notr if c == 0 and m >= K else below if c > 0 else und).append(n)
            row = {'K_train16': K, 'rl_solves': len(rl), 'base_within_reach': len(reach), 'delta_cov': len(rl) - len(reach),
                   'cm_set': cm, 'cm_zero': notr, 'cm_found_below': below, 'cm_undetermined': und,
                   'stdA_theorems': len(bt), 'stdA_attempts': sum(v['tried'] for v in bt.values())}
            res[N] = row
            print(f"| {N} | {K:,.0f} | {len(rl)} | {len(reach)} | {len(rl) - len(reach):+d} | {len(cm)} | {len(notr)} | {len(below)} | {len(und)} |")
    json.dump(res, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
