#!/usr/bin/env python3
"""Shortcuts in term size: every Lean-accepted DEVIATING greedy attempt of KAL-D (s0-s2) and KAL-D+A (s0-s2) on tf1200,
its lean_check term size (project definition, run here) against the algorithm's proof of the same theorem; also its
action count.  -> out/termsize_dev.json
"""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc
sys.path.insert(0, kc.ROOT)
from state_env import decompose
import lean_check

SYM = {'~': '¬', '&': '∧', 'v': '∨', '>': '→', 'F': 'False'}


def header(prompt):
    p, g = kc.split_prompt(prompt)
    fm = lambda s: ' '.join(SYM.get(t, t) for t in s.split())
    return 'theorem t (P Q R S : Prop)' + ''.join(f' (h{i + 1} : {fm(x)})' for i, x in enumerate(p)) + f' : {fm(g)} := by '


recs = list(kc.rows(os.path.join(kc.ROOT, 'data', 'kalmar', 'tf1200_kal_sl.jsonl')))
algo_src = {}
items = []
for m in ('kalD_s0', 'kalD_s1', 'kalD_s2', 'kalDA_s0', 'kalDA_s1', 'kalDA_s2'):
    for r in kc.rows(os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'free', f'{m}__tf1200_greedy.rows.jsonl.gz')):
        if r['valid'] and not r['follow']:
            i = r['i']
            if i not in algo_src:
                steps, toks, env = decompose(recs[i]['prompt'], recs[i]['proof'], canon=True)
                algo_src[i] = header(recs[i]['prompt']) + re.sub(r' \.(elim|1|2)\b', r'.\1', ' '.join(toks))
            items.append((m, i, header(recs[i]['prompt']) + r['text'], r['n_actions'], r['algo_actions']))
ids = sorted(algo_src)
ra, _, _ = lean_check.check([algo_src[i] for i in ids], workers=1, chunk=100)
asz = {i: x['size'] for i, x in zip(ids, ra)}
rm, _, _ = lean_check.check([x[2] for x in items], workers=1, chunk=100)
out = collections.defaultdict(collections.Counter)
for (m, i, src, na, aa), x in zip(items, rm):
    c = out[m]
    c['n'] += 1; c['lean_check_ok'] += x['ok']
    if x['ok'] and asz.get(i):
        c['size_shorter'] += x['size'] < asz[i]; c['size_longer'] += x['size'] > asz[i]; c['size_equal'] += x['size'] == asz[i]
        c['size_sum'] += x['size']; c['algo_size_sum'] += asz[i]
    c['act_shorter'] += na < aa; c['act_longer'] += na > aa
res = {m: dict(c) for m, c in out.items()}
res['algo_ok'] = sum(x['ok'] for x in ra)
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'termsize_dev.json'), 'w'), indent=1)
