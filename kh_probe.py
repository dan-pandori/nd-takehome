#!/usr/bin/env python3
"""cap-horizon probe: the CONTROL's generator settings (gen.sample_one short mode, max_prem 3,
max_depth 3), output filter only -- what is the yield per pruned length at 7..14?
  python3 kh_probe.py --tries 200000 --seed 12345 --out artifacts/kh/probe_s12345.json
"""
import argparse, collections, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import Gen, sample_one, canon_key, Fail

ap = argparse.ArgumentParser()
ap.add_argument('--tries', type=int, default=100000)
ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--long', action='store_true')
ap.add_argument('--out', default=None)
a = ap.parse_args()
rng = random.Random(a.seed)
g = Gen(rng, max_prem=3, max_depth=3)
per_len = collections.Counter(); cls = collections.defaultdict(set)
stats = collections.Counter(); t0 = time.time()
for _ in range(a.tries):
    stats['tries'] += 1
    try:
        r = sample_one(g, rng, a.long)
    except (Fail, RecursionError):
        stats['fail'] += 1; continue
    L = r['n_lines']
    per_len[L] += 1
    if L >= 7:
        cls[L].add(canon_key(r['thm']))
out = {'tries': a.tries, 'seed': a.seed, 'long': a.long, 'fail': stats['fail'],
       'secs': round(time.time() - t0, 1),
       'raw_per_len': {str(k): per_len[k] for k in sorted(per_len)},
       'classes_per_len_ge7': {str(k): len(cls[k]) for k in sorted(cls)}}
print(json.dumps(out, indent=1))
if a.out:
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)
