#!/usr/bin/env python3
"""organism-analysis Q2 exposure: how often each step class appears in the EI ladders' RL training records
(oa_exposure.py output, rounds 1-8, distinct (prompt, proof) RL records per round), and whether a class's exposure share
predicts its hard-step gain (Spearman across classes; gains from artifacts/oa/q2_results.json).  Post hoc: the share of
negation boxes that prove ¬¬X (artifacts/oa/exposure_dneg/, c12 / c6 only).  Writes artifacts/oa/q2_exposure.json.
"""
import collections, json, os, sys
import numpy as np
from scipy.stats import spearmanr

Q2 = json.load(open('artifacts/oa/q2_results.json'))
out = {}
for run in ('c12', 'c6'):
    tot = collections.Counter(); per_round = {}
    for s in (0, 1, 2):
        f = f'artifacts/oa/exposure/{run}_s{s}.json'
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        for r, v in d.items():
            tot.update(v['class_steps'])
            per_round.setdefault(r, collections.Counter()).update(v['class_steps'])
    n = sum(v for k, v in tot.items() if k != 'box:neg:dneg')
    share = {k: v / n for k, v in tot.items() if k != 'box:neg:dneg'}
    xs, ys, cl = [], [], []
    for k, d in Q2['transfer'].items():
        r, c = k.split('|')
        if r == run and c in share and d['rl'][1] >= 5:
            xs.append(share[c]); ys.append(d['rl'][0]); cl.append(c)
    rho = spearmanr(xs, ys)[0]
    out[run] = {'share': {k: round(v, 4) for k, v in sorted(share.items(), key=lambda kv: -kv[1])},
                'spearman_share_vs_rl_gain': [round(float(rho), 3), len(xs)], 'classes': cl,
                'per_round_steps': {r: sum(v for k, v in c.items() if k != 'box:neg:dneg') for r, c in sorted(per_round.items())}}
    print(f'{run}: RL training steps by class (share, rounds 1-8, 3 seeds): ' +
          ', '.join(f'{k} {v:.1%}' for k, v in list(out[run]['share'].items())[:12]))
    print(f'   Spearman(class share, median rl-solved hard-step gain) = {rho:.3f} over {len(xs)} classes')
    # post hoc ¬¬ share
    dn = collections.Counter()
    for s in (0, 1, 2):
        f = f'artifacts/oa/exposure_dneg/{run}_s{s}.json'
        if os.path.exists(f):
            for r, v in json.load(open(f)).items():
                dn['neg'] += v['class_steps'].get('box:neg', 0); dn['dneg'] += v['class_steps'].get('box:neg:dneg', 0)
                dn['all'] += sum(x for k, x in v['class_steps'].items() if k != 'box:neg:dneg')
    if dn['neg']:
        out[run]['posthoc_dneg'] = {'dneg_steps': dn['dneg'], 'neg_steps': dn['neg'], 'all_steps': dn['all'],
                                    'dneg_share_of_neg': round(dn['dneg'] / dn['neg'], 4), 'dneg_share_of_all': round(dn['dneg'] / dn['all'], 5)}
        print(f'   POST HOC: ¬¬X boxes {dn["dneg"]} of {dn["neg"]} negation boxes ({dn["dneg"] / dn["neg"]:.1%}); '
              f'{dn["dneg"] / dn["all"]:.3%} of all RL training steps')
json.dump(out, open('artifacts/oa/q2_exposure.json', 'w'), indent=1)
