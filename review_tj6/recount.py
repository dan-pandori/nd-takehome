#!/usr/bin/env python3
"""Reviewer (trajectory-cap6) phase-1 recount; adapted from review_tj/recount.py (reviewer code from the cap-12
review), independent of tj_*/tj6_*.py.  Reads artifacts/tj6/eval/s{seed}_{ck}__{pool}_x{xs}.jsonl only."""
import json, os, collections, math, sys
R = os.path.expanduser('~/review/trajectory-cap6'); E = f'{R}/artifacts/tj6/eval'
CK = ['p0','p50','p100','p200','p400','p800','p1600','p3000','p5000','p8000','p12000','p16000','p20000','pend'] + [f'r{i}' for i in range(1,9)]
POOLS = ['tb72', 'h250']
def load(s, ck, pool, xs, E=E):
    f = f'{E}/s{s}_{ck}__{pool}_x{xs}.jsonl'
    if not os.path.exists(f): return None
    return {json.loads(l)['name']: json.loads(l) for l in open(f) if l.strip()}
def passk(n, c, k):
    if n - c < k: return 1.0
    return 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))
CUT = ('truncat', 'step cap', 'max_steps', 'eof')
def cut(rec): return sum(1 for z in rec['reasons'] if any(c in z for c in CUT))
if __name__ == '__main__':
    out = {'missing': [], 'counts': {}, 'groups': {}, 'passk': {}, 'trunc': {}, 'trunc_max': {}, 'reasons_vocab': collections.Counter(), 'alost': {}}
    for s in (0, 1, 2):
        for ck in CK:
            for pool in POOLS:
                for xs in (0, 1):
                    d = load(s, ck, pool, xs); key = f's{s}_{ck}_{pool}_x{xs}'
                    if d is None: out['missing'].append(key); continue
                    bad = [n for n, r in d.items() if r['n_ok'] != r['n_tried'] - len(r['reasons']) or r['solved'] != bool(r['proofs']) or r['n_tried'] != 256]
                    out['counts'][key] = {'n': len(d), 'solved': sum(bool(r['proofs']) for r in d.values()), 'incons': len(bad)}
                    for r in d.values():
                        for z in r['reasons']: out['reasons_vocab'][z] += 1
    for s in (0, 1, 2):
        g = {}
        for pool in POOLS:
            r0 = load(s, 'pend', pool, 0); r8 = load(s, 'r8', pool, 0)
            for n in r0:
                a, b = bool(r0[n]['proofs']), bool(r8[n]['proofs'])
                g[f'{pool}:{n}'] = 'A' if a else ('B' if b else 'C')
                if a and not b: out['alost'].setdefault(str(s), []).append(f'{pool}:{n}')
        out['groups'][str(s)] = g
        c = collections.Counter(g.values()); cp = {p: collections.Counter(v for k, v in g.items() if k.startswith(p)) for p in POOLS}
        print(f'seed {s}: groups {dict(c)}  tb72 {dict(cp["tb72"])} h250 {dict(cp["h250"])}  A-lost {len(out["alost"].get(str(s),[]))}')
    for s in (0, 1, 2):
        for pool in POOLS:
            print(f'seed {s} {pool}: r0 x0 {out["counts"][f"s{s}_pend_{pool}_x0"]["solved"]}  r8 x0 {out["counts"][f"s{s}_r8_{pool}_x0"]["solved"]}  '
                  f'r0 x1 {out["counts"][f"s{s}_pend_{pool}_x1"]["solved"]}  r8 x1 {out["counts"][f"s{s}_r8_{pool}_x1"]["solved"]}')
    for s in (0, 1, 2):
        g = out['groups'][str(s)]
        for ck in CK:
            for xs in (0, 1):
                per = collections.defaultdict(lambda: collections.defaultdict(list)); tr = collections.defaultdict(lambda: [0, 0])
                for pool in POOLS:
                    d = load(s, ck, pool, xs)
                    for n, r in d.items():
                        G = g[f'{pool}:{n}']
                        for grp in (G, 'all', f'{pool}:{G}'):
                            for k in (1, 8, 64, 256): per[grp][k].append(passk(r['n_tried'], r['n_ok'], k))
                            tr[grp][0] += cut(r); tr[grp][1] += r['n_tried']
                out['passk'][f's{s}_{ck}_x{xs}'] = {grp: {k: sum(v) / len(v) for k, v in kk.items()} for grp, kk in per.items()}
                out['trunc'][f's{s}_{ck}_x{xs}'] = {grp: v[0] / v[1] for grp, v in tr.items()}
    print('missing', out['missing'])
    print('inconsistent', {k: v['incons'] for k, v in out['counts'].items() if v['incons']})
    print('reason vocab (cut-like)', {k: v for k, v in out['reasons_vocab'].items() if any(c in k for c in CUT)})
    print('reason vocab top', out['reasons_vocab'].most_common(12))
    for s in (0,1,2):
        for ck in ('p0','p1600','p8000','pend','r1','r4','r8'):
            p = out['passk'][f's{s}_{ck}_x1']
            print(f's{s} {ck:6s} x1 ' + '  '.join(f"{G}: " + '/'.join(f"{p[G][k]:.3f}" for k in (1,8,64,256)) for G in ('A','B','C') if G in p))
    # truncation per stratum (pool x group x ckpt x xs): count strata > 0.1 %
    big = [(k, grp, v) for k, d in out['trunc'].items() for grp, v in d.items() if ':' in grp and v > 0.001]
    print('strata (pool:group) with cut-off > 0.1 %:', len(big), 'of', sum(1 for d in out['trunc'].values() for g in d if ':' in g))
    for k, grp, v in sorted(big, key=lambda x: -x[2])[:25]: print('   ', k, grp, f'{100*v:.2f}%')
    for s in (0,1,2):
        for ck in ('pend','r8'):
            print(f'trunc s{s} {ck} x0', {g: f'{100*v:.3f}%' for g, v in out['trunc'][f's{s}_{ck}_x0'].items()})
    json.dump(out, open(f'{R}/rv6/recount.json', 'w'), indent=0, default=dict)
