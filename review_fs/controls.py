"""Reviewer negative/positive controls for rv/leanrc.py, on arm C's stored literal texts (stage1-dynamics)."""
import json, random, sys, os
sys.path.insert(0, 'rv'); sys.path.insert(0, '.')
from leanrc import check
recs = [json.loads(l) for l in open('data/p2/heldout.jsonl')]
rng = random.Random(7)
C = {s: [json.loads(l) for l in open(f'rv/oldc/c_s{s}.jsonl')] for s in range(8)}
ok_items, rej_items = [], []
for s in range(8):
    for i, r in enumerate(C[s]):
        assert r['name'] == recs[i]['name']
        if r['lean_ok']: ok_items.append((s, i))
        elif r['parsed']: rej_items.append((s, i))
print('C counted', len(ok_items), 'parsed-rejected', len(rej_items))
pos = rng.sample(ok_items, 60)
neg_rej = rng.sample(rej_items, 60)
T = lambda s, i: C[s][i]['text']
P = lambda i: recs[i]['prompt']
flips = []
for s, i in rng.sample(ok_items, 400):
    t = T(s, i)
    for a, b in (('Or.inl', 'Or.inr'), ('Or.inr', 'Or.inl'), ('.1 ', '.2 '), ('.2 ', '.1 ')):
        if a in t:
            flips.append((P(i), t.replace(a, b, 1))); break
    if len(flips) >= 60: break
bynp = {}
for i, r in enumerate(recs): bynp.setdefault(r['n_prem'], []).append(i)
mism = []
for s, i in rng.sample(ok_items, 60):
    j = rng.choice([j for j in bynp[recs[i]['n_prem']] if recs[j]['thm'] != recs[i]['thm']])
    mism.append((P(j), T(s, i)))
trunc = []
for s, i in rng.sample(ok_items, 30):
    w = T(s, i).split(); trunc.append((P(i), ' '.join(w[:max(1, len(w) - 3)])))
sorry = [(P(i), 'sorry') for s, i in rng.sample(ok_items, 5)]
groups = [('untouched counted (must pass)', [(P(i), T(s, i)) for s, i in pos], True),
          ('recorded parsed-but-rejected (must fail)', [(P(i), T(s, i)) for s, i in neg_rej], False),
          ('one Or.inl/inr or .1/.2 flip (nearly all fail)', flips, False),
          ('proof paired with other theorem, same #premises (must fail)', mism, False),
          ('last 3 tokens dropped (must fail)', trunc, False),
          ('bare sorry (must fail)', sorry, False)]
allit = [x for _, it, _ in groups for x in it]
res = check(allit)
k = 0
for name, it, want in groups:
    r = res[k:k + len(it)]; k += len(it)
    print(f'{name}: n={len(it)} accepted={sum(r)}')
k = len(pos) + len(neg_rej)
for (p, t), r in zip(flips, res[k:k + len(flips)]):
    if r: print('ACCEPTED FLIP:', p, '||', t[:300])
