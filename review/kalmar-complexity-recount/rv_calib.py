#!/usr/bin/env python3
"""Reviewer check of the calibration programs (run kalmar-complexity).

  python3 rv_calib.py blc      # the committed calib/*.blc on my own random cases, my evaluator and codecs
  python3 rv_calib.py py       # the golfed Python calibration programs on my own random cases
  python3 rv_calib.py rasp     # RASP-L calibration programs: my own op / attention-depth count of each graph,
                               # plus the executor's randomised test re-run with a new seed
"""
import json, os, random, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
sys.path.insert(0, HERE); sys.path.insert(0, WS); sys.path.insert(0, os.path.join(WS, 'kalmar'))
import rv_blc as B
from rv_blc import app


def rand_f(rng, d):
    if d == 0 or rng.random() < 0.25:
        return ('bot',) if rng.random() < 0.1 else ('atom', rng.choice('PQRS'))
    k = rng.choice(['not', 'and', 'or', 'imp'])
    if k == 'not':
        return ('not', rand_f(rng, d - 1))
    return (k, rand_f(rng, d - 1), rand_f(rng, d - 1))


def ev(f, v):
    k = f[0]
    if k == 'atom':
        return v[f[1]]
    if k == 'bot':
        return False
    if k == 'not':
        return not ev(f[1], v)
    a, b = ev(f[1], v), ev(f[2], v)
    return (a and b) if k == 'and' else (a or b) if k == 'or' else ((not a) or b)


def valid(prem, goal):
    import itertools
    for bits in itertools.product([True, False], repeat=4):
        v = dict(zip('PQRS', bits))
        if all(ev(p, v) for p in prem) and not ev(goal, v):
            return False
    return True


def le_bits(n):
    o = []
    while n:
        o.append(bool(n & 1)); n >>= 1
    return o


def blc(n=300, seed=4242):
    rng = random.Random(seed)
    d = os.path.join(WS, 'kalmar_complexity/programs/blc/calib')
    k12 = [json.loads(l)['prompt'] for _, l in zip(range(400), open(os.path.join(WS, 'data/kh/train_k12.jsonl')))]
    sys.path.insert(0, HERE)
    from rv_blc_test import parse_prompt
    res = {}
    for name in ['copy', 'reverse', 'parity', 'add', 'sort', 'eval', 'taut']:
        s = open(os.path.join(d, name + '.blc')).read().strip()
        t = B.parse_bits(s)
        ok = 0; ntrue = 0
        for i in range(n):
            m = B.M()
            if name in ('copy', 'reverse', 'sort'):
                xs = [rng.randrange(0, 10) for _ in range(rng.randrange(0, 14))]
                th = m.closed(app(t, B.e_list(xs, B.e_church)))
                got = B.d_list(m, th, B.d_church)
                exp = xs if name == 'copy' else xs[::-1] if name == 'reverse' else sorted(xs)
            elif name == 'parity':
                xs = [rng.random() < 0.5 for _ in range(rng.randrange(0, 25))]
                got = B.d_bool(m, m.closed(app(t, B.e_list(xs, B.e_bool))))
                exp = sum(xs) % 2 == 1
            elif name == 'add':
                a_, b_ = rng.randrange(0, 1 << rng.randrange(0, 20)), rng.randrange(0, 1 << rng.randrange(0, 20))
                inp = B.e_pair(B.e_list(le_bits(a_), B.e_bool), B.e_list(le_bits(b_), B.e_bool))
                got = B.d_list(m, m.closed(app(t, inp)), B.d_bool)
                exp = le_bits(a_ + b_)
            elif name == 'eval':
                f = rand_f(rng, rng.randrange(0, 7))
                v = {x: rng.random() < 0.5 for x in 'PQRS'}
                inp = B.e_pair(B.e_formula(f), B.e_list([v[x] for x in 'PQRS'], B.e_bool))
                got = B.d_bool(m, m.closed(app(t, inp)))
                exp = ev(f, v)
            else:
                if i % 2 == 0:
                    prem, goal = parse_prompt(k12[rng.randrange(len(k12))])
                else:
                    prem = [rand_f(rng, rng.randrange(0, 4)) for _ in range(rng.randrange(0, 4))]
                    goal = rand_f(rng, rng.randrange(0, 4))
                got = B.d_bool(m, m.closed(app(t, B.e_sequent(prem, goal))))
                exp = valid(prem, goal)
            ok += got == exp
            ntrue += exp is True
        res[name] = {'bits': len(s), 'cl_bits': B.cl_bits(B.to_cl_min(t)), 'ok': ok, 'n': n,
                     'expected_true' if name in ('parity', 'eval', 'taut') else 'note': ntrue}
        print(name, res[name], flush=True)
    json.dump(res, open(os.path.join(HERE, 'out', 'calib_blc.json'), 'w'), indent=1)


