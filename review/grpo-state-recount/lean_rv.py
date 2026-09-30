#!/usr/bin/env python3
"""Reviewer (grpo-state): Lean re-check of counted proofs.  lean_recheck.py is the state-env reviewer's own ND -> Lean
translator (copied from review_se/, not executor code).  Per arm directory: up to 150 target proofs from the last
found_<r>.jsonl + every proof of the last found_transfer_<r>.jsonl.  Controls: rule flips must fail, sorry must be
flagged (sorryAx axiom), statement swaps must fail.  Run from the phase-1 copy: REPO=. python3 <this> """
import json, glob, random, os, sys, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_recheck import translate, seq_render, check
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lean_rv.json')
rng = random.Random(20260930)
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
def last(d, pat):
    fs = [f for f in glob.glob(f'{d}/{pat}_*.jsonl') if re.fullmatch(pat + r'_\d+\.jsonl', os.path.basename(f))]
    return max(fs, key=lambda f: int(re.findall(r'(\d+)\.jsonl', f)[0])) if fs else None
sample = collections.OrderedDict()
for d in sorted([x for x in glob.glob('artifacts/grpo_state/*/') if os.path.exists(x + 'args.json')]):
    arm = os.path.basename(d.rstrip('/')); items = []
    f = last(d, 'found'); T = rd(f)
    items += [('target', x) for x in rng.sample(T, min(150, len(T)))]
    ft = last(d, 'found_transfer')
    if ft: items += [('transfer', x) for x in rd(ft)]
    sample[arm] = items
res = {}
allitems = []
for arm, items in sample.items():
    pairs = [(x['prompt'], x['proof']) for _, x in items]
    bad_tok = [pf for _, pf in pairs if re.search(r'sorry|admit|exact\?|LEANREJ|LEANPARSE', pf)]
    r1 = check(pairs, translate); r2 = check(pairs, seq_render)
    res[arm] = {'n': len(pairs), 'n_target': sum(1 for s, _ in items if s == 'target'), 'n_transfer': sum(1 for s, _ in items if s == 'transfer'),
                'mine_ok': sum(ok for ok, _ in r1), 'seq_ok': sum(ok for ok, _ in r2), 'marker_or_sorry_in_text': len(bad_tok),
                'mine_rej': [(p, pf, why) for (p, pf), (ok, why) in zip(pairs, r1) if not ok][:5],
                'seq_rej': [(p, pf, why) for (p, pf), (ok, why) in zip(pairs, r2) if not ok][:5]}
    print(arm, {k: v for k, v in res[arm].items() if not k.endswith('_rej')}, flush=True)
    allitems += pairs
def flip(pf):
    for a, b in (('ORI1', 'ORI2'), ('ANDE1', 'ANDE2')):
        if f': {a} ' in pf: return pf.replace(f': {a} ', f': {b} ', 1)
        if f': {b} ' in pf: return pf.replace(f': {b} ', f': {a} ', 1)
    return None
flips = rng.sample([(p, flip(pf)) for p, pf in allitems if flip(pf)], 200)
swap = []
for p, pf in rng.sample(allitems, 200):
    q = rng.choice(allitems)[0]
    if q != p: swap.append((q, pf))
def sorry_render(p, pf, nm):
    s = translate(p, pf, nm); return s[:s.index(':= by ') + 6] + 'sorry'
ctl = {'flip_fail': (sum(not ok for ok, _ in check(flips, translate)), len(flips)),
       'swap_fail': (sum(not ok for ok, _ in check(swap, translate)), len(swap)),
       'sorry_fail': (sum(not ok for ok, _ in check(allitems[:100], sorry_render)), 100)}
print('controls', ctl, flush=True)
json.dump({'arms': res, 'controls': ctl}, open(OUT, 'w'), indent=1)
