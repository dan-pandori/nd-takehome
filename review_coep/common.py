"""review_coep/common.py -- reviewer's loaders for run create-or-elicit-paper (written independently of coe/ and paper/).

Paths are relative to RV_ROOT (default ~/review/create-or-elicit-paper, the phase-1 copy of the run repository).
"""
import gzip, json, os, collections

ROOT = os.environ.get('RV_ROOT', os.path.expanduser('~/review/create-or-elicit-paper'))
EVAL = os.path.join(ROOT, 'artifacts/coe_paper/eval')
CUTOFF = ('lean_seq parse: env: action truncated', 'lean_seq parse: env: step cap')
NAMES_EXH = 'lean_seq parse: env: names exhausted'


def P(*a):
    return os.path.join(ROOT, *a)


def jl(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as f:
        return [json.loads(l) for l in f if l.strip()]


def strict_names():
    return [l.strip() for l in open(P('data/coe/sigma_heldout_strict.txt')) if l.strip()]


def families():
    """classical family -> list of strict held-out member names (families.json, reviewed in create-or-elicit)."""
    d = json.load(open(P('data/coe/families.json')))['families']
    return {k: list(v['strict_heldout']) for k, v in d.items() if v['classical']}


def families_trained():
    d = json.load(open(P('data/coe/families.json')))['families']
    return {k: list(v['strict_trained']) for k, v in d.items() if v['classical']}


def bar(m):
    """>= 50 % of m members"""
    return (m + 1) // 2


def reasons_list(r):
    rs = r.get('reasons', [])
    if isinstance(rs, dict):
        out = []
        for k, v in rs.items():
            out += [k] * v
        return out
    return list(rs)


def read_rows(path):
    """state_eval rows -> {name: row}; asserts one row per name"""
    rows = jl(path)
    d = {}
    for r in rows:
        assert r['name'] not in d, (path, r['name'])
        d[r['name']] = r
    return d


def solved_set(rows):
    return {n for n, r in rows.items() if r['n_ok'] > 0}


def cutoffs(rows, names=None):
    """(attempts cut off by action/step caps, attempts, names-exhausted) over names"""
    c = t = ne = 0
    for n, r in rows.items():
        if names is not None and n not in names:
            continue
        rl = reasons_list(r)
        c += sum(1 for x in rl if x in CUTOFF)
        ne += sum(1 for x in rl if x == NAMES_EXH)
        t += r['n_tried']
    return c, t, ne


def fam_counts(solved, fams):
    return {f: len(set(m) & solved) for f, m in fams.items()}


def at_bar(solved, fams):
    return [f for f, m in fams.items() if len(set(m) & solved) >= bar(len(m))]
