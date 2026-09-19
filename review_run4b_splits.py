"""Reviewer split check for round3-run4b: renaming-class disjointness between every training file and every evaluation pool.
Own class key (review_run4b_lib.key_ordered / key_sorted: least text over the 24 atom permutations; premises in order / sorted)."""
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_run4b_lib import key_ordered, key_sorted, prompt_to_thm, max_depth_written, n_written
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def keys(rows):
    ko, ks = set(), set()
    for r in rows:
        thm = prompt_to_thm(r['prompt'])
        ko.add(key_ordered(thm)); ks.add(key_sorted(thm))
    return ko, ks
train = rd('data/p2/train_depth3_f0_a1.jsonl')
print('train records', len(train), 'n_lines', sorted(collections.Counter(r['n_lines'] for r in train).items()))
d = collections.Counter(max_depth_written(r['proof']) for r in train)
print('train written max depth hist', sorted(d.items()), '-> depth>=3 proofs in the Stage-1 set:', sum(v for k, v in d.items() if k >= 3))
tko, tks = keys(train)
print('train classes ordered / sorted', len(tko), len(tks))
pools = {'req (RL+eval, 300)': rd('data/r3_1/depth3_req.jsonl'), 'req_transfer (100)': rd('data/r3_1/depth3_req_transfer.jsonl'),
         'neighbours (300)': rd('data/r3_1/depth3_nb.jsonl'), 'optional pool (first 300 of targets_depth3)': rd('data/p2/targets_depth3.jsonl')[:300],
         'heldout (5000)': rd('data/p2/heldout.jsonl')}
for f in ('targets/test_short_prompts.jsonl', 'targets/test_long_prompts.jsonl'):
    if os.path.exists(f): pools[f] = rd(f)
K = {}
for n, rows in pools.items():
    ko, ks = keys(rows); K[n] = (ko, ks)
    print(f'{n}: rows {len(rows)} classes {len(ko)}/{len(ks)} | overlap with Stage-1 train: ordered {len(ko & tko)} sorted {len(ks & tks)}')
mix = rd('data/r3_1/depth3_mix.jsonl'); mko, mks = keys(mix)
print('mix pool rows', len(mix), 'classes', len(mko), len(mks), '= req U nb?', mko == K['req (RL+eval, 300)'][0] | K['neighbours (300)'][0])
for n in pools:
    if n.startswith('req (') or n.startswith('neigh'): continue
    print(f'EI training pool (mix) vs {n}: ordered {len(mko & K[n][0])} sorted {len(mks & K[n][1])}')
print('req vs neighbours: ordered', len(K['req (RL+eval, 300)'][0] & K['neighbours (300)'][0]), 'sorted', len(K['req (RL+eval, 300)'][1] & K['neighbours (300)'][1]))
print('req vs req_transfer: sorted', len(K['req (RL+eval, 300)'][1] & K['req_transfer (100)'][1]))
print('within-pool duplicate classes: req', 300 - len(K['req (RL+eval, 300)'][1]), 'transfer', 100 - len(K['req_transfer (100)'][1]), 'nb', 300 - len(K['neighbours (300)'][1]))
