#!/usr/bin/env python3
"""coe-dose01: every accepted proof of a strict sigma-covered held-out member (the 106 that the figure's y counts; the same
sets as coe/coe_rounds.py) from a ladder's last found_transfer file, one row per distinct proof with the round that first
sampled it.  Small enough to pull and Lean-check (the found files stay on the pod / in the bucket).
  python3 coe/d01_heldout_proofs.py --dir artifacts/coe/ladder/la_dose01_s0 --out artifacts/coe/rounds/heldout_proofs_la_dose01_s0.jsonl.gz"""
import argparse, collections, gzip, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from coe.coe_rounds import last_file, read_jsonl

ap = argparse.ArgumentParser()
ap.add_argument('--dir', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--families', default='data/coe/families.json')
a = ap.parse_args()
fam = json.load(open(a.families))
sets_ho = {f: d['strict_heldout'] for f, d in fam['families'].items() if d['classical']}
if fam['generated_classical']['transfer']['strict']:
    sets_ho['generated'] = fam['generated_classical']['transfer']['strict']
member = {n: f for f, m in sets_ho.items() for n in m}
lt = last_file(a.dir, 'found_transfer')
n, first = 0, {}
with gzip.open(a.out, 'wt') as g:
    for x in read_jsonl(lt[1]):
        if x['name'] in member:
            g.write(json.dumps({'name': x['name'], 'family': member[x['name']], 'round': x['round'], 'thm': x['thm'],
                                'prompt': x['prompt'], 'proof': x['proof'], 'written': x['written'], 'pruned': x['pruned']}) + '\n')
            n += 1
            first[x['name']] = min(first.get(x['name'], 99), x['round'])
by_r = collections.Counter(first.values())
cum, s = {}, 0
for r in range(1, max(by_r, default=0) + 1):
    s += by_r.get(r, 0); cum[r] = s
print(f'{lt[1]}: {n} proofs of {len(first)} / {len(member)} strict held-out members; cumulative members by round {cum}')
