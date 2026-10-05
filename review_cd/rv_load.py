#!/usr/bin/env python3
"""Reviewer loaders (capability-defs review; written independently of capability_defs/analysis/cd_reads.py).
Reads the ORIGINAL per-theorem read files (not organism-analysis's compacted copies):
  cap 12: trajectory (W/trajectory/artifacts/tj/eval), rl-continue r12/r16 x1, this run's J5 r16 x0,
          mcts-a pool reads (x2), C-only (x4), r8 C k 2,560 (x10), rl-from-ckpt replay-only control c<S>_pend_r8 (ctrl8)
  cap 6:  trajectory-cap6, rl-continue-cap6 r16 tb72 x1, J5 cap-6 r16 h250 x1
Each read -> {name: (n_ok, n_tried, proofs)}."""
import gzip, json, os, glob
H = os.path.expanduser('~')
RV = os.environ.get('RV_ROOT', os.path.join(H, 'review', 'capability-defs'))   # repo copy holding artifacts/cd, data/
CD = os.path.join(RV, 'artifacts', 'cd')
TJ = f'{H}/work/trajectory/artifacts/tj/eval'
TJ6 = f'{H}/work/trajectory-cap6/artifacts/tj6/eval'
RC = f'{H}/work/rl-continue/artifacts/rc/eval'
RC6 = f'{H}/work/rl-continue-cap6/artifacts/rc6/eval'
RFC = f'{H}/work/rl-from-ckpt/artifacts/rfc/eval'
PT = ['p0', 'p50', 'p100', 'p200', 'p400', 'p800', 'p1600', 'p3000', 'p5000', 'p8000', 'p12000', 'p16000', 'p20000', 'pend']
RL = [f'r{i}' for i in range(1, 9)]
STEPS = {'p0': 0, 'p50': 50, 'p100': 100, 'p200': 200, 'p400': 400, 'p800': 800, 'p1600': 1600, 'p3000': 3000,
         'p5000': 5000, 'p8000': 8000, 'p12000': 12000, 'p16000': 16000, 'p20000': 20000}


def rows(p):
    op = gzip.open if p.endswith('.gz') else open
    with op(p, 'rt') as f:
        for l in f:
            if l.strip():
                yield json.loads(l)


def path(cap, s, ck, pool, x):
    if cap == 12:
        if x in (0, 1) and (ck in PT or ck in RL):
            return f'{TJ}/s{s}_{ck}__{pool}_x{x}.jsonl'
        if ck in ('r12', 'r16') and x == 1:
            return f'{RC}/s{s}_{ck}__{pool}_x1.jsonl'
        if ck == 'r16' and x == 0:
            return f'{CD}/j5/s{s}_r16__{pool}_x0.jsonl'
        if ck in ('pend', 'r8') and x == 2:
            return f'{CD}/in/mcts/s{s}_{ck}__{pool}__sample.jsonl'
        if ck in ('pend', 'r8') and x == 4 and pool == 'C':
            return f'{CD}/in/mcts/s{s}_{ck}__C__sample.jsonl'
        if ck == 'r8' and x == 10 and pool == 'C':
            return f'{CD}/in/mcts_x10/s{s}_r8__C__sample.jsonl'
        if ck == 'ctrl8' and x in (0, 1):
            return f'{RFC}/c{s}_pend_r8__{pool}_x{x}.jsonl'
    if cap == 6:
        if x in (0, 1) and (ck in PT or ck in RL):
            return f'{TJ6}/s{s}_{ck}__{pool}_x{x}.jsonl'
        if ck == 'r16' and x == 1 and pool == 'tb72':
            return f'{RC6}/s{s}_r16__tb72_x1.jsonl'
        if ck == 'r16' and x == 1 and pool == 'h250':
            return f'{CD}/j5/c6_s{s}_r16__h250_x1.jsonl'
    return None


_c = {}
def read(cap, s, ck, pool, x):
    k = (cap, s, ck, pool, x)
    if k not in _c:
        p = path(*k)
        if p is None or not os.path.exists(p):
            _c[k] = None
        else:
            _c[k] = {r['name']: (int(r['n_ok']), int(r['n_tried']), list(r.get('proofs') or [])) for r in rows(p)}
    return _c[k]


def both(cap, s, ck, x):
    """tb72 + h250 merged, or None if either pool is missing."""
    a, b = read(cap, s, ck, 'tb72', x), read(cap, s, ck, 'h250', x)
    if a is None or b is None:
        return None
    d = dict(a); d.update(b)
    return d


def pool_names(pool):
    f = {'tb72': 'textbook72.jsonl', 'h250': 'holdout250.jsonl'}[pool]
    return [r['name'] for r in rows(f'{RV}/data/bs/{f}')]


def prompts():
    out = {}
    for f in ('textbook72.jsonl', 'holdout250.jsonl'):
        for r in rows(f'{RV}/data/bs/{f}'):
            out[r['name']] = r['prompt']
    return out


NAMES = None
def names():
    global NAMES
    if NAMES is None:
        NAMES = pool_names('tb72') + pool_names('h250')
    return NAMES
