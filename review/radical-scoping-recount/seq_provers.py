"""Reviewer-owned exact propositional decision procedures (unbounded, independent of minlen / nd_verify):
  classical G3c (all rules invertible), optionally without L-or  -> 'needs ORE' label in classical ND
  (ND without OrE ~ G3c+cut without L-or; cut elimination introduces no L-or, so cut-free G3c minus L-or decides it);
  intuitionistic G4ip (Dyckhoff)                                   -> 'needs a classical rule (DN)' = classically valid
  but not intuitionistically valid."""
from functools import lru_cache
BOT = ('F',)
def parse(toks, i=0):
    t = toks[i]
    if t == 'F': return BOT, i + 1
    if t in 'PQRS': return ('a', t), i + 1
    assert t == '('
    if toks[i + 1] == '~':
        a, j = parse(toks, i + 2); assert toks[j] == ')'; return ('i', a, BOT), j + 1
    a, j = parse(toks, i + 1); op = toks[j]; b, k = parse(toks, j + 1); assert toks[k] == ')'
    return ({'&': 'c', 'v': 'd', '>': 'i'}[op], a, b), k + 1
def parse_prompt(p):
    t = p.split(); assert t[0] == 'THM'; i = 1; prem = []
    while t[i] != 'SEQ':
        f, i = parse(t, i); prem.append(f)
        if t[i] == ',': i += 1
    c, i = parse(t, i + 1); return prem, c

@lru_cache(None)
def g3c(G, D, use_lor=True):
    G, D = frozenset(G), frozenset(D)
    if BOT in G or (G & D): return True
    for f in G:
        if f[0] == 'c': return g3c((G - {f}) | {f[1], f[2]}, D, use_lor)
        if f[0] == 'd' and use_lor: return g3c((G - {f}) | {f[1]}, D, use_lor) and g3c((G - {f}) | {f[2]}, D, use_lor)
        if f[0] == 'i': return g3c(G - {f}, D | {f[1]}, use_lor) and g3c((G - {f}) | {f[2]}, D, use_lor)
    for f in D:
        if f[0] == 'c': return g3c(G, (D - {f}) | {f[1]}, use_lor) and g3c(G, (D - {f}) | {f[2]}, use_lor)
        if f[0] == 'd': return g3c(G, (D - {f}) | {f[1], f[2]}, use_lor)
        if f[0] == 'i': return g3c(G | {f[1]}, (D - {f}) | {f[2]}, use_lor)
    return False

def imp(a, b): return ('i', a, b)
@lru_cache(None)
def g4ip(G, C):
    G = frozenset(G)
    if BOT in G or C in G: return True
    # invertible left rules
    for f in G:
        R = G - {f}
        if f[0] == 'c': return g4ip(R | {f[1], f[2]}, C)
        if f[0] == 'd': return g4ip(R | {f[1]}, C) and g4ip(R | {f[2]}, C)
        if f[0] == 'i':
            a, b = f[1], f[2]
            if a == BOT: return g4ip(R, C)
            if a[0] == 'a' and a in G: return g4ip(R | {b}, C)
            if a[0] == 'c': return g4ip(R | {imp(a[1], imp(a[2], b))}, C)
            if a[0] == 'd': return g4ip(R | {imp(a[1], b), imp(a[2], b)}, C)
    if C[0] == 'c': return g4ip(G, C[1]) and g4ip(G, C[2])
    if C[0] == 'i': return g4ip(G | {C[1]}, C[2])
    if C[0] == 'd' and (g4ip(G, C[1]) or g4ip(G, C[2])): return True
    for f in G:  # non-invertible L-imp with implication antecedent
        if f[0] == 'i' and f[1][0] == 'i':
            (c, d), b = f[1][1:], f[2]; R = G - {f}
            if g4ip(R | {imp(d, b)}, imp(c, d)) and g4ip(R | {b}, C): return True
    return False

def labels(prompt):
    prem, c = parse_prompt(prompt); G = frozenset(prem)
    cl = g3c(G, frozenset({c})); return dict(classical=cl, intuitionistic=g4ip(G, c), classical_no_lor=g3c(G, frozenset({c}), False))

if __name__ == '__main__':
    tests = [('THM SEQ ( P v ( ~ P ) ) PRF', (True, False, True)), ('THM ( ~ ( ~ P ) ) SEQ P PRF', (True, False, True)),
             ('THM ( P v Q ) SEQ ( Q v P ) PRF', (True, True, False)), ('THM ( P v Q ) , ( ~ P ) SEQ Q PRF', (True, True, False)),
             ('THM ( ( P > Q ) > P ) SEQ P PRF', (True, False, True)), ('THM SEQ ( ~ ( ~ ( P v ( ~ P ) ) ) ) PRF', (True, True, True)),
             ('THM P SEQ Q PRF', (False, False, False)), ('THM ( ~ ( P & Q ) ) SEQ ( ( ~ P ) v ( ~ Q ) ) PRF', (True, False, True)),
             ('THM ( ( ~ P ) v ( ~ Q ) ) SEQ ( ~ ( P & Q ) ) PRF', (True, True, False)), ('THM ( P > Q ) SEQ ( ( ~ Q ) > ( ~ P ) ) PRF', (True, True, True))]
    for p, exp in tests:
        l = labels(p); got = (l['classical'], l['intuitionistic'], l['classical_no_lor'])
        print('OK ' if got == exp else 'BAD', p, got)
