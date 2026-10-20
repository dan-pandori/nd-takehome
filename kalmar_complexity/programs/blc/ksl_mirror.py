#!/usr/bin/env python3
"""Python mirror of the BLC K-sl program's design (continuation-passing, scopes as functions, line numbers assigned by
the algorithm).  Used only to validate the design against kalmar.build(..., 'sl') before writing lambda terms.

Structured proof = list of lines (n, d, formula, rule, refs): n = line number, d = box depth, refs = cited line numbers
(box citations as start/end).  Emission order = render order, so numbering in the algorithm is the reference numbering.

Scope (kalmar.py: a stack of dicts with setdefault, innermost first):  I = innermost scope as a function
I(t, g, f, nf) that checks its entries OLDEST first and calls g(line) if the match is the newest entry of the innermost
scope (= the last line written in the current box), f(line) for an older match, nf() if none;  O(t, f, nf) = the outer
scopes.  push / open / lookup as below.
"""
import os
import sys

sys.setrecursionlimit(100000)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "kalmar"))
BOT = ('bot',)


def ksl(prems, goal):
    def push(sc, phi, m):
        I, O = sc
        return (lambda t, g, f, nf: I(t, f, f, lambda: g(m) if t == phi else nf()), O)

    def open_(sc, h, m):
        I, O = sc
        return (lambda t, g, f, nf: g(m) if t == h else nf(), lambda t, f, nf: I(t, f, f, lambda: O(t, f, nf)))

    def lookup(sc, t, g, f, nf):
        I, O = sc
        return I(t, g, f, lambda: O(t, f, nf))

    def emit(phi, rule, refs, sc, n, d, k):
        return [(n, d, phi, rule, refs)] + k(n, push(sc, phi, n), n + 1)

    def box(h, body, sc, n, d, k):          # k(start, end, n')
        return [(n, d + 1, h, 'AS', [])] + body(n, open_(sc, h, n), n + 1, d + 1, lambda j, sc2, n2: k(n, j, n2))

    def negI(h, body, sc, n, d, k):
        return box(h, body, sc, n, d, lambda s, e, n2: emit(('not', h), 'NEGI', [s, e], sc, n2, d, k))

    def impI(phi, h, body, sc, n, d, k):
        return box(h, body, sc, n, d, lambda s, e, n2: emit(phi, 'IMPI', [s, e], sc, n2, d, k))

    def val(phi, hyps):
        t = phi[0]
        if t == 'atom':
            return phi in hyps
        if t == 'bot':
            return False
        if t == 'not':
            return not val(phi[1], hyps)
        a, b = val(phi[1], hyps), val(phi[2], hyps)
        return (a and b) if t == 'and' else (a or b) if t == 'or' else ((not a) or b)

    def lit(phi, hyps, sc, n, d, k):          # k(j, sc, n)
        t = val(phi, hyps)
        target = phi if t else ('not', phi)
        found = lambda j: k(j, sc, n)
        return lookup(sc, target, found, found, lambda: derive(phi, t, hyps, sc, n, d, k))

    def derive(phi, t, hyps, sc, n, d, k):
        c = phi[0]
        if c == 'bot':
            return negI(BOT, lambda h, sc, n, d, kb: kb(h, sc, n), sc, n, d, k)
        if c == 'not':
            def after(a, sc, n):
                if t:
                    return k(a, sc, n)
                return negI(phi, lambda h, sc, n, d, kb: emit(BOT, 'NEGE', [a, h], sc, n, d, kb), sc, n, d, k)
            return lit(phi[1], hyps, sc, n, d, after)
        A, B = phi[1], phi[2]
        vA, vB = val(A, hyps), val(B, hyps)
        if c == 'and':
            if t:
                return lit(A, hyps, sc, n, d, lambda a, sc, n: lit(B, hyps, sc, n, d, lambda b, sc, n:
                           emit(phi, 'ANDI', [a, b], sc, n, d, k)))
            Z, rule = (A, 'ANDE1') if not vA else (B, 'ANDE2')
            return lit(Z, hyps, sc, n, d, lambda a, sc, n: negI(phi, lambda h, sc, n, d, kb:
                       emit(Z, rule, [h], sc, n, d, lambda x, sc, n: emit(BOT, 'NEGE', [x, a], sc, n, d, kb)),
                       sc, n, d, k))
        if c == 'or':
            if t:
                if vA:
                    return lit(A, hyps, sc, n, d, lambda a, sc, n: emit(phi, 'ORI1', [a], sc, n, d, k))
                return lit(B, hyps, sc, n, d, lambda b, sc, n: emit(phi, 'ORI2', [b], sc, n, d, k))

            def orneg(na, nb, sc, n):
                def body(h, sc, n, d, kb):
                    return box(A, lambda h1, sc, n, d, kb1: emit(BOT, 'NEGE', [h1, na], sc, n, d, kb1), sc, n, d,
                               lambda s1, e1, n1: box(B, lambda h2, sc, n, d, kb2: emit(BOT, 'NEGE', [h2, nb], sc, n, d,
                                                                                         kb2), sc, n1, d,
                                                      lambda s2, e2, n2: emit(BOT, 'ORE', [h, s1, e1, s2, e2], sc, n2,
                                                                              d, kb)))
                return negI(phi, body, sc, n, d, k)
            return lit(A, hyps, sc, n, d, lambda na, sc, n: lit(B, hyps, sc, n, d, lambda nb, sc, n:
                       orneg(na, nb, sc, n)))
        # implication
        if vB:
            return lit(B, hyps, sc, n, d, lambda b, sc, n: impI(phi, A, lambda h, sc, n, d, kb:
                       emit(B, 'R', [b], sc, n, d, kb), sc, n, d, k))
        if not vA:
            return lit(A, hyps, sc, n, d, lambda a, sc, n: impI(phi, A, lambda h, sc, n, d, kb:
                       emit(BOT, 'NEGE', [h, a], sc, n, d, lambda f, sc, n: emit(B, 'BOTE', [f], sc, n, d, kb)),
                       sc, n, d, k))
        return lit(A, hyps, sc, n, d, lambda a, sc, n: lit(B, hyps, sc, n, d, lambda nb, sc, n: negI(phi,
                   lambda h, sc, n, d, kb: emit(B, 'IMPE', [h, a], sc, n, d, lambda y, sc, n:
                                               emit(BOT, 'NEGE', [y, nb], sc, n, d, kb)), sc, n, d, k)))

    def lem(X, sc, n, d, k):
        em = ('or', X, ('not', X))
        nem = ('not', em)
        found = lambda j: k(j, sc, n)

        def outer(h, sc, n, d, kb):
            def inner(p, sc, n, d, kb2):
                return emit(em, 'ORI1', [p], sc, n, d, lambda j1, sc, n: emit(BOT, 'NEGE', [j1, h], sc, n, d, kb2))
            return negI(X, inner, sc, n, d, lambda nx, sc, n: emit(em, 'ORI2', [nx], sc, n, d, lambda j2, sc, n:
                        emit(BOT, 'NEGE', [j2, h], sc, n, d, kb)))
        return lookup(sc, em, found, found, lambda: negI(nem, outer, sc, n, d, lambda j, sc, n:
                      emit(em, 'DN', [j], sc, n, d, k)))

    def leaf(hyps, sc, n, d, k):
        def efq(ps, i):
            if not ps:
                return lookup(sc, goal, lambda j: k(j, sc, n), lambda j: emit(goal, 'R', [j], sc, n, d, k),
                              lambda: lit(goal, hyps, sc, n, d, k))
            p = ps[0]
            if val(p, hyps):
                return efq(ps[1:], i + 1)
            return lit(p, hyps, sc, n, d, lambda np_, sc, n: emit(BOT, 'NEGE', [i, np_], sc, n, d,
                       lambda f, sc, n: k(f, sc, n) if goal == BOT else emit(goal, 'BOTE', [f], sc, n, d, k)))
        return efq(prems, 1)

    def split(atoms, hyps, sc, n, d, k):
        if not atoms:
            return leaf(hyps, sc, n, d, k)
        (X, em), rest = atoms[0], atoms[1:]
        NX = ('not', X)
        return box(X, lambda h, sc, n, d, kb: split(rest, [X] + hyps, sc, n, d, kb), sc, n, d,
                   lambda s1, e1, n1: box(NX, lambda h, sc, n, d, kb: split(rest, [NX] + hyps, sc, n, d, kb), sc, n1, d,
                                          lambda s2, e2, n2: emit(goal, 'ORE', [em, s1, e1, s2, e2], sc, n2, d, k)))

    def occurs(X, f):
        return f == X or (f[0] in ('not', 'and', 'or', 'imp') and any(occurs(X, g) for g in f[1:]))

    def lems(xs, acc, sc, n):
        if not xs:
            return split(acc, [], sc, n, 0, lambda j, sc, n: [])
        X = xs[0]
        if not any(occurs(X, f) for f in prems + [goal]):
            return lems(xs[1:], acc, sc, n)
        return lem(X, sc, n, 0, lambda j, sc, n: lems(xs[1:], acc + [(X, j)], sc, n))

    def prs(ps, sc, n):
        if not ps:
            return lems([('atom', x) for x in 'PQRS'], [], sc, n)
        return emit(ps[0], 'PR', [], sc, n, 0, lambda j, sc, n: prs(ps[1:], sc, n))

    empty = (lambda t, g, f, nf: nf(), lambda t, f, nf: nf())
    return prs(prems, empty, 1)


def fnd_toks(f):
    t = f[0]
    if t == 'atom':
        return [f[1]]
    if t == 'bot':
        return ['F']
    if t == 'not':
        return ['(', '~'] + fnd_toks(f[1]) + [')']
    return ['('] + fnd_toks(f[1]) + [{'and': '&', 'or': 'v', 'imp': '>'}[t]] + fnd_toks(f[2]) + [')']


def render(lines):
    out = []
    for n, d, f, rule, refs in lines:
        out += [f'N{n}'] + ['|'] * d + fnd_toks(f) + [':', rule] + [f'N{r}' for r in refs] + [';']
    return out + ['QED']


if __name__ == '__main__':
    from kalmar_complexity.common import sample_prompts, ref_sl
    from nd2lean import parse_prompt
    import json
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20261020
    ok = 0
    for p in sample_prompts(n, seed):
        prem, goal = parse_prompt(p)
        got = ' '.join(render(ksl(prem, goal)))
        want = ref_sl(p)['proof']
        if got == want:
            ok += 1
        else:
            print('MISMATCH', p)
            print(' got ', got[:300])
            print(' want', want[:300])
            break
    print(f'{ok}/{n}')
