#!/usr/bin/env python3
"""calibration programs: randomized tests against Python (imported by test_blc.py; runnable alone)."""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nd_codec  # noqa: E402,F401
import blc  # noqa: E402

CALIB = ['copy', 'reverse', 'parity', 'add', 'sort', 'eval', 'taut']


def bits_le(n):
    out = []
    while n:
        out.append(bool(n & 1))
        n >>= 1
    return out


def rand_formula(rng, depth):
    if depth == 0 or rng.random() < 0.3:
        return ('bot',) if rng.random() < 0.1 else ('atom', rng.choice('PQRS'))
    k = rng.choice(['not', 'and', 'or', 'imp'])
    if k == 'not':
        return ('not', rand_formula(rng, depth - 1))
    return (k, rand_formula(rng, depth - 1), rand_formula(rng, depth - 1))


def cases(name, rng, n, k12=None):
    """-> list of (input term, expected python value, decoder)"""
    from kalmar import val, countermodel
    out = []
    for i in range(n):
        if name in ('copy', 'reverse', 'sort'):
            xs = [rng.randrange(0, 8 if name == 'sort' else 20) for _ in range(rng.randrange(0, 12))]
            exp = xs if name == 'copy' else xs[::-1] if name == 'reverse' else sorted(xs)
            out.append((blc.enc_list(xs, blc.enc_church), exp, lambda m, t: blc.dec_list(m, t, blc.dec_church)))
        elif name == 'parity':
            xs = [rng.random() < 0.5 for _ in range(rng.randrange(0, 20))]
            out.append((blc.enc_list(xs, blc.enc_bool), sum(xs) % 2 == 1, blc.dec_bool))
        elif name == 'add':
            a, b = rng.randrange(0, 1 << rng.randrange(0, 16)), rng.randrange(0, 1 << rng.randrange(0, 16))
            inp = blc.enc_pair(blc.enc_list(bits_le(a), blc.enc_bool), blc.enc_list(bits_le(b), blc.enc_bool))
            out.append((inp, bits_le(a + b), lambda m, t: blc.dec_list(m, t, blc.dec_bool)))
        elif name == 'eval':
            f = rand_formula(rng, rng.randrange(0, 6))
            v = {x: rng.random() < 0.5 for x in 'PQRS'}
            inp = blc.enc_pair(blc.enc_formula(f), blc.enc_list([v[x] for x in 'PQRS'], blc.enc_bool))
            out.append((inp, val(f, v), blc.dec_bool))
        elif name == 'taut':
            if k12 is not None and i % 2 == 0:
                prem, goal = k12[i % len(k12)]          # valid K12 sequents
            else:
                prem = [rand_formula(rng, rng.randrange(0, 4)) for _ in range(rng.randrange(0, 3))]
                goal = rand_formula(rng, rng.randrange(0, 4))
            out.append((blc.enc_sequent(prem, goal), countermodel(prem, goal) is None, blc.dec_bool))
    return out


def check(name, db, n=200, seed=0, k12=None, machine=blc.Machine):
    rng = random.Random(seed)
    ok, steps = 0, []
    for inp, exp, dec in cases(name, rng, n, k12):
        m = machine()
        th = m.closed((2, db, inp))
        got = dec(m, th)
        if got == exp:
            ok += 1
        steps.append(m.beta)
    return ok, steps


if __name__ == '__main__':
    import statistics as st
    for name in CALIB:
        prog = blc.Program.load(os.path.join(HERE, 'calib', name + '.lam'))
        prog.optimise()
        db = prog.debruijn()
        ok, steps = check(name, db, 200, seed=1)
        print(f'{name:8s} {prog.bits():5d} bits  CL {blc.cl_bits(blc.to_cl_best(db)):5d}  {ok}/200  '
              f'beta mean {st.mean(steps):.0f} max {max(steps)}')
