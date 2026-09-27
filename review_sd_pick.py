#!/usr/bin/env python3
# (reviewer of run stage1-dynamics; independent of the executor.  Phase 1 was run in ~/review/stage1-dynamics.)
"""Pick the counted proofs I will re-check in Lean: >=100 per arm, stratified over
seeds and over all six reported slices (len2..len6 and the depth-3 slice)."""
import json, random, collections, os, sys

ARMS = {'C': ['c_s%d' % s for s in range(8)],
        'W-24k': ['w_s%d' % s for s in range(8)],
        'W-6k': ['w6_s%d' % s for s in range(8)],
        'W-12k': ['w12_s%d' % s for s in range(8)],
        'F': ['f_s%d' % s for s in range(4)]}
PER_ARM = 120
rng = random.Random(20260927)
held = {r['name']: r for r in (json.loads(l) for l in open('data/p2/heldout.jsonl'))}

spec = {}
for arm, stems in ARMS.items():
    pool = collections.defaultdict(list)   # slice -> [(stem, rec)]
    for st in stems:
        p = f'artifacts/sd/ev/{st}.jsonl'
        for l in open(p):
            r = json.loads(l)
            if not r['lean_ok']:
                continue
            h = held[r['name']]
            key = 'depth3' if h['pat']['depth3'] else 'len%d' % h['n_lines']
            pool[key].append((st, r))
    keys = sorted(pool)
    per = PER_ARM // len(keys) + 1
    picked = []
    for k in keys:
        picked += rng.sample(pool[k], min(per, len(pool[k])))
    rng.shuffle(picked)
    picked = picked[:PER_ARM]
    spec[arm] = [{'name': r['name'], 'text': r['text'], 'ckpt': st,
                  'n_tok': r['n_tok'], 'n_have': r['n_have'],
                  'slice': 'depth3' if held[r['name']]['pat']['depth3'] else 'len%d' % held[r['name']]['n_lines']}
                 for st, r in picked]
    print(arm, len(spec[arm]), 'from', len({x['ckpt'] for x in spec[arm]}), 'checkpoints',
          dict(sorted(collections.Counter(x['slice'] for x in spec[arm]).items())))

# pass@8 examples: the literal text of one accepted sample per solved theorem
for f in sorted(os.listdir('artifacts/sd/passk')):
    if not f.endswith('.jsonl'):
        continue
    recs = [json.loads(l) for l in open('artifacts/sd/passk/' + f)]
    ok = [r for r in recs if r.get('solved_at_k') and r.get('example')]
    pick = rng.sample(ok, min(40, len(ok)))
    tag = 'passk:' + f[:-len('.depth3.k8.jsonl')]
    spec[tag] = [{'name': r['name'], 'text': r['example'], 'ckpt': f, 'slice': 'depth3'} for r in pick]
    print(tag, len(spec[tag]), 'of', len(ok), 'solved')

json.dump(spec, open('review_sd_leanspec.json', 'w'), indent=1)
print('total', sum(len(v) for v in spec.values()))
