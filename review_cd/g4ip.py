#!/usr/bin/env python3
"""Reviewer's own G4ip (Dyckhoff's contraction-free intuitionistic sequent calculus) for the ND prompt syntax.
Formulas: ('a', 'P') | ('F',) | ('&', A, B) | ('v', A, B) | ('>', A, B); ~A is ('>', A, F)."""
import functools
FALSE = ('F',)
def parse_toks(t, i=0):
    x = t[i]
    if x == '(':
        if t[i + 1] == '~':
            a, j = parse_toks(t, i + 2); assert t[j] == ')'; return ('>', a, FALSE), j + 1
        a, j = parse_toks(t, i + 1); op = t[j]; b, k = parse_toks(t, j + 1); assert t[k] == ')'
        return ({'&': '&', 'v': 'v', '>': '>'}[op], a, b), k + 1
    if x == 'F': return FALSE, i + 1
    return ('a', x), i + 1
def parse(s):
    f, j = parse_toks(s.split()); return f
def sequent(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, concl = body.split(' SEQ ')
    toks = prem.split(); out = []; cur = []; d = 0
    for t in toks:
        if t == ',' and d == 0: out.append(cur); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur: out.append(cur)
    return [parse_toks(p)[0] for p in out], parse(concl)
@functools.lru_cache(maxsize=None)
def prove(G, C):
    """G: frozenset of formulas, C: formula."""
    if C in G or FALSE in G: return True
    # invertible right rules
    if C[0] == '&': return prove(G, C[1]) and prove(G, C[2])
    if C[0] == '>': return prove(G | {C[1]}, C[2])
    # invertible left rules
    for A in G:
        if A[0] == '&': return prove((G - {A}) | {A[1], A[2]}, C)
        if A[0] == 'v': return prove((G - {A}) | {A[1]}, C) and prove((G - {A}) | {A[2]}, C)
        if A[0] == '>':
            a, b = A[1], A[2]
            if a == FALSE: return prove(G - {A}, C)
            if a[0] == 'a' and a in G: return prove((G - {A}) | {b}, C)
            if a[0] == '&': return prove((G - {A}) | {('>', a[1], ('>', a[2], b))}, C)
            if a[0] == 'v': return prove((G - {A}) | {('>', a[1], b), ('>', a[2], b)}, C)
    # non-invertible: right disjunction, left (A > B) > D
    if C[0] == 'v' and (prove(G, C[1]) or prove(G, C[2])): return True
    for A in G:
        if A[0] == '>' and A[1][0] == '>':
            (_, (_, a, b), d) = A
            rest = G - {A}
            if prove(rest | {('>', b, d)}, ('>', a, b)) and prove(rest | {d}, C): return True
    return False
def intuit_provable(prompt):
    P, C = sequent(prompt); return prove(frozenset(P), C)
if __name__ == '__main__':
    T = {'THM SEQ ( P v ( ~ P ) ) PRF': False, 'THM SEQ ( ~ ( ~ ( P v ( ~ P ) ) ) ) PRF': True, 'THM SEQ ( ( P & Q ) > P ) PRF': True,
         'THM SEQ ( ( ( P > Q ) > P ) > P ) PRF': False, 'THM ( ~ ( ~ P ) ) SEQ P PRF': False, 'THM P SEQ ( ~ ( ~ P ) ) PRF': True,
         'THM SEQ ( ( ( Q & R ) & ( ~ R ) ) v ( ~ ( ( Q & R ) & ( ~ R ) ) ) ) PRF': True, 'THM ( P > Q ) SEQ ( ( ~ Q ) > ( ~ P ) ) PRF': True,
         'THM ( ( ~ Q ) > ( ~ P ) ) SEQ ( P > Q ) PRF': False, 'THM ( ~ ( P & Q ) ) SEQ ( ( ~ P ) v ( ~ Q ) ) PRF': False,
         'THM ( ~ ( P v Q ) ) SEQ ( ( ~ P ) & ( ~ Q ) ) PRF': True, 'THM SEQ ( ( ~ ( ~ ( ~ P ) ) ) > ( ~ P ) ) PRF': True}
    for p, e in T.items():
        assert intuit_provable(p) == e, (p, e)
    print('g4ip self-test ok', len(T))
