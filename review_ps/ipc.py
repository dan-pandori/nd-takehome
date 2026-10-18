"""Reviewer's own intuitionistic provability (Dyckhoff's G4ip / LJT) + classical truth tables.
Written from Dyckhoff 1992 (contraction-free sequent calculus), not from intuit.py.
Formulas as in nd.py; ~A is treated as A > F."""
import itertools
import sys

sys.setrecursionlimit(10000)


def norm(f):
    if isinstance(f, str):
        return f
    if f[0] == "~":
        return (">", norm(f[1]), "F")
    return (f[0], norm(f[1]), norm(f[2]))


def atoms(f, acc):
    if isinstance(f, str):
        if f != "F":
            acc.add(f)
    else:
        for g in f[1:]:
            atoms(g, acc)
    return acc


def ev(f, v):
    if isinstance(f, str):
        return False if f == "F" else v[f]
    if f[0] == "~":
        return not ev(f[1], v)
    a = ev(f[1], v)
    if f[0] == "&":
        return a and ev(f[2], v)
    if f[0] == "v":
        return a or ev(f[2], v)
    return (not a) or ev(f[2], v)


def assignments(fs):
    at = sorted(set().union(*[atoms(f, set()) for f in fs])) if fs else []
    for bits in itertools.product([False, True], repeat=len(at)):
        yield dict(zip(at, bits))


def classically_valid(prem, concl):
    return all(ev(concl, v) for v in assignments(prem + [concl]) if all(ev(p, v) for p in prem))


def satisfiable(fs):
    return any(all(ev(p, v) for p in fs) for v in assignments(fs))


_memo = {}


def prove(gamma, goal):
    """gamma: frozenset of normalised formulas; goal: normalised formula."""
    key = (gamma, goal)
    if key in _memo:
        return _memo[key]
    _memo[key] = False  # G4ip terminates; this only guards accidental re-entry
    res = _prove(gamma, goal)
    _memo[key] = res
    return res


def _prove(G, g):
    if "F" in G or g in G:
        return True
    # invertible left rules
    for f in G:
        if isinstance(f, tuple):
            if f[0] == "&":
                return prove((G - {f}) | {f[1], f[2]}, g)
            if f[0] == "v":
                R = G - {f}
                return prove(R | {f[1]}, g) and prove(R | {f[2]}, g)
            if f[0] == ">":
                a, b = f[1], f[2]
                if a == "F":
                    return prove(G - {f}, g)
                if isinstance(a, str) and a in G:
                    return prove((G - {f}) | {b}, g)
                if isinstance(a, tuple) and a[0] == "&":
                    return prove((G - {f}) | {(">", a[1], (">", a[2], b))}, g)
                if isinstance(a, tuple) and a[0] == "v":
                    return prove((G - {f}) | {(">", a[1], b), (">", a[2], b)}, g)
    # invertible right rules
    if isinstance(g, tuple):
        if g[0] == "&":
            return prove(G, g[1]) and prove(G, g[2])
        if g[0] == ">":
            return prove(G | {g[1]}, g[2])
    # non-invertible: right disjunction, left (C > D) > B
    if isinstance(g, tuple) and g[0] == "v":
        if prove(G, g[1]) or prove(G, g[2]):
            return True
    for f in G:
        if isinstance(f, tuple) and f[0] == ">" and isinstance(f[1], tuple) and f[1][0] == ">":
            c, d, b = f[1][1], f[1][2], f[2]
            R = G - {f}
            if prove(R | {(">", d, b)}, (">", c, d)) and prove(R | {b}, g):
                return True
    return False


def intuitionistic(prem, concl):
    if len(_memo) > 2_000_000:
        _memo.clear()
    return prove(frozenset(norm(p) for p in prem), norm(concl))


if __name__ == "__main__":
    from nd import parse_thm
    tests = [("|- ( P v ( ~ P ) )", False), ("|- ( ( ~ ( ~ P ) ) > P )", False),
             ("|- ( ( ( P > Q ) > P ) > P )", False), ("|- ( ~ ( ~ ( P v ( ~ P ) ) ) )", True),
             ("|- ( ( P > Q ) > ( ( ~ Q ) > ( ~ P ) ) )", True), ("|- ( ( ~ ( P & Q ) ) > ( ( ~ P ) v ( ~ Q ) ) )", False),
             ("|- ( ( ( ~ P ) v ( ~ Q ) ) > ( ~ ( P & Q ) ) )", True), ("|- ( ( ~ ( ~ ( ~ P ) ) ) > ( ~ P ) )", True),
             ("|- ( ( ( ~ P ) > P ) > P )", False), ("|- ( ( P > Q ) v ( Q > P ) )", False),
             ("( P v Q ) , ( ~ P ) |- Q", True), ("( ~ ( P v Q ) ) |- ( ( ~ P ) & ( ~ Q ) )", True),
             ("( ( ~ P ) > Q ) , ( ~ Q ) |- P", False), ("( ( ~ P ) > Q ) , ( ~ Q ) |- ( ~ ( ~ P ) )", True),
             ("( P > Q ) |- ( ( ~ P ) v Q )", False), ("|- ( ~ ( ~ ( ( ~ ( ~ P ) ) > P ) ) )", True),
             ("( ( P > Q ) > Q ) , ( ( Q > P ) > P ) |- ( P v Q )", False), ("|- ( ( P & ( ~ P ) ) > Q )", True),
             ("P , ( ~ P ) |- F", True), ("|- ( ( ( ( ( P > Q ) > P ) > P ) > Q ) > Q )", True),
             ("|- ( ( ( ( P > Q ) > P ) > P ) > Q )", False), ("( ( P > Q ) > P ) |- ( ~ ( ~ P ) )", True),
             ("( ( ~ P ) > F ) |- P", False), ("( ~ ( P > Q ) ) |- P", False), ("( ~ ( P > Q ) ) |- ( ~ Q )", True), ("dummy", None)]
    for t, want in tests[:-1]:
        prem, concl = parse_thm(t)
        got = intuitionistic(prem, concl)
        cv = classically_valid(prem, concl)
        print("OK " if got == want else "BAD", got, "classical", cv, t)
