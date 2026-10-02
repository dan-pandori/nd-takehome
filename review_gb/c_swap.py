#!/usr/bin/env python3
"""Reviewer robustness: C' = theorems unsolved by EI pend (x0) and by EI r8 on sample seed 1; count C' solves on sample
seed 0 for EI r8 and each GRPO r8 (the pre-registered C with the two sample seeds swapped)."""
import json, os
R = os.path.expanduser('~/review/grpo-best/artifacts/gb')
def sv(f):
    s = set(); n = []
    for p in ('tb72', 'h250'):
        for l in open(f.format(p=p)):
            r = json.loads(l); n.append(r['name'])
            if r['n_ok']: s.add(r['name'])
    return s, n
for arm in ('EI', 'default', 'unlikely', 'passk'):
    row = []
    for s in (0, 1, 2):
        pe, names = sv(f'{R}/ei_eval/s{s}_pend__{{p}}_x0.jsonl')
        e1, _ = sv(f'{R}/ei_eval/s{s}_r8__{{p}}_x1.jsonl')
        C2 = [n for n in names if n not in pe and n not in e1]
        f = f'{R}/ei_eval/s{s}_r8__{{p}}_x0.jsonl' if arm == 'EI' else f'{R}/eval/gb_{arm}_s{s}_r8__{{p}}_x0.jsonl'
        x0, _ = sv(f)
        row.append((len(C2), sum(1 for n in C2 if n in x0)))
    print(arm, row, 'mean', sum(b for a, b in row) / 3)