def py(n=2000, seed=777):
    sys.path.insert(0, os.path.join(WS, 'kalmar_complexity/programs/python/calib'))
    import importlib
    M = {k: importlib.import_module(k) for k in ['copy', 'reverse', 'parity', 'parity_nb', 'sort', 'sort_nb', 'add',
                                                  'add_nb', 'eval', 'taut']}
    rng = random.Random(seed)

    def tf(f):        # kalmar tuple -> the golfed programs' formula form
        k = f[0]
        if k == 'atom':
            return f[1]
        if k == 'bot':
            return 'F'
        if k == 'not':
            return ('~', tf(f[1]))
        return ({'and': '&', 'or': 'v', 'imp': '>'}[k], tf(f[1]), tf(f[2]))
    ok = collections.Counter()
    for _ in range(n):
        l = [rng.randint(-5, 30) for _ in range(rng.randint(0, 15))]
        b = [rng.randint(0, 1) for _ in range(rng.randint(0, 30))]
        x, y = rng.randint(0, 10 ** 9), rng.randint(0, 10 ** 9)
        ok['copy'] += M['copy'].c(l) == l
        ok['reverse'] += list(M['reverse'].r(l)) == l[::-1]
        ok['parity'] += M['parity'].p(b) == sum(b) % 2
        ok['parity_nb'] += M['parity_nb'].p(b) == sum(b) % 2
        ok['sort'] += list(M['sort'].s(l)) == sorted(l)
        ok['sort_nb'] += M['sort_nb'].s(l) == sorted(l)
        ok['add'] += M['add'].a(x, y) == x + y
        bx = [int(c) for c in bin(x)[2:][::-1]]; by = [int(c) for c in bin(y)[2:][::-1]]
        r = M['add_nb'].a(bx, by)
        ok['add_nb'] += sum(d << i for i, d in enumerate(r)) == x + y
        f = rand_f(rng, rng.randrange(0, 7)); v = {a: rng.random() < 0.5 for a in 'PQRS'}
        ok['eval'] += bool(M['eval'].V(tf(f), {**v, 'F': 0})) == ev(f, v)
        prem = [rand_f(rng, rng.randrange(0, 4)) for _ in range(rng.randrange(0, 4))]
        goal = rand_f(rng, rng.randrange(0, 4))
        ok['taut'] += bool(M['taut'].T([tf(p) for p in prem], tf(goal))) == valid(prem, goal)
    res = {'n': n, 'ok': dict(ok)}
    json.dump(res, open(os.path.join(HERE, 'out', 'calib_py.json'), 'w'), indent=1)
    print(res)


def rasp():
    sys.path.insert(0, os.path.join(WS, 'kalmar_complexity/programs/rasp'))
    import rasp as R, calibration as CA
    from rv_rasp import graph
    res = {}
    for name in [n for n in dir(CA) if n.endswith('_prog')]:
        R.reset()
        try:
            outs = getattr(CA, name)()
        except TypeError:
            continue
        outs = list(outs.values()) if isinstance(outs, dict) else (list(outs) if isinstance(outs, (list, tuple)) else [outs])
        nodes = graph(outs)
        kinds = collections.Counter(nd.kind for nd in nodes)
        depth = {}
        for nd in nodes:
            dd = max((depth[x.id] for x in nd.args), default=0)
            depth[nd.id] = dd + (1 if nd.kind in ('aggregate', 'sel_width') else 0)
        res[name] = {'ops_incl_selects': sum(v for k, v in kinds.items() if k not in ('tokens', 'indices', 'const')),
                     'ops_excl_selects': sum(v for k, v in kinds.items() if k not in ('tokens', 'indices', 'const', 'select')),
                     'attn_depth': max(depth[o.id] for o in outs), 'flagged': sum(1 for nd in nodes if nd.flags)}
        print(name, res[name], flush=True)
    json.dump(res, open(os.path.join(HERE, 'out', 'calib_rasp.json'), 'w'), indent=1)


if __name__ == '__main__':
    {'blc': blc, 'py': py, 'rasp': rasp}[sys.argv[1]]()
