#!/usr/bin/env python3
"""Reviewer (grpo-state): which ORI1/ORI2/ANDE1/ANDE2 flip controls pass Lean -- are they all symmetric (A v A / A & A)?"""
import json, glob, re, os, sys, random, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lean_recheck import translate, check
LINE = re.compile(r'N(\d+) ((?:\| )*)(.*) : (\w+)((?: N\d+)*)')
SW = {'ORI1': 'ORI2', 'ORI2': 'ORI1', 'ANDE1': 'ANDE2', 'ANDE2': 'ANDE1'}
def halves_equal(g):
    toks = g[2:-2].split(' '); depth = 0
    for i, t in enumerate(toks):
        if t == '(': depth += 1
        elif t == ')': depth -= 1
        elif depth == 0 and t in ('v', '&'):
            return toks[:i] == toks[i + 1:]
    return False
def flip(pf):
    parts = pf.split(' ; '); P = {}
    for s in parts:
        m = LINE.fullmatch(s.strip())
        if m: P[int(m.group(1))] = m
    for k, s in enumerate(parts):
        m = LINE.fullmatch(s.strip())
        if m and m.group(4) in SW:
            r = m.group(4); ref = int(m.group(5).split()[0][1:])
            g = m.group(3).strip() if r.startswith('ORI') else P[ref].group(3).strip()
            q = parts[:]; q[k] = s.replace(': ' + r, ': ' + SW[r], 1)
            return ' ; '.join(q), halves_equal(g)
    return None
items = []
for f in sorted(glob.glob('artifacts/grpo_state/*/found_*.jsonl')):
    items += [json.loads(l) for l in open(f)]
random.Random(5).shuffle(items)
fl = [(x['prompt'],) + z for x in items for z in [flip(x['proof'])] if z][:400]
res = check([(p, q) for p, q, _ in fl], translate)
c = collections.Counter(f'sym={s} lean_ok={ok}' for (_, _, s), (ok, _) in zip(fl, res))
print(dict(c)); json.dump(dict(c), open(f'{HERE}/flip_why.json', 'w'))
