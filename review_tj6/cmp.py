#!/usr/bin/env python3
"""Compare reviewer re-scores (rv6/b0_*, b0cross_*: base 0; full_*: 33-base marginal) with the executor's score files."""
import json, glob, os, re, collections
R = os.path.expanduser('~/review/trajectory-cap6'); S = f'{R}/artifacts/tj6/score'
lab = lambda f: 'p1600' if 'step1600' in f else ('r8' if '_r8' in f else 'pend')
rows = []
for f in sorted(glob.glob(f'{R}/rv6/b0_*.jsonl') + glob.glob(f'{R}/rv6/b0cross_*.jsonl') + glob.glob(f'{R}/rv6/full_*.jsonl')):
    b = os.path.basename(f); s = int(re.search(r'_s(\d)_', b).group(1)); ck = lab(b)
    d = f'{S}/cross_s{s}' if b.startswith('b0cross') else f'{S}/s{s}'
    ex = {json.loads(l)['tid']: json.loads(l)['T1.0'] for l in open(f'{d}/s{s}_{ck}.jsonl')}
    for l in open(f):
        m = json.loads(l); e = ex[m['tid']]
        if m['b0only']: rows.append((b, m['tid'], abs(sum(m['b0_steps']) - e['raw_b0_total']), None))
        else: rows.append((b, m['tid'], abs(m['total'] - e['total']), abs(min(m['step_lp']) - e['w1'])))
by = collections.defaultdict(list)
for f, t, d, dw in rows: by[f].append(d)
for f, v in by.items(): print(f'{f}: n {len(v)} max |diff| {max(v):.5f}')
print('overall n', len(rows), 'max', max(r[2] for r in rows), 'n>0.01', sum(r[2] > 0.01 for r in rows))
full = [r for r in rows if r[3] is not None]
if full: print('full-marginal targets', len(full), 'max |dtotal|', max(r[2] for r in full), 'max |dw1|', max(r[3] for r in full))
