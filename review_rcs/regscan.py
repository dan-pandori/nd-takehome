#!/usr/bin/env python3
"""Reviewer: summarise a run's results registry by (role, phase, metric) — sums of value, row counts, arms."""
import json, glob, sys, collections
run = sys.argv[1]
rows = []
for f in sorted(glob.glob(f'/home/dan/work/{run}/artifacts/{run}/registry/*.jsonl')):
    for line in open(f):
        rows.append(json.loads(line))
c = collections.defaultdict(lambda: [0, 0.0, set(), set()])
for r in rows:
    if r['metric'] not in ('gpu_seconds', 'gen_tokens', 'train_tokens', 'train_steps', 'attempts', 'actions', 'lean_checks', 'prompt_tokens'):
        continue
    k = (r.get('role'), (r.get('labels') or {}).get('phase'), r['metric'])
    c[k][0] += 1; c[k][1] += r['value'] or 0; c[k][2].add(r.get('arm')); c[k][3].add((r.get('labels') or {}).get('gpu') or r.get('host'))
print(run, len(rows), 'rows')
for k in sorted(c, key=lambda k: tuple(str(x) for x in k)):
    n, s, arms, g = c[k]
    print(f'  {str(k[0]):10s} {str(k[1]):10s} {k[2]:13s} n={n:5d} sum={s:14.4g} arms={sorted(map(str, arms))[:8]}')
