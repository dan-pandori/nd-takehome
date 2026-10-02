#!/usr/bin/env python3
"""Reviewer: headline with groups defined from the independent x1 draw (B' = r0 x1 fails, r8 x1 solves), and from both
draws (B'' = r0 fails in x0 AND x1, r8 solves in x0)."""
import json, os, statistics as st
from recount import load
R = os.path.expanduser('~/review/trajectory-cap6'); S = f'{R}/artifacts/tj6/score'; med = st.median
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
for lab in ('x1', 'x0&x1'):
    res = {k: [] for k in ('own', 'ref')}
    for s in (0, 1, 2):
        B = []
        for p in ('tb72', 'h250'):
            r0a, r0b, r8a, r8b = load(s, 'pend', p, 0), load(s, 'pend', p, 1), load(s, 'r8', p, 0), load(s, 'r8', p, 1)
            for n in r0a:
                if lab == 'x1' and not r0b[n]['proofs'] and r8b[n]['proofs']: B.append(n)
                if lab == 'x0&x1' and not r0a[n]['proofs'] and not r0b[n]['proofs'] and r8a[n]['proofs']: B.append(n)
        sc = {ck: {r['tid']: min(r['T1.0']['step_lp']) for r in rd(f'{S}/s{s}/s{s}_{ck}.jsonl')} for ck in ('p1600', 'pend', 'r8')}
        for kind in ('own', 'ref'):
            T = [('ev:' if kind == 'own' else 'ref:') + n for n in B if (('ev:' if kind == 'own' else 'ref:') + n) in sc['pend']]
            res[kind].append((len(T), med([sc['r8'][t] - sc['pend'][t] for t in T]), med([sc['pend'][t] - sc['p1600'][t] for t in T])))
    for kind, v in res.items():
        print(f'groups {lab}, B {kind}: ' + ' '.join(f'[n{n} dRL {a:.2f} dPT {b:.2f}]' for n, a, b in v) + f'  IQM diff {st.mean(a - b for _, a, b in v):.2f}, dRL>dPT {sum(a > b for _, a, b in v)}/3')
