#!/usr/bin/env python3
"""Theorem-level labels for every record of a set (does the THEOREM force a strategy, whatever the proof does?):

  classical  : valid classically but not intuitionistically (G4ip, intuit.py), so every proof uses DN somewhere;
  dneg       : the sequent contains a double negation, semantically: ¬¬X, ¬X → ⊥, ¬(X → ⊥) or (X → ⊥) → ⊥;
  sigma_cov  : classical and no dneg (create-or-elicit's "σ-covered"): every proof must eliminate a double negation it
               built itself (a working proof by contradiction or a disguised one);
  inconsistent : the premises are jointly unsatisfiable (truth table over P Q R S), so ex falso proves anything.

  python3 proof_strategies/theorem_level.py --in SET.jsonl[.gz] --out OUT.jsonl.gz
"""
import argparse, gzip, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from intuit import prove, elim_not                     # noqa: E402
from minlen import parse_thm                           # noqa: E402

BOT = ('bot',)


def neg_body(f):
    """X if f is a negation of X (¬X or X → ⊥), else None."""
    if f[0] == 'not':
        return f[1]
    if f[0] == 'imp' and f[2] == BOT:
        return f[1]
    return None


def has_dneg(f):
    b = neg_body(f)
    if b is not None and neg_body(b) is not None:
        return True
    return any(has_dneg(g) for g in f[1:] if isinstance(g, tuple))


def ev(f, v):
    t = f[0]
    if t == 'atom':
        return v[f[1]]
    if t == 'bot':
        return False
    if t == 'not':
        return not ev(f[1], v)
    if t == 'and':
        return ev(f[1], v) and ev(f[2], v)
    if t == 'or':
        return ev(f[1], v) or ev(f[2], v)
    return (not ev(f[1], v)) or ev(f[2], v)


def label(prompt):
    prem, concl = parse_thm(prompt)
    classical = not prove(tuple(elim_not(p) for p in prem), elim_not(concl))
    dn = any(has_dneg(f) for f in list(prem) + [concl])
    vals = [dict(zip('PQRS', bits)) for bits in itertools.product((False, True), repeat=4)]
    inconsistent = bool(prem) and not any(all(ev(p, v) for p in prem) for v in vals)
    return {'classical': classical, 'dneg': dn, 'sigma_cov': classical and not dn, 'inconsistent': inconsistent}


def selftest():
    cases = {'THM ( ~ ( ~ P ) ) SEQ P PRF': (True, True, False, False),
             'THM ( ( P > Q ) > P ) SEQ P PRF': (True, False, True, False),
             'THM P , ( ~ P ) SEQ Q PRF': (False, False, False, True),
             'THM ( ( ~ P ) > F ) SEQ P PRF': (True, True, False, False),
             'THM ( P > Q ) , ( ~ Q ) SEQ ( ~ P ) PRF': (False, False, False, False),
             'THM SEQ ( P v ( ~ P ) ) PRF': (True, False, True, False)}
    for p, want in cases.items():
        got = label(p)
        assert (got['classical'], got['dneg'], got['sigma_cov'], got['inconsistent']) == want, (p, got)
    print('theorem_level selftest ok')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp')
    ap.add_argument('--out')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    op = (lambda f: gzip.open(f, 'rt')) if a.inp.endswith('.gz') else open
    n = 0
    tot = {'classical': 0, 'dneg': 0, 'sigma_cov': 0, 'inconsistent': 0}
    with gzip.open(a.out, 'wt') as fo:
        for i, line in enumerate(op(a.inp)):
            r = json.loads(line)
            lab = label(r['prompt'])
            fo.write(json.dumps({'i': i, **lab}) + '\n')
            n += 1
            for k in tot:
                tot[k] += lab[k]
    print(json.dumps({'in': a.inp, 'n': n, **tot}))


if __name__ == '__main__':
    main()
