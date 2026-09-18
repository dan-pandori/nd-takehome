#!/usr/bin/env python3
"""Run 4 base reachability: for each draw and source arm, the base-model (own Stage-1) log-probabilities of the DEPTH-3
proofs found (novelty.py output, start-index marginalised, T = 0.8). python3 run4_novelty.py [--out artifacts/r4/novelty_summary.json]"""
import json, glob, math, os, sys, argparse, statistics, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patterns import classify
L256, L1E4, L1E5 = math.log(1 / 256), math.log(1e-4), math.log(1e-5)
ap = argparse.ArgumentParser(); ap.add_argument('--out', default='artifacts/r4/novelty_summary.json'); a = ap.parse_args()
res = {}
print(f"{'draw':5s} {'src':16s} {'d3 proofs':>9s} {'<1/256':>7s} {'<1e-4':>6s} {'<1e-5':>6s} {'median':>7s} {'max':>7s} | {'d3 thms':>7s} {'thm>1/256':>9s} {'thm<1e-5':>8s}")
for fn in sorted(glob.glob('artifacts/r4/novelty_depth3_f0_a1_s*_proofs.jsonl')):
    draw = int(fn.split('_s')[-1].split('_')[0])
    recs = [json.loads(l) for l in open(fn) if l.strip()]
    thms = {(t['src'], t['name']): t for t in (json.loads(l) for l in open(fn.replace('_proofs', '_theorems')) if l.strip())}
    cache = {}
    by = collections.defaultdict(list)
    for r in recs:
        pn = r['proof']
        if pn not in cache:
            cache[pn] = classify(pn)
        cl = cache[pn]
        if cl and cl['depth3']:
            by[r['src']].append(r)
    res[draw] = {}
    for src, rs in sorted(by.items()):
        lp = [r['base_logp_T08'] for r in rs]
        names = {r['name'] for r in rs}
        # per theorem: log of summed probability over that theorem's depth-3 proofs is not in the theorems file (it sums all
        # proofs); use the max over depth-3 proofs as the theorem's value (lower bound of the sum)
        tmax = collections.defaultdict(lambda: -1e9)
        for r in rs:
            tmax[r['name']] = max(tmax[r['name']], r['base_logp_T08'])
        d = {'n_depth3_proofs': len(rs), 'below_1_256': sum(x < L256 for x in lp), 'below_1e4': sum(x < L1E4 for x in lp), 'below_1e5': sum(x < L1E5 for x in lp),
             'median_logp_T08': statistics.median(lp), 'max_logp_T08': max(lp), 'n_depth3_theorems': len(names),
             'theorems_above_1_256': sum(v > L256 for v in tmax.values()), 'theorems_below_1e5': sum(v < L1E5 for v in tmax.values())}
        res[draw][src] = d
        print(f"s{draw:<4d} {src:16s} {d['n_depth3_proofs']:9d} {d['below_1_256']:7d} {d['below_1e4']:6d} {d['below_1e5']:6d} {d['median_logp_T08']:7.1f} {d['max_logp_T08']:7.2f} | {d['n_depth3_theorems']:7d} {d['theorems_above_1_256']:9d} {d['theorems_below_1e5']:8d}")
json.dump(res, open(a.out, 'w'), indent=1)
