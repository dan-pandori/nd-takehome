#!/usr/bin/env python3
"""Reviewer phase-2 checks of executor claims: RL-only solves from x_start<-12, selection-free reach, lowest-x example."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
R = os.path.expanduser('~/review/rl-from-ckpt'); rc = json.load(open(f'{R}/review_rfc/rv/recount.json'))['solved']
X = json.load(open(f'{R}/review_rfc/rv/x.json')); xs = X['xs']; xc = X['xc']
S = lambda k: set(rc[k]) | set(rc[k.replace('tb72', 'h250')])
ST = ['p1600', 'p5000', 'p12000', 'p16000']
low = []
for st in ST + ['pend']:
    n = 0
    for s in (0, 1, 2):
        y = S(f'T s{s} r8 tb72 x1') if st == 'pend' else S(f'L s{s} {st} r8 tb72 x1')
        start = S(f'T s{s} {st} tb72 x0') | S(f'T s{s} {st} tb72 x1'); ctrl = S(f'C s{s} {st} r8 tb72 x0') | S(f'C s{s} {st} r8 tb72 x1')
        for nm, v in xs[f'{s}|{st}'].items():
            if v < -12 and nm in y and nm not in start and nm not in ctrl: n += 1; low.append((v, st, s, nm, xc[f'{s}|{st}'][nm]))
    print('RL-only from x_start<-12', st, n)
low.sort(); print('lowest', low[:3])
print('reach (union x0|x1), only-start / only-pend per seed:')
for st in ST:
    out = []
    for s in (0, 1, 2):
        L = S(f'L s{s} {st} r8 tb72 x0') | S(f'L s{s} {st} r8 tb72 x1'); E = S(f'T s{s} r8 tb72 x0') | S(f'T s{s} r8 tb72 x1')
        out.append(f'{len(L - E)}/{len(E - L)}')
    print(' ', st, ', '.join(out))
v, st, s, nm, _ = low[0]
for l in open(f'{R}/artifacts/rfc/eval/s{s}_{st}_r8__h250_x1.jsonl'):
    r = json.loads(l)
    if r['name'] == nm:
        print(nm, 'n_ok', r['n_ok'], 'n distinct stored', len(r['proofs']))
        rr = rlean.check([(r['prompt'], rlean.render(r['prompt'], p)) for p in r['proofs']], size=True)
        print('lean ok', sum(o for o, _, _ in rr), 'sizes', sorted(z for _, _, z in rr)[:5], 'min ND lines', min(p.count(' ; ') for p in r['proofs']))
