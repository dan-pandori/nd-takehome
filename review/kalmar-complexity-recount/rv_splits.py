#!/usr/bin/env python3
"""Split disjointness by renaming class (run kalmar-complexity review).  Keys: (a) atom-renaming class = min over the
24 bijections of P Q R S of the renamed sequent text; (b) (a) plus premise order (min over premise permutations, and
over duplicate-free premise multisets).  Training sets: K12 [0, 155000) (KAL-D / the control), [0, 16884) (B2),
[0, 8192) (B3).  Evaluation pools: tf1200 (Q4 outcome, B1-snap, B3 read-out), val300 (its first 300)."""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
PERMS = list(itertools.permutations('PQRS'))


def parts(prompt):
    t = prompt.split()[1:-1]
    k = t.index('SEQ')
    prem, cur, depth = [], [], 0
    for x in t[:k]:
        if x == ',' and depth == 0:
            prem.append(' '.join(cur)); cur = []
            continue
        depth += (x == '(') - (x == ')')
        cur.append(x)
    if cur:
        prem.append(' '.join(cur))
    return prem, ' '.join(t[k + 1:])


def ren(s, p):
    m = dict(zip('PQRS', p))
    return ' '.join(m.get(x, x) for x in s.split())


def key_a(prompt):
    prem, g = parts(prompt)
    return min(' , '.join(ren(x, p) for x in prem) + ' |- ' + ren(g, p) for p in PERMS)


def key_b(prompt):
    prem, g = parts(prompt)
    best = None
    for p in PERMS:
        ps = sorted(set(ren(x, p) for x in prem))
        k = ' , '.join(ps) + ' |- ' + ren(g, p)
        best = k if best is None or k < best else best
    return best


def main():
    k12 = [json.loads(l)['prompt'] for l in open(os.path.join(WS, 'data/kh/train_k12.jsonl'))]
    tf = [json.loads(l)['prompt'] for l in open(os.path.join(WS, 'data/kalmar/tf1200_kal_sl.jsonl'))]
    out = {}
    for kn, kf in (('renaming', key_a), ('renaming+premise_order', key_b)):
        K = [kf(p) for p in k12]
        T = [kf(p) for p in tf]
        res = {}
        for name, lo, hi in (('K12 all (KAL-D, control)', 0, 155000), ('K12 [0,16884) (B2)', 0, 16884),
                             ('K12 [0,8192) (B3)', 0, 8192)):
            s = set(K[lo:hi])
            res[name] = {'tf1200': sum(t in s for t in T), 'val300': sum(t in s for t in T[:300])}
        res['tf1200 distinct classes'] = len(set(T))
        out[kn] = res
        print(kn, res, flush=True)
    json.dump(out, open(os.path.join(HERE, 'out', 'splits.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
