"""organism-analysis: loaders for the inherited reads and per-step scores (pulled to data/oa_in/).

Runs: c12 = trajectory (best-cap12 s0-s2), c6 = trajectory-cap6 (best-cap6 s0-s2), rfc = rl-from-ckpt (best-cap12
s0-s2 ladders started at p1600 / p5000 / p12000 / p16000).  Checkpoint labels: p<step>, pend (= r0 of c12 / c6),
r1..r8; for rfc r0 = the start checkpoint (trajectory's p<X> read / score), r2, r4, r8, c8 (replay-only control).
"""
import functools, glob, gzip, json, math, os

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'oa_in')
RUNDIR = {'c12': 'trajectory', 'c6': 'trajectory-cap6', 'rfc': 'rl-from-ckpt'}
SCOREDIR = {'c12': 'tj', 'c6': 'tj6', 'rfc': 'rfc'}
SEEDS = (0, 1, 2)
STARTS = ('p1600', 'p5000', 'p12000', 'p16000')
PT = ['p0', 'p50', 'p100', 'p200', 'p400', 'p800', 'p1600', 'p3000', 'p5000', 'p8000', 'p12000', 'p16000', 'p20000',
      'pend']
PEND_STEP = {('c12', 0): 24077, ('c12', 1): 24345, ('c12', 2): 24328}   # trajectory summary; c6 from its summary
PEND_STEP.update({('c6', 0): 24511, ('c6', 1): 24120, ('c6', 2): 24113})   # trajectory-cap6 numbers.md


def step_of(ck, run='c12', seed=0):
    return PEND_STEP[(run, seed)] if ck == 'pend' else int(ck[1:])


@functools.lru_cache(maxsize=None)
def read(run, label, pool, x):
    """-> {name: (n_ok, n_tried, proofs)} for one stored read, or None if absent.
    run c12/c6: label s<S>_<ck>; rfc: s<S>_<X>_r<k> or c<S>_<X>_r8."""
    f = os.path.join(ROOT, 'reads', RUNDIR[run], f'{label}__{pool}_x{x}.jsonl.gz')
    if not os.path.exists(f):
        return None
    out = {}
    for l in gzip.open(f, 'rt'):
        d = json.loads(l)
        out[d['name']] = (int(d['n_ok']), int(d['n_tried']), d['proofs'] or [])
    return out


def read_both(run, label, x):
    a, b = read(run, label, 'tb72', x), read(run, label, 'h250', x)
    if a is None or b is None:
        return None
    return {**a, **b}


def rfc_label(seed, start, rnd):
    """the read label of rfc ladder (seed, start) at round rnd (0 = the start checkpoint, read by trajectory)."""
    if rnd == 0:
        return 'c12', f's{seed}_{start}'
    return 'rfc', f's{seed}_{start}_r{rnd}'


@functools.lru_cache(maxsize=None)
def score(run, seed, ck, start=None):
    """-> {tid: T1.0 summary dict with step_lp}.  rfc: ck in r0/r2/r4/r8/c8 under start."""
    if run == 'rfc':
        f = os.path.join(ROOT, 'rfc', 'score', f's{seed}_{start}', f's{seed}_{start}_{ck}.jsonl')
    else:
        f = os.path.join(ROOT, SCOREDIR[run], 'score', f's{seed}', f's{seed}_{ck}.jsonl')
    if not os.path.exists(f):
        return None
    return {d['tid']: d['T1.0'] for d in map(json.loads, open(f))}


@functools.lru_cache(maxsize=None)
def targets_meta(run, seed, start=None):
    """-> {tid: meta (actions_b0, step_kind, term_size, n_steps, ...)} from the scorer's targets.jsonl."""
    if run == 'rfc':
        f = os.path.join(ROOT, 'rfc', 'score', f's{seed}_{start}', 'targets.jsonl')
    else:
        f = os.path.join(ROOT, SCOREDIR[run], 'score', f's{seed}', 'targets.jsonl')
    return {d['tid']: d for d in map(json.loads, open(f))}


@functools.lru_cache(maxsize=None)
def ref_inputs():
    """-> {name: target input row (prompt, proof, pool, min_lines_ub)} for the 315 reference proofs."""
    out = {}
    for d in map(json.loads, open(os.path.join(ROOT, 'tj', 'targets', 'targets_s0.jsonl'))):
        if d['kind'] == 'ref':
            out[d['name']] = d
    return out


def nd_lines(proof):
    return sum(1 for s in proof.split(' ; ') if s.startswith('N'))
