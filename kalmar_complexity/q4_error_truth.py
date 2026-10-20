#!/usr/bin/env python3
"""Q4 extension: kalmar-pretrain's error_truth scoring (kalmar/error_truth.py, same rule) broken down by step type, and
the per-type rate of false-formula errors (per state) against the demand measures (run kalmar-complexity).
  python3 kalmar_complexity/q4_error_truth.py <errors_kalD_s2__tf1200.errors.jsonl.gz>
  (the file is in hf://buckets/dan-pandori/nd-rl/kalmar-pretrain/artifacts/kalmar/tf/)  -> artifacts/kc/q4/error_truth_by_type.json"""
import collections, gzip, json, os, sys
import numpy as np
from scipy import stats
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'kalmar'))
from state_env import parse_ftoks
from lean_tok import ParseFail
g = lambda t: 'close' if t.startswith('close:') else t


def ev(f, v):
    t = f[0]
    if t == 'atom': return v[f[1]]
    if t == 'bot': return False
    if t == 'not': return not ev(f[1], v)
    a, b = ev(f[1], v), ev(f[2], v)
    return (a and b) if t == 'and' else (a or b) if t == 'or' else ((not a) or b)


def hyps(state):
    toks, out, i = state.split(), [], 0
    while i < len(toks):
        if toks[i] == ':' and i > 0 and (toks[i - 1].startswith('n') or toks[i - 1].startswith('h')):
            f, used = parse_ftoks(toks, i + 1); out.append(f); i += 1 + used; continue
        i += 1
    return out


def declared(act):
    toks = act.split()
    if len(toks) < 4 or toks[0] != 'have':
        return None
    try:
        return parse_ftoks(toks, 3)[0]
    except ParseFail:
        return None


c = collections.defaultdict(collections.Counter)
for l in gzip.open(sys.argv[1], 'rt'):
    r = json.loads(l); t = g(r['tag'])
    c[t]['errors'] += 1
    try:
        H = hyps(r['state'])
    except ParseFail:
        continue
    v = {}
    for f in H:
        if f[0] == 'atom': v[f[1]] = True
        elif f[0] == 'not' and f[1][0] == 'atom': v[f[1][1]] = False
    fm = declared(r['model'])
    try:
        if not all(ev(f, v) for f in H):
            continue
        c[t]['scored'] += 1
        if fm is not None and not ev(fm, v):
            c[t]['model_false'] += 1
    except KeyError:
        continue
R = json.load(open(os.path.join(ROOT, 'artifacts/kc/q4/q4_results.json')))
PT = json.load(open(os.path.join(ROOT, 'artifacts/kc/q4/per_type.json')))['types']
types = R['types']
tot = collections.Counter()
for t in c: tot.update(c[t])
out = {'totals': dict(tot), 'by_type': {t: dict(c[t]) for t in c}, 'rho': {}}
y = [c[t]['model_false'] / PT[t]['states'] for t in types]
rng = np.random.default_rng(0)
for k in ('rasp_eff_depth', 'explored', 'log2_ops', 'decl_len', 'focus_h', 'py_bytes', 'log_freq'):
    x = [R['predictors'][t][k] for t in types]
    r = stats.spearmanr(x, y)[0]
    p = float(np.mean([abs(stats.spearmanr(x, rng.permutation(y))[0]) >= abs(r) - 1e-12 for _ in range(5000)]))
    out['rho'][k] = {'rho': float(r), 'p': p}
json.dump(out, open(os.path.join(ROOT, 'artifacts/kc/q4/error_truth_by_type.json'), 'w'), indent=1)
print('totals', dict(tot))
print('false-formula errors per state, by type:', {t: round(1000 * c[t]['model_false'] / PT[t]['states'], 1) for t in sorted(types, key=lambda t: -c[t]['model_false'] / PT[t]['states'])}, '(per 1,000 states)')
print('rho:', {k: (round(v['rho'], 2), round(v['p'], 3)) for k, v in out['rho'].items()})
