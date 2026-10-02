"""C5/C6 leakage: evaluation theorems (textbook72 + holdout250, prompts from the raw reads) vs training sets of the models
(K12 800b5486 for best-cap12; cap-6 set 29276f24 for best-cap6; RL targets 365450be, which the ladders train on),
class = atom renaming + premise order (audit/scripts/canon.py, claim-audit's own canonicaliser)."""
import json, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canon import canon
H = os.path.expanduser('~')
ev = {}
for f in glob.glob(H + '/work/trajectory/artifacts/tj/eval/s0_pend__*_x0.jsonl'):
    for l in open(f):
        r = json.loads(l); ev[r['name']] = canon(r['prompt'])
print('eval theorems', len(ev))
inv = {}
for n, k in ev.items(): inv.setdefault(k, []).append(n)
for lab, path in (('K12', H + '/work/best-state/data/kh/train_k12.jsonl'), ('cap6', H + '/work/best-state/data/p2/train_depth3_f0_a1.jsonl'),
                  ('rl_targets', H + '/work/trajectory/data/ladder/rl_targets.jsonl')):
    hits = set(); n = 0
    for l in open(path):
        r = json.loads(l); n += 1
        k = canon(r['prompt'])
        if k in inv: hits.update(inv[k])
    print(f'{lab}: {n} records; eval theorems sharing a class: {len(hits)} {sorted(hits)}')
