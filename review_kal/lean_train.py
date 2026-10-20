#!/usr/bin/env python3
"""K12-Kalmár validity with no run code at all: my builder (kc.kalmar) -> my ND->Lean renderer (rlean.render) -> my Lean
harness (rlean.check, Lean 4.34.1, axioms check), on a seeded sample of the 155,000 theorems plus every read set's
algorithm proofs; controls: one Or.inl/Or.inr flip at an ORI line (must mostly fail), proof paired with another theorem of
the same premise count (must fail).

  python3 review_kal/lean_train.py [--n 400] -> out/lean_train.json
"""
import argparse, collections, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc, rlean

ap = argparse.ArgumentParser()
ap.add_argument('--n', type=int, default=400)
a = ap.parse_args()
rng = random.Random(99)
pick = set(rng.sample(range(155000), a.n))
prompts = [json.loads(l)['prompt'] for i, l in enumerate(kc.opener(os.path.join(kc.ROOT, 'data', 'kalmar', 'train_kal_sl.jsonl.gz'))) if i in pick]
for fn in ('tf1200_kal_sl.jsonl', 'g1_premises.jsonl', 'g2_large.jsonl', 'g3_classical.jsonl', 'hand_proved_14_kal_sl.jsonl', 'ge17_kal_sl.jsonl'):
    rs = list(kc.rows(os.path.join(kc.ROOT, 'data', 'kalmar', fn)))
    prompts += [r['prompt'] for r in rng.sample(rs, min(40, len(rs)))]
items = [(p, rlean.render(p, kc.kalmar(p)['proof'])) for p in prompts]
res = rlean.check_robust(items)
ok = sum(x[0] for x in res)
out = {'n': len(items), 'accepted': ok, 'fails': [rlean.stmt(items[i][0])[1] and i for i, x in enumerate(res) if not x[0]][:10]}
# controls
fl = []
for p, t in items[:200]:
    nd = kc.kalmar(p)['proof']
    if ' : ORI1 ' in nd or ' : ORI2 ' in nd:
        fl.append((p, rlean.render(p, nd, flip=('Or.inl', 'Or.inr'))))
r2 = rlean.check_robust(fl)
by_np = collections.defaultdict(list)
for p, t in items:
    by_np[len(kc.split_prompt(p)[0])].append(p)
mis = [(rng.choice([q for q in by_np[len(kc.split_prompt(p)[0])] if q != p]), t) for p, t in items[:150]]
r3 = rlean.check_robust(mis)
out['controls'] = {'flip_all_ORI_lines': {'n': len(fl), 'passed': sum(x[0] for x in r2)}, 'mismatched': {'n': len(mis), 'passed': sum(x[0] for x in r3)}}
print(json.dumps(out))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'lean_train.json'), 'w'), indent=1)
