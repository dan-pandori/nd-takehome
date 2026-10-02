#!/usr/bin/env python3
"""C5 selection control for 'RL lifts its own proofs' at cap 12: score file rev12_s<S> (cap-12 seed S checkpoints) holds
eventual proofs of all cap-12 seeds (ev12s*) and cap-6 seeds (ev6s*). For B12(seed S, x0 groups) compare dRL of the own
proof, other cap-12 seeds' proofs (not selected by this model's r8), cap-6 proofs, and minlen references (score/s<S>)."""
import json, statistics as st, sys
sys.path.insert(0, '/home/dan/review/claim-audit/rv')
from importlib import util
spec = util.spec_from_file_location('c5', '/home/dan/review/claim-audit/rv/C567_c5.py')
R = '/home/dan/review/claim-audit/rv/C567_raw'
def solved(s, ck):
    o = {}
    for p in ('h250', 'tb72'):
        for l in open(f'{R}/trajectory/artifacts/tj/eval/s{s}_{ck}__{p}_x0.jsonl'):
            r = json.loads(l); o[r['name']] = r['solved']
    return o
def load(path):
    d = {}
    for l in open(path):
        r = json.loads(l); d[r['tid']] = r['T1.0']['w1']
    return d
tot = {}
for s in (0, 1, 2):
    a, b = solved(s, 'pend'), solved(s, 'r8')
    B = [n for n in a if not a[n] and b[n]]
    d = {ck: load(f'{R}/trajectory-cap6/artifacts/tj6/score/rev12_s{s}/s{s}_{ck}.jsonl') for ck in ('p1600', 'pend', 'r8')}
    ref = {ck: load(f'{R}/trajectory/artifacts/tj/score/s{s}/s{s}_{ck}.jsonl') for ck in ('p1600', 'pend', 'r8')}
    def agg(prefixes, D):
        rl, pt, r0 = [], [], []
        for n in B:
            v = [(D['r8'][p + n] - D['pend'][p + n], D['pend'][p + n] - D['p1600'][p + n], D['pend'][p + n]) for p in prefixes if p + n in D['pend']]
            if v:
                rl.append(st.mean(x[0] for x in v)); pt.append(st.mean(x[1] for x in v)); r0.append(st.mean(x[2] for x in v))
        return len(rl), st.median(r0), st.median(rl), st.median(pt)
    rows = {'own': agg([f'ev12s{s}:'], d), 'cross-seed cap12': agg([f'ev12s{t}:' for t in (0, 1, 2) if t != s], d),
            'cap6 proofs': agg([f'ev6s{t}:' for t in (0, 1, 2)], d), 'minlen ref': agg(['ref:'], ref)}
    for k, v in rows.items():
        print(f's{s} {k:17s} n={v[0]:3d} w1_r0 {v[1]:6.2f} dRL {v[2]:5.2f} dPT {v[3]:5.2f}')
        tot.setdefault(k, []).append(v)
for k, v in tot.items():
    print(f'IQM(mean of 3) {k:17s} w1_r0 {st.mean(x[1] for x in v):6.2f} dRL {st.mean(x[2] for x in v):5.2f} dPT {st.mean(x[3] for x in v):5.2f}')
