#!/usr/bin/env python3
"""Reviewer Lean re-check for run textbook72: every stored accepted proof of every checkpoint, two renderings
(mine: own ND -> Lean translator; seq: lean_tok rendering of the lean_seq text), plus negative controls.
  REPO=~/review/textbook72 python3 review_tb72_lean_recheck.py OUT.json"""
import json, os, sys, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_tb72_lean_lib import translate, seq_render, check
REPO = os.environ['REPO']; OUT = sys.argv[1]
rng = random.Random(20260930)
items = []   # (ckpt, name, prompt, proof)
for fn in sorted(os.listdir(f'{REPO}/artifacts/textbook72/eval')):
    if not fn.endswith('.jsonl'): continue
    for l in open(f'{REPO}/artifacts/textbook72/eval/{fn}'):
        r = json.loads(l)
        for p in r['proofs']: items.append((fn[:-6], r['name'], r['prompt'], p))
res = {'n': len(items)}
pp = [(p, pf) for _, _, p, pf in items]
for tag, render in (('mine', translate), ('seq', seq_render)):
    rr = check(pp, render)
    by = collections.defaultdict(lambda: [0, 0]); bad = []
    for (c, n, p, pf), (ok, why) in zip(items, rr):
        by[c][0] += ok; by[c][1] += 1
        if not ok: bad.append((c, n, p, pf, why))
    res[tag] = {'per_ckpt': dict(by), 'rejected': bad[:50], 'n_rejected': len(bad)}
    print(tag, dict(by), len(bad), flush=True)
# controls (must be rejected)
def flip(pf):
    for a, b in (('ORI1', 'ORI2'), ('ANDE1', 'ANDE2')):
        if f': {a} ' in pf: return pf.replace(f': {a} ', f': {b} ', 1)
        if f': {b} ' in pf: return pf.replace(f': {b} ', f': {a} ', 1)
    return None
flips = [(p, flip(pf)) for p, pf in pp if flip(pf)]
flips = rng.sample(flips, min(300, len(flips)))
prompts = sorted({p for p in pp for p in [p[0]]})
def npr(p):
    lhs = p.split('SEQ')[0][3:].strip(); return len(lhs.split(' , ')) if lhs else 0
swap = []
for p, pf in rng.sample(pp, 300):
    q = rng.choice([x for x in prompts if x != p and npr(x) == npr(p)] or [x for x in prompts if x != p])
    swap.append((q, pf))
def sorry_render(p, pf, nm):
    s = translate(p, pf, nm); i = s.rfind('exact ')
    return s[:i] + 'sorry'
sor = rng.sample(pp, 100)
res['controls'] = {}
for tag, its, rend in (('flip', flips, translate), ('swap_prompt', swap, translate), ('sorry', sor, sorry_render)):
    rr = check(its, rend)
    res['controls'][tag] = {'n': len(its), 'accepted': sum(ok for ok, _ in rr)}
    print('control', tag, res['controls'][tag], flush=True)
json.dump(res, open(OUT, 'w'), indent=1)
