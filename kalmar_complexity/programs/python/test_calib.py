#!/usr/bin/env python3
"""Randomised tests of the calibration programs in calib/ (run kalmar-complexity).  eval / taut are checked against
kalmar.val / kalmar.countermodel on K12 theorems; taut also on the same sequents without premises (mostly invalid)."""
import importlib, os, random, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, 'calib')); sys.path.insert(0, H)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(H))))
from kalmar_complexity.common import sample_prompts
import kalmar as KM
from parse import S


def tok2km(f):
    if f == 'F': return ('bot',)
    if isinstance(f, str): return ('atom', f)
    if f[0] == '~': return ('not', tok2km(f[1]))
    return ({'&': 'and', 'v': 'or', '>': 'imp'}[f[0]], tok2km(f[1]), tok2km(f[2]))


def main(seed=1, n=500):
    R = random.Random(seed)
    m = {k: importlib.import_module(k) for k in ['copy', 'reverse', 'parity', 'parity_nb', 'sort', 'sort_nb', 'add',
                                                  'add_nb', 'eval', 'taut']}
    bits = lambda z: [int(c) for c in bin(z)[2:][::-1]] if z else []
    val = lambda bl: sum(d << i for i, d in enumerate(bl))
    ok = {}
    for _ in range(n):
        l = [R.randint(0, 9) for _ in range(R.randint(0, 12))]
        b = [R.randint(0, 1) for _ in range(R.randint(0, 20))]
        x, y = R.randint(0, 10 ** 6), R.randint(0, 10 ** 6)
        for k, good in [('copy', m['copy'].c(l) == l), ('reverse', m['reverse'].r(l) == l[::-1]),
                        ('parity', m['parity'].p(b) == sum(b) % 2), ('parity_nb', m['parity_nb'].p(b) == sum(b) % 2),
                        ('sort', list(m['sort'].s(l)) == sorted(l)), ('sort_nb', m['sort_nb'].s(l) == sorted(l)),
                        ('add', m['add'].a(x, y) == x + y), ('add_nb', val(m['add_nb'].a(bits(x), bits(y))) == x + y)]:
            ok[k] = ok.get(k, 0) + bool(good)
    ok['eval'] = ok['taut'] = ok['taut_noprem'] = 0
    for p in sample_prompts(n, seed + 4):
        P, G = S(p)
        v = {a: R.random() < 0.5 for a in 'PQRS'}
        ok['eval'] += bool(m['eval'].V(G, {**v, 'F': 0})) == KM.val(tok2km(G), v)
        ok['taut'] += bool(m['taut'].T(P, G)) == (KM.countermodel([tok2km(q) for q in P], tok2km(G)) is None)
        ok['taut_noprem'] += bool(m['taut'].T([], G)) == (KM.countermodel([], tok2km(G)) is None)
    print(f'{n} cases each:', ok)
    return ok


if __name__ == '__main__':
    main()
