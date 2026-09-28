#!/usr/bin/env python3
"""Reviewer: controls first, then the sample.  Run from the review copy with REPO=. ; writes review_se/recheck.json"""
import json, glob, random, os, sys, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_recheck import translate, seq_render, check
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recheck.json')
rng = random.Random(20260928)
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
sample = collections.OrderedDict()
for d in sorted(glob.glob('artifacts/se/la_*')):
    fn = f'{d}/found_transfer_8.jsonl'
    if not os.path.exists(fn): continue
    F = rd(fn); T = rd(f'{d}/found_8.jsonl')
    longs = [x for x in F if x['L_true'] >= 12]
    rest = [x for x in F if x['L_true'] < 12]
    pick = longs + rng.sample(rest, min(120, len(rest))) + rng.sample(T, min(30, len(T)))
    sample[os.path.basename(d)] = [(x['prompt'], x['proof'], x['name'], x['L_true']) for x in pick]
for fn in sorted(glob.glob('artifacts/se/heldout_*.jsonl')):
    H = [r for r in rd(fn) if r['proofs']]
    pick = rng.sample(H, 100)
    sample[os.path.basename(fn)] = [(r['prompt'], r['proofs'][0], r['name'], r['n_lines']) for r in pick]

allitems = [(p, pf) for v in sample.values() for p, pf, _, _ in v]
# ---- controls ----
ctl = {}
base = rng.sample(allitems, 150)
def flip(pf):
    for a, b in (('ORI1', 'ORI2'), ('ANDE1', 'ANDE2')):
        if f': {a} ' in pf: return pf.replace(f': {a} ', f': {b} ', 1)
        if f': {b} ' in pf: return pf.replace(f': {b} ', f': {a} ', 1)
    return None
flips = [(p, flip(pf)) for p, pf in allitems if flip(pf)]
flips = rng.sample(flips, min(150, len(flips)))
def npr(p):
    lhs = p.split('SEQ')[0][3:].strip()
    return len(lhs.split(' , ')) if lhs else 0
byn = collections.defaultdict(list)
for p, pf in allitems: byn[npr(p)].append(p)
swap = []
for p, pf in rng.sample(allitems, 150):
    others = [q for q in byn[npr(p)] if q != p]
    if others: swap.append((rng.choice(others), pf))
rej = []
for fn in sorted(glob.glob('artifacts/se/heldout_*.jsonl')):
    for r in rd(fn):
        if not r['proofs'] and r['fail_example'] and r['fail_example'].startswith('LEANREJ '):
            rej.append((r['prompt'], r['fail_example'][8:]))
rej = rng.sample(rej, min(200, len(rej)))
def sorry_render(p, pf, nm):
    s = translate(p, pf, nm); return s[:s.index(':= by ') + 6] + 'sorry'
for rname, render in (('mine', translate), ('seq', seq_render)):
    c = {}
    c['untouched_pass'] = sum(ok for ok, _ in check(base, render)), len(base)
    c['flip_fail'] = sum(not ok for ok, _ in check(flips, render)), len(flips)
    c['swap_fail'] = sum(not ok for ok, _ in check(swap, render)), len(swap)
    rr = check(rej, render)
    c['leanrej_fail'] = sum(not ok for ok, _ in rr), len(rej)
    c['leanrej_passed_examples'] = [(p, pf) for (p, pf), (ok, _) in zip(rej, rr) if ok][:5]
    ctl[rname] = c
    print(rname, {k: v for k, v in c.items() if k != 'leanrej_passed_examples'}, flush=True)
ctl['sorry_fail'] = sum(not ok for ok, _ in check(base[:20], sorry_render)), 20
print('sorry', ctl['sorry_fail'], flush=True)
# ---- main pass ----
res = {}
for k, v in sample.items():
    items = [(p, pf) for p, pf, _, _ in v]
    a = check(items, translate); b = check(items, seq_render)
    res[k] = {'n': len(v), 'n_Ltrue_ge12': sum(1 for x in v if x[3] >= 12 and not k.startswith('heldout')),
              'mine_rejected': [(v[i][2], a[i][1]) for i in range(len(v)) if not a[i][0]],
              'seq_rejected': [(v[i][2], b[i][1]) for i in range(len(v)) if not b[i][0]]}
    print(k, res[k]['n'], 'ge12', res[k]['n_Ltrue_ge12'], 'rej mine', len(res[k]['mine_rejected']), 'seq', len(res[k]['seq_rejected']), flush=True)
json.dump({'controls': ctl, 'sample': res}, open(OUT, 'w'), indent=1)
