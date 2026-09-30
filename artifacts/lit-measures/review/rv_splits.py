#!/usr/bin/env python3
"""Reviewer: renaming-class disjointness, premise-order insensitive (F is falsum, not an atom)."""
import json, itertools, sys
def key(thm):
    lhs, rhs = thm.split(' |- ')
    prem = [p.strip() for p in lhs.split(' , ')] if lhs.strip() else []
    best = None
    perms = itertools.permutations(prem) if len(prem) <= 5 else [sorted(prem)]
    for pp in perms:
        m = {}; out = []
        for t in (' , '.join(pp) + ' |- ' + rhs).split():
            if len(t) == 1 and t.isupper() and t != 'F':
                m.setdefault(t, 'ABCDEGHIJ'[len(m)]); out.append(m[t])
            else: out.append(t)
        s = ' '.join(out)
        if best is None or s < best: best = s
    return best
def keys(fn, fld='thm'):
    return {key(json.loads(l)[fld]) for l in open(fn) if l.strip()}
if __name__ == '__main__':
    tr = keys(sys.argv[1]); print('train classes', len(tr))
    for f in sys.argv[2:]:
        k = keys(f); print(f, 'classes', len(k), 'overlap with train', len(k & tr))
