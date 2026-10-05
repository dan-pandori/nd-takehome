#!/usr/bin/env python3
"""Reviewer: J3 guided (logical) reads vs plain reads; Q13 (guided pend solves of B)."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
CD = L.CD; PR = L.prompts()
S = json.load(open(f'{L.RV}/review_cd/out_sets.json'))
# h250_gt prompts == holdout250 prompts?
g = {r['name']: r['prompt'] for r in L.rows(f'{L.RV}/data/cd/h250_gt.jsonl')}
print('h250_gt names == holdout250:', set(g) == set(L.pool_names('h250')), ' prompts identical:', all(PR[n] == g[n] for n in g))
for f in ('tb72_textbook_dev', 'tb72_textbook_train'):
    d = {r['name']: r['prompt'] for r in L.rows(f'{L.RV}/data/gt/{f}.jsonl')}
    print(f, len(d), 'prompts == textbook72:', all(PR.get(n) == p for n, p in d.items()))
def guided(cap, s, ck):
    p = f'{CD}/j3/{"c6_" if cap == 6 else ""}s{s}_{ck}_logical.rows.jsonl.gz'
    if not os.path.exists(p): return None
    return {r['name']: (r['n_ok'], r['k'], r['file']) for r in L.rows(p)}
for cap in (12, 6):
    print(f'\ncap {cap}: solved@256  guided (logical, seed 1) vs plain x1 (and x0)   [tb72 dev58 / train14 / h250]')
    for s in (0, 1, 2):
        for ck in ('pend', 'r8', 'r16'):
            G = guided(cap, s, ck)
            if G is None: print(f'  s{s} {ck}: missing'); continue
            P1 = L.both(cap, s, ck, 1); P0 = L.both(cap, s, ck, 0)
            def cnt(D, fl=None):
                if D is None: return None
                return sum(1 for n in D if (D[n][0] > 0) and (fl is None or G[n][2] == fl))
            gs = {f: sum(1 for n in G if G[n][0] > 0 and G[n][2] == f) for f in ('tb72_textbook_dev', 'tb72_textbook_train', 'h250_gt')}
            ps = {f: sum(1 for n in G if P1 and P1[n][0] > 0 and G[n][2] == f) for f in gs} if P1 else None
            k = {v[1] for v in G.values()}
            print(f'  s{s} {ck:4s}: guided {sum(gs.values()):3d} ({gs["tb72_textbook_dev"]}/{gs["tb72_textbook_train"]}/{gs["h250_gt"]})  '
                  f'plain x1 {cnt(P1)} ' + (f'({ps["tb72_textbook_dev"]}/{ps["tb72_textbook_train"]}/{ps["h250_gt"]})' if ps else '') +
                  f'  plain x0 {cnt(P0)}  guided>=plain x1: {sum(gs.values()) >= (cnt(P1) or 0)}  k {k}')
print('\nQ13: guided pend solves of B (eqk r8 x0), cap 12')
for s in (0, 1, 2):
    G = guided(12, s, 'pend'); B = S['eqk'][f's{s}_r8_x0']
    h = [n for n in B if G[n][0] > 0]
    B16 = S['eqk'][f's{s}_r16_x1']; h16 = [n for n in B16 if G[n][0] > 0]
    print(f'  s{s}: {len(h)}/{len(B)} = {len(h) / len(B):.2f};  r16 x1 B: {len(h16)}/{len(B16)} = {len(h16) / len(B16):.2f}')
