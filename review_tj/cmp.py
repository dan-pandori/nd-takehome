#!/usr/bin/env python3
"""Compare reviewer scores (rv/full/*.jsonl full marginal; rv/b0_*.jsonl base 0) with the executor's score files."""
import json, glob, os, re
R = os.path.expanduser('~/review/trajectory'); S = f'{R}/artifacts/tj/score'
lab = lambda f: 'p1600' if 'step1600' in f else ('r8' if '_r8' in f else 'pend')
rows = []
for f in sorted(glob.glob(f'{R}/rv/full/*.jsonl') + glob.glob(f'{R}/rv/b0_*.jsonl')):
    s = int(re.search(r'_s(\d)', os.path.basename(f)).group(1)); ck = lab(f) if 'full_' not in f else 'pend'
    ex = {json.loads(l)['tid']: json.loads(l)['T1.0'] for l in open(f'{S}/s{s}/s{s}_{ck}.jsonl')}
    for l in open(f):
        m = json.loads(l); e = ex[m['tid']]
        if m['b0only']:
            d = abs(sum(m['b0_steps']) - e['raw_b0_total']); dw = None
        else:
            d = abs(m['total'] - e['total']); dw = abs(min(m['step_lp']) - min(e['step_lp']))
        rows.append((os.path.basename(f), m['tid'], d, dw))
import collections
by = collections.defaultdict(list)
for f, t, d, dw in rows: by[f].append(d)
for f, v in by.items(): print(f'{f}: n {len(v)} max |diff| {max(v):.5f}')
print('overall n', len(rows), 'max', max(r[2] for r in rows), 'n>0.01', sum(r[2] > 0.01 for r in rows))
full = [r for r in rows if r[3] is not None]
if full: print('full-marginal targets', len(full), 'max |dw1|', max(r[3] for r in full))
