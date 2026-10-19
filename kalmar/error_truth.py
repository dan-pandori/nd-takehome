#!/usr/bin/env python3
"""How many teacher-forced disagreements assert a formula that is FALSE in the branch (run kalmar-pretrain)?

  python3 kalmar/error_truth.py artifacts/kalmar/tf/errors_kalD_s2__tf1200.errors.jsonl.gz

The branch valuation is read off the atom hypotheses in the state (`X` or `¬ X`).  Only states where every atom of every
hypothesis and of the declared formula is valued, and EVERY hypothesis is true under that valuation, are scored: there a
correct step can only declare a true formula (inside a ¬I box whose assumption is false, a false line is legitimate,
so those states are skipped).  Counts: scored disagreements, of which the declared formula is false; and, as a check,
how often the algorithm's own formula is false in the same states (must be 0).
"""
import collections, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_env import parse_ftoks
from lean_tok import ParseFail
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from error_classes import classify


def ev(f, v):
    t = f[0]
    if t == 'atom':
        return v[f[1]]
    if t == 'bot':
        return False
    if t == 'not':
        return not ev(f[1], v)
    a, b = ev(f[1], v), ev(f[2], v)
    return (a and b) if t == 'and' else (a or b) if t == 'or' else ((not a) or b)


def hyps(state):
    toks = state.split()
    out, i = [], 0
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
        f, used = parse_ftoks(toks, 3)
        return f
    except ParseFail:
        return None


rows = [json.loads(l) for l in gzip.open(sys.argv[1], 'rt')]
c = collections.Counter()
for r in rows:
    try:
        H = hyps(r['state'])
    except ParseFail:
        continue
    v = {}
    for f in H:
        if f[0] == 'atom':
            v[f[1]] = True
        elif f[0] == 'not' and f[1][0] == 'atom':
            v[f[1][1]] = False
    fm, fa = declared(r['model']), declared(r['algorithm'])
    try:
        if not all(ev(f, v) for f in H):
            continue
        c['scored'] += 1
        if fa is not None and not ev(fa, v):
            c['algorithm_false'] += 1
        if fm is not None and not ev(fm, v):
            c['model_false'] += 1
            c['model_false|' + classify(r)] += 1
    except KeyError:
        continue
print(f"{len(rows)} disagreements; scored (every hypothesis true, all atoms valued) {c['scored']}; model declares a false "
      f"formula {c['model_false']} ({100 * c['model_false'] / len(rows):.1f} % of all disagreements); algorithm false {c['algorithm_false']}")
print({k: v for k, v in c.items() if k.startswith('model_false|')})
