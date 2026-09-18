#!/usr/bin/env python3
"""Reviewer: upper-bound every solved theorem's true length by (a) the shortest verified proof any arm wrote and
(b) the proof obtained by merging an ORE's two boxes when both assume the same formula (( A v A ) eliminations; the verifier
accepts `ORE Nj Ns Ne Ns Ne`). Every constructed proof is checked with nd_verify. Then recompute L* with corrected labels."""
import json, glob, collections, sys
from nd_verify import verify_text
from rv_recount import rv_nlines, rv_norm, lstar, ARMS, A

def lines_of(proof):
    body = proof.split('QED')[0]
    return [seg.split() for seg in body.split(';') if seg.strip()]

def merge_ore(proof):
    """try to delete the second box of one ORE whose boxes have identical hypotheses and identical final formula. -> new proof or None"""
    L = lines_of(rv_norm(proof))
    for i, toks in enumerate(L):
        c = toks.index(':')
        if toks[c + 1] != 'ORE':
            continue
        refs = [int(t[1:]) for t in toks[c + 2:]]
        if len(refs) != 5:
            continue
        j, s1, e1, s2, e2 = refs
        if s1 == s2 or s2 != e1 + 1:
            continue
        f = lambda n: [t for t in L[n - 1][1:L[n - 1].index(':')] if t != '|']
        if f(s1) != f(s2):
            continue
        # lines inside box 2 must not be cited by anything other than this ORE / lines inside box 2
        drop = set(range(s2, e2 + 1))
        ok = True
        for k, tk in enumerate(L, 1):
            if k in drop or k == i + 1:
                continue
            ck = tk.index(':')
            if any(int(t[1:]) in drop for t in tk[ck + 2:]):
                ok = False
        if not ok:
            continue
        newL = []
        shift = len(drop)
        def rn(n):
            return n if n < s2 else n - shift
        for k, tk in enumerate(L, 1):
            if k in drop:
                continue
            ck = tk.index(':')
            if k == i + 1:
                r = [j, s1, e1, s1, e1]
            else:
                r = [int(t[1:]) for t in tk[ck + 2:]]
            newL.append(['N%d' % rn(k)] + tk[1:ck + 2] + ['N%d' % rn(x) for x in r])
        return ' ; '.join(' '.join(t) for t in newL) + ' ; QED'
    return None

def main():
    T = {json.loads(l)['name']: json.loads(l) for l in open('data/ladder/transfer.jsonl')}
    G = {json.loads(l)['name']: json.loads(l) for l in open('data/ladder/rl_targets.jsonl')}
    ub = {}; how = {}
    for d in sorted(glob.glob(f'{A}/la_*/')):
        for fn, P in ((d + 'found_transfer_8.jsonl', T), (d + 'found_8.jsonl', G)):
            for l in open(fn):
                x = json.loads(l); rec = P[x['name']]
                n = rv_nlines(x['proof'])
                if n < ub.get(x['name'], 99):
                    ub[x['name']] = n; how[x['name']] = 'written'
                p = x['proof']
                for _ in range(3):
                    p = merge_ore(p)
                    if p is None:
                        break
                    ok, reason, nl = verify_text(rec['prompt'] + ' ' + p)
                    if not ok:
                        break
                    if nl < ub.get(x['name'], 99):
                        ub[x['name']] = nl; how[x['name']] = 'merged_ore'
    corr = {}
    for P, nm in ((T, 'transfer'), (G, 'targets')):
        bad = [n for n in ub if n in P and ub[n] < P[n]['L_true']]
        print(nm, 'solved-ever', sum(1 for n in ub if n in P), 'label falsified', len(bad),
              sorted(collections.Counter((P[n]['L_true'], ub[n], how[n]) for n in bad).items()))
        for n in P:
            corr[n] = min(P[n]['L_true'], ub.get(n, 99))
    json.dump({'ub': ub, 'how': how, 'corrected': corr}, open('review_out/label_ub.json', 'w'))
    rc = json.load(open('review_out/recount.json'))
    print('\narm        L*_transfer(label) ge10  L*_transfer(corrected) ge9 ge10 ge11 | L*_targets(label) (corrected) ge10 ge11')
    res = {}
    for arm in ARMS:
        row = {}
        for pool in ('transfer', 'targets'):
            names = rc[arm][pool]['8']['solved_names']
            P = T if pool == 'transfer' else G
            lab = [P[n]['L_true'] for n in names]; co = [corr[n] for n in names]
            row[pool] = {'lstar_label': lstar(lab), 'lstar_corr': lstar(co), 'ge_corr': {L: sum(1 for x in co if x >= L) for L in range(7, 13)},
                         'ge_label': {L: sum(1 for x in lab if x >= L) for L in range(7, 13)}}
        res[arm] = row
        t, g = row['transfer'], row['targets']
        print(f"{arm:10s} {t['lstar_label']:3d} {t['ge_label'][10]:4d}   {t['lstar_corr']:3d} {t['ge_corr'][9]:4d} {t['ge_corr'][10]:4d} {t['ge_corr'][11]:3d} | {g['lstar_label']:3d} {g['lstar_corr']:3d} {g['ge_corr'][10]:4d} {g['ge_corr'][11]:3d}")
    json.dump(res, open('review_out/lstar_corrected.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
