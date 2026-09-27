#!/usr/bin/env python3
# (reviewer of run stage1-dynamics; independent of the executor.  Phase 1 was run in ~/review/stage1-dynamics.)
"""Reviewer's independent split-disjointness recount for stage1-dynamics.

My own renaming-class canonicaliser: a theorem's class is the lexicographic minimum,
over all 24 bijections of {P,Q,R,S}, of (sorted premise multiset, conclusion).  I never
read the pools' own `key` field.  Also my own depth-3 predicate and line counter.
"""
import json, hashlib, itertools, sys, collections

ATOMS = ['P', 'Q', 'R', 'S']
PERMS = [dict(zip(ATOMS, p)) for p in itertools.permutations(ATOMS)]


def canon(thm):
    """thm 'p1 , p2 |- c' -> 16-byte digest of its renaming class (my own key)."""
    lhs, _, rhs = thm.partition('|-')
    prems = [p.strip() for p in lhs.split(',') if p.strip()]
    best = None
    for m in PERMS:
        ps = sorted(' '.join(m.get(t, t) for t in p.split()) for p in prems)
        c = ' '.join(m.get(t, t) for t in rhs.split())
        s = '|'.join(ps) + '|-' + c
        if best is None or s < best:
            best = s
    return hashlib.blake2b(best.encode(), digest_size=16).digest()


def nd_lines(proof):
    out = []
    for chunk in proof.split(';'):
        t = chunk.split()
        if not t or t[0] == 'QED':
            continue
        d, j = 0, 1
        while j < len(t) and t[j] == '|':
            d += 1; j += 1
        out.append(d)
    return out


def scan(path, want_depth=True):
    cls, n, bylen, d3, maxd = [], 0, collections.Counter(), 0, 0
    for l in open(path):
        if not l.strip():
            continue
        r = json.loads(l)
        n += 1
        cls.append(canon(r['thm']))
        L = len(nd_lines(r['proof']))
        bylen[L] += 1
        if want_depth:
            m = max(nd_lines(r['proof']))
            maxd = max(maxd, m)
            if m >= 3:
                d3 += 1
    return cls, n, bylen, d3, maxd


def main():
    held_cls, hn, hbylen, hd3, hmaxd = scan('data/p2/heldout.jsonl')
    held = set(held_cls)
    print(f'heldout: n={hn} distinct classes={len(held)} bins={dict(sorted(hbylen.items()))} '
          f'depth>=3 records={hd3} max depth={hmaxd}')
    # depth-3 slice classes
    d3_cls = set()
    for l in open('data/p2/heldout.jsonl'):
        r = json.loads(l)
        if max(nd_lines(r['proof'])) >= 3:
            d3_cls.add(canon(r['thm']))
    print(f'  depth-3 slice: {len(d3_cls)} distinct classes')

    for path in ['data/p2/train_depth3_f0_a1.jsonl', 'data/sd/train_fresh.jsonl']:
        cls, n, bylen, d3, maxd = scan(path)
        s = set(cls)
        inter = s & held
        print(f'\n{path}: n={n} distinct classes={len(s)} dup classes within file={n-len(s)}')
        print(f'  bins={dict(sorted(bylen.items()))} '
              f'shares={ {k: round(v/n*100,2) for k,v in sorted(bylen.items())} }')
        print(f'  records with a depth>=3 line: {d3}  max box depth: {maxd}')
        print(f'  RENAMING-CLASS COLLISIONS with heldout: {len(inter)}')
        print(f'  RENAMING-CLASS COLLISIONS with the depth-3 slice: {len(s & d3_cls)}')

    # reproduce the fresh-set construction from the four pools
    print('\nfresh-set construction, recomputed from data/nf/train_p{1..4}.jsonl:')
    seen = set(); tot = 0; dup = 0; hcoll = 0; newc = {}
    for i in range(1, 5):
        p = f'data/nf/train_p{i}.jsonl'
        a = b = 0
        for l in open(p):
            if not l.strip():
                continue
            r = json.loads(l); tot += 1
            k = canon(r['thm'])
            if k in held:
                hcoll += 1; continue
            if k in seen:
                dup += 1; b += 1; continue
            seen.add(k); a += 1
        newc[p] = (a, b)
        print(f'  {p}: new classes {a}, duplicate of an earlier pool {b}')
    print(f'  records in {tot}, distinct classes out {len(seen)}, dropped duplicates {dup}, '
          f'dropped for a heldout-class collision {hcoll}')


main()
