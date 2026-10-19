"""Replicate controls.py's flip selection (same RNG sequence) and count how many flips are no-ops
(ORI on X v X, ANDE on X & X). No Lean needed; counts only."""
import gzip, json, random, sys
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
from nd import parse_prompt, Proof
rng = random.Random(7)
K = [json.loads(l) for l in gzip.open('/home/dan/review/proof-strategies/data/ps/in/train_k12.jsonl.gz', 'rt')]
sample = rng.sample(K, 600)
by_np = {}
for r in K[:20000]:
    p, c = parse_prompt(r['prompt'])
    by_np.setdefault(len(p), []).append((p, c, r['thm']))
for r in sample[300:500]:
    p, c = parse_prompt(r['prompt'])
    while True:
        p2, c2, t2 = rng.choice(by_np[len(p)])
        if t2 != r['thm']:
            break
fl = 0; noop = 0
for r in K[1000:]:
    if fl >= 200:
        break
    p, c = parse_prompt(r['prompt'])
    P = Proof(p, c, r['proof'])
    cand = [k for k in P.order if P.L[k]['rule'] in ('ORI1', 'ORI2', 'ANDE1', 'ANDE2')]
    if not cand:
        continue
    k = rng.choice(cand)
    fl += 1
    x = P.L[k]
    if x['rule'] in ('ORI1', 'ORI2'):
        f = x['f']; noop += (f[1] == f[2])
    else:
        a = P.L[x['refs'][0]]['f']; noop += (a[1] == a[2])
print({'flips': fl, 'no_op_flips': noop})
