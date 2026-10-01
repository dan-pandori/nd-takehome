#!/usr/bin/env python3
"""Reviewer (trajectory) phase-1 recount, written independently of tj_*.py.
Reads artifacts/tj/eval/s{seed}_{ck}__{pool}_x{xs}.jsonl only.  Outputs rv/recount.json."""
import json, os, collections, math, statistics as st
R = os.path.expanduser('~/review/trajectory'); E = f'{R}/artifacts/tj/eval'
CK = ['p0','p50','p100','p200','p400','p800','p1600','p3000','p5000','p8000','p12000','p16000','p20000','pend'] + [f'r{i}' for i in range(1,9)]
POOLS = ['tb72', 'h250']
def load(s, ck, pool, xs):
    f = f'{E}/s{s}_{ck}__{pool}_x{xs}.jsonl'
    if not os.path.exists(f): return None
    return {json.loads(l)['name']: json.loads(l) for l in open(f) if l.strip()}
def passk(n, c, k):
    if n - c < k: return 1.0
    return 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))
def cut(rec):
    return sum(1 for z in rec['reasons'] if ('trunc' in z or 'step cap' in z or 'max_steps' in z or 'eof' in z))
out = {'missing': [], 'counts': {}, 'groups': {}, 'passk': {}, 'trunc': {}, 'reasons_vocab': collections.Counter()}
for s in (0, 1, 2):
    for ck in CK:
        for pool in POOLS:
            for xs in (0, 1):
                d = load(s, ck, pool, xs)
                key = f's{s}_{ck}_{pool}_x{xs}'
                if d is None: out['missing'].append(key); continue
                # n_ok consistency: n_ok == n_tried - len(reasons) ; solved == bool(proofs)
                bad = [n for n, r in d.items() if r['n_ok'] != r['n_tried'] - len(r['reasons']) or r['solved'] != bool(r['proofs']) or r['n_tried'] != 256]
                out['counts'][key] = {'n': len(d), 'solved': sum(bool(r['proofs']) for r in d.values()), 'incons': len(bad)}
                for r in d.values():
                    for z in r['reasons']: out['reasons_vocab'][z.split(':')[0] if 'parse' not in z else z] += 1
for s in (0, 1, 2):
    g = {}
    for pool in POOLS:
        r0 = load(s, 'pend', pool, 0); r8 = load(s, 'r8', pool, 0)
        for n in r0:
            a, b = bool(r0[n]['proofs']), bool(r8[n]['proofs'])
            g[f'{pool}:{n}'] = 'A' if a else ('B' if b else 'C')
            if a and not b: g[f'{pool}:{n}'] = 'A'; out.setdefault('alost', {}).setdefault(str(s), []).append(f'{pool}:{n}')
    out['groups'][str(s)] = g
    c = collections.Counter(g.values()); cp = {p: collections.Counter(v for k, v in g.items() if k.startswith(p)) for p in POOLS}
    print(f'seed {s}: groups {dict(c)}  tb72 {dict(cp["tb72"])} h250 {dict(cp["h250"])}  A-lost {len(out.get("alost",{}).get(str(s),[]))}')
for s in (0, 1, 2):
    for pool in POOLS:
        print(f'seed {s} {pool}: r0 x0 {out["counts"][f"s{s}_pend_{pool}_x0"]["solved"]}  r8 x0 {out["counts"][f"s{s}_r8_{pool}_x0"]["solved"]}  '
              f'r0 x1 {out["counts"][f"s{s}_pend_{pool}_x1"]["solved"]}  r8 x1 {out["counts"][f"s{s}_r8_{pool}_x1"]["solved"]}')
# pass@k by group (groups from that training seed's x0; pass@k from x1), per checkpoint; plus truncation per group
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
print('reason vocab', out['reasons_vocab'].most_common(40))
for s in (0,1,2):
    for ck in ('p0','p1600','p8000','pend','r1','r4','r8'):
        p = out['passk'][f's{s}_{ck}_x1']
        print(f's{s} {ck:6s} x1 ' + '  '.join(f"{G}: " + '/'.join(f"{p[G][k]:.3f}" for k in (1,8,64,256)) for G in ('A','B','C') if G in p))
json.dump(out, open(f'{R}/rv/recount.json', 'w'), indent=0, default=dict)
