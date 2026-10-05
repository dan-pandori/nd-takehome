#!/usr/bin/env python3
"""capability-defs: one loader for every per-theorem read used in Part 3 (pure python, runs on the VPS).

Sources (see capability_defs/analysis/INVENTORY.md):
  cap 12  trajectory reads (organism-analysis compacted copies): s<S>_<ck>__{tb72,h250}_x{0,1}, ck in CKS (22),
          rl-continue reads: s<S>_r{12,16}__{tb72,h250}_x1 (full rows)
  cap 6   trajectory-cap6 reads (compacted), same 22 checkpoints; rl-continue-cap6: s<S>_r16__tb72_x1, s<S>_r16__h250C_x1
  mcts-a  cap-12 pend / r8 fresh-seed plain reads (bucket copies in artifacts/cd/in/): pool reads s<S>_<ck>__<pool>__sample
          -> x = 2; the C-only read s<S>_<ck>__C__sample -> x = 4 (pool 'C'); r8 C at k 2,560 (eval_x10) -> x = 10.
          Also rrQ100 / long2 (x = 2).
Each read -> {name: (n_ok, n_tried, proofs)}.  `proofs` = every distinct Lean-accepted ND proof of that read.
"""
import gzip, json, os

HOME = os.path.expanduser('~')
OA = f'{HOME}/work/organism-analysis/data/oa_in/reads'
RC = f'{HOME}/work/rl-continue/artifacts/rc/eval'
RC6 = f'{HOME}/work/rl-continue-cap6/artifacts/rc6/eval'
MC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'artifacts', 'cd', 'in')
CKS = ['p0', 'p50', 'p100', 'p200', 'p400', 'p800', 'p1600', 'p3000', 'p5000', 'p8000', 'p12000', 'p16000', 'p20000',
       'pend'] + [f'r{i}' for i in range(1, 9)]
PT_STEPS = {'p0': 0, 'p50': 50, 'p100': 100, 'p200': 200, 'p400': 400, 'p800': 800, 'p1600': 1600, 'p3000': 3000,
            'p5000': 5000, 'p8000': 8000, 'p12000': 12000, 'p16000': 16000, 'p20000': 20000}
POOLS = ('tb72', 'h250')
SEEDS = (0, 1, 2)
_cache = {}


def _rows(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def read(cap, s, ck, pool, x):
    """per-theorem dict for one read, or None if that read does not exist."""
    key = (cap, s, ck, pool, x)
    if key in _cache:
        return _cache[key]
    path = None
    if cap == 12 and ck in ('pend', 'r8') and x in (2, 4, 10):
        if x == 2 and pool in ('tb72', 'h250', 'rrQ100', 'long2'):
            path = f'{MC}/mcts/s{s}_{ck}__{pool}__sample.jsonl'
        elif x == 4 and pool == 'C':
            path = f'{MC}/mcts/s{s}_{ck}__C__sample.jsonl'
        elif x == 10 and pool == 'C' and ck == 'r8':
            path = f'{MC}/mcts_x10/s{s}_r8__C__sample.jsonl'
    elif ck in CKS:
        sub = 'trajectory' if cap == 12 else 'trajectory-cap6'
        path = f'{OA}/{sub}/s{s}_{ck}__{pool}_x{x}.jsonl.gz'
    elif cap == 12 and ck in ('r12', 'r16') and x == 1:
        path = f'{RC}/s{s}_{ck}__{pool}_x1.jsonl'
    elif cap == 6 and ck == 'r16' and x == 1:
        path = f'{RC6}/s{s}_r16__' + ('tb72' if pool == 'tb72' else 'h250C') + '_x1.jsonl'
    if path is None or not os.path.exists(path):
        _cache[key] = None
        return None
    d = {}
    for r in _rows(path):
        d[r['name']] = (int(r['n_ok']), int(r['n_tried']), list(r.get('proofs') or []))
    _cache[key] = d
    return d


def names(pool):
    """theorem names of a pool, in file order (from the pend x0 read of cap-12 s0)."""
    return list(read(12, 0, 'pend', pool, 0).keys())


def all_names():
    return [n for p in POOLS for n in names(p)]


def pool_of():
    return {n: p for p in POOLS for n in names(p)}


def counts(cap, s, ck, x):
    """{name: (n_ok, n_tried)} over both pools for one checkpoint and draw (None if missing for both)."""
    out = {}
    for pool in POOLS:
        d = read(cap, s, ck, pool, x)
        if d:
            out.update({n: v[:2] for n, v in d.items()})
    return out or None


def refs():
    """reference (shortest known) ND proofs: {name: proof} for 315 of the 322 theorems."""
    return {r['name']: r['proof'] for r in _rows(f'{HOME}/work/trajectory/data/tj/ref_targets.jsonl')}


def prompts():
    out = {}
    for p, f in (('tb72', 'textbook72.jsonl'), ('h250', 'holdout250.jsonl')):
        for r in _rows(f'{HOME}/work/trajectory/data/bs/{f}'):
            out[r['name']] = r['prompt']
    return out
