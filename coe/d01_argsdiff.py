#!/usr/bin/env python3
"""coe-dose01: every difference between a 0.1 % ladder's args.json and the 1 % ladder's of the same seed (keys and the
argv in _meta).  python3 coe/d01_argsdiff.py [--out artifacts/coe-dose01/argsdiff.md]"""
import argparse, json
ap = argparse.ArgumentParser(); ap.add_argument('--out'); a = ap.parse_args()
L = ['| seed | key | 1 % (`la_dose1_s<S>`) | 0.1 % (`la_dose01_s<S>`) |', '|---|---|---|---|']
for s in range(3):
    x = json.load(open(f'artifacts/coe/ladder/la_dose1_s{s}/args.json')); y = json.load(open(f'artifacts/coe/ladder/la_dose01_s{s}/args.json'))
    for k in sorted(set(x) | set(y)):
        if k == '_meta':
            for m in sorted(set(x[k]) | set(y[k])):
                if x[k].get(m) != y[k].get(m):
                    L.append(f'| s{s} | _meta.{m} | `{x[k].get(m)}` | `{y[k].get(m)}` |')
        elif x.get(k) != y.get(k):
            L.append(f'| s{s} | {k} | `{x.get(k)}` | `{y.get(k)}` |')
txt = '\n'.join(L); print(txt)
if a.out: open(a.out, 'w').write(txt + '\n')
