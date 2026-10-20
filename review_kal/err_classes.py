#!/usr/bin/env python3
"""Own re-classification of KAL-D s2's 6,903 teacher-forced disagreements (artifacts/kalmar/tf/errors_kalD_s2__tf1200.errors.jsonl.gz),
with my own Lean-syntax formula parser, using the class definitions the run states (first match wins):
truncated / malformed / close-timing / exact-citation / same-formula / polarity / other-subformula (in the state) / corrupted.
Also: the share of declared formulas that are FALSE under the branch valuation read from the state's atom hypotheses
(scored only where every hypothesis in the state is true under it).  -> out/err_classes.json
"""
import collections, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

OPS = {'∧': '&', '∨': 'v', '→': '>'}


def pf(t, i):
    x = t[i]
    if x == '(':
        if t[i + 1] == '¬':
            a, j = pf(t, i + 2)
            if t[j] != ')':
                raise ValueError
            return ('~', a), j + 1
        a, j = pf(t, i + 1)
        op = t[j]
        if op not in OPS:
            raise ValueError
        b, k = pf(t, j + 1)
        if t[k] != ')':
            raise ValueError
        return (OPS[op], a, b), k + 1
    if x == 'False':
        return ('F',), i + 1
    if x in ('P', 'Q', 'R', 'S'):
        return ('a', x), i + 1
    raise ValueError(x)


def declared(act):
    t = act.split()
    if len(t) < 4 or t[0] != 'have' or t[2] != ':':
        raise ValueError
    f, j = pf(t, 3)
    if j >= len(t) or t[j] != ':=':
        raise ValueError
    return f


def subs(f, acc):
    acc.add(f)
    for g in f[1:] if f[0] not in ('a', 'F') else ():
        subs(g, acc)


def state_formulas(st):
    body = st.split('<st>', 1)[1].split('<act>')[0]
    hyps, goal = body.rsplit('⊢', 1) if '⊢' in body else (body, None)
    fs = []
    for part in hyps.split('<nl>'):
        part = part.strip()
        if ':' in part:
            t = part.split(':', 1)[1].split()
            if t:
                fs.append(pf(t, 0)[0])
    g = pf(goal.split(), 0)[0] if goal and goal.strip() else None
    return fs, g


c = collections.Counter(); truth = collections.Counter()
for r in kc.rows(os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'tf', 'errors_kalD_s2__tf1200.errors.jsonl.gz')):
    m, a = r['model'], r['algorithm']
    if m.endswith('…'):
        c['truncated'] += 1; continue
    mt, at = m.split(), a.split()
    if not mt or mt[0] not in ('have', 'exact'):
        c['malformed'] += 1; continue
    if mt[0] != at[0]:
        c['close-timing'] += 1; continue
    if mt[0] == 'exact':
        c['exact-citation'] += 1; continue
    try:
        fm = declared(m)
    except (ValueError, IndexError):
        c['malformed'] += 1; continue
    fa = declared(a)
    fs, g = state_formulas(r['state'])
    if fm == fa:
        cls = 'same-formula'
    elif fm == ('~', fa) or fa == ('~', fm):
        cls = 'polarity'
    else:
        pool = set()
        for f in fs + ([g] if g else []):
            subs(f, pool)
        cls = 'other-subformula' if fm in pool else 'corrupted'
    c[cls] += 1
    # truth of the declared formula under the valuation of the atom hypotheses, where all hypotheses are true under it
    v = {}
    for f in fs:
        if f[0] == 'a':
            v[f[1]] = True
        elif f[0] == '~' and f[1][0] == 'a':
            v[f[1][1]] = False
    ats = kc.atoms_in(fs + [fm, fa] + ([g] if g else []))
    if all(x in v for x in ats) and all(kc.val(f, v) for f in fs):
        truth['scored'] += 1
        truth['model_false'] += not kc.val(fm, v)
        truth['algo_false'] += not kc.val(fa, v)
        if not kc.val(fm, v):
            truth['false_' + cls] += 1
tot = sum(c.values())
out = {'n': tot, 'classes': {k: (v, round(100 * v / tot, 1)) for k, v in c.most_common()}, 'truth': dict(truth)}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'err_classes.json'), 'w'), indent=1)
